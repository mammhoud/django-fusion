"""Django adapter for the Unpoly server protocol."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, cast

from django.http import HttpRequest, HttpResponse

UP_METHOD_COOKIE = "_up_method"


class BaseAdapter:
    """Framework-agnostic adapter interface for Unpoly."""

    def request_headers(self) -> Mapping[str, str]:
        raise NotImplementedError  # pragma: no cover

    def request_params(self) -> Mapping[str, str]:
        raise NotImplementedError  # pragma: no cover

    def redirect_uri(self, response: Any) -> str | None:
        raise NotImplementedError  # pragma: no cover

    def set_redirect_uri(self, response: Any, uri: str) -> None:
        raise NotImplementedError  # pragma: no cover

    def set_headers(self, response: Any, headers: Mapping[str, str]) -> None:
        raise NotImplementedError  # pragma: no cover

    def set_cookie(self, response: Any, needs_cookie: bool = False) -> None:
        raise NotImplementedError  # pragma: no cover

    @property
    def method(self) -> str:
        raise NotImplementedError  # pragma: no cover

    @property
    def location(self) -> str:
        raise NotImplementedError  # pragma: no cover

    def deserialize_data(self, data: str) -> object:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    def serialize_data(self, data: object) -> str:
        return json.dumps(data, separators=(",", ":"), ensure_ascii=True)


class DjangoAdapter(BaseAdapter):
    """Adapter implementation for Django requests/responses."""

    def __init__(self, request: HttpRequest):
        self.request = request

    def request_headers(self) -> Mapping[str, str]:
        return cast(Mapping[str, str], self.request.headers)

    def request_params(self) -> Mapping[str, str]:
        return self.request.GET

    def redirect_uri(self, response: HttpResponse) -> str | None:
        if 300 <= response.status_code < 400:
            return cast(Mapping[str, str], response.headers).get("Location")
        return None

    def set_redirect_uri(self, response: HttpResponse, uri: str) -> None:
        response.headers["Location"] = uri

    def set_headers(self, response: HttpResponse, headers: Mapping[str, str]) -> None:
        for k, v in headers.items():
            response.headers[k] = v

    def set_cookie(self, response: HttpResponse, needs_cookie: bool = False) -> None:
        if needs_cookie:
            response.set_cookie(UP_METHOD_COOKIE, self.method)
        elif UP_METHOD_COOKIE in self.request.COOKIES:
            response.delete_cookie(UP_METHOD_COOKIE)

    @property
    def method(self) -> str:
        return cast(str, self.request.method)

    @property
    def location(self) -> str:
        return self.request.get_full_path_info()
