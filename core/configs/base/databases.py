# ====================================
# 🗄️ Database Configuration
# ====================================
import os
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

def _resolve_env_placeholder(value: str, default: str = "") -> str:
    """Resolve `@env VAR fallback` placeholders used in YAML config files."""
    if isinstance(value, str) and value.startswith("@env "):
        parts = value.split(maxsplit=2)
        env_name = parts[1] if len(parts) > 1 else ""
        fallback = parts[2] if len(parts) > 2 else default
        return os.environ.get(env_name, fallback) if env_name else default
    return value


if db_conf:
    def _db_get(key, default=None):
        try:
            value = db_conf.get(key, default)
            if isinstance(value, str) and value.startswith("@env "):
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
