# CI/CD Pipeline Health Dashboard

A comprehensive, production-ready dashboard for monitoring CI/CD pipeline health with real-time metrics, alerting, and modern observability features.

---

## ✨ Features

- **Ingestion API**  For pipeline run events (success/failure, duration, timestamps, metadata).
- **Real-time Pipeline Monitoring** Responsive React frontend with real-time update via WebSocket (Last build status, Success/Failure counts, Success rate, Avg duration).
- **Smart Alerting** Gmail notifications for pipeline failures
- **Local GitHub Actions integration**  Track GitHub Actions or other CI/CD tools (self-hosted runner posts results to the API).
- **Production Ready** Dockerized, scalable architecture with monitoring
- **Industry Standards** Follows DevOps best practices and patterns

---

## 🧱 Architecture

- **Backend:** Python (FastAPI), SQLAlchemy 2.x
- **Database:** PostgreSQL (Docker)
- **Frontend:** React (Vite)
- **Alerting:** Gmail SMTP
- **CI/CD Source:** GitHub Actions (self-hosted runner on your Windows machine)
- **Containerization:** Docker & docker-compose

---

## 📁 Repository Structure

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
    .env.example
    index.html
    vite.config.js
    package.json
    public/
      favicon.svg
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
  .github/
    workflows/
      ci.yml
```

---

## 🚀 Quick Start 

### 1) Prerequisites
- **Docker Desktop** (WSL2 backend)
- **VS Code**
- **Python 3.11+**, **Node 20+**

### 2) Configure environment
Copy templates and set variables:

```powershell
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env
```

# Gmail alerts (optional but recommended)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_gmail_app_password   # Gmail App Password (not your normal password)
ALERT_TO=recipient@gmail.com

**frontend/.env:**
```env
VITE_API_URL=http://localhost:8000
```

### 3) Launch with Docker

```powershell
docker compose up --build
```
- Backend: <http://localhost:8000/docs> 
- Frontend: <http://localhost:5173>

### 4) Seed sample data (choose one)

**PowerShell (host):**
```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/simulate?count=20&fail_rate=0.35" `
  -ContentType "application/json" `
  -Body '{"pipelines":["web","api","worker"]}'
```

**Inside backend container:**
```powershell
docker exec -it <backend-container-name> python scripts/simulate_events.py --pipelines "web,api,worker" --count 20 --fail-rate 0.35
```

**curl (CMD):**
```bash
curl -X POST "http://localhost:8000/api/simulate?count=20&fail_rate=0.35" ^
  -H "Content-Type: application/json" ^
  -d "{\"pipelines\":[\"web\",\"api\",\"worker\"]}"
```

The UI updates **instantly** via WebSocket.

---

## 🤖 GitHub Actions Integration (Self-Hosted Runner)

This repository ships with a workflow at **.github/workflows/ci.yml** that posts job results to your dashboard.

### 1) Add a self-hosted runner (Windows)
1. GitHub → **Settings → Actions → Runners → New self-hosted runner → Windows**.
2. Follow the commands (`config.cmd`, then `run.cmd`) and keep the runner running.

### 2) Set repository secret
- **Settings → Secrets and variables → Actions → New repository secret**
  - **Name:** `DASHBOARD_URL`
  - **Value:** `http://localhost:8000`

### 3) Run the workflow
- GitHub → **Actions → CI (Self-Hosted -> Dashboard) → Run workflow**.
- Pick **force_fail = true/false** to simulate a failing/successful pipeline.
- The workflow:
  - Probes `GET /health`
  - Runs a trivial step
  - **Always posts** a run event with status, duration, timestamps, branch, commit, and actor.

**Verify arrivals:**  
- API: <http://localhost:8000/api/runs?limit=20>  
- Dashboard: <http://localhost:5173> (cards, last build, table update live)

---

## 📄 License

MIT (or your preferred license).
