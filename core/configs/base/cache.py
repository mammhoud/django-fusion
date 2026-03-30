# ====================================
# 💾 Cache & Redis Configuration
# ====================================
import multiprocessing

from .. import settings, tracker

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
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,
    },
    "session": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "session_cache_table",
    },
}

# # ====================================
# # 💾 Cache Configuration
# # ====================================
# # Use Redis but with shorter timeouts for demo
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://localhost:6379/2",  # Different DB for demo
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "SOCKET_CONNECT_TIMEOUT": 5,
#             "SOCKET_TIMEOUT": 5,
#             "IGNORE_EXCEPTIONS": True,
#             "PARSER_CLASS": "redis.connection.PythonParser",
#         },
#         "KEY_PREFIX": "demo",
#         "TIMEOUT": 60,  # 1 minute for demo
#     }
# }

# Use database sessions
SESSION_ENGINE = "django.contrib.sessions.backends.db"

# -------------------------------
# Django-Q Configuration
# -------------------------------
Q_CLUSTER = {
    "name": f"{tracker.module}_Cluster",
    "workers": multiprocessing.cpu_count() * 2 + 1,
    "recycle": 500,
    "timeout": 60 * 10,
    "retry": 60 * 12,
    "queue_limit": 100,
    "bulk": 10,
    "orm": "default",  # Use ORM instead of Redis
}

# -------------------------------
# Celery Configuration
# -------------------------------
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

