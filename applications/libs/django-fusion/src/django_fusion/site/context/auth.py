from django.conf import settings


def AUTH_SETTINGS(request):  # noqa: ARG001
    """Expose some settings from django-allauth in templates."""
    return {
        "ACCOUNT_ALLOW_REGISTRATION": settings.ACCOUNT_ALLOW_REGISTRATION,
    }
