# Prompt Logs — CI/CD Pipeline Health Dashboard (Concise)

1. **Scope Definition** — “Build a CI/CD dashboard (FastAPI + React + Postgres, Dockerized) with real‑time metrics and Gmail alerts.”
2. **Requirements** — “List metrics (success/failure, avg time, last status); exclude Grafana/Prometheus; Windows 11 + VS Code.”
3. **Backend Scaffolding** — “Create SQLAlchemy models and FastAPI endpoints for ingest, summary, runs, simulate; add WebSocket.”
4. **Frontend Scaffolding** — “Vite React app with KPI cards + recent runs table; call REST and subscribe to WS.”
5. **Docker/Compose** — “Write Dockerfiles and docker‑compose for API, DB, UI; map ports 8000/5173/5432.”
6. **CORS Fix** — “Enable CORS for http://localhost:5173 and 127.0.0.1; add preflight; allow all in dev.”
7. **GitHub Actions Flow** — “Windows self‑hosted runner; powershell steps; `force_fail` input; POST to `/api/events/run`.”
8. **Async Fix** — “Replace `asyncio.create_task` with FastAPI `BackgroundTasks` for WS broadcast.”
