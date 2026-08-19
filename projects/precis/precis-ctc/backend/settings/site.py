"""Site identity, branding, render mode, languages, and task center.

Every value resolves through ``cfg()`` (env var → Dynaconf YAML → fallback)
so operators can override branding, colors, render mode, and the supported
content languages without editing code.
"""

from pathlib import Path

from configs.default import *  # noqa: E402,F401,F403

__all__ = [
    "WEBSITE_NAME",
    "WEBSITE_IDENTIFIER",
    "WAGTAIL_SITE_NAME",
    "FUSION_TASK_SITE_NAME",
    "FUSION_TASK_EXECUTION_MODEL",
    "FUSION_TASK_MODULES",
    "FUSION_SITE_NAME",
    "FUSION_COMPANY_NAME",
    "FUSION_CREATOR_NAME",
    "FUSION_PRIMARY_COLOR",
    "FUSION_SECONDARY_COLOR",
    "FUSION_RENDER_FIRST",
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
# Site Identity
# ═══════════════════════════════════════════════════════════════════
WEBSITE_NAME = "precis-ctc"
WEBSITE_IDENTIFIER = "precis-ctc"
WAGTAIL_SITE_NAME = cfg("WAGTAIL_SITE_NAME", "CTC Research")

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
LANGUAGES = [
    ("en", "English"),
    ("sv", "Swedish"),
    ("fr", "French"),
    ("de", "German"),
    ("es", "Spanish"),
    ("ar", "Arabic"),
    ("pt-br", "Portuguese (Brazil)"),
]
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
