# ====================================
# 🗄️ Database Configuration
# ====================================
from ..settings.setup import settings

# -------------------------------
# Database Configuration
# -------------------------------


def _get_config_value(config, key, default=None):
    """Read values from Dynaconf boxes or plain dictionaries."""
    if config is None:
        return default

    if hasattr(config, "get"):
        value = config.get(key, default)
        if value is not None:
            return value

    return getattr(config, key, default)


def _sqlite_database(name="db.sqlite3", atomic_requests=True):
    """Build a SQLite database configuration for local development/testing."""
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": name,
        "ATOMIC_REQUESTS": atomic_requests,
    }


def _postgres_database(db_conf):
    """Build a PostgreSQL database configuration from Dynaconf/env values."""
    return {
        "ENGINE": _get_config_value(db_conf, "ENGINE", "django.db.backends.postgresql"),
        "NAME": _get_config_value(db_conf, "NAME", "vresume"),
        "USER": _get_config_value(db_conf, "USER", "vresume"),
        "PASSWORD": _get_config_value(db_conf, "PASSWORD", "mk_pAssWord123"),
        "HOST": _get_config_value(db_conf, "HOST", "vresume-postgres"),
        "PORT": _get_config_value(db_conf, "PORT", "5432"),
        "CONN_MAX_AGE": _get_config_value(db_conf, "CONN_MAX_AGE", 0),
        "CONN_HEALTH_CHECKS": True,
        "OPTIONS": _get_config_value(db_conf, "OPTIONS", {}),
        "ATOMIC_REQUESTS": _get_config_value(db_conf, "ATOMIC_REQUESTS", False),
    }


# Dynaconf loads the environment-specific DATABASES section from
# configs/settings/ENV/database.yml. This keeps Django, local env vars, and
# Docker Compose on a single DB_* contract.
db_conf = _get_config_value(settings.section("DATABASES"), "default")
db_engine = _get_config_value(db_conf, "ENGINE", "django.db.backends.sqlite3")

if db_engine == "django.db.backends.postgresql":
    DATABASES = {"default": _postgres_database(db_conf)}
else:
    DATABASES = {
        "default": _sqlite_database(
            name=_get_config_value(db_conf, "NAME", "db.sqlite3"),
            atomic_requests=_get_config_value(db_conf, "ATOMIC_REQUESTS", True),
        )
    }

# -------------------------------
# Database Router (if needed)
# -------------------------------
DATABASE_ROUTERS = settings.get_list("DATABASE_ROUTERS", [])
