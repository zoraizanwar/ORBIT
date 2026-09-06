import ipaddress
import os
import re
from urllib.parse import urlparse
from typing import Optional


class SecurityValidationError(Exception):
    """Raised when an input violates ORBIT security, SSRF, or path traversal policies."""
    pass


class SecurityHardening:
    """
    Security & Input Validation Engine for ORBIT Local-First Geospatial Platform.
    Enforces SSRF defense, path traversal prevention, and raster resource bounding.
    """

    # Maximum dimensions to prevent decompression bombs
    MAX_RASTER_DIMENSION = 16384  # 16K max pixels
    MAX_UNCOMPRESSED_MB = 256     # 256 MB max memory per read window

    BLOCKED_HOSTNAMES = {
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "169.254.169.254",  # AWS/GCP/Azure instance metadata service
        "metadata.google.internal",
    }

    ALLOWED_SCHEMES = {"http", "https"}

    @classmethod
    def validate_remote_url(cls, url: str) -> str:
        """
        Validates remote STAC / COG asset URLs.
        Blocks SSRF attempts against localhost, link-local, private RFC-1918 subnets, and metadata endpoints.
        """
        if not url or not isinstance(url, str):
            raise SecurityValidationError("Invalid URL: must be a non-empty string.")

        parsed = urlparse(url.strip())
        if parsed.scheme.lower() not in cls.ALLOWED_SCHEMES:
            raise SecurityValidationError(f"Invalid URL scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise SecurityValidationError("Invalid URL: missing hostname.")

        hostname_lower = hostname.lower()

        # Check blocked hostnames
        if hostname_lower in cls.BLOCKED_HOSTNAMES:
            raise SecurityValidationError(f"Access to blocked host '{hostname}' is forbidden (SSRF protection).")

        # Check IP address targets
        try:
            ip = ipaddress.ip_address(hostname_lower)
            if ip.is_private:
                raise SecurityValidationError(f"Access to private RFC-1918 IP address '{hostname}' is forbidden.")
            if ip.is_loopback:
                raise SecurityValidationError(f"Access to loopback address '{hostname}' is forbidden.")
            if ip.is_link_local:
                raise SecurityValidationError(f"Access to link-local address '{hostname}' is forbidden.")
            if ip.is_multicast:
                raise SecurityValidationError(f"Access to multicast address '{hostname}' is forbidden.")
            if ip.is_reserved:
                raise SecurityValidationError(f"Access to reserved IP address '{hostname}' is forbidden.")
        except ValueError:
            # Not an IP literal, valid hostname string
            pass

        return url.strip()

    @classmethod
    def validate_local_path(cls, file_path: str, allowed_base_dir: Optional[str] = None) -> str:
        """
        Sanitizes local file paths to prevent directory traversal outside authorized storage roots.
        """
        if not file_path or not isinstance(file_path, str):
            raise SecurityValidationError("Invalid path: must be a non-empty string.")

        # Detect traversal sequences
        if ".." in file_path or "%2e%2e" in file_path.lower():
            raise SecurityValidationError("Directory traversal attempt detected in file path.")

        norm_path = os.path.normpath(file_path)

        if allowed_base_dir:
            norm_base = os.path.normpath(allowed_base_dir)
            if not norm_path.startswith(norm_base):
                raise SecurityValidationError(f"Path '{file_path}' traverses outside allowed directory '{allowed_base_dir}'.")

        return norm_path

    @classmethod
    def validate_raster_bounds(cls, width: int, height: int, dtype_itemsize: int = 4) -> None:
        """
        Validates raster window dimensions and estimated memory allocation.
        """
        if width <= 0 or height <= 0:
            raise SecurityValidationError(f"Raster dimensions must be positive (got {width}x{height}).")

        if width > cls.MAX_RASTER_DIMENSION or height > cls.MAX_RASTER_DIMENSION:
            raise SecurityValidationError(
                f"Raster dimensions ({width}x{height}) exceed maximum allowed limit of {cls.MAX_RASTER_DIMENSION}px."
            )

        estimated_mb = (width * height * dtype_itemsize) / (1024 * 1024)
        if estimated_mb > cls.MAX_UNCOMPRESSED_MB:
            raise SecurityValidationError(
                f"Estimated uncompressed raster read size ({estimated_mb:.1f} MB) exceeds maximum limit of {cls.MAX_UNCOMPRESSED_MB} MB."
            )

    @classmethod
    def sanitize_error_message(cls, exception: Exception) -> str:
        """
        Strips internal paths, database connection strings, and sensitive tokens from error text.
        """
        raw_msg = str(exception)
        # Strip Windows absolute paths
        cleaned = re.sub(r"[A-Za-z]:\\[^ \n\r\t]+", "[INTERNAL_PATH]", raw_msg)
        # Strip Unix absolute paths
        cleaned = re.sub(r"/(?:Users|home|var|etc|opt)/[^ \n\r\t]+", "[INTERNAL_PATH]", cleaned)
        # Strip database credentials if present
        cleaned = re.sub(r"postgresql://[^@]+@", "postgresql://[REDACTED]@", cleaned)
        return cleaned[:300]
