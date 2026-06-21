"""django_osoul.contrib.context — context processors."""
from .auth import AUTH_SETTINGS  # noqa: F401
from .cookies import COOKIES  # noqa: F401
from .htmx import CONTEXT as HTMX  # noqa: F401
from .languages import LANGUAGES  # noqa: F401
from .settings import SETTINGS  # noqa: F401

# Aliases for backward compatibility
LANGUAGES_CONTEXT = LANGUAGES

__all__ = ["AUTH_SETTINGS", "COOKIES", "HTMX", "LANGUAGES", "LANGUAGES_CONTEXT", "SETTINGS"]
