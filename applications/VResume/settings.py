"""Website-local Django settings for vresume."""
import os
import sys
from pathlib import Path

# ============================================================
# Path Configuration
# ============================================================
_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"

# Ensure correct import paths
for _path in (str(_SITE_APP_DIR), str(_SITE_DIR), str(_WORKSPACE_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ============================================================
# Site Configuration
# ============================================================
from configs.site import configure_site_environment

configure_site_environment("vresume", module="CMS", default_port=5072)

# ============================================================
# Internal Dependency Handling
# ============================================================
# django_osoul and ceptor_ai are real workspace dependencies. Do not install
# fake sys.modules shims here; dependency failures should surface during checks.

# ============================================================
# Import Shared Django Settings
# ============================================================
from configs.settings import *  # noqa: E402,F401,F403

# ============================================================
# Monkey-patch: django-webpack-loader v3.2.3 expects flat-string
# chunks but webpack-bundle-tracker v3+ outputs dict chunks like
# {"name": "foo.js", "path": "...", "url": "..."}.
#
# Patches filter_chunks (extract name before regex match) and
# get_bundle (skip nonexistent assets["assets"], return chunks
# directly since v3+ already includes urls).
# ============================================================
def _patch_webpack_loader():
    from webpack_loader.loaders import WebpackLoader

    def _patched_filter_chunks(self, chunks):
        filtered_chunks = []
        for chunk in (chunks or []):
            chunk_name = chunk["name"] if isinstance(chunk, dict) else chunk
            ignore = any(
                regex.match(chunk_name) for regex in self.config["ignores"]
            )
            if not ignore:
                filtered_chunks.append(chunk)
        return filtered_chunks

    def _patched_get_bundle(self, bundle_name):
        assets = self.get_assets()
        chunks = assets.get("chunks", {}).get(bundle_name, [])
        # v3+ chunks are dicts with 'name' and 'url' — return as-is
        return self.filter_chunks(chunks)

    WebpackLoader.filter_chunks = _patched_filter_chunks
    WebpackLoader.get_bundle = _patched_get_bundle


_patch_webpack_loader()

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
WEBSITE_NAME = "vresume"
WEBSITE_IDENTIFIER = "vresume"
SITE_ID = 3

# ── Local apps (site-specific plugins, www packages, and page apps) ──
# Each website ships its own set of plugins and www sub-packages.
# These are appended to the shared INSTALLED_APPS built by configs.base.apps.
LOCAL_APPS = [
    "www.core",
    "plugins.accounts.apps.AccountsConfig",
    "ceptor_ai",
    "django_osoul.analyzer.apps.AnalyzerAppConfig",
    "pages.home",
    "pages.about",
    "pages.cv",
    "pages.connect",
    "pages.portfolio",
    "pages.blog",
    "pages.events",
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
# The previous TeamMembership ordering check is fixed in ceptor_ai.
SILENCED_SYSTEM_CHECKS = []

# Disable workflows until legacy imported Wagtail tasks are cleaned.
WAGTAIL_WORKFLOW_ENABLED = False

# ============================================================
# VResume Admin Sidebar (Unfold)
# ============================================================
# Override the shared minimal UNFOLD sidebar with VResume's curated
# navigation including page-specific model admin links.
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD["SITE_HEADER"] = _("VResume")
UNFOLD["SITE_TITLE"] = _("VResume Admin")
UNFOLD["SITE_SYMBOL"] = "person"
UNFOLD["LOGIN"] = {
    "image": lambda request: static("images/avatar/01.jpg"),
}
# ============================================================
# Celery Beat Schedule — VResume-specific periodic tasks
# ============================================================
# These tasks reference VResume page apps (pages.connect, pages.blog)
# that don't exist in LMS sites.  Inlined here so each site controls
# its own schedule.
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # ── Campaign Tasks ──
    "process-scheduled-campaigns": {
        "task": "pages.connect.services.campaign_tasks.process_scheduled_campaigns",
        "schedule": 300.0,  # Every 5 minutes
        "options": {"queue": "default", "priority": 5},
    },
    "cleanup-old-campaigns": {
        "task": "pages.connect.services.campaign_tasks.cleanup_old_campaigns",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2:00 AM UTC
        "options": {"queue": "default", "priority": 3},
        "kwargs": {"days_old": 30},
    },
    # ── Analytics Tasks ──
    "update-article-engagement-metrics": {
        "task": "pages.blog.services.analytics_tasks.update_article_engagement_metrics",
        "schedule": crontab(hour="*/4", minute=0),  # Every 4 hours
        "options": {"queue": "default", "priority": 2},
    },
    "generate-trending-articles": {
        "task": "pages.blog.services.analytics_tasks.generate_trending_articles",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight UTC
        "options": {"queue": "default", "priority": 2},
        "kwargs": {"days": 7, "limit": 10},
    },
    "cleanup-old-article-reads": {
        "task": "pages.blog.services.analytics_tasks.cleanup_old_article_reads",
        "schedule": crontab(hour=3, minute=0),  # Daily at 3:00 AM UTC
        "options": {"queue": "default", "priority": 1},
        "kwargs": {"days_old": 90},
    },
}

UNFOLD["SIDEBAR"] = {
    "show_search": True,
    "show_all_applications": False,
    "navigation": [
        {
            "title": _("Dashboard"),
            "separator": False,
            "items": [
                {
                    "title": _("Dashboard"),
                    "icon": "dashboard",
                    "link": reverse_lazy("admin:index"),
                },
            ],
        },
        {
            "title": _("Content"),
            "separator": True,
            "items": [
                {
                    "title": _("Blog Posts"),
                    "icon": "article",
                    "link": reverse_lazy("admin:blog_blogpost_changelist"),
                },
                {
                    "title": _("Blog Authors"),
                    "icon": "person",
                    "link": reverse_lazy("admin:blog_blogauthor_changelist"),
                },
                {
                    "title": _("Blog Tags"),
                    "icon": "label",
                    "link": reverse_lazy("admin:blog_blogtag_changelist"),
                },
            ],
        },
        {
            "title": _("Portfolio"),
            "separator": True,
            "items": [
                {
                    "title": _("Projects"),
                    "icon": "work",
                    "link": reverse_lazy("admin:portfolio_project_changelist"),
                },
                {
                    "title": _("Portfolio Tags"),
                    "icon": "sell",
                    "link": reverse_lazy("admin:portfolio_portfoliotag_changelist"),
                },
            ],
        },
        {
            "title": _("Connect"),
            "separator": True,
            "items": [
                {
                    "title": _("Form Submissions"),
                    "icon": "inbox",
                    "link": reverse_lazy("admin:connect_formsubmission_changelist"),
                },
                {
                    "title": _("Subscribers"),
                    "icon": "group",
                    "link": reverse_lazy("admin:connect_subscriber_changelist"),
                },
                {
                    "title": _("Campaigns"),
                    "icon": "campaign",
                    "link": reverse_lazy("admin:connect_campaign_changelist"),
                },
                {
                    "title": _("Email Deliveries"),
                    "icon": "mail",
                    "link": reverse_lazy("admin:connect_emaildelivery_changelist"),
                },
            ],
        },
        {
            "title": _("Site Settings"),
            "separator": True,
            "items": [
                {
                    "title": _("vResume Settings"),
                    "icon": "settings",
                    "link": reverse_lazy("admin:home_vresumesettings_changelist"),
                },
                {
                    "title": _("Services"),
                    "icon": "build",
                    "link": reverse_lazy("admin:home_service_changelist"),
                },
                {
                    "title": _("Testimonials"),
                    "icon": "format_quote",
                    "link": reverse_lazy("admin:home_testimonial_changelist"),
                },
                {
                    "title": _("Team Members"),
                    "icon": "people",
                    "link": reverse_lazy("admin:home_teammember_changelist"),
                },
                {
                    "title": _("Sliders"),
                    "icon": "view_carousel",
                    "link": reverse_lazy("admin:home_slider_changelist"),
                },
            ],
        },
        {
            "title": _("Automation"),
            "separator": True,
            "items": [
                {
                    "title": _("Periodic Tasks"),
                    "icon": "schedule",
                    "link": reverse_lazy("admin:django_celery_beat_periodictask_changelist"),
                },
                {
                    "title": _("Crontab Schedules"),
                    "icon": "timer",
                    "link": reverse_lazy("admin:django_celery_beat_crontabschedule_changelist"),
                },
                {
                    "title": _("Interval Schedules"),
                    "icon": "repeat",
                    "link": reverse_lazy("admin:django_celery_beat_intervalschedule_changelist"),
                },
            ],
        },
        {
            "title": _("Users & Auth"),
            "separator": True,
            "items": [
                {
                    "title": _("Users"),
                    "icon": "manage_accounts",
                    "link": reverse_lazy("admin:auth_user_changelist"),
                },
                {
                    "title": _("Groups"),
                    "icon": "group_work",
                    "link": reverse_lazy("admin:auth_group_changelist"),
                },
            ],
        },
    ],
}

