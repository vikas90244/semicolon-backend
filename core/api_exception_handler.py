from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    PermissionDenied,
    NotFound,
)

def _get_error_code(exc):
    if isinstance(exc, ValidationError):
        return "VALIDATION_ERROR"
    if isinstance(exc, NotAuthenticated):
        return "UNAUTHORIZED"
    if isinstance(exc, PermissionDenied):
        return "FORBIDDEN"
    if isinstance(exc, NotFound):
        return "NOT_FOUND"
    return "INTERNAL_SERVER_ERROR"


def _extract_message(data):
    if isinstance(data, dict):
        val = next(iter(data.values()), "Invalid request")
        if isinstance(val, list):
            return str(val[0])
        return str(val)
    if isinstance(data, list):
        return str(data[0])
    return str(data)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Unhandled server error
    if response is None:
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Internal server error",
                    "code": "INTERNAL_SERVER_ERROR",
                    "status": 500,
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = _get_error_code(exc)
    message = _extract_message(response.data)

    return Response(
        {
            "success": False,
            "error": {
                "message": message,
                "code": code,
                "status": response.status_code,
            },
        },
        status=response.status_code,
    )
