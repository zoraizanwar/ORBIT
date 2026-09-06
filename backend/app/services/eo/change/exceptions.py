class ChangeDetectionError(Exception):
    """Base domain exception for all change detection errors."""
    pass


class IncompatibleMeasurementsError(ChangeDetectionError):
    """Raised when comparing measurements with incompatible types or metrics."""
    pass


class IncompatibleSensorsError(ChangeDetectionError):
    """Raised when two observations cannot be reliably cross-compared."""
    pass


class IncompatibleUnitsError(ChangeDetectionError):
    """Raised when measurement units do not match."""
    pass


class TemporalOrderError(ChangeDetectionError):
    """Raised when T1 acquisition date is not strictly earlier than T2."""
    pass


class InsufficientDataError(ChangeDetectionError):
    """Raised when data points have excessive nodata or cloud contamination."""
    pass


class InvalidThresholdError(ChangeDetectionError):
    """Raised when threshold bounds are invalid."""
    pass


class SpatialGridMismatchError(ChangeDetectionError):
    """Raised when raster extents or CRS cannot be aligned."""
    pass
