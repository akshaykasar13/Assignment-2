# Requirement Analysis — CI/CD Pipeline Health Dashboard

## 1) Key Features
- **Ingest CI runs**: record status (`success|failure|running`), duration, timestamps, branch, commit, actor, pipeline.
- **Real‑time metrics**: total, success/failure counts, success rate, average duration, last build status (global + per pipeline).
- **Recent runs history**: latest N executions with metadata.
- **Email alerts (Gmail)**: on failure events.
- **Local simulation**: seed data via `/api/simulate` for demos/tests.
- **GitHub Actions integration**: Windows self‑hosted runner posts results after each job.
- **Dockerized dev**: one command up; Windows 11 + VS Code friendly.

## 2) Tech Choices (Rationale)
- **FastAPI + SQLAlchemy**: modern, fast, type‑friendly; clean Pydantic models & background tasks; great for REST + WS.
- **PostgreSQL**: robust relational store; good for aggregates, indices, and future growth.
- **React (Vite)**: fast dev server, minimal boilerplate, easy WS + fetch; clean component model for cards/table.
- **Docker Compose**: reproducible local env; isolates Postgres; consistent ports.
- **Windows PowerShell workflow**: aligns with self‑hosted Windows runner.
- **BackgroundTasks for WS**: avoids event‑loop issues from sync routes; reliable broadcast.

## 3) APIs / Tools Required
- **Backend Endpoints**:
  - `POST /api/events/run` — ingest a run
  - `GET /api/metrics/summary` — KPI summary (windowed)
  - `GET /api/runs?limit=N` — recent runs
  - `POST /api/simulate?count&fail_rate` — demo data
  - `GET /health` — health check
  - `WS /ws/metrics` — live metrics broadcast
- **External Tools / Services**:
  - **GitHub Actions (self‑hosted Windows runner)** — posts to the API.
  - **Gmail SMTP** — alerts (App Password).
  - **Docker Desktop (WSL2)** + **VS Code** — local setup & dev.
  - (Optional) **ngrok/Cloudflare Tunnel** if exposing API beyond localhost.
