class STACError(Exception):
    """Base exception for STAC operations in ORBIT."""
    pass


class STACProviderError(STACError):
    """Raised when a remote STAC API provider returns an error."""
    pass


class STACTimeoutError(STACProviderError):
    """Raised when a STAC API request times out."""
    pass


class STACInvalidResponseError(STACProviderError):
    """Raised when a STAC API returns unparseable or non-compliant GeoJSON."""
    pass


class STACAuthenticationError(STACProviderError):
    """Raised when provider authentication fails."""
    pass


class STACRateLimitError(STACProviderError):
    """Raised when provider rate limits are exceeded (HTTP 429)."""
    pass


class STACGeometryError(STACError):
    """Raised when spatial geometry in STAC item is invalid or out of bounds."""
    pass


class STACMetadataValidationError(STACError):
    """Raised when required STAC metadata properties are missing or corrupted."""
    pass
