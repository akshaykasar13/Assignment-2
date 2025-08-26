# Technical Design — CI/CD Pipeline Health Dashboard

## 1) High‑Level Architecture
**Goal:** A local, Dockerized system that ingests CI pipeline runs (GitHub Actions), persists them, computes metrics, pushes live updates, and emails on failures.

**Components**
- **Frontend (React + Vite @ :5173)**: SPA showing KPIs (cards) and a Recent Runs table; subscribes to WebSocket for live updates.
- **Backend (FastAPI @ :8000)**: REST API for ingest & queries; computes aggregates; broadcasts via WebSocket; sends Gmail alerts.
- **Database (PostgreSQL @ :5432)**: Stores pipelines and runs via SQLAlchemy ORM.
- **CI Source (GitHub Actions)**: Self‑hosted Windows runner posts job results to the API.
- **Containerization**: Docker & docker‑compose (single network).

**Data Flow**
1. GitHub Action completes → posts JSON to **`POST /api/events/run`**.  
2. Backend commits to DB → recomputes summary → **broadcasts** via **`/ws/metrics`**.  
3. Frontend, already connected via WS, updates KPIs instantly; recent runs fetched via REST.  
4. On failures, backend sends **Gmail SMTP** alert (best‑effort).

```

## 2) API Structure (routes & sample responses)

### Health
- **GET `/health`** → `{ "ok": true, "time": "..." }`

### Ingest a run
- **POST `/api/events/run`**  
  Request body:
  ```json
  {
    "pipeline": "web",
    "status": "success",             // "success" | "failure" | "running"
    "started_at": "2025-08-25T20:28:03Z",   // optional; default now
    "finished_at": "2025-08-25T20:28:10Z",  // optional; computed if missing
    "duration_sec": 7,                        // optional; computed if missing
    "branch": "main",
    "commit": "5184f9...",
    "triggered_by": "octocat"
  }
  ```
  Success response (200):
  ```json
  {
    "id": 123,
    "pipeline": "web",
    "status": "success",
    "started_at": "2025-08-25T20:28:03Z",
    "finished_at": "2025-08-25T20:28:10Z",
    "duration_sec": 7.0,
    "branch": "main",
    "commit": "5184f9...",
    "triggered_by": "octocat"
  }
  ```

### Summary metrics
- **GET `/api/metrics/summary?minutes=1440`**  
  Sample response:
  ```json
  {
    "window_minutes": 1440,
    "total": 22,
    "success": 17,
    "failure": 5,
    "success_rate": 0.7727,
    "avg_duration_sec": 95.3,
    "last_status": "failure",
    "last_finished_at": "2025-08-25T20:28:10Z",
    "per_pipeline": [
      {
        "pipeline": "web",
        "total": 10,
        "success": 8,
        "failure": 2,
        "success_rate": 0.8,
        "avg_duration_sec": 81.2,
        "last_status": "success",
        "last_finished_at": "2025-08-25T20:20:00Z"
      }
    ]
  }
  ```

### Recent runs
- **GET `/api/runs?limit=20`** → list of the most recent runs (pipeline, status, branch, commit, duration, timestamps, actor).

### Simulator
- **POST `/api/simulate?count=10&fail_rate=0.25`** body `{ "pipelines": ["web","api"] }` → quickly seed demo data.

### WebSocket
- **WS `/ws/metrics`** → server broadcasts on each ingest:  
  ```json
  { "type": "metrics_update", "payload": { /* same shape as /api/metrics/summary */ } }
  ```

---

## 3) Database Schema

### Tables
**pipelines**
- `id` (PK, int)  
- `name` (str, unique, indexed)

**runs**
- `id` (PK, int)  
- `pipeline_id` (FK → pipelines.id)  
- `status` (enum: `success`, `failure`, `running`)  
- `started_at` (timestamptz, UTC)  
- `finished_at` (timestamptz, UTC, nullable)  
- `duration_sec` (float, nullable)  
- `branch` (str)  
- `commit` (str)  
- `triggered_by` (str)

### Indexes
- `runs(pipeline_id, started_at DESC)`
- `runs(status)`
- Optionally `runs(started_at)` for time‑window scans.

### Notes
- All timestamps are UTC.  
- Aggregations use SQLAlchemy `case(..., else_=0)` and `GROUP BY (pipeline.id, pipeline.name)` to satisfy PostgreSQL rules.

---

## 4) UI Layout (Explanation)

**Top‑level layout**
- **Header**: project title + quick environment hint (local).
- **KPI Cards** (grid, responsive):
  - Total Runs
  - Success / Failure & **Success Rate**
  - **Average Duration**
  - **Last Build Status** (+ time)
- **Recent Runs Table**:
  - Columns: Pipeline, Status, Branch, Commit (short), Duration, Started/Finished (relative), Triggered By
  - Sorted by `started_at` desc; shows latest ~20
- **Live Updates**: opens WS on mount; on `metrics_update`, refresh KPIs and optionally re‑fetch recent runs.
- **Empty/Error States**: friendly messages; retry buttons for fetch; simple toasts on network errors.
- **Config**: `VITE_API_URL` for API base; CORS open in dev; favicon in `public/`.
