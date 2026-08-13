# ====================================
# 🛠️ Development Environment Settings
# ====================================
import os
from pathlib import Path

from configs.base import *

from ..conf import settings

# ====================================
# 🔧 Core Settings
# ====================================
MODULE = settings.MODULE.value
DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_DIR = Path(settings.WEBSITE_DIR)
WORKSPACE_BASE_DIR = BASE_DIR.parent
WEBSITE_NAME = settings.WEBSITE_NAME
SITE_DOMAIN = settings.SITE_DOMAIN
DOMAIN_NAME = settings.DOMAIN_NAME
SITE_URL = settings.get(
    "SITE_URL",
    f"{'https' if settings.SSL_ENABLED else 'http'}://{SITE_DOMAIN}",
)
BASE_URL = SITE_URL
WAGTAILADMIN_BASE_URL = settings.get("WAGTAILADMIN_BASE_URL", SITE_URL)

# ====================================
# 💾 Cache Configuration
# ====================================
# Use local memory cache for development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 60,  # 1 minute
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    },
    "file": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "cache",
        "TIMEOUT": 60 * 60,  # 1 hour
        "OPTIONS": {
            "MAX_ENTRIES": 10000,
        },
    },
}

# ====================================
# 🚀 Feature Flags
# ====================================
ENABLE_SWAGGER = True
ENABLE_DEBUG_TOOLBAR = True
ENABLE_GRAPHQL = True
ENABLE_API_DOCS = True


# ====================================
# 🔗 External Services
# ====================================
# Development API keys — load from environment, never hardcode
GOOGLE_MAP_API_KEY = os.environ.get("GOOGLE_MAP_API_KEY", "")
GOOGLE_ANALYTICS_ID = os.environ.get("GOOGLE_ANALYTICS_ID", "")
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")

# ====================================
# 📄 Template Configuration
# ====================================
# TEMPLATES[0]["OPTIONS"]["string_if_invalid"] = "INVALID_EXPRESSION"  # Show errors
if "TEMPLATES" in dir() and TEMPLATES:  # noqa: F821
    TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa: F821


# ====================================
# 🧪 Testing Configuration
# ====================================
TEST_RUNNER = "django.test.runner.DiscoverRunner"
TEST_DISCOVERY_ROOT = BASE_DIR / "tests"
TEST_DISCOVER_PATTERN = "test_*.py"

# ====================================
# 📦 Package Management
# ====================================
# Django Extensions
SHELL_PLUS = "ipython"
SHELL_PLUS_PRINT_SQL = True
SHELL_PLUS_PRINT_SQL_TRUNCATE = 1000
SHELL_PLUS_IMPORTS = [
    "from django.db import connection",
    "from django.db.models import Count, Sum, Avg, Max, Min",
    "import json",
    "from pprint import pprint",
]

# ====================================
# 🔐 Security Headers (Development)
# ====================================
SECURE_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

# ====================================
# 🚦 Rate Limiting
# ====================================
RATE_LIMIT_ENABLED = False  # Disable in development

# ====================================
# 📊 Development Metrics
# ====================================
ENABLE_METRICS = True
ENABLE_HEALTH_CHECKS = True
ENABLE_PROFILING = True

# ====================================
# 🎭 Development Features
# ====================================
DEV_FEATURES = {
    "AUTO_CREATE_SUPERUSER": True,
    "LOAD_FIXTURES": True,
    "ENABLE_DEBUG_PAGES": True,
    "SHOW_SQL_QUERIES": True,
    "ENABLE_PERFORMANCE_LOGGING": True,
}

# ====================================
# 🐳 Docker Development
# ====================================
# Docker-specific settings
if settings.RUNNING_ENV.value == "docker":
    if "INTERNAL_IPS" in dir():  # noqa: F821
        INTERNAL_IPS.append("web")  # noqa: F821

# ====================================
# 🔧 Development Commands
# ====================================
# # Custom management commands
# MANAGEMENT_COMMANDS = {
#     "create_dev_data": "core.management.commands.create_dev_data",
#     "reset_dev_db": "core.management.commands.reset_dev_db",
#     "run_dev_server": "core.management.commands.run_dev_server",
# }

# ====================================
# 🎯 Development Goals
# ====================================
DEV_GOALS = {
    "FAST_STARTUP": True,
    "HOT_RELOAD": True,
    "EASY_DEBUGGING": True,
    "QUICK_ITERATION": True,
    "MINIMAL_DEPS": True,
}
