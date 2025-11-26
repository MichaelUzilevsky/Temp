class DomainException(Exception):
    """Base class for all domain-level exceptions."""
    status_code: int = 500
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None):
        if message:
            self.message = message
        super().__init__(self.message)


class RepositoryException(DomainException):
    status_code = 500
    message = "Database error"


class IntegrityViolationException(RepositoryException):
    status_code = 400
    message = "Integrity constraint violated"


class NotFoundException(RepositoryException):
    status_code = 404
    message = "Resource not found"


class TimelineConflictException(DomainException):
    """
    Raised when events overlap and auto_fix is False.
    Contains details about which events conflicted.
    """
    status_code = 409

    def __init__(self, message: str, conflicting_events: list[dict] = None):
        super().__init__(message)
        self.conflicting_events = conflicting_events or []


class ResourceUnavailableException(DomainException):
    """Raised when a specific resource is locked by another Mission."""
    status_code = 409
    message = "Resource is used by another Mission."
