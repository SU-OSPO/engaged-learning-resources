"""Standardized JSON error responses for API."""
from django.http import JsonResponse

# Standard status labels
STATUS_LABELS = {400: "Bad request", 404: "Not found", 500: "Server error"}


def json_error_response(status, error=None, detail=""):
    """Return a consistent JSON error payload."""
    if error is None:
        error = STATUS_LABELS.get(status, "Error")
    return JsonResponse(
        {"error": error, "status": status, "detail": detail},
        status=status,
    )


def handler404(request, exception=None):
    return json_error_response(404, "Not found", "Resource not found.")


def handler500(request):
    return json_error_response(500, "Server error", "An unexpected error occurred.")
