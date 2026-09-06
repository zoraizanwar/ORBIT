class AIIntelligenceError(Exception):
    """Base exception for ORBIT AI intelligence and synthesis operations."""
    pass


class InsufficientEvidenceError(AIIntelligenceError):
    """Raised when evidence package has insufficient grounded observations to produce a valid interpretation."""
    def __init__(self, message: str, required_types: list, available_types: list):
        super().__init__(message)
        self.required_types = required_types
        self.available_types = available_types


class ClaimValidationError(AIIntelligenceError):
    """Raised when an AI-generated claim fails deterministic grounding or cites invalid evidence."""
    def __init__(self, message: str, invalid_claims: list):
        super().__init__(message)
        self.invalid_claims = invalid_claims


class HallucinationError(AIIntelligenceError):
    """Raised when an AI response introduces unsupported numerical values, dates, or non-existent sensors."""
    def __init__(self, message: str, ungrounded_tokens: list):
        super().__init__(message)
        self.ungrounded_tokens = ungrounded_tokens


class ProviderUnavailableError(AIIntelligenceError):
    """Raised when no local or external LLM provider is reachable."""
    pass


class PromptSecurityError(AIIntelligenceError):
    """Raised when evidence text contains potential prompt injection or unauthorized token sequences."""
    pass
