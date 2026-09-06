class RasterError(Exception):
    """Base exception for raster operations in ORBIT."""
    pass


class RasterNotFoundError(RasterError):
    """Raised when the specified raster asset file or remote URL is unreachable."""
    pass


class RasterCorruptedError(RasterError):
    """Raised when a raster file is unreadable or has corrupted headers."""
    pass


class RasterCRSMismatchError(RasterError):
    """Raised when coordinate reference systems cannot be aligned."""
    pass


class RasterOutOfBoundsError(RasterError):
    """Raised when the requested AOI does not intersect the raster bounds."""
    pass


class BandNotFoundError(RasterError):
    """Raised when a requested spectral or radar band cannot be resolved in the asset."""
    pass


class InvalidAOIError(RasterError):
    """Raised when the AOI polygon geometry is topologically invalid or empty."""
    pass


class IncompatibleResolutionError(RasterError):
    """Raised when bands of differing spatial resolutions cannot be harmonized without resampling."""
    pass
