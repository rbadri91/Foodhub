"""Consistent JSON error envelope: {"error": {"code", "message", "details"}}."""
from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error": {
                "code": response.status_code,
                "message": exc.__class__.__name__,
                "details": response.data,
            }
        }
    return response
