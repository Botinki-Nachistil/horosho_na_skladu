class SharedError(Exception):
    """Base shared-layer exception."""


class TokenValidationError(SharedError):
    """Raised when JWT validation fails."""
