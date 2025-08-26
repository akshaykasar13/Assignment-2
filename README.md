CI/CD Pipeline Health Dashboard 🚀
A comprehensive, production-ready dashboard for monitoring CI/CD pipeline health with real-time metrics, alerting, and modern observability features.

🌟 Features
- **Ingestion API**  For pipeline run events (success/failure, duration, timestamps, metadata).
- **Real-time Pipeline Monitoring** Responsive React frontend with real-time update via WebSocket (Last build status, Success/Failure counts, Success rate, Avg duration).
- **Smart Alerting** Gmail notifications for pipeline failures
- **Local GitHub Actions integration**  Track GitHub Actions or other CI/CD tools (self-hosted runner posts results to the API).
- **Production Ready** Dockerized, scalable architecture with monitoring
- **Industry Standards** Follows DevOps best practices and patterns

🏗️ Architecture
Backend: Python FastAPI, SQLAlchemy 2.x
DB: PostgreSQL (Docker)
Frontend: React (Vite)
Alerting: Gmail SMTP (optional)
Containerization: Docker & docker-compose
CI Source: GitHub Actions (self-hosted runner on your Windows machine)

🚀 Quick Start
Prerequisites
Docker & Docker Compose
VS Code
Node 20+ and Python 3.11+ if running outside Docker
PostgreSQL (for local development)
Using Docker (Recommended)
# Clone the repository
git clone <your-repo-url>
cd ci-cd-dashboard

2) Configure environment
copy backend\.env.example backend\.env
copy frontend\.env.example frontend\.env

In backend/.env, set SMTP if you want email alerts:

SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password   # Gmail App Password (not your normal password)
ALERT_TO=recipient@gmail.com

3) Launch everything
docker compose up --build
API: http://localhost:8000/docs
Frontend: http://localhost:5173

# Start all services
docker-compose up -d

4) Seed some runs (choose one)
# PowerShell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/simulate?count=20&fail_rate=0.35" -ContentType "application/json" -Body '{"pipelines":["web","api","worker"]}'

# or inside the backend container
docker exec -it cicd_backend python scripts/simulate_events.py --pipelines "web,api,worker" --count 20 --fail-rate 0.35

# or curl (cmd)
curl -X POST "http://localhost:8000/api/simulate?count=20&fail_rate=0.35" -H "Content-Type: application/json" -d "{"pipelines":["web","api","worker"]}"

The frontend updates in real time via WebSocket.

Project Structure
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

Useful API endpoints
GET /health – liveness
GET /api/metrics/summary?minutes=1440 – metrics snapshot
GET /api/runs?limit=50 – recent runs
POST /api/events/run – ingest a run event
POST /api/simulate?count=10&fail_rate=0.25 – generate sample runs
WS /ws/metrics – realtime push on new events

🤝 Contributing
Fork the repository
Create a feature branch
Make your changes
Add tests
Submit a pull request

## 📄 License

MIT (or your preferred license).

Built with ❤️ using modern DevOps practices and industry standards