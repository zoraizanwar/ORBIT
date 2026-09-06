import hashlib
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.logging import logger
from app.core.security_hardening import SecurityHardening


class AcquiredAssetRecord(BaseModel):
    asset_key: str
    source_url: str
    local_path: str
    file_size_bytes: int
    sha256_checksum: str
    acquisition_timestamp: str
    mime_type: Optional[str] = None
    is_test_fixture: bool = False
    metadata: Dict[str, Any] = {}


class AssetAcquisitionRequest(BaseModel):
    source_url: str = Field(..., description="HTTP/HTTPS remote URL or local file URI")
    asset_key: str = Field(..., description="Canonical or provider asset key e.g. B04, B08, visual")
    scene_id: Optional[str] = None
    max_size_bytes: int = Field(268435456, description="Max allowed file size in bytes (default 256MB)")
    timeout_seconds: float = Field(30.0, description="HTTP download timeout in seconds")
    is_test_fixture: bool = False


class SecureAssetAcquisitionService:
    """
    Local-First Secure Earth Observation Asset Acquisition & Cache Engine.
    Enforces SSRF prevention, path traversal boundaries, and cryptographic SHA-256 fingerprinting.
    """

    ALLOWED_EXTENSIONS = {".tif", ".tiff", ".jp2", ".json", ".xml", ".png", ".jpg", ".jpeg", ".nc"}

    @classmethod
    def get_cache_directory(cls) -> Path:
        """Returns the authorized local asset storage directory."""
        cache_dir = Path(settings.ORBIT_DATA_DIR) / "cache" / "eo_assets"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    @classmethod
    async def acquire_asset(
        cls,
        request: AssetAcquisitionRequest,
    ) -> AcquiredAssetRecord:
        """
        Securely downloads or caches a remote/local Earth Observation asset.
        """
        source_url = request.source_url.strip()
        asset_key = request.asset_key.strip()
        scene_id = request.scene_id or "unclassified_scene"

        # 1. URL & Security Validation
        if source_url.startswith("http://") or source_url.startswith("https://"):
            SecurityHardening.validate_remote_url(source_url)
        elif source_url.startswith("file://") or os.path.exists(source_url):
            # Local file URI handling
            local_raw_path = source_url.replace("file://", "")
            SecurityHardening.validate_local_path(local_raw_path)
        else:
            raise ValueError(f"Unsupported URL scheme or inaccessible path: '{source_url}'")

        # 2. Determine target destination in local cache
        cache_root = cls.get_cache_directory()
        sanitized_scene = "".join(c for c in scene_id if c.isalnum() or c in ("-", "_")).strip()
        sanitized_key = "".join(c for c in asset_key if c.isalnum() or c in ("-", "_")).strip()
        
        # Determine extension
        ext = Path(source_url.split("?")[0]).suffix.lower()
        if not ext or ext not in cls.ALLOWED_EXTENSIONS:
            ext = ".tif"

        scene_cache_dir = cache_root / sanitized_scene
        scene_cache_dir.mkdir(parents=True, exist_ok=True)
        target_path = scene_cache_dir / f"{sanitized_key}{ext}"

        # 3. Check if cached and verified
        if target_path.exists() and target_path.stat().st_size > 0:
            file_size = target_path.stat().st_size
            sha256_hash = cls._compute_file_sha256(target_path)
            now_iso = datetime.now(timezone.utc).isoformat()
            logger.info(f"Asset cache hit: {target_path} (size={file_size} bytes, sha256={sha256_hash[:8]}...)")
            return AcquiredAssetRecord(
                asset_key=asset_key,
                source_url=source_url,
                local_path=str(target_path.resolve()),
                file_size_bytes=file_size,
                sha256_checksum=sha256_hash,
                acquisition_timestamp=now_iso,
                is_test_fixture=request.is_test_fixture,
                metadata={"cache_status": "HIT"},
            )

        # 4. Handle Local File Copy
        if source_url.startswith("file://") or (not source_url.startswith("http") and os.path.exists(source_url)):
            src_p = Path(source_url.replace("file://", ""))
            if not src_p.is_file():
                raise FileNotFoundError(f"Local asset source not found: {src_p}")
            if src_p.stat().st_size > request.max_size_bytes:
                raise ValueError(f"File size ({src_p.stat().st_size} bytes) exceeds limit ({request.max_size_bytes} bytes)")
            
            shutil.copyfile(src_p, target_path)
            sha256_hash = cls._compute_file_sha256(target_path)
            now_iso = datetime.now(timezone.utc).isoformat()
            return AcquiredAssetRecord(
                asset_key=asset_key,
                source_url=source_url,
                local_path=str(target_path.resolve()),
                file_size_bytes=target_path.stat().st_size,
                sha256_checksum=sha256_hash,
                acquisition_timestamp=now_iso,
                is_test_fixture=request.is_test_fixture,
                metadata={"cache_status": "LOCAL_INGESTED"},
            )

        # 5. Remote HTTP/HTTPS Streaming Download
        sha256_engine = hashlib.sha256()
        bytes_received = 0
        now_iso = datetime.now(timezone.utc).isoformat()

        try:
            with tempfile.NamedTemporaryFile(delete=False, dir=str(scene_cache_dir), suffix=".tmp") as tmp_file:
                tmp_path = Path(tmp_file.name)
                
                async with httpx.AsyncClient(timeout=request.timeout_seconds, follow_redirects=True) as client:
                    async with client.stream("GET", source_url) as response:
                        if response.status_code != 200:
                            raise ValueError(f"Remote server returned HTTP status {response.status_code} for asset download")
                        
                        # Validate Content-Length if present
                        content_length = response.headers.get("Content-Length")
                        if content_length and int(content_length) > request.max_size_bytes:
                            raise ValueError(
                                f"Declared asset size ({content_length} bytes) exceeds maximum allowable limit ({request.max_size_bytes} bytes)"
                            )

                        async for chunk in response.aiter_bytes(chunk_size=65536):
                            if not chunk:
                                continue
                            bytes_received += len(chunk)
                            if bytes_received > request.max_size_bytes:
                                raise ValueError(
                                    f"Downloaded payload exceeded size cap of {request.max_size_bytes} bytes"
                                )
                            sha256_engine.update(chunk)
                            tmp_file.write(chunk)

            # Atomic move into final cache location
            shutil.move(str(tmp_path), str(target_path))
            sha256_hex = sha256_engine.hexdigest()

            logger.info(
                f"Successfully acquired remote asset {asset_key} ({bytes_received} bytes) -> {target_path} [SHA-256: {sha256_hex[:8]}...]"
            )

            return AcquiredAssetRecord(
                asset_key=asset_key,
                source_url=source_url,
                local_path=str(target_path.resolve()),
                file_size_bytes=bytes_received,
                sha256_checksum=sha256_hex,
                acquisition_timestamp=now_iso,
                is_test_fixture=request.is_test_fixture,
                metadata={"cache_status": "DOWNLOADED"},
            )

        except Exception as e:
            if 'tmp_path' in locals() and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception:
                    pass
            sanitized_err = SecurityHardening.sanitize_error_message(str(e))
            logger.error(f"Failed to acquire asset from {source_url}: {sanitized_err}")
            raise RuntimeError(f"Asset acquisition failed: {sanitized_err}") from e

    @classmethod
    def _compute_file_sha256(cls, file_path: Path) -> str:
        """Computes SHA-256 checksum of a local file in 64KB blocks."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
