import os
import asyncio
from typing import List, Optional

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, case

from database import SessionLocal, init_db
import models, schemas
from websocket_manager import WebSocketManager
from emailer import send_failure_alert
from utils import utcnow

app = FastAPI(title="CI/CD Pipeline Health API", version="0.1.3")

# ----------------------------- CORS -----------------------------
# For quick dev, set CORS_ALLOW_ALL=1 (default). For strict, set CORS_ALLOW_ALL=0
# and (optionally) FRONTEND_ORIGINS="http://localhost:5173,http://127.0.0.1:5173"
CORS_ALLOW_ALL = os.getenv("CORS_ALLOW_ALL", "1") == "1"
if CORS_ALLOW_ALL:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=".*",
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        allow_credentials=False,
    )
else:
    origins_from_env = os.getenv("FRONTEND_ORIGINS") or os.getenv("FRONTEND_ORIGIN", "")
    parsed = [o.strip().rstrip("/") for o in origins_from_env.split(",") if o.strip()]
    defaults = ["http://localhost:5173", "http://127.0.0.1:5173"]
    allowed_origins = list({*parsed, *defaults})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        allow_credentials=False,
    )

# Handle stray preflights explicitly
@app.options("/{rest_of_path:path}")
def cors_preflight(rest_of_path: str):
    return Response(status_code=204)

# ----------------------------- DB -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

init_db()

# ----------------------------- WS -----------------------------
ws_manager = WebSocketManager()

@app.get("/health")
def health():
    return {"ok": True, "time": utcnow().isoformat()}

@app.websocket("/ws/metrics")
async def ws_metrics(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)

# ----------------------------- Helpers -----------------------------
def get_or_create_pipeline(db: Session, name: str) -> models.Pipeline:
    pipeline = db.execute(select(models.Pipeline).where(models.Pipeline.name == name)).scalar_one_or_none()
    if pipeline is None:
        pipeline = models.Pipeline(name=name)
        db.add(pipeline)
        db.commit()
        db.refresh(pipeline)
    return pipeline

def _last_status_to_schema(value):
    try:
        return schemas.RunStatus(value.value)  # DB enum -> schema enum
    except Exception:
        return schemas.RunStatus(value)        # plain string -> schema enum

# ----------------------------- Ingest -----------------------------
@app.post("/api/events/run", response_model=schemas.RunOut)
def ingest_run(event: schemas.RunIn, db: Session = Depends(get_db)):
    pipeline = get_or_create_pipeline(db, event.pipeline)

    started_at = event.started_at or utcnow()
    finished_at = event.finished_at
    duration = event.duration_sec
    if event.status != schemas.RunStatus.running:
        if finished_at is None:
            finished_at = utcnow()
        if duration is None and started_at and finished_at:
            duration = (finished_at - started_at).total_seconds()

    new_run = models.Run(
        pipeline_id=pipeline.id,
        status=models.RunStatus(event.status.value),
        started_at=started_at,
        finished_at=finished_at,
        duration_sec=duration,
        branch=event.branch,
        commit=event.commit,
        triggered_by=event.triggered_by,
    )
    db.add(new_run)
    db.commit()
    db.refresh(new_run)

    if event.status == schemas.RunStatus.failure:
        subj = f"[CI/CD] Failure: {pipeline.name} @ {finished_at or started_at}"
        body = (
            f"Pipeline: {pipeline.name}\n"
            f"Status: FAILURE\n"
            f"Started: {started_at}\n"
            f"Finished: {finished_at}\n"
            f"Duration(s): {duration}"
        )
        send_failure_alert(subj, body)

    # Recompute & broadcast metrics (JSON-safe)
    summary = compute_summary_metrics(db, minutes=None)
    asyncio.create_task(ws_manager.broadcast({"type": "metrics_update", "payload": jsonable_encoder(summary)}))

    return schemas.RunOut(
        id=new_run.id,
        pipeline=pipeline.name,
        status=schemas.RunStatus(new_run.status.value),
        started_at=new_run.started_at,
        finished_at=new_run.finished_at,
        duration_sec=new_run.duration_sec,
        branch=new_run.branch,
        commit=new_run.commit,
        triggered_by=new_run.triggered_by,
    )

