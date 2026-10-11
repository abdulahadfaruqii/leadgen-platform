"""
Custom exceptions for the LeadGen platform.
"""


class LeadGenException(Exception):
    """Base exception for the platform."""

    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AgentException(LeadGenException):
    """Exception raised by AI agents."""
    pass


class ScrapingException(LeadGenException):
    """Exception raised during web scraping."""
    pass


class ValidationException(LeadGenException):
    """Exception raised for validation errors."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, status_code=422, details=details)


class NotFoundException(LeadGenException):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class RateLimitException(LeadGenException):
    """Exception raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)


class AIProviderException(LeadGenException):
    """Exception raised by AI provider APIs."""
    pass
