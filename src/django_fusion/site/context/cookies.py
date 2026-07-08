from django.middleware.csrf import get_token


def COOKIES(request):
    """Safe context processor that won't raise KeyError."""
    # Use get_token() which handles token generation if needed
    csrf_token = get_token(request)

    return {
        "csrf_token": csrf_token,
    }
