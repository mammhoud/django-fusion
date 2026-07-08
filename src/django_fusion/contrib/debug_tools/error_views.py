"""
Custom error views for django_fusion.

This module provides custom error views for Django projects with a
unified error page renderer that passes status code, title, message,
and traceback to a single ``errors/nxx.html`` template.

Functions:
    custom_error_view: Render errors/nxx.html with structured context.
    handler400: Handler for 400 Bad Request errors.
    handler403: Handler for 403 Permission Denied errors.
    handler404: Handler for 404 Page Not Found errors.
    handler500: Handler for 500 Internal Server Error.

Usage in urls.py::

    from django_fusion.contrib.debug_tools.error_views import (
        handler400, handler403, handler404, handler500,
    )
"""

import sys
import traceback

from django.shortcuts import render


def custom_error_view(request, exception=None, status_code: int = 500):
    """Render errors/nxx.html with structured context for any HTTP error code."""
    _titles = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Permission Denied",
        404: "Page Not Found",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout",
    }
    error_title = _titles.get(status_code, "Error")
    error_message = (
        getattr(exception, "message", str(exception))
        if exception
        else "An unexpected error occurred."
    )

    exc_type, exc_value, exc_tb = sys.exc_info()
    error_logs = (
        "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        if exc_tb
        else ""
    )

    return render(
        request,
        "errors/nxx.html",
        {
            "status_code": status_code,
            "error_title": error_title,
            "error_message": error_message,
            "error_logs": error_logs,
            "exception": str(exception) if exception else None,
        },
        status=status_code,
    )


# Django handler callables
def handler400(request, exception=None, **kwargs):
    return custom_error_view(request, exception, status_code=400)


def handler403(request, exception=None, **kwargs):
    return custom_error_view(request, exception, status_code=403)


def handler404(request, exception=None, **kwargs):
    return custom_error_view(request, exception, status_code=404)


def handler500(request, **kwargs):
    return custom_error_view(request, None, status_code=500)
