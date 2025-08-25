# CI/CD Pipeline Health Dashboard (Windows 11 + VS Code)

This is a complete local project to monitor CI/CD pipeline runs (simulated GitHub Actions), visualize real-time metrics, and send email alerts via Gmail. **No Grafana/Prometheus.**

## Stack
- **Backend:** Python FastAPI
- **DB:** PostgreSQL (Docker)
- **Frontend:** React (Vite)
- **Alerting:** Gmail SMTP (optional)
- **Containerization:** Docker & docker-compose

---

## Quick Start

### 1) Prereqs
- Docker Desktop (WSL2 backend)
- VS Code
- (Optional) Node 20+ and Python 3.11+ if running outside Docker

### 2) Configure environment
```powershell
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
```
In `backend/.env`, set SMTP if you want email alerts:
```
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password   # Gmail App Password (not your normal password)
ALERT_TO=recipient@gmail.com
```

### 3) Launch everything
```powershell
docker compose up --build
```
- API: http://localhost:8000/docs
- Frontend: http://localhost:5173

### 4) Seed some runs (choose one)
```powershell
# PowerShell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/simulate?count=20&fail_rate=0.35" -ContentType "application/json" -Body '{"pipelines":["web","api","worker"]}'

# or inside the backend container
docker exec -it cicd_backend python scripts/simulate_events.py --pipelines "web,api,worker" --count 20 --fail-rate 0.35

# or curl (cmd)
curl -X POST "http://localhost:8000/api/simulate?count=20&fail_rate=0.35" -H "Content-Type: application/json" -d "{"pipelines":["web","api","worker"]}"
```

The frontend updates **in real time** via WebSocket.

---

## Project Structure
```
ci-cd-dashboard/
  docker-compose.yml
  README.md
  tests.http
  .vscode/
    tasks.json
    launch.json
  backend/
    Dockerfile
    requirements.txt
    .env.example
    main.py
    database.py
    models.py
    schemas.py
    emailer.py
    websocket_manager.py
    utils.py
    scripts/
      simulate_events.py
  frontend/
    Dockerfile
    .dockerignore
    .env.example
    index.html
    vite.config.js
    package.json
    src/
      main.jsx
      App.jsx
      api.js
      ws.js
      components/
        Header.jsx
        MetricsCards.jsx
        RunsTable.jsx
        StatusPill.jsx
        LastBuild.jsx
```

## Useful API endpoints
- `GET /health` – liveness
- `GET /api/metrics/summary?minutes=1440` – metrics snapshot
- `GET /api/runs?limit=50` – recent runs
- `POST /api/events/run` – ingest a run event
- `POST /api/simulate?count=10&fail_rate=0.25` – generate sample runs
- `WS /ws/metrics` – realtime push on new events
