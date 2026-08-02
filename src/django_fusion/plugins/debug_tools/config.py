"""
Configuration constants for django_fusion debug tools.

This module provides configuration constants for development tools
including Silk, Django Debug Toolbar, Livereload, and monitoring.

Constants:
    BASE_DIR: Base directory path for the project.
    ENABLE_SILK_PROFILING: Enable Silk profiling.
    DEBUG_TOOLBAR_ENABLED: Enable Django Debug Toolbar.
    LIVERELOAD_ENABLED: Enable Livereload.
    ENABLE_METRICS: Enable Prometheus metrics.
    SENTRY_ENABLED: Enable Sentry error tracking.

Usage in Django settings::

    from django_fusion.contrib.debug_tools.config import DEBUG_TOOLBAR_ENABLED
"""

from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ====================================
# 🎛️ Development Mode
# ====================================
# Set these in your settings.py:

# ====================================
# 📊 Silk Profiling Configuration
# ====================================
ENABLE_SILK_PROFILING = True
SILK_ENABLED = ENABLE_SILK_PROFILING
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
SILKY_PYTHON_PROFILER_RESULT_PATH = BASE_DIR / 'profiles'
SILKY_META = True
SILKY_AUTHENTICATION = True
SILKY_AUTHORISATION = True
SILKY_MAX_RECORDED_REQUESTS = 10**4
SILKY_MAX_RECORDED_REQUESTS_CHECK_PERCENT = 10
SILKY_INTERCEPT_PERCENT = 50  # Profile 50% of requests
SILKY_ANALYZE_QUERIES = True

# ====================================
# 🛠️ Debug Toolbar Configuration
# ====================================
DEBUG_TOOLBAR_ENABLED = True

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": "configs.utils.debug_toolbar.callbacks.show_toolbar",
    "DISABLE_PANELS": ["debug_toolbar.panels.history.HistoryPanel", "debug_toolbar.panels.redirects.RedirectsPanel"],
    "RESULTS_CACHE_SIZE": 25,
    "SHOW_COLLAPSED": False,
    "UPDATE_ON_FETCH": False,
    "INSERT_BEFORE": "<script>",
    "SQL_WARNING_THRESHOLD": 200,
    "IS_RUNNING_TESTS": False,
}

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
]

# ====================================
# 🔄 Livereload Configuration
# ====================================
LIVERELOAD_ENABLED = True
LIVERELOAD_DEFAULT_PORT = 35729
LIVERELOAD_DEFAULT_HOST = 'localhost'

# ====================================
# 📊 Monitoring Configuration
# ====================================
ENABLE_METRICS = True
ENABLE_HEALTH_CHECKS = True
ENABLE_PROFILING = True
SENTRY_ENABLED = False  # Set to True if using Sentry

# ====================================
# 🎛️ Tool-specific App Names
# ====================================
DEBUG_TOOLBAR_APP = "debug_toolbar"
SILK_APP = "silk"
LIVERELOAD_APP = "livereload"
PROMETHEUS_APP = "django_prometheus"

# ====================================
# 🔗 Middleware Classes
# ====================================
DEBUG_TOOLBAR_MIDDLEWARE = "debug_toolbar.middleware.DebugToolbarMiddleware"
SILK_MIDDLEWARE = "silk.middleware.SilkyMiddleware"
LIVERELOAD_MIDDLEWARE = "livereload.middleware.LiveReloadScript"
PROMETHEUS_BEFORE_MIDDLEWARE = "django_prometheus.middleware.PrometheusBeforeMiddleware"
PROMETHEUS_AFTER_MIDDLEWARE = "django_prometheus.middleware.PrometheusAfterMiddleware"

# ====================================
# 🎯 Default Positions
# ====================================
DEFAULT_MIDDLEWARE_POSITIONS = {
    'prometheus_before': 0,      # First
    'silk': 1,                   # After prometheus
    'livereload': 2,             # After silk
    'debug_toolbar': 3,          # After livereload
    'prometheus_after': None,    # Last (append)
}

# ====================================
# 📁 Auto-reload Configuration
# ====================================
AUTORELOAD_TEMPLATE_LOADERS = [
    ('django.template.loaders.filesystem.Loader', [str(BASE_DIR / 'templates')]),
    ('django.template.loaders.app_directories.Loader',),
]

AUTORELOAD_WATCH_PATHS = [
    'templates',
    'static',
    'media',
]

# ====================================
# 🔍 Template Debugging
# ====================================
TEMPLATE_DEBUG = True  # Enable detailed template errors
