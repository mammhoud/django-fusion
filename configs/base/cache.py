# ====================================
# 💾 Cache & Redis Configuration
# ====================================
import multiprocessing

from ..settings.conf import settings
from ..settings.conf import settings as tracker

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

# Use session cache for sessions
if tracker.is_production:
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "session"

# -------------------------------
# Django-Q Configuration
# -------------------------------
Q_CLUSTER = {
    "name": f"{tracker.MODULE.value}_Cluster",
    "workers": multiprocessing.cpu_count() * 2 + 1,
    "recycle": 500,  # Recycle workers after 500 tasks
    "timeout": 60 * 10,  # 10 minutes
    "retry": 60 * 12,  # 12 minutes
    "queue_limit": 100,
    "bulk": 10,
    "orm": "default",
    "redis": {
        "host": REDIS_URL.split("://")[1].split(":")[0],
        "port": int(REDIS_URL.split(":")[-1].split("/")[0]),
        "db": int(REDIS_URL.split("/")[-1]) if "/" in REDIS_URL else 0,
        "password": None,
        "socket_timeout": 5,
        "socket_connect_timeout": 5,
        "retry_on_timeout": True,
    },
}

# -------------------------------
# Celery Configuration
# -------------------------------
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["json", "msgpack"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = settings.TIME_ZONE if hasattr(settings, 'TIME_ZONE') else "UTC"
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 20 * 60  # 20 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
CELERY_WORKER_CONCURRENCY = multiprocessing.cpu_count() * 2 + 1


CELERY_TASK_ALWAYS_EAGER = settings.core.CELERY.TASK_ALWAYS_EAGER
CELERY_FLOWER_USER = settings.core.CELERY.FLOWER_USER
CELERY_FLOWER_PASSWORD = settings.core.CELERY.FLOWER_PASSWORD
CELERY_TASK_EAGER_PROPAGATES = True
# CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_NONE} if REDIS_SSL else None
# CELERY_REDIS_BACKEND_USE_SSL = CELERY_BROKER_USE_SSL
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_WORKER_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

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

