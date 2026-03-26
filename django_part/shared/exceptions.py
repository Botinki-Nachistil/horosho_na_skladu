from __future__ import annotations


class SharedError(Exception):
    status_code: int = 400
    code: str = "ERROR"

    def __init__(self, message: str, details: dict | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(SharedError):
    status_code = 404
    code = "NOT_FOUND"


class ValidationError(SharedError):
    status_code = 400
    code = "VALIDATION_ERROR"


class PermissionDeniedError(SharedError):
    status_code = 403
    code = "PERMISSION_DENIED"


class InvalidStateError(SharedError):
    status_code = 409
    code = "INVALID_STATE"


class TokenValidationError(SharedError):
    status_code = 401
    code = "TOKEN_INVALID"