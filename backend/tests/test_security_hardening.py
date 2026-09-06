import pytest
from app.core.security_hardening import SecurityHardening, SecurityValidationError


def test_ssrf_validation_blocks_private_and_metadata_ips():
    # Localhost / Loopback
    with pytest.raises(SecurityValidationError, match="SSRF protection"):
        SecurityHardening.validate_remote_url("http://localhost:8000/stac")

    with pytest.raises(SecurityValidationError, match="SSRF protection"):
        SecurityHardening.validate_remote_url("http://127.0.0.1/stac")

    # Cloud Metadata Service
    with pytest.raises(SecurityValidationError, match="SSRF protection"):
        SecurityHardening.validate_remote_url("http://169.254.169.254/latest/meta-data")

    # RFC-1918 Private Subnets
    with pytest.raises(SecurityValidationError, match="RFC-1918"):
        SecurityHardening.validate_remote_url("https://10.0.0.1/raster.tif")

    with pytest.raises(SecurityValidationError, match="RFC-1918"):
        SecurityHardening.validate_remote_url("https://192.168.1.100/raster.tif")

    # Invalid Scheme
    with pytest.raises(SecurityValidationError, match="scheme"):
        SecurityHardening.validate_remote_url("file:///etc/passwd")


def test_ssrf_validation_permits_legitimate_stac_urls():
    valid_url = "https://planetarycomputer.microsoft.com/api/stac/v1/collections"
    assert SecurityHardening.validate_remote_url(valid_url) == valid_url

    earth_search_url = "https://earth-search.aws.element84.com/v1"
    assert SecurityHardening.validate_remote_url(earth_search_url) == earth_search_url


def test_path_traversal_prevention():
    with pytest.raises(SecurityValidationError, match="traversal"):
        SecurityHardening.validate_local_path("../../secret/passwords.txt")

    with pytest.raises(SecurityValidationError, match="traversal"):
        SecurityHardening.validate_local_path("data/%2e%2e/system/config.json")


def test_raster_bounds_and_memory_safety():
    # Valid window
    SecurityHardening.validate_raster_bounds(512, 512, dtype_itemsize=4)

    # Invalid dimensions
    with pytest.raises(SecurityValidationError, match="exceed maximum allowed limit"):
        SecurityHardening.validate_raster_bounds(20000, 20000)

    # Excessive memory read
    with pytest.raises(SecurityValidationError, match="Estimated uncompressed raster read size"):
        SecurityHardening.validate_raster_bounds(12000, 12000, dtype_itemsize=8)  # ~1.1 GB


def test_error_message_sanitization():
    raw_error = Exception("Failed connecting to postgresql://user:supersecret@db:5432/orbit at C:\\Users\\User\\secret\\file.py")
    cleaned = SecurityHardening.sanitize_error_message(raw_error)

    assert "supersecret" not in cleaned
    assert "C:\\Users" not in cleaned
    assert "postgresql://[REDACTED]@" in cleaned
    assert "[INTERNAL_PATH]" in cleaned
