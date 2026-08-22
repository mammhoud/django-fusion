"""Site identity, branding, render mode, languages, and task center.

Every value resolves through ``cfg()`` (env var → Dynaconf YAML → fallback)
so operators can override branding, colors, render mode, and the supported
content languages without editing code.

Site identity also sources from the project config cascade (configs/*.yml)
via django-fusion's ``config.project`` loader — the same base-URL resolution
precis-main uses — so the admin URL/domains follow the resolved origin.
"""

import os
from pathlib import Path

from configs.default import *  # noqa: E402,F401,F403

__all__ = [
    "WEBSITE_NAME",
    "WEBSITE_IDENTIFIER",
    "WAGTAIL_SITE_NAME",
    "WAGTAILADMIN_BASE_URL",
    "DEFAULT_FROM_EMAIL",
    "FUSION_TASK_SITE_NAME",
    "FUSION_TASK_EXECUTION_MODEL",
    "FUSION_TASK_MODULES",
    "FUSION_SITE_NAME",
    "FUSION_COMPANY_NAME",
    "FUSION_CREATOR_NAME",
    "FUSION_PRIMARY_COLOR",
    "FUSION_SECONDARY_COLOR",
    "FUSION_RENDER_FIRST",
    "LANGUAGE_CODE",
    "LANGUAGE_SESSION_KEY",
    "LANGUAGE_COOKIE_NAME",
    "LANGUAGE_COOKIE_AGE",
    "LANGUAGE_COOKIE_DOMAIN",
    "LANGUAGE_COOKIE_PATH",
    "LANGUAGE_COOKIE_SECURE",
    "LANGUAGE_COOKIE_HTTPONLY",
    "LANGUAGE_COOKIE_SAMESITE",
    "LANGUAGES",
    "FUSION_DEFAULT_CURRENCY",
    "LANGUAGES_BIDI",
    "LOCALE_PATHS",
    "WAGTAIL_I18N_ENABLED",
    "WAGTAIL_CONTENT_LANGUAGES",
    "WAGTAIL_I18N_LOCALE_MODEL",
]

_SITE_DIR = Path(__file__).resolve().parent.parent
_WORKSPACE_DIR = _SITE_DIR.parent

# ═══════════════════════════════════════════════════════════════════
# Layered config cascade (project configs, precis-main parity)
# ═══════════════════════════════════════════════════════════════════
# Sources env-read *defaults* from the project configs dir (configs/README.md):
# shared Env YAML → configs/*.yml → Env/_site.yml → .env, with environment
# variables always winning. The cascade is optional sugar — a container or
# checkout without configs/ behaves exactly as before (env-only).
# See libs/django-fusion/src/django_fusion/config/project.py.
try:
    from django_fusion.config.project import load_config

    _cascade = load_config(_SITE_DIR)
except Exception:  # pragma: no cover — cascade is optional; never break boot
    _cascade = None


def _cfg(key: str, default=None):
    """Return a cascade value (env already wins inside the cascade) or default."""
    if _cascade is None:
        return default
    value = _cascade.get(key, default)
    return default if value is None else value


def _cfg_list(key: str, default: str) -> str:
    """Return a cascade list/string as a comma-joined string or default."""
    value = _cfg(key, None)
    if isinstance(value, (list, tuple)):
        return ",".join(str(item) for item in value)
    if value:
        return str(value)
    return default


# ── Base-URL resolution (per-origin site identity) ────────────────────────
# Resolve the backend origin's site identity from the cascade so admin URLs
# and domains follow the resolved host — the same contract precis-main's
# `make config-show` prints. Environment still wins for identity keys.
_BACKEND_BASE_URL = (
    os.environ.get("WAGTAILADMIN_BASE_URL")
    or _cfg("ADMIN.wagtailadmin_base_url", "https://ctc-research.com")
)
_resolved = (
    _cascade.resolve(_BACKEND_BASE_URL, "back") if _cascade is not None else {}
)
_resolved_site = _resolved.get("SITE", {}) if isinstance(_resolved, dict) else {}


def _site_cfg(key: str, default=None):
    """Resolved SITE value → cascade SITE value → default."""
    if isinstance(_resolved_site, dict) and _resolved_site.get(key) is not None:
        return _resolved_site[key]
    return _cfg(f"SITE.{key}", default)


# ═══════════════════════════════════════════════════════════════════
# Site Identity
# ═══════════════════════════════════════════════════════════════════
WEBSITE_NAME = os.environ.get(
    "WEBSITE_NAME", _site_cfg("runtime_name", _site_cfg("name", "precis-ctc"))
)
WEBSITE_IDENTIFIER = os.environ.get("WEBSITE_IDENTIFIER", WEBSITE_NAME)
WAGTAIL_SITE_NAME = os.environ.get(
    "WAGTAIL_SITE_NAME",
    _site_cfg("wagtail_site_name", _cfg("ADMIN.wagtail_site_name", "CTC Research")),
)
WAGTAILADMIN_BASE_URL = os.environ.get(
    "WAGTAILADMIN_BASE_URL",
    _cfg("ADMIN.wagtailadmin_base_url", "https://ctc-research.com"),
)
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    _site_cfg("default_email", "CTC Research <noreply@ctc-research.com>"),
)

