"""Template context processors."""


def email_backend(request):
    """Expose whether outgoing mail is printed (console) vs sent via SMTP."""
    from django.conf import settings

    backend = getattr(settings, "EMAIL_BACKEND", "")
    return {
        "email_is_console": "console" in backend,
    }
