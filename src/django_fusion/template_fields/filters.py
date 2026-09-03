"""
django_fusion.template_fields.filters
=====================================

Filter registry for the dynamic template field system.

Filters transform resolved values before they are inserted into the rendered
output (``{{ order.total|currency:"USD" }}``). The registry is deliberately
small and deterministic — every filter is a pure function of its value and
arguments, and none of them evaluate code.

Output marked ``safe=True`` is treated as trusted HTML (e.g. ``linebreaks``
produces its own escaped markup); everything else is HTML-escaped by the
engine before it is inserted.
"""

from __future__ import annotations

import html
import re
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

from django.utils.safestring import mark_safe

FilterFunc = Callable[[Any, tuple[Any, ...]], Any]


class _MissingType:
    """Sentinel for a value that could not be resolved."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "<missing>"

    def __bool__(self) -> bool:
        return False


#: Shared "missing value" sentinel. Filters and the engine both recognize it
#: so ``{{ missing|default:"N/A" }}`` falls back instead of leaking a repr.
MISSING = _MissingType()

#: Django-style date format tokens mapped to ``strftime`` codes. Only the
#: common subset is supported; unknown tokens pass through literally.
_DATE_TOKENS: dict[str, str] = {
    "d": "%d",  # 01-31
    "D": "%a",  # Mon
    "j": "%-d",  # 1-31
    "l": "%A",  # Monday
    "m": "%m",  # 01-12
    "M": "%b",  # Jan
    "n": "%-m",  # 1-12
    "Y": "%Y",  # 2024
    "y": "%y",  # 24
    "H": "%H",  # 00-23
    "i": "%M",  # 00-59
    "s": "%S",  # 00-59
    "g": "%-I",  # 1-12
    "G": "%-H",  # 0-23
    "h": "%I",  # 01-12
    "a": "%p",  # AM/PM
    "A": "%p",  # AM/PM
    "P": "%I:%M %p",  # 3:30 p.m.
}


def _to_datetime(value: Any) -> datetime | None:
    """Coerce a date/datetime/ISO string to a datetime (or None)."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    if isinstance(value, str):
        candidate = value.strip()
        for parser in (datetime.fromisoformat,):
            try:
                return parser(candidate)
            except ValueError:
                continue
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                return datetime.strptime(candidate, fmt)
            except ValueError:
                continue
    return None


def _django_to_strftime(fmt: str) -> str:
    """Convert a Django-style date format to a strftime format string."""
    out: list[str] = []
    i = 0
    while i < len(fmt):
        char = fmt[i]
        if char == "\\" and i + 1 < len(fmt):
            out.append(fmt[i + 1])
            i += 2
            continue
        if char in _DATE_TOKENS:
            out.append(_DATE_TOKENS[char])
        else:
            out.append(char)
        i += 1
    return "".join(out)


def _text(value: Any) -> str:
    if value is None or value is MISSING:
        return ""
    return str(value)


def filter_currency(value: Any, args: tuple[Any, ...]) -> str:
    """Format a number as currency (``{{ order.total|currency:"USD" }}``)."""
    code = str(args[0]) if args else "USD"
    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "AED": "د.إ",
        "SAR": "﷼",
        "EGP": "E£",
    }
    symbol = symbols.get(code.upper(), f"{code.upper()} ")
    try:
        number = float(value)
    except (TypeError, ValueError):
        return f"{symbol}{_text(value)}"
    formatted = f"{number:,.2f}"
    return f"{symbol}{formatted}"


def filter_date(value: Any, args: tuple[Any, ...]) -> str:
    """Format a date/datetime (``{{ created|date:"M d, Y" }}``)."""
    fmt = str(args[0]) if args else "M d, Y"
    dt = _to_datetime(value)
    if dt is None:
        return _text(value)
    return dt.strftime(_django_to_strftime(fmt))


def filter_upper(value: Any, args: tuple[Any, ...]) -> str:
    return _text(value).upper()


def filter_lower(value: Any, args: tuple[Any, ...]) -> str:
    return _text(value).lower()


def filter_title(value: Any, args: tuple[Any, ...]) -> str:
    return _text(value).title()


def filter_truncate(value: Any, args: tuple[Any, ...]) -> str:
    """Truncate a string with an ellipsis (``{{ text|truncate:30 }}``)."""
    try:
        limit = max(0, int(args[0]))
    except (TypeError, ValueError):
        limit = 30
    text = _text(value)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def filter_default(value: Any, args: tuple[Any, ...]) -> str:
    """Fallback when the value is falsy or missing (``{{ company|default:"N/A" }}``)."""
    fallback = str(args[0]) if args else ""
    if value is MISSING or value is None or value == "" or value is False:
        return fallback
    return _text(value)


