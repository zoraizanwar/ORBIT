# ORBIT: Local Development Environment Guide

## 1. Prerequisites & Required Software

| Software | Minimum Version | Verification Command (PowerShell) | Purpose in ORBIT |
|---|---|---|---|
| **Python** | `3.11+` (e.g. 3.13) | `py --version` or `python --version` | FastAPI Backend, Celery Workers, Raster Processing, AI |
| **Node.js** | `18.0+` (e.g. 20 LTS) | `node --version` | React 18, Vite, TypeScript, Tailwind CSS Workstation |
| **npm** | `9.0+` | `npm --version` | Frontend dependency management |
| **Docker Desktop** | `24.0+` | `docker --version` | PostgreSQL 16 + PostGIS 3.4 and Redis 7.2 containers |
| **Git** | `2.40+` | `git --version` | Version control & source provenance |

---

## 2. Windows PowerShell Quickstart Sequence

### Step 1: Clone Repository & Create Environment Configuration
```powershell
# In project root: C:\Users\...\ORBIT
Copy-Item .env.example .env
```

### Step 2: Start Infrastructure (PostgreSQL/PostGIS & Redis)
```powershell
# Start PostGIS and Redis in background via Docker Compose
docker compose up -d

# Verify containers are healthy
docker compose ps
```

### Step 3: Set Up Python Backend Virtual Environment
```powershell
cd backend

# Create virtual environment using Python 3.11+
py -m venv venv

# Activate virtual environment in PowerShell
.\venv\Scripts\Activate.ps1

# Upgrade pip and install all development dependencies
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

### Step 4: Run Backend Database Migrations & Health Check
```powershell
# Run database schema migrations via Alembic
alembic upgrade head

# Start FastAPI backend development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive API Docs: `http://127.0.0.1:8000/docs`
- Health Check Endpoint: `http://127.0.0.1:8000/api/v1/health`

### Step 5: Start Celery Background Worker (in separate PowerShell terminal)
```powershell
cd backend
.\venv\Scripts\Activate.ps1

# Start Celery worker using Windows-compatible solo pool
celery -A app.celery_app.celery_app worker --loglevel=info --pool=solo
```

### Step 6: Set Up and Start React Frontend (in separate PowerShell terminal)
```powershell
cd frontend

# Install Node dependencies
npm install

# Start Vite development workstation
npm run dev
```
- Workstation URL: `http://127.0.0.1:5173`

---

## 3. Running Automated Tests & Quality Checks

### Backend Test Suite (PyTest)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pytest -v
```

### Frontend TypeScript & Build Verification
```powershell
cd frontend
npm run build
```

---

## 4. Common Troubleshooting Scenarios

1. **Docker Desktop Daemon Not Running**:
   - Error: `error during connect: This error may indicate that the docker daemon is not running.`
   - Solution: Launch Docker Desktop from the Windows Start menu and ensure the whale icon is green before executing `docker compose up -d`.
2. **PowerShell Execution Policy Restriction**:
   - Error: `File ... Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
   - Solution: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell.
3. **Port 5432 or 6379 Already in Use**:
   - If local PostgreSQL or Redis services are already running natively on Windows, update `POSTGRES_PORT=5433` or `REDIS_PORT=6380` in `.env` and `docker-compose.yml`.
