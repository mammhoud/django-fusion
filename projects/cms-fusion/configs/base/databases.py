# ====================================
# 🗄️ Database Configuration
# ====================================
import os
import re
from pathlib import Path

from ..settings.conf import settings

BASE_DIR = Path(__file__).resolve().parents[2]

# Safe defaults for local/dev boot
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "dev_db.sqlite3"),
        "ATOMIC_REQUESTS": False,
    }
}

# Optional dynaconf override if DATABASES.default is available
try:
    db_conf = settings.get("DATABASES.default") if hasattr(settings, "get") else None
except Exception:
    db_conf = None


_JINJA_ENV_GET_RE = re.compile(
    r"""@jinja\s*\{\{.*?env\.get\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]*)['\"])?.*?}}""",
)


def _resolve_env_placeholder(value: str, default: str = "") -> str:
    """Resolve `@env VAR fallback` and `@jinja` placeholders from YAML config files.

    Handles:
      - ``@env VAR_NAME fallback``   — direct environment lookup
      - ``@jinja {{ env.get('VAR_NAME', 'fallback') }}`` — Dynaconf Jinja template

    When the resolved value is a relative path and *default* is an absolute path,
    *default* is preferred (handles the case where the YAML fallback is relative
    while the code-level default is an absolute path).
    """
    if not isinstance(value, str):
        return value

    # @env VAR fallback
    if value.startswith("@env "):
        parts = value.split(maxsplit=2)
        env_name = parts[1] if len(parts) > 1 else ""
        fallback = parts[2] if len(parts) > 2 else default
        resolved = os.environ.get(env_name, fallback) if env_name else default
        return _prefer_abs(resolved, default)

    # @jinja {{ env.get('VAR', 'fallback') }}
    match = _JINJA_ENV_GET_RE.match(value.strip())
    if match:
        env_name = match.group(1)
        fallback = match.group(2) if match.group(2) is not None else default
        resolved = os.environ.get(env_name)
        if resolved is not None:
            return resolved
        return _prefer_abs(fallback, default)

    return value


def _prefer_abs(resolved: str, default: str) -> str:
    """Return the caller's *default* (absolute) when *resolved* is a relative path.

    This prevents relative YAML fallbacks (e.g. ``projects/dev_db.sqlite3``)
    from overriding the code-level absolute path from ``DATABASES["default"]``.
    """
    if not resolved or resolved.startswith("/") or resolved.startswith(":memory:"):
        return resolved
    if default and default.startswith("/"):
        return default
    return resolved


if db_conf:
    def _db_get(key, default=None):
        try:
            value = db_conf.get(key, default)
            if isinstance(value, str) and (
                value.startswith("@env ") or value.startswith("@jinja")
            ):
                return _resolve_env_placeholder(value, default)
            return value
        except ImportError:
            return default

    DATABASES["default"] = {
        "ENGINE": _db_get("ENGINE", DATABASES["default"]["ENGINE"]),
        "NAME": _db_get("NAME", DATABASES["default"]["NAME"]),
        "USER": _db_get("USER", ""),
        "PASSWORD": _db_get("PASSWORD", ""),
        "HOST": _db_get("HOST", ""),
        "PORT": _db_get("PORT", ""),
        "CONN_MAX_AGE": _db_get("CONN_MAX_AGE", 60),
        "CONN_HEALTH_CHECKS": _db_get("CONN_HEALTH_CHECKS", True),
        "OPTIONS": _db_get("OPTIONS", {}),
        "ATOMIC_REQUESTS": _db_get("ATOMIC_REQUESTS", False),
    }

DATABASE_ROUTERS = []

MIGRATION_MODULES = {
    "sites": "www.migrations",
    "www_core": None,
}
