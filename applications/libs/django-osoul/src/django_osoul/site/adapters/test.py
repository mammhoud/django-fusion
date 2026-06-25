from __future__ import annotations

from typing import TYPE_CHECKING

from contrib.setup.ext.adapter import BaseAdapter

UP_METHOD_COOKIE = "_up_method"


if TYPE_CHECKING:  # pragma: no cover
	from collections.abc import Mapping



class SimpleAdapter(BaseAdapter):
	def __init__(
		self,
		method: str = "GET",
		location: str = "/",
		headers: dict[str, str] | None = None,
		params: dict[str, str] | None = None,
		redirect_uri: str | None = None,
	):
		self._method = method
		self._location = location
		self.headers = headers or {}
		self.params = params or {}
		self._redirect_uri = redirect_uri
		self.response_redirect_uri: str | None = None
		self.response_headers: Mapping[str, str] | None = None
		self.cookie: bool | None = None

	def request_headers(self) -> Mapping[str, str]:
		return self.headers

	def request_params(self) -> Mapping[str, str]:
		return self.params

	def redirect_uri(self, response: object) -> str | None:
		return self._redirect_uri

	def set_redirect_uri(self, response: object, uri: str) -> None:
		self.response_redirect_uri = uri

	def set_headers(self, response: object, headers: Mapping[str, str]) -> None:
		self.response_headers = headers

	def set_cookie(self, response: object, needs_cookie: bool = False) -> None:
		self.cookie = needs_cookie

	@property
	def method(self) -> str:
		return self._method

	@property
	def location(self) -> str:
		return self._location
