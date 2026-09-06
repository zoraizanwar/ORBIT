class ForecastingError(Exception):
    """Base exception for all ORBIT forecasting operations."""
    pass


class InsufficientDataError(ForecastingError):
    """Raised when historical time-series has fewer observations or temporal span than required."""
    def __init__(self, message: str, required_count: int, available_count: int):
        super().__init__(message)
        self.required_count = required_count
        self.available_count = available_count


class InvalidHorizonError(ForecastingError):
    """Raised when forecast horizon violates bounds (e.g. past dates, negative horizon, beyond 2050)."""
    pass


class ModelFitError(ForecastingError):
    """Raised when statistical/numerical model fitting fails (e.g. singular matrix, zero degrees of freedom)."""
    pass


class QualityFilterError(ForecastingError):
    """Raised when quality filtering encounters fatal schema violations or 100% rejected observations."""
    pass


class ScenarioError(ForecastingError):
    """Raised when an unrecognized or unsupported scenario is requested."""
    pass
