# ====================================
# 💾 Cache & Redis Configuration
# ====================================
import importlib

from ..settings.conf import settings
from ..settings.conf import settings as tracker


def _dramatiq_middleware_available(path: str) -> bool:
    """Best-effort middleware availability check for the dramatiq broker.

    Mirrors `core.configs.base.middlewares._middleware_available` so a missing
    optional middleware (e.g. ``dramatiq.middleware.Prometheus`` from
    ``dramatiq-prometheus`` when that extra isn't installed) degrades the
    middleware list at module-load time rather than crashing Django app init.
    """
    module_name, _, class_name = path.rpartition(".")
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return False
    return hasattr(module, class_name)

# -------------------------------
# Redis Configuration
# -------------------------------
REDIS_URL = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/0')
REDIS_SSL = REDIS_URL.startswith("rediss://")

# -------------------------------
# Django Cache Configuration
# -------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 100,
                "retry_on_timeout": True,
            },
            "IGNORE_EXCEPTIONS": not tracker.is_production,
            "PARSER_CLASS": "redis.connection.HiredisParser" if not REDIS_SSL else "redis.connection.PythonParser",
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "COMPRESSOR_LEVEL": 5,
        },
        "KEY_PREFIX": f"{tracker.MODULE.value.lower()}:{tracker.SERVER_ENV.value}",
        "TIMEOUT": 300,  # 5 minutes default
    },
    "session": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"{REDIS_URL.rsplit('/', 1)[0]}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": f"{tracker.MODULE.value.lower()}:session",
    },
}

# Use session cache for sessions
if tracker.is_production:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "session"

# -------------------------------
# Dramatiq Configuration
# -------------------------------
DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.redis.RedisBroker",
    "OPTIONS": {
        "url": REDIS_URL,
    },
    "MIDDLEWARE": [
        m
        for m in [
            "dramatiq.middleware.Prometheus",
            "dramatiq.middleware.AgeLimit",
            "dramatiq.middleware.TimeLimit",
            "dramatiq.middleware.Callbacks",
            "dramatiq.middleware.Retries",
            "django_dramatiq.middleware.AdminMiddleware",
            "django_dramatiq.middleware.DbConnectionsMiddleware",
        ]
        if _dramatiq_middleware_available(m)
    ],
}

# -------------------------------
# Dramatiq Configuration
# -------------------------------
FUSION_TASKS = {
    "BACKEND": "django_fusion.tasks.backends.dramatiq.DramatiqBackend",
    "BROKER_URL": REDIS_URL,
}
DRAMATIQ_BROKER_URL = REDIS_URL

# -------------------------------
# Cache Timeouts
# -------------------------------
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = f"{tracker.MODULE.value.lower()}_middleware"

# -------------------------------
# Redis Health Check
# -------------------------------
REDIS_HEALTH_CHECK = {
    "enabled": True,
    "timeout": 3,
    "retries": 3,
    "interval": 30,  # seconds
}

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

