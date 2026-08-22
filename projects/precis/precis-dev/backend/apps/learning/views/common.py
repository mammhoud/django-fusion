from __future__ import annotations

import json
from functools import wraps

from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render


def _is_htmx(request) -> bool:
    """Recognize HTMX requests without treating ``HX-Request: false`` as true."""
    header = request.headers.get("HX-Request", "").strip().lower()
    return bool(getattr(request, "htmx", False) or header in {"true", "1", "yes", "on"})


def _hx_or_json(
    request,
    template: str,
    context: dict,
    payload: dict,
    status: int = 200,
    redirect_to: str | None = None,
    headers: dict | None = None,
):
    if _is_htmx(request):
        response = render(request, template, context, status=status)
    elif redirect_to and status < 400:
        response = HttpResponseRedirect(redirect_to)
    else:
        response = JsonResponse(payload, status=status)
    if headers:
        for key, value in headers.items():
            response[key] = value
    return response


def _login_response(request):
    if _is_htmx(request):
        response = HttpResponse(status=401)
        response["HX-Trigger"] = json.dumps({"fusion:open-login": {}})
        return response
    return HttpResponseRedirect("/accounts/login/?next=/learning/")


def learning_login_required(view):
    """Protect learner views while keeping HTMX requests in the current page."""

    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _login_response(request)
        return view(request, *args, **kwargs)

    return wrapped
