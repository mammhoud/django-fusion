# ====================================
# 🛠️ Development Environment Settings
# ====================================
from pathlib import Path

from configs.base import *
from ..conf import settings

DEBUG = True
TEMPLATE_DEBUG = DEBUG
MODULE = "cms"

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# ---- Cache (local memory for dev) ----
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 60,
        "OPTIONS": {"MAX_ENTRIES": 1000},
    },
    "file": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "cache",
        "TIMEOUT": 3600,
        "OPTIONS": {"MAX_ENTRIES": 10000},
    },
}

# ---- Feature Flags ----
ENABLE_SWAGGER = True
ENABLE_DEBUG_TOOLBAR = True
ENABLE_GRAPHQL = True
ENABLE_API_DOCS = True

# ---- External service keys — read from env, never hardcoded ----
GOOGLE_MAP_API_KEY = settings.get("GOOGLE_MAP_API_KEY", "")
GOOGLE_ANALYTICS_ID = settings.get("GOOGLE_ANALYTICS_ID", "")
STRIPE_PUBLIC_KEY = settings.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_SECRET_KEY = settings.get("STRIPE_SECRET_KEY", "")

# ---- Templates ----
TEMPLATES[0]["OPTIONS"]["debug"] = True

# ---- Testing ----
TEST_RUNNER = "django.test.runner.DiscoverRunner"
TEST_DISCOVERY_ROOT = BASE_DIR / "tests"
TEST_DISCOVER_PATTERN = "test_*.py"

# ---- Django Extensions (shell_plus) ----
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000
SHELL_PLUS_IMPORTS = [
    "from django.db import connection",
    "from django.db.models import Count, Sum, Avg, Max, Min",
    "import json",
    "from pprint import pprint",
]

# ---- Rate Limiting ----
RATE_LIMIT_ENABLED = False

# ---- Django-RQ (required even if empty) ----
RQ_QUEUES = {}

# ---- Docker: allow container hostname in INTERNAL_IPS ----
if settings.is_docker:
    INTERNAL_IPS.append("core")
