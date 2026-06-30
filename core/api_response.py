from rest_framework.response import Response
from django.http import JsonResponse

def api_success(data=None, message=None, status=200, headers=None):
    return Response(
        {
            "success": True,
            "data": data,
            "message": message,
        },
        status=status,
        headers=headers
    )

def api_error(message, code="ERROR", status=400):
    return Response(
        {
            "success": False,
            "error": {
                "message": message,
                "code": code,
                "status": status
            }
        },
        status=status
    )

def ratelimit_error(request, exception=None):
    """
    Handler for rate limit exceeded errors.
    Called by django-ratelimit when rate limit is exceeded.
    """
    return JsonResponse(
        {
            "success": False,
            "error": {
                "message": "Rate limit exceeded. Please try again later.",
                "code": "RATE_LIMIT_EXCEEDED",
                "status": 429
            }
        },
        status=429
    )
