from rest_framework.response import Response

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
