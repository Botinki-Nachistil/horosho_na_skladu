from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import exception_handler

from shared.exceptions import SharedError


def unified_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, SharedError):
        return Response(
            {
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=exc.status_code,
        )

    if response is not None:
        original = response.data

        if isinstance(original, dict) and "detail" in original:
            code = getattr(original["detail"], "code", "ERROR").upper()
            message = str(original["detail"])
            details = {}
        elif isinstance(original, dict):
            code = "VALIDATION_ERROR"
            message = "Validation failed."
            details = original
        else:
            code = "ERROR"
            message = str(original)
            details = {}

        response.data = {
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        }
        return response

    return Response(
        {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "details": {},
            }
        },
        status=500,
    )