# ── ALLOWED_HOSTS — merge cascade hosts (additive; never removes) ────────
# The shared stack (configs/Env/sites.yml + compose env) already covers the
# public hosts; the cascade SITE.allowed_hosts is merged in for parity with
# precis-main so a host added in configs/site.yml is honoured immediately.
_cascade_hosts = _cfg_list("SITE.allowed_hosts", "")
if _cascade_hosts:
    for _host in (h.strip() for h in _cascade_hosts.split(",") if h.strip()):
        if _host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(_host)

# ── Task Center (website-record contract) ──────────────────────────
# The shared worker writes django_fusion's BackgroundTaskLog; the authenticated
# /tasks/ page (and the scheduled sync_task_history job) mirror it into
# apps.tasks.TaskExecution filtered by this site so the website record stays
# fresh without a Task Center page view.
FUSION_TASK_SITE_NAME = cfg("FUSION_TASK_SITE_NAME", WEBSITE_NAME)
FUSION_TASK_EXECUTION_MODEL = cfg("FUSION_TASK_EXECUTION_MODEL", "tasks.TaskExecution")
FUSION_TASK_MODULES = [
    "plugins.workers.email_tasks",
    "plugins.workers.course_tasks",
    "plugins.workers.content_tasks",
    "plugins.workers.legacy_email_tasks",
    "plugins.workers.campaign_tasks",
]


# ═══════════════════════════════════════════════════════════════════
# Branding — teal theme (env var > _site.yml > fallback)
# ═══════════════════════════════════════════════════════════════════
FUSION_SITE_NAME = cfg("FUSION_SITE_NAME", "CTC Research")
FUSION_COMPANY_NAME = cfg("FUSION_COMPANY_NAME", "CTC Research")
FUSION_CREATOR_NAME = cfg("FUSION_CREATOR_NAME", "CTC Research Team")
FUSION_PRIMARY_COLOR = cfg("FUSION_PRIMARY_COLOR", "#00a1b3")
FUSION_SECONDARY_COLOR = cfg("FUSION_SECONDARY_COLOR", "#008080")


# ═══════════════════════════════════════════════════════════════════
# Render-First — disabled by default for LMS
# ═══════════════════════════════════════════════════════════════════
# Astro is the active document renderer after the cms-fusion consolidation.
# Requests may still override this with X-Fusion-Render-First for compatibility.
# The same flag drives asset loading: with ``render_first_gates_assets`` on in
# FUSION_PIPELINE, webpack/skeleton links are only served while render-first
# is active (see django-fusion ``AssetPipelineOptions``).
FUSION_RENDER_FIRST = cfg("FUSION_RENDER_FIRST", True)

# Keep the Wagtail locale contract aligned with dump-data.json. In particular,
# pt-br is an existing public fixture locale and must not be normalized to pt.
# The shared CD settings provide the Wagtail switches; these explicit values
# make this site's supported content languages unambiguous.
LANGUAGE_CODE = cfg("LANGUAGE_CODE", "en")
# Django's stock set_language view only writes the cookie. The CTC API also
# stores this key in the session so Wagtail/API/HTMX requests share one
# preference even when a client suppresses or refreshes cookies.
LANGUAGE_SESSION_KEY = cfg("LANGUAGE_SESSION_KEY", "_language")
LANGUAGE_COOKIE_NAME = cfg("LANGUAGE_COOKIE_NAME", "django_language")
LANGUAGE_COOKIE_AGE = int(cfg("LANGUAGE_COOKIE_AGE", 60 * 60 * 24 * 365))
LANGUAGE_COOKIE_DOMAIN = cfg("LANGUAGE_COOKIE_DOMAIN", None)
LANGUAGE_COOKIE_PATH = cfg("LANGUAGE_COOKIE_PATH", "/")
LANGUAGE_COOKIE_SECURE = bool(cfg("LANGUAGE_COOKIE_SECURE", not DEBUG))
LANGUAGE_COOKIE_HTTPONLY = bool(cfg("LANGUAGE_COOKIE_HTTPONLY", False))
LANGUAGE_COOKIE_SAMESITE = cfg("LANGUAGE_COOKIE_SAMESITE", "Lax")

# Unified catalog currency — one setting drives products + courses + editions
# pricing across both websites (precis-landing parity). Products and courses
# fall back to it when no per-record currency is set.
FUSION_DEFAULT_CURRENCY = cfg("FUSION_DEFAULT_CURRENCY", "USD")
LANGUAGES_BIDI = ["ar"]
# The Docker image consolidates the project asset tree at /app/assets while
# local development keeps it at <site>/assets. Resolve both from the shared
# asset root so gettext loads the same catalogs in local, test, and container
# processes instead of silently falling back to English.
_LOCALE_DIR = _WORKSPACE_DIR / "assets" / "locale"
_LOCALE_FALLBACK_DIR = _SITE_DIR / "assets" / "locale"
LOCALE_PATHS = [
    str(path)
    for path in (_LOCALE_DIR, _LOCALE_FALLBACK_DIR)
    if path.exists()
]
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES
WAGTAIL_I18N_LOCALE_MODEL = "wagtailcore.Locale"


# ═══════════════════════════════════════════════════════════════════
# Branding Context Processor — resolved from _site.yml
# ═══════════════════════════════════════════════════════════════════
TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    cfg("FUSION_BRANDING_BACKEND",
        "django_fusion.contrib.branding.context_processors.fusion_branding_context")
)

# SEO metadata context — exposes request.seo_context (resolved from
# SiteSettings by the Wagtail serve hook) to base.html so meta tags are
# Wagtail-managed rather than hardcoded.
TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    "apps.pages.context_processors.seo_context_processor"
)
