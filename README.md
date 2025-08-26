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

## 🚀 Setup & Run Instructions

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
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_gmail_app_password   # Gmail App Password (not your normal password)
ALERT_TO=recipient@gmail.com
```

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

**Verify arrivals:**  
- API: <http://localhost:8000/api/runs?limit=20>  
- Dashboard: <http://localhost:5173> (cards, last build, table update live)

---

## 🤖 How AI Tools Were Used (with prompt examples)
1.AI assisted scaffolding, debugging, and Windows-friendly CI:

2.Create FastAPI + SQLAlchemy models for pipeline runs (enum status/timestamps/duration) and an ingest endpoint.”

3.Fix CORS so React on http://localhost:5173
 can call FastAPI on :8000; include preflight, allow localhost & 127.0.0.1.”

4.GitHub Actions POST returns 500—show a Windows PowerShell step that prints the API error body.”

5.asyncio.create_task fails in a sync FastAPI route—refactor to BackgroundTasks for websocket broadcasting.”

6.PostgreSQL GROUP BY error—update SQLAlchemy aggregate to group by id & name and count successes/failures.”

7.Write Dockerfiles and docker-compose for FastAPI, Vite, Postgres (local dev).”

---
## 🔍 Key Learning & Assumptions
**Learning**

1.CORS: exact origins matter (no trailing slash). For dev, CORS_ALLOW_ALL=1 is simplest; harden later.

2.Sync vs async: use BackgroundTasks for work triggered in sync routes.

3.Windows runners: default shell is powershell, not pwsh.

4.Surface errors: in Actions, use Invoke-WebRequest to print the error body.

5.Postgres: include all non-aggregated columns in GROUP BY; use case(..., else_=0) for counts.

**Assumptions**

1.Self-hosted runner is on the same machine (DASHBOARD_URL=http://localhost:8000).

2.Timestamps are UTC.

3.Target use is local dev/demo; add API key + strict CORS if exposing publicly.


## 📄 License

MIT (or your preferred license).
