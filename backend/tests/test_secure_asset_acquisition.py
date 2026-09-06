import os
import tempfile
from pathlib import Path
import pytest
from app.services.eo.acquisition.secure_downloader import (
    SecureAssetAcquisitionService,
    AssetAcquisitionRequest,
)


@pytest.mark.asyncio
async def test_acquire_asset_blocks_ssrf_private_and_metadata_ips():
    """Verifies that private IP, loopback, and metadata URLs are blocked before opening HTTP connection."""
    ssrf_targets = [
        "http://127.0.0.1/test.tif",
        "http://localhost:8000/band.tif",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.5/asset.tif",
        "http://192.168.1.100/data.tif",
    ]
    for url in ssrf_targets:
        req = AssetAcquisitionRequest(source_url=url, asset_key="B04")
        with pytest.raises(Exception) as exc_info:
            await SecureAssetAcquisitionService.acquire_asset(req)
        assert any(term in str(exc_info.value).lower() for term in ["ssrf", "blocked", "private", "metadata", "loopback", "security", "scheme"])


@pytest.mark.asyncio
async def test_acquire_asset_local_ingestion_and_sha256(tmp_path):
    """Verifies that safe local file paths can be ingested with SHA-256 computation and caching."""
    sample_file = tmp_path / "sample_band.tif"
    sample_content = b"TEST_GEOTIFF_PAYLOAD_CHUNK_DATA_FOR_VERIFICATION"
    sample_file.write_bytes(sample_content)

    req = AssetAcquisitionRequest(
        source_url=str(sample_file),
        asset_key="B04",
        scene_id="test_scene_001",
        is_test_fixture=True,
    )

    record = await SecureAssetAcquisitionService.acquire_asset(req)
    assert record.asset_key == "B04"
    assert record.file_size_bytes == len(sample_content)
    assert len(record.sha256_checksum) == 64
    assert Path(record.local_path).exists()
    assert record.is_test_fixture is True

    # Test cache hit on second call
    record_hit = await SecureAssetAcquisitionService.acquire_asset(req)
    assert record_hit.metadata.get("cache_status") == "HIT"
    assert record_hit.sha256_checksum == record.sha256_checksum


@pytest.mark.asyncio
async def test_acquire_asset_enforces_size_cap(tmp_path):
    """Verifies that files exceeding max_size_bytes are rejected."""
    sample_file = tmp_path / "large_file.tif"
    sample_file.write_bytes(b"A" * 1024)

    req = AssetAcquisitionRequest(
        source_url=str(sample_file),
        asset_key="B08",
        scene_id="test_scene_large",
        max_size_bytes=512,  # Cap is 512 bytes, file is 1024 bytes
    )

    with pytest.raises(Exception) as exc_info:
        await SecureAssetAcquisitionService.acquire_asset(req)
    assert "exceeds" in str(exc_info.value).lower() or "limit" in str(exc_info.value).lower()
