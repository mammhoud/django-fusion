"""Site-specific Django settings for lms-fusion.

Imports shared Fusion defaults from configs.default, then applies
LMS-specific branding, CORS origins, and feature flags.
"""

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
# Site Environment — seed env vars before importing shared settings
# ═══════════════════════════════════════════════════════════════════
from configs.site import configure_site_environment  # noqa: E402

configure_site_environment("lms-fusion", module="FUSION", default_port=5070)


# ═══════════════════════════════════════════════════════════════════
# Shared Fusion Settings — CD layer, base Django, common FUSION_*
# Also provides the ``cfg()`` helper for resolving site settings
# from env vars, Dynaconf YAML (Env/_site.yml), or Python fallback.
# ═══════════════════════════════════════════════════════════════════
from configs.default import *  # noqa: E402,F401,F403


# ═══════════════════════════════════════════════════════════════════
# Site Identity
# ═══════════════════════════════════════════════════════════════════
WEBSITE_NAME = "lms-fusion"
WEBSITE_IDENTIFIER = "lms-fusion"
WAGTAIL_SITE_NAME = cfg("WAGTAIL_SITE_NAME", "Fusion LMS")


# ═══════════════════════════════════════════════════════════════════
# Branding — teal theme (env var > _site.yml > fallback)
# ═══════════════════════════════════════════════════════════════════
FUSION_SITE_NAME = cfg("FUSION_SITE_NAME", "Fusion LMS")
FUSION_COMPANY_NAME = cfg("FUSION_COMPANY_NAME", "Fusion Inc.")
FUSION_CREATOR_NAME = cfg("FUSION_CREATOR_NAME", "Fusion Team")
FUSION_PRIMARY_COLOR = cfg("FUSION_PRIMARY_COLOR", "#00a1b3")
FUSION_SECONDARY_COLOR = cfg("FUSION_SECONDARY_COLOR", "#008080")


# ═══════════════════════════════════════════════════════════════════
# Render-First — disabled by default for LMS
# ═══════════════════════════════════════════════════════════════════
FUSION_RENDER_FIRST_DEFAULT = cfg("FUSION_RENDER_FIRST_DEFAULT", False)


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
    "http://localhost:3458",
    "http://127.0.0.1:3458",
])

# Allow custom fusion headers for render-first negotiation.
from corsheaders.defaults import default_headers  # noqa: E402

CORS_ALLOW_HEADERS = [*default_headers, "x-fusion-render-first"]


# ═══════════════════════════════════════════════════════════════════
# Bolt API — complex nested config, kept inline (not in YAML)
# ═══════════════════════════════════════════════════════════════════
FUSION_BOLT = {
    "enabled": True,
    "prefix": "/api",
    "openapi_title": "Fusion LMS API",
    "openapi_version": "1.0.0",
    "auth_backends": ["jwt"],
    "serializer_format": "dict",
    "cors_origins": [
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ],
    "component_auto_register": True,
}
