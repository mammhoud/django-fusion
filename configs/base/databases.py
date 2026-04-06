# ====================================
# 🗄️ Database Configuration
# default/development = SQLite
# production/staging  = PostgreSQL from env
# ====================================
from ..settings.conf import Environment, settings

db_conf = settings.DATABASES.default if (
    hasattr(settings, "DATABASES") and hasattr(settings.DATABASES, "default")
) else None

def _pg_from_conf(conn_max_age=0, atomic=False):
    """Build a PostgreSQL DATABASES dict from dynaconf db_conf."""
    return {
        "ENGINE": getattr(db_conf, "ENGINE", "django.db.backends.postgresql"),
        "NAME": getattr(db_conf, "NAME", "db_structa"),
        "USER": getattr(db_conf, "USER", "postgres"),
        "PASSWORD": getattr(db_conf, "PASSWORD", ""),
        "HOST": getattr(db_conf, "HOST", "postgres"),
        "PORT": getattr(db_conf, "PORT", "5432"),
        "CONN_MAX_AGE": conn_max_age,
        "CONN_HEALTH_CHECKS": True,
        "ATOMIC_REQUESTS": atomic,
        "OPTIONS": dict(getattr(db_conf, "OPTIONS", {})),
    }

# ---- development / default: SQLite ----
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": settings.get("DB_NAME", "db.sqlite3"),
        "ATOMIC_REQUESTS": False,
    }
}

# ---- production / staging: PostgreSQL ----
if settings.SERVER_ENV in (Environment.PRODUCTION, Environment.STAGING):
    if db_conf:
        DATABASES["default"] = _pg_from_conf(conn_max_age=0, atomic=False)
    else:
        # Fallback — should not happen if .env is set correctly
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "fallback.sqlite3",
                "ATOMIC_REQUESTS": False,
            }
        }

DATABASE_ROUTERS = []
