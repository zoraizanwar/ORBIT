# ORBIT Security Architecture & Defensive Hardening

## 1. Overview

ORBIT is designed with a **Defense-in-Depth** security architecture tailored for geospatial data processing, remote imagery extraction, and AI intelligence synthesis in local-first and enterprise self-hosted environments.

---

## 2. Implemented Security Controls

### 2.1 Server-Side Request Forgery (SSRF) Protection
The `SecurityHardening` module (`backend/app/core/security_hardening.py`) enforces strict network isolation when discovering or fetching STAC metadata and raster assets from external endpoints:

- **Protocol Restriction**: Only `http://` and `https://` schemes are allowed. Schemes like `file://`, `gopher://`, or `ftp://` are immediately rejected.
- **Private & Localhost IP Filtering**: Blocks requests resolving to:
  - `127.0.0.0/8` (Loopback / Localhost)
  - `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (RFC-1918 Private Networks)
  - `169.254.0.0/16` (Link-Local & Cloud Metadata Endpoints: `169.254.169.254`)
  - IPv6 Loopback (`::1`) and Unique Local (`fc00::/7`)

### 2.2 Path Traversal & File Boundary Defense
When reading local rasters, vector files, or report templates:
- Path normalization blocks directory traversal tokens (`..`, `%2e%2e`, `.\`, `./`).
- Enforces an absolute jail boundary rooted within authorized project storage directories.

### 2.3 Raster Bounds & Memory Exhaustion Safeguards
High-resolution satellite rasters can cause denial-of-service via memory exhaustion (decompression bombs). ORBIT enforces:
- Maximum window read dimension: **16,384 x 16,384 pixels**.
- Maximum uncompressed memory allocation per read operation: **256 MB**.
- Bounding-box validation preventing infinite bounding queries or negative extent coordinates.

### 2.4 Error Message Sanitization & Credential Redaction
- Strips internal file system paths and stack traces from API responses.
- Automatically redacts sensitive keys (`password`, `token`, `secret`, `api_key`, `authorization`) in all structured observability log events.
- Produces normalized JSON error envelopes with structured error codes (`UNPROCESSABLE_ENTITY`, `NOT_FOUND`, `SECURITY_VIOLATION`).

---

## 3. Threat Model Matrix

| Threat Category | Potential Vector | ORBIT Defensive Mitigation | Test Verification |
| :--- | :--- | :--- | :--- |
| **SSRF** | STAC query injection to `http://169.254.169.254` | IP resolution block & scheme whitelist | `tests/test_security_hardening.py` |
| **Path Traversal** | Raster asset path manipulation `../../etc/passwd` | Jail boundary enforcement & traversal parsing | `tests/test_security_hardening.py` |
| **Memory Exhaustion** | 100,000 x 100,000 raster read request | 16k dimension limit & 256MB memory cap | `tests/test_security_hardening.py` |
| **Credential Leakage** | Database error throwing connection string | Sanitizer regex scrubbing DB URLs & tokens | `tests/test_security_hardening.py` |
| **AI Hallucination** | LLM generating unverified facts | Epistemic validation gate & citation graph | `tests/test_ai_endpoints.py` |
