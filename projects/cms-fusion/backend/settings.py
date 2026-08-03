"""Site-specific Django settings for cms-fusion.

Imports shared Fusion defaults from configs.default, then applies
CMS-specific branding, CORS origins, and feature flags.
"""

import os
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# Path Configuration — ensure correct import resolution
# ═══════════════════════════════════════════════════════════════════
_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_PROJECTS_DIR = _WORKSPACE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"
_APPS_DIR = _SITE_DIR / "apps"

for _path in (str(_PROJECTS_DIR), str(_WORKSPACE_DIR), str(_SITE_DIR),
              str(_SITE_APP_DIR), str(_APPS_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)


# ═══════════════════════════════════════════════════════════════════
# Site Environment — force cms-fusion env vars before shared settings
# ============================================================
from configs.site import configure_site_environment, WORKSPACE_DIR  # noqa: E402

_cms_site_dir = str(WORKSPACE_DIR / "cms-fusion")
for _key, _val in [
    ("WEBSITE_DIR", _cms_site_dir),
    ("DJANGO_WEBSITE_DIR", _cms_site_dir),
    ("WEBSITE", "cms-fusion"),
    ("WEBSITE_NAME", "cms-fusion"),
    ("DJANGO_WEBSITE", "cms-fusion"),
]:
    if _key not in os.environ:
        os.environ[_key] = _val

configure_site_environment("cms-fusion", module="FUSION", default_port=5070)


# ═══════════════════════════════════════════════════════════════════
# Shared Fusion Settings — CD layer, base Django, common FUSION_*
# Also provides the ``cfg()`` helper for resolving site settings
# from env vars, Dynaconf YAML (Env/_site.yml), or Python fallback.
# ═══════════════════════════════════════════════════════════════════
from configs.default import *  # noqa: E402,F401,F403


# ═══════════════════════════════════════════════════════════════════
# Site Identity
# ═══════════════════════════════════════════════════════════════════
WEBSITE_NAME = "cms-fusion"
WEBSITE_IDENTIFIER = "cms-fusion"
WAGTAIL_SITE_NAME = cfg("WAGTAIL_SITE_NAME", "Fusion CMS")


# ═══════════════════════════════════════════════════════════════════
# Branding — purple theme (env var > _site.yml > fallback)
# ═══════════════════════════════════════════════════════════════════
FUSION_SITE_NAME = cfg("FUSION_SITE_NAME", "Fusion CMS")
FUSION_COMPANY_NAME = cfg("FUSION_COMPANY_NAME", "Fusion Inc.")
FUSION_CREATOR_NAME = cfg("FUSION_CREATOR_NAME", "Fusion Team")
FUSION_PRIMARY_COLOR = cfg("FUSION_PRIMARY_COLOR", "#7c3aed")
FUSION_SECONDARY_COLOR = cfg("FUSION_SECONDARY_COLOR", "#5b21b6")


# ═══════════════════════════════════════════════════════════════════
# Render-First — enabled by default for CMS
# ═══════════════════════════════════════════════════════════════════
FUSION_RENDER_FIRST_DEFAULT = cfg("FUSION_RENDER_FIRST_DEFAULT", True)


# ═══════════════════════════════════════════════════════════════════
# Branding Context Processor — resolved from _site.yml
# ═══════════════════════════════════════════════════════════════════
TEMPLATES[0]["OPTIONS"]["context_processors"].append(
    cfg("FUSION_BRANDING_BACKEND",
        "django_fusion.contrib.branding.context_processors.fusion_branding_context")
)


# ═══════════════════════════════════════════════════════════════════
# CORS Origins — resolved from _site.yml (YAML key: CORS_ORIGINS)
# ═══════════════════════════════════════════════════════════════════
CORS_ALLOWED_ORIGINS = cfg("CORS_ORIGINS", [
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
])
