from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from urllib.parse import urlencode

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.template.response import SimpleTemplateResponse

from django_fusion.plugins.htmx import HtmxDetails
from django_fusion.plugins.unpoly import DjangoAdapter, Unpoly
import logging

logger = logging.getLogger(__name__)

UP_METHOD_COOKIE = "_up_method"


class SiteMiddleware:
    """
    Unified middleware for:
    - HTMX: Injects `request.htmx` with `HtmxDetails`.
    - Unpoly: Attaches Unpoly rendering logic (`request.up`) and headers.
    - Permissions: Enforces `.has_view_permission()` on `site` and `app`.
    - Context: Dynamically injects context from `app.get_context_data(request)`.
    - Async support.
    """

    sync_capable = True
    async_capable = True
    exclude_redirect_headers = ("X-Up-Method",)

    def __init__(
        self,
        get_response: (
            Callable[[HttpRequest], HttpResponseBase]
            | Callable[[HttpRequest], Awaitable[HttpResponseBase]]
        ),
    ):
        self.get_response = get_response
        self.async_mode = iscoroutinefunction(get_response)

        if self.async_mode:
            markcoroutinefunction(self)

    def __call__(self, request: HttpRequest) -> HttpResponseBase | Awaitable[HttpResponseBase]:
        start = time.monotonic()
        if self.async_mode:
            return self.__acall__(request)

        self._preprocess_request(request)
        response = self.get_response(request)
        duration = time.monotonic() - start
        logger.debug(f"Request {request.path} took {duration:.2f}s")  # Log request duration [Note]

        return self._finalize(request, response)

    async def __acall__(self, request: HttpRequest) -> HttpResponseBase:
        self._preprocess_request(request)
        response = await self.get_response(request)
        return self._finalize(request, response)

    # -------------------------
    # Request Init
    # -------------------------

    def _preprocess_request(self, request: HttpRequest) -> None:
        """
        Attach protocol metadata to the request object:

        - HTMX: adds `request.htmx` and `request.is_htmx`
        - Unpoly: adds `request.up` and `request.is_unpoly`
        - Sanitizes Unpoly GET parameters (like `X-Up-*`)
        """
        # HTMX integration
        request.htmx = HtmxDetails(request)  # type: ignore[attr-defined]
        request.is_htmx = bool(request.htmx)

        # Unpoly integration
        up_params = self._get_up_params(request)
        if hasattr(request, "GET") and request.GET:
            request.GET = self._remove_up_params(request.GET, up_params)

        request.is_unpoly = "X-Up-Version" in request.headers
        request.up = Unpoly(DjangoAdapter(request))
        request._up_params = up_params  # stored for finalization

    # -------------------------
    # Response Finalization
    # -------------------------

    def _finalize(self, request: HttpRequest, response: HttpResponseBase) -> HttpResponseBase:
        up_params = getattr(request, "_up_params", [])
        response["X-Up-Method"] = request.method

        self._handle_method_cookie(request, response)

        if hasattr(request, "up"):
            request.up.finalize_response(response)

        # restore headers from GET params
        for header, value in up_params:
            response[header] = value

        if 300 <= response.status_code < 400:
            response = self._handle_redirect_headers(response)

        return response

    # -------------------------
    # Unpoly Internals
    # -------------------------

    def _get_up_headers(self, response: HttpResponseBase) -> list[tuple[str, str]]:
        return [(k, v) for k, v in response.items() if k.startswith("X-Up-")]

    def _get_up_redirect_headers(self, response: HttpResponseBase) -> list[tuple[str, str]]:
        return [
            (k, v)
            for k, v in self._get_up_headers(response)
            if k not in self.exclude_redirect_headers
        ]

    def _get_up_params(self, request: HttpRequest) -> list[tuple[str, str]]:
        return [(k, v) for k, v in request.GET.items() if k.startswith("X-Up-")]

    def _remove_up_params(self, GET, up_params):
        cleaned = GET.copy()
        for param, _ in up_params:
            cleaned.pop(param, None)
        return cleaned

    def _handle_redirect_headers(self, response: HttpResponseBase) -> HttpResponseBase:
        if not hasattr(response, "url"):
            return response

        response["X-Up-Location"] = response.url
        params = {k: v for k, v in self._get_up_redirect_headers(response)}
        if params:
            separator = "?" if "?" not in response.url else "&"
            response["Location"] += separator + urlencode(params)
        return response

    def _handle_method_cookie(self, request: HttpRequest, response: HttpResponseBase):
        if request.method != "GET" and "X-Up-Target" not in request:
            response.set_cookie(UP_METHOD_COOKIE, request.method)
        else:
            response.delete_cookie(UP_METHOD_COOKIE)

    # -------------------------
    # Permission Checks
    # -------------------------

    def _check_permission(self, obj, user) -> None:
        if obj and hasattr(obj, "has_view_permission") and not obj.has_view_permission(user):
            logger.warning(f"Permission denied: user={user} tried to access object={obj}")
            raise PermissionDenied

    def process_view(
        self, request: HttpRequest, view_func: Callable, view_args: list, view_kwargs: dict
    ) -> HttpResponse | None:
        """
        Apply `.has_view_permission(user)` check on `site` and `app` in resolver match metadata.
        """
        if getattr(view_func, "disable_site_middleware", False):
            return None

        if not hasattr(request, "user"):
            raise ImproperlyConfigured(
                "Missing `request.user`. Ensure `AuthenticationMiddleware` is before `SmartSiteMiddleware`."
            )

        match = getattr(request, "resolver_match", None)
        if not match:
            return None

        try:
            extra = getattr(match.url_name, "extra", {}) or {}
        except AttributeError:
            return None

        site = extra.get("site")
        app = extra.get("app")

        self._check_permission(site, request.user)
        self._check_permission(app, request.user)

        for name, value in extra.items():
            setattr(match, name, value)

        return None

    # -------------------------
    # Template Context Injector
    # -------------------------

    def process_template_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """
        Injects additional context from `app.get_context_data(request)` into template response.
        """
        match = getattr(request, "resolver_match", None)
        if not match:
            return response

        app = getattr(match, "app", None)
        if not app or not hasattr(app, "get_context_data"):
            return response

        try:
            context = app.get_context_data(request)
            if context and isinstance(response, SimpleTemplateResponse):
                if response.context_data is None:
                    response.context_data = {}

                for key, value in context.items():
                    if key in response.context_data:
                        raise ValueError(
                            f"App context key '{key}' clashes with view response context"
                        )
                    response.context_data[key] = value
        except Exception as e:
            logger.error(f"Error injecting app context from '{app}': {e!s}", exc_info=True)

        return response
