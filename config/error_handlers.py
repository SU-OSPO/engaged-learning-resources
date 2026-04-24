"""JSON error responses for specific views (not used as project-wide 404/500)."""
from django.http import JsonResponse

STATUS_LABELS = {400: "Bad request", 404: "Not found", 500: "Server error"}


def json_error_response(status, error=None, detail=""):
    if error is None:
        error = STATUS_LABELS.get(status, "Error")
    return JsonResponse(
        {"error": error, "status": status, "detail": detail},
        status=status,
    )