# ----------------------------- Reads -----------------------------
@app.get("/api/runs", response_model=List[schemas.RunOut])
def list_runs(limit: int = 50, db: Session = Depends(get_db)):
    stmt = (
        select(models.Run, models.Pipeline.name)
        .join(models.Pipeline, models.Pipeline.id == models.Run.pipeline_id)
        .order_by(desc(models.Run.started_at))
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    out = []
    for run, pipeline_name in rows:
        out.append(
            schemas.RunOut(
                id=run.id,
                pipeline=pipeline_name,
                status=schemas.RunStatus(run.status.value),
                started_at=run.started_at,
                finished_at=run.finished_at,
                duration_sec=run.duration_sec,
                branch=run.branch,
                commit=run.commit,
                triggered_by=run.triggered_by,
            )
        )
    return out

def _pipeline_metrics(db: Session, window_start):
    filters = []
    if window_start:
        filters.append(models.Run.started_at >= window_start)

    # FIX: group by BOTH id and name for Postgres
    stmt = (
        select(
            models.Pipeline.name,
            func.count(models.Run.id),
            func.sum(case((models.Run.status == models.RunStatus.success, 1), else_=0)),
            func.sum(case((models.Run.status == models.RunStatus.failure, 1), else_=0)),
            func.avg(models.Run.duration_sec),
            func.max(models.Run.finished_at),
        )
        .join(models.Run, models.Run.pipeline_id == models.Pipeline.id, isouter=True)
        .group_by(models.Pipeline.id, models.Pipeline.name)
    )
    if filters:
        stmt = stmt.where(*filters)

    rows = db.execute(stmt).all()
    per = []
    for name, total, succ, fail, avg_dur, last_finished in rows:
        total = int(total or 0)
        succ = int(succ or 0)
        fail = int(fail or 0)
        success_rate = (succ / total) if total else 0.0

        last_status = None
        if total:
            sub = (
                select(models.Run.status)
                .join(models.Pipeline, models.Pipeline.id == models.Run.pipeline_id)
                .where(models.Pipeline.name == name)
                .order_by(desc(models.Run.started_at))
                .limit(1)
            )
            last_status_row = db.execute(sub).scalar_one_or_none()
            last_status = _last_status_to_schema(last_status_row) if last_status_row else None

        per.append(
            schemas.PipelineMetrics(
                pipeline=name,
                total=total,
                success=succ,
                failure=fail,
                success_rate=round(success_rate, 4),
                avg_duration_sec=float(avg_dur) if avg_dur is not None else None,
                last_status=last_status,
                last_finished_at=last_finished,
            )
        )
    return per

def compute_summary_metrics(db: Session, minutes: Optional[int] = None) -> dict:
    window = int(os.getenv("METRICS_DEFAULT_WINDOW", "1440")) if minutes is None else minutes
    from datetime import datetime, timezone, timedelta
    window_start = datetime.now(timezone.utc) - timedelta(minutes=window)

    filters = [models.Run.started_at >= window_start]
    stmt = select(
        func.count(models.Run.id),
        func.sum(case((models.Run.status == models.RunStatus.success, 1), else_=0)),
        func.sum(case((models.Run.status == models.RunStatus.failure, 1), else_=0)),
        func.avg(models.Run.duration_sec),
        func.max(models.Run.finished_at),
    ).where(*filters)

    total, succ, fail, avg_dur, last_finished = db.execute(stmt).one()
    total = int(total or 0)
    succ = int(succ or 0)
    fail = int(fail or 0)
    success_rate = (succ / total) if total else 0.0

    last_status = None
    if total:
        sub = (
            select(models.Run.status)
            .where(models.Run.started_at >= window_start)
            .order_by(desc(models.Run.started_at))
            .limit(1)
        )
        last_status_row = db.execute(sub).scalar_one_or_none()
        if last_status_row is not None:
            last_status = _last_status_to_schema(last_status_row)

    per = _pipeline_metrics(db, window_start)

    return {
        "window_minutes": window,
        "total": total,
        "success": succ,
        "failure": fail,
        "success_rate": round(success_rate, 4),
        "avg_duration_sec": float(avg_dur) if avg_dur is not None else None,
        "last_status": last_status,
        "last_finished_at": last_finished,
        "per_pipeline": [p.model_dump() for p in per],
    }

# Return plain dict so FastAPI handles JSON & response_model
@app.get("/api/metrics/summary", response_model=schemas.SummaryMetrics)
def metrics_summary(minutes: Optional[int] = Query(None), db: Session = Depends(get_db)):
    return compute_summary_metrics(db, minutes)

# ----------------------------- Simulator -----------------------------
@app.post("/api/simulate")
def simulate(count: int = 10, fail_rate: float = 0.25, pipelines: Optional[List[str]] = None, db: Session = Depends(get_db)):
    import random
    from datetime import timedelta

    pipelines = pipelines or ["web", "api"]
    created = 0
    for _ in range(count):
        name = random.choice(pipelines)
        status = schemas.RunStatus.failure if random.random() < fail_rate else schemas.RunStatus.success
        start = utcnow() - timedelta(minutes=random.randint(0, 180))
        dur = random.randint(30, 600)
        finish = start + timedelta(seconds=dur)
        ingest_run(
            schemas.RunIn(
                pipeline=name, status=status, started_at=start, finished_at=finish, duration_sec=dur,
                branch="main", commit=f"{random.randint(0, 16**7):07x}", triggered_by="local-sim"
            ),
            db
        )
        created += 1
    return {"ok": True, "created": created}
