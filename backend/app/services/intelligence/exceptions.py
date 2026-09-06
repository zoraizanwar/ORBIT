class IntelligenceError(Exception):
    """Base exception for all advanced geospatial intelligence operations."""
    pass


class RuleExecutionError(IntelligenceError):
    """Raised when a deterministic intelligence rule fails validation or execution."""
    pass


class IncompatibleEvidenceError(IntelligenceError):
    """Raised when evidence items cannot be correlated due to fundamental modality or domain incompatibility."""
    pass


class SpatialCorrelationError(IntelligenceError):
    """Raised when spatial correlation evaluation fails."""
    pass


class TemporalCorrelationError(IntelligenceError):
    """Raised when temporal window comparison fails or violates chronological bounds."""
    pass


class EvidenceGraphError(IntelligenceError):
    """Raised when evidence graph construction or traversal fails."""
    pass
