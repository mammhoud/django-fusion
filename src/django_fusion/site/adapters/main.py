from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from django.http import HttpRequest, HttpResponse

from .base import BaseAdapter

UP_METHOD_COOKIE = "_up_method"

class DjangoAdapter(BaseAdapter):
	def __init__(self, request: HttpRequest):
		self.request = request

	def request_headers(self) -> Mapping[str, str]:
		return cast(Mapping[str, str], self.request.headers)

	def request_params(self) -> Mapping[str, str]:
		return self.request.GET

	def redirect_uri(self, response: HttpResponse) -> str | None:
		return (
			cast(Mapping[str, str], response.headers).get("Location")
			if 300 <= response.status_code < 400
			else None
		)

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
