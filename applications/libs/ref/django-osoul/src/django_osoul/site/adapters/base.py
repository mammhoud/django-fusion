from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

UP_METHOD_COOKIE = "_up_method"


class BaseAdapter:
	"""
	Provides the entrypoint for other frameworks to use this library.

	Implements common functionality that is not often overriden as well
	as framework specific hooks.
	"""

	def request_headers(self) -> Mapping[str, str]:
		"""Reads the request headers from the current request.

		Needs to be implemented."""
		raise NotImplementedError  # pragma: no cover

	def request_params(self) -> Mapping[str, str]:
		"""Reads the GET params from the current request.

		Needs to be implemented."""
		raise NotImplementedError  # pragma: no cover

	def redirect_uri(self, response: Any) -> str | None:
		"""Returns the redirect target of a response or None if the response
		is not a redirection (ie if it's status code is not in the range 300-400).

		Needs to be implemented."""
		raise NotImplementedError  # pragma: no cover

	def set_redirect_uri(self, response: Any, uri: str) -> None:
		"""Set a new redirect target for the current response. This is used to
		pass unpoly parameters via GET params through redirects.

		Needs to be implemented."""
		raise NotImplementedError  # pragma: no cover

	def set_headers(self, response: Any, headers: Mapping[str, str]) -> None:
		"""Set headers like `X-Up-Location` on the current response.

		Needs to be implemented."""
		raise NotImplementedError  # pragma: no cover

	def set_cookie(self, response: Any, needs_cookie: bool = False) -> None:
		"""Set or delete the `_up_method <https://unpoly.com/_up_method>`_ cookie.

		The implementation should set the cookie if `needs_cookie` is `True` and
		otherwise remove it if set.

		Needs to be implemented."""
		raise NotImplementedError  # pragma: no cover

	@property
	def method(self) -> str:
		"""Exposes the current request's method (GET/POST etc)

		Needs to be implemented."""
		raise NotImplementedError  # pragma: no cover

	@property
	def location(self) -> str:
		"""Exposes the current request's location (path including query params)

		Needs to be implemented."""
		raise NotImplementedError  # pragma: no cover

	def deserialize_data(self, data: str) -> object:
		"""Deserializes data passed in by Unpoly.

		By default it simply reads it as JSON, but can be overriden if custom
		decoders are needed.
		"""
		try:
			return json.loads(data)
		except json.JSONDecodeError:
			return None

	def serialize_data(self, data: object) -> str:
		"""Serializes the data for passing it to Unpoly.

		By default it simply serializes it as JSON, but can be overriden if custom
		encoders are needed.
		"""
		return json.dumps(data, separators=(",", ":"), ensure_ascii=True)
