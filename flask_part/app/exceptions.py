from __future__ import annotations


class APIError(Exception):
    status_code: int = 500
    code: str = "internal_error"
    message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)
        if message:
            self.message = message


class NotFoundError(APIError):
    status_code = 404
    code = "not_found"
    message = "Not found"


class ValidationError(APIError):
    status_code = 400
    code = "validation_error"
    message = "Validation error"


class PermissionDeniedError(APIError):
    status_code = 403
    code = "permission_denied"
    message = "Permission denied"


class AuthenticationError(APIError):
    status_code = 401
    code = "authentication_error"
    message = "Authentication required"


class InvalidStateError(APIError):
    status_code = 409
    code = "invalid_state"
    message = "Invalid state transition"
