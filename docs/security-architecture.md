# ORBIT: Security Architecture & Tenant Isolation

## 1. Authentication & Session Security

ORBIT employs a hardened authentication lifecycle designed to meet enterprise defense and intelligence security postures:

```
+-----------------------------------------------------------------------------------+
| 1. CREDENTIAL HASHING: Argon2id (Memory: 64MB, Iterations: 3, Parallelism: 4)      |
|    - Exceeds OWASP password storage requirements                                  |
|    - Resistant to GPU/ASIC cracking attacks                                       |
+-----------------------------------------------------------------------------------+
                                         | Login Verification
                                         v
+-----------------------------------------------------------------------------------+
| 2. TOKEN LIFECYCLE: Asymmetric Dual-Token Model (RS256 / Ed25519)                 |
|    - Short-Lived Access Tokens: JWT, 15-minute expiration, in-memory client storage|
|    - Long-Lived Refresh Tokens: Opaque UUIDv4, 7-day expiration, HttpOnly Cookies |
|    - Automatic Token Rotation with Replay Attack Detection                        |
+-----------------------------------------------------------------------------------+
```

---

## 2. Role-Based Access Control (RBAC) & Tenant Isolation

Every workspace, project, and analysis run is isolated by cryptographic ownership checks:

| User Role | Permissions & Access Scope |
|---|---|
| `VIEWER` | Read-only access to published intelligence dossiers, map tiles, and historical profiles. Cannot initiate compute runs. |
| `ANALYST` | Full create/read/update within owned projects. Can execute analysis runs, query EO catalogs, export GeoPackages and PDF reports. |
| `RESEARCHER`| Access to historical deep-time engines, Islamic source annotations, raw algorithm parameter tuning. |
| `ADMIN` | User lifecycle management, rate-limit governance, system telemetry, audit log inspection, provider credentials. |

### Data Isolation Invariant:
All database queries for workspace artifacts enforce tenancy at the SQL query compilation level:
```python
# FastAPI Dependency Injection enforcing tenant boundary
def get_user_project(project_id: UUID, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    project = db.scalars(stmt).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found or unauthorized access.")
    return project
```

---

## 3. Input Validation & Spatial Geometry Sanitization

1. **Bounding Box & Polygon Constraints**:
   - Polygons submitted for AOI analysis are validated with Shapely `is_valid` and PostGIS `ST_IsValid`. Self-intersecting geometries are rejected or sanitized via `ST_MakeValid`.
   - Maximum AOI surface area is capped based on user tier (e.g., $10,000\text{ km}^2$ per local run) to prevent Denial of Service (DoS) memory exhaustion.
   - Coordinate bounding limits are strictly bounded to $[-180, 180]$ longitude and $[-85.0511, 85.0511]$ latitude.
2. **Subprocess Isolation**:
   - No dynamic shell execution (`shell=True` is strictly banned in all Python codebases).
   - Any external CLI tools (e.g., `osmium-tool`, `gdal_translate`) are executed via explicit argument arrays with sanitized integer/UUID inputs.
3. **Audit Logging**:
   - All analytical runs, report downloads, and access elevation requests are appended to an immutable `auth.audit_logs` table with client IP, User-Agent, and cryptographic action hash.
