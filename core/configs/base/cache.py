# ====================================
# 💾 Cache & Session Configuration
# ====================================
import multiprocessing

from .. import settings, tracker

REDIS_URL = settings.get("REDIS_URL", "redis://localhost:6379/0")
REDIS_SSL = REDIS_URL.startswith("rediss://")

# Default: local memory cache (dev/local)
# Override in production via Redis if REDIS_URL is set
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

SESSION_ENGINE = "django.contrib.sessions.backends.db"

# ---- Django-Q ----
Q_CLUSTER = {
    "name": f"{tracker.MODULE.value}_Cluster",
    "workers": multiprocessing.cpu_count() * 2 + 1,
    "recycle": 500,
    "timeout": 600,
    "retry": 720,
    "queue_limit": 100,
    "bulk": 10,
    "orm": "default",
}

# ---- Celery (eager in dev — tasks run inline) ----
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
