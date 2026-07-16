"""Website-local Django settings for ctc-research."""
import os
import sys
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"

# Ensure correct import paths.
# Iteration order is REVERSED so `sys.path.insert(0, …)` puts the per-site
# `www/` (which carries `www.core`, `www.worker`, etc.) at the front of
# sys.path[0], ahead of the workspace `/app` whose `/app/www` only contains
# the shared `ci/` and `worker/` subpackages — without `core/`. Doing this
# in the apparent “natural” order leaves `/app` at sys.path[0] and
# `import www.core` then fails with ModuleNotFoundError because the workspace
# `www` shadows the site `www`.
for _path in (str(_WORKSPACE_DIR), str(_SITE_DIR), str(_SITE_APP_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ============================================================
# Site Configuration
# ============================================================
from configs.site import configure_site_environment

configure_site_environment("ctc-research", module="LMS", default_port=5070)

# ============================================================
# Internal Dependency Handling
# ============================================================
# django_fusion and ceptor_ai are real workspace dependencies. Do not install
# fake sys.modules shims here; dependency failures should surface during checks.

# ============================================================
# Import Shared Django Settings
# ============================================================
from configs.settings import *  # noqa: E402,F401,F403

# ============================================================
# URL and Application Configuration
# ============================================================
ROOT_URLCONF = "www.urls"

# ASGI/WSGI applications live in the site-local server.py.
# The start script places this site directory on PYTHONPATH and launches
# server:application, so Django can keep the same import path.
ASGI_APPLICATION = "server.application"
WSGI_APPLICATION = "server.application"

# ============================================================
# Website-Specific Settings
# ============================================================
WEBSITE_NAME = "ctc-research"
WEBSITE_IDENTIFIER = "ctc-research"
SITE_ID = 1

# ── Local apps (site-specific plugins, www packages, and page apps) ──
# NOTE: `www.worker` is NOT listed here because `core.configs.base.apps`
# already registers it globally as a shared worker module — including it
# here would register the same app label twice and Django would raise
# `ImproperlyConfigured: Application labels aren't unique`.
LOCAL_APPS = [
    "www.core",
    "www.core.content.apps.ContentConfig",
    "www.core.handlers.apps.AccountsConfig",
    "plugins.accounts.apps.AccountsConfig",
    "plugins.lms.apps.LmsConfig",
    "plugins.blog.apps.BlogConfig",
    "plugins.products.apps.ProductsConfig",
    "plugins.profile.apps.ProfileConfig",
    "ceptor_ai",
    "django_fusion.analyzer.apps.AnalyzerAppConfig",
]
INSTALLED_APPS += LOCAL_APPS

# ============================================================
# ceptor_ai required settings
# ============================================================
# PROFILE_MODEL is a required ForeignKey target in ceptor_ai models.
# Point it to Django's built-in User model since this project
# does not have a separate profile model.
PROFILE_MODEL = "auth.User"

# ============================================================
# Silenced system checks
# ============================================================
# Keep only legacy duplicated app/model checks silenced; the previous
# TeamMembership ordering check is fixed in ceptor_ai.
SILENCED_SYSTEM_CHECKS = [
    "models.E028",  # legacy accounts/handlers shared service table during migration
    "models.E030",  # legacy accounts/handlers shared indexes during migration
    "models.E032",  # legacy accounts/handlers shared constraints during migration
    "fields.E304",  # legacy duplicated profile reverse accessors
    "fields.E305",  # legacy duplicated profile reverse query names
    "fields.E340",  # legacy duplicated many-to-many intermediary tables
]
WAGTAIL_WORKFLOW_ENABLED = False
