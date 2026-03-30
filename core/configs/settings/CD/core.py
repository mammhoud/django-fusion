# ====================================
# 🛠️ Development Environment Settings
# ====================================
import os
from pathlib import Path

from configs.base import *

from ..conf import Environment, settings

# ====================================
# 🔧 Core Settings
# ====================================
MODULE = "lms"
DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

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
# Development API keys
GOOGLE_MAP_API_KEY = "dev_google_map_key"
GOOGLE_ANALYTICS_ID = "UA-XXXXX-Y-DEV"
STRIPE_PUBLIC_KEY = "pk_test_dev_key"
STRIPE_SECRET_KEY = "sk_test_dev_key"

# ====================================
# 📄 Template Configuration
# ====================================
# TEMPLATES[0]["OPTIONS"]["string_if_invalid"] = "INVALID_EXPRESSION"  # Show errors
TEMPLATES[0]["OPTIONS"]["debug"] = True


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

    INTERNAL_IPS.append("web")

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

# from django_grep.contrib.debug_tools import quick_setup

# config = quick_setup(
#     installed_apps=INSTALLED_APPS,
#     middleware=MIDDLEWARE,
#     debug=DEBUG,
#     sentry_dsn=os.getenv("SENTRY_DSN"),
#     print_status=False,
# )

# INSTALLED_APPS = config["installed_apps"]
# MIDDLEWARE = config["middleware"]
#
