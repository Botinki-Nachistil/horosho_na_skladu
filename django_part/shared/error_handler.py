from __future__ import annotations

import logging

from django.db import IntegrityError
from rest_framework.response import Response
from rest_framework.views import exception_handler

from shared.exceptions import SharedError, ValidationError

logger = logging.getLogger(__name__)


def unified_exception_handler(exc, context):
    if isinstance(exc, SharedError):
        if exc.status_code in (401, 403):
            logger.warning(
                "auth_error code=%s message=%s",
                exc.code,
                exc.message,
            )
        return Response(
            {"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
            status=exc.status_code,
        )

    if isinstance(exc, IntegrityError):
        logger.warning("db_integrity_error error=%s", str(exc))
        return Response(
            {"error": {
                "code": "VALIDATION_ERROR",
                "message": "Resource already exists or constraint violated.",
                "details": {},
            }},
            status=400,
        )

    response = exception_handler(exc, context)

    if response is None:
        logger.error("unhandled_exception error=%s", str(exc), exc_info=True)
        return Response(
            {"error": {"code": "INTERNAL_ERROR", "message": str(exc), "details": {}}},
            status=500,
        )

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

    response.data = {"error": {"code": code, "message": message, "details": details}}
    return response