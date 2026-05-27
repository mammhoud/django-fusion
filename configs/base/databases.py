# ====================================
# 🗄️ Database Configuration
# ====================================
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

if db_conf:
    DATABASES["default"] = {
        "ENGINE": db_conf.get("ENGINE", DATABASES["default"]["ENGINE"]),
        "NAME": db_conf.get("NAME", DATABASES["default"]["NAME"]),
        "USER": db_conf.get("USER", ""),
        "PASSWORD": db_conf.get("PASSWORD", ""),
        "HOST": db_conf.get("HOST", ""),
        "PORT": db_conf.get("PORT", ""),
        "CONN_MAX_AGE": db_conf.get("CONN_MAX_AGE", 60),
        "CONN_HEALTH_CHECKS": db_conf.get("CONN_HEALTH_CHECKS", True),
        "OPTIONS": db_conf.get("OPTIONS", {}),
        "ATOMIC_REQUESTS": db_conf.get("ATOMIC_REQUESTS", False),
    }

DATABASE_ROUTERS = []

MIGRATION_MODULES = {
    "sites": "www.migrations",
    "www_core": None,
}
