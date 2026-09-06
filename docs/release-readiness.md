# ORBIT Release Readiness & Deployment Guide

## 1. System Requirements & Prerequisites

- **Host OS**: Windows 11 / Windows 10, Linux (Ubuntu 22.04+), or macOS (13+).
- **Python**: Python 3.11 or Python 3.13 (`py --version`).
- **Node.js**: Node.js 18 LTS or 20 LTS (`node --version`).
- **Database**: PostgreSQL 16 with PostGIS 3.4 (`postgresql-16-postgis-3`).
- **Cache & Message Broker**: Redis 7.2.

---

## 2. Local-Native Setup (Zero Mandatory Cloud Dependencies)

### Step 1: Clone Repository & Configure Environment
```powershell
git clone https://github.com/orbit-geospatial/orbit.git
cd orbit
Copy-Item .env.example .env
```

### Step 2: Database Initialization & Migrations
```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

# Apply complete Alembic DAG up to 0010_multi_source_fusion
alembic upgrade head
```

### Step 3: Run Backend Service
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
- Swagger UI / OpenAPI Spec: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`

### Step 4: Run Celery Worker (Optional Background Queue)
```powershell
celery -A app.celery_app.celery_app worker --loglevel=info --pool=solo
```

### Step 5: Start Frontend Workstation
```powershell
cd ../frontend
npm install
npm run dev
```
- Application Web UI: `http://127.0.0.1:5173`

---

## 3. Verification Commands

```powershell
# 1. Full Backend Regression Suite (205 tests)
cd backend
py -m pytest -v

# 2. Full Frontend Regression Suite (54 tests)
cd ../frontend
npm test

# 3. Frontend Production Build
npm run build
```

---

## 4. Operational Invariants Checklist

- [x] Epistemic ladder strictly maintained across all 5 tiers.
- [x] Zero elevation of AI interpretations or predictions to observed facts.
- [x] Zero fabrication of satellite telemetry or historical observations.
- [x] Forecasting guarded when fewer than 4 historical observations exist.
- [x] Multi-source fusion preserves cross-sensor contradictions without consensus erasure.
- [x] All operational runs cryptographically sealed with SHA-256 digests.
- [x] Sandboxed local filesystem access with strict SSRF and path traversal guards.
