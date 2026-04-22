# ====================================
# 🗄️ Database Configuration
# ====================================
from ..settings.conf import Environment, settings

# -------------------------------
# Database Configuration
# -------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "dev_db.sqlite3",
        "ATOMIC_REQUESTS": False,
    }
}
db_conf = settings.DATABASES.default
# print(db_conf)
# Determine database engine based on environment
if settings.SERVER_ENV == Environment.DEVELOPMENT:
    # Demo environment: SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "dev_db.sqlite3",
            "ATOMIC_REQUESTS": True,
        }
    }
elif settings.SERVER_ENV == Environment.DEMO:
    if hasattr(settings, "DATABASES") and hasattr(settings.DATABASES, "default"):
        DATABASES["default"] = {
            "ENGINE": db_conf.ENGINE,
            "NAME": db_conf.NAME,
            "USER": db_conf.USER if hasattr(db_conf, "USER") else "",
            "PASSWORD": db_conf.PASSWORD if hasattr(db_conf, "PASSWORD") else "",
            "HOST": db_conf.HOST if hasattr(db_conf, "HOST") else "",
            "PORT": db_conf.PORT if hasattr(db_conf, "PORT") else "",
            "CONN_MAX_AGE": 60,  # Persistent connections (60s) — enables CONN_HEALTH_CHECKS
            "CONN_HEALTH_CHECKS": True,
            "ATOMIC_REQUESTS": False,
        }
    else:
        # Fallback SQLite
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "demo.sqlite3",
                "ATOMIC_REQUESTS": False,
            }
        }
elif settings.SERVER_ENV in [Environment.PRODUCTION, Environment.STAGING]:
    # Production/Staging: PostgreSQL from settings
    if hasattr(settings, "DATABASES") and hasattr(settings.DATABASES, "default"):
        DATABASES["default"] = {
            "ENGINE": db_conf.ENGINE,
            "NAME": db_conf.NAME,
            "USER": db_conf.USER,
            "PASSWORD": db_conf.PASSWORD,
            "HOST": db_conf.HOST,
            "PORT": db_conf.PORT,
            "CONN_MAX_AGE": 60,  # Persistent connections (60s) — enables CONN_HEALTH_CHECKS
            "CONN_HEALTH_CHECKS": True,
            "OPTIONS": db_conf.get("OPTIONS", {}),
            "ATOMIC_REQUESTS": False,
        }
    else:
        # Fallback SQLite
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": "production.sqlite3",
                "ATOMIC_REQUESTS": False,
            }
        }

# -------------------------------
# Database Router (if needed)
# -------------------------------
DATABASE_ROUTERS = []
# print(DATABASES)

# -------------------------------
# Migration Modules
# -------------------------------
# Point django.contrib.sites migrations to our custom location
MIGRATION_MODULES = {
    "sites": "www.migrations",
}

# # -------------------------------
# # Connection Health Check
# # -------------------------------
# DATABASE_CONNECTION_HEALTH_CHECK = {
#     'enabled': True,
#     'timeout': 5,
#     'retries': 3,
# }