def filter_yesno(value: Any, args: tuple[Any, ...]) -> str:
    """Map a boolean to words (``{{ is_paid|yesno:"Paid,Pending" }}``)."""
    mapping = str(args[0]) if args else "yes,no"
    parts = [part.strip() for part in mapping.split(",")]
    if value in (True, 1, "1", "true", "True", "yes", "Yes"):
        return parts[0] if parts else "yes"
    if value in (False, 0, "0", "false", "False", "no", "No", "", None):
        return parts[1] if len(parts) > 1 else "no"
    return parts[2] if len(parts) > 2 else _text(value)


def filter_phone(value: Any, args: tuple[Any, ...]) -> str:
    """Basic phone formatting (``{{ phone|phone:"+1" }}``)."""
    prefix = str(args[0]) if args else ""
    digits = re.sub(r"\D", "", _text(value))
    if not digits:
        return _text(value)
    if len(digits) == 10:
        return f"{prefix} ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"{prefix} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    return f"{prefix} {digits}"


def filter_length(value: Any, args: tuple[Any, ...]) -> str:
    if value is None:
        return "0"
    try:
        return str(len(value))
    except TypeError:
        return "1"


def filter_join(value: Any, args: tuple[Any, ...]) -> str:
    sep = str(args[0]) if args else ", "
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return sep.join(_text(item) for item in value)
    except TypeError:
        return _text(value)


def filter_linebreaks(value: Any, args: tuple[Any, ...]) -> str:
    """Convert newlines to paragraphs/breaks — output is trusted HTML."""
    text = html.escape(_text(value))
    paragraphs = [p.strip() for p in text.split("\n\n")]
    rendered = []
    for paragraph in paragraphs:
        if not paragraph:
            continue
        inline = paragraph.replace("\n", "<br>")
        rendered.append(f"<p>{inline}</p>")
    return mark_safe("".join(rendered))


def filter_url_encode(value: Any, args: tuple[Any, ...]) -> str:
    from urllib.parse import quote

    return quote(_text(value), safe="")


#: Schemes that must never appear in a rendered href/URL.
_BLOCKED_URL_SCHEMES = ("javascript:", "data:", "vbscript:", "file:")


def sanitize_url(value: Any) -> str:
    """Strip dangerous URL schemes; return a safe URL string.

    Applies to any dynamic value that will be placed in an ``href``/``src``
    attribute. Relative paths and http(s) URLs pass through; blocked schemes
    are replaced with ``#`` so a crafted value cannot execute script.
    """
    text = _text(value).strip()
    lowered = text.lower()
    for scheme in _BLOCKED_URL_SCHEMES:
        if lowered.startswith(scheme):
            return "#"
    return text


def filter_safe_url(value: Any, args: tuple[Any, ...]) -> str:
    """Sanitize a URL value for use in an href — output is trusted HTML."""
    return mark_safe(sanitize_url(value))


class FilterRegistry:
    """Registry of named value filters.

    Filters are looked up by name at parse time so an unknown filter is a
    validation error, never a silent no-op.
    """

    def __init__(self) -> None:
        self._filters: dict[str, FilterFunc] = {}
        self._safe: set[str] = set()

    def register(self, name: str, func: FilterFunc, *, safe: bool = False) -> None:
        if not name or not name.isidentifier():
            raise ValueError(f"Invalid filter name: {name!r}")
        self._filters[name] = func
        if safe:
            self._safe.add(name)
        else:
            self._safe.discard(name)

    def get(self, name: str) -> FilterFunc | None:
        return self._filters.get(name)

    def is_safe(self, name: str) -> bool:
        return name in self._safe

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._filters))

    def apply(self, name: str, value: Any, args: tuple[Any, ...]) -> Any:
        func = self._filters.get(name)
        if func is None:
            raise KeyError(f"Unknown filter: {name}")
        return func(value, args)


_default_registry = FilterRegistry()


def _register_builtin_filters() -> None:
    _default_registry.register("currency", filter_currency)
    _default_registry.register("date", filter_date)
    _default_registry.register("upper", filter_upper)
    _default_registry.register("lower", filter_lower)
    _default_registry.register("title", filter_title)
    _default_registry.register("truncate", filter_truncate)
    _default_registry.register("default", filter_default)
    _default_registry.register("yesno", filter_yesno)
    _default_registry.register("phone", filter_phone)
    _default_registry.register("length", filter_length)
    _default_registry.register("join", filter_join)
    _default_registry.register("linebreaks", filter_linebreaks, safe=True)
    _default_registry.register("url_encode", filter_url_encode)
    _default_registry.register("safe_url", filter_safe_url, safe=True)


_register_builtin_filters()


def register_filter(name: str, func: FilterFunc, *, safe: bool = False) -> None:
    """Register a custom filter on the default registry (product extension point)."""
    _default_registry.register(name, func, safe=safe)


def get_filter(name: str) -> FilterFunc | None:
    return _default_registry.get(name)


def default_registry() -> FilterRegistry:
    return _default_registry


__all__ = [
    "FilterRegistry",
    "FilterFunc",
    "MISSING",
    "default_registry",
    "get_filter",
    "register_filter",
    "sanitize_url",
]
