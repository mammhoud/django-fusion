"""Asset consolidation for ctc-research — media, static, templates, bundles.

All templates, static, media, and styles live under the workspace-level
assets/ directory. Media is served from the monorepo-shared media tree,
project-named (``projects/assets/media/ctc-research``) so the shared Nginx
proxy maps ctc-research.com → /var/www/media/ctc-research. The runtime
container overrides MEDIA_ROOT via the MEDIA_ROOT env var (/app/media).
"""

import os
from pathlib import Path

from configs.default import *  # noqa: E402,F401,F403

__all__ = [
    "MEDIA_ROOT",
    "CTC_MEDIA_SOURCE_DIR",
    "CTC_MEDIA_CONTENT_DIR",
    "CTC_MEDIA_DUMP_IMAGE_DIR",
    "CTC_MEDIA_MANIFEST_PATH",
    "CTC_MEDIA_CONTENT_URL",
    "STATICFILES_FINDERS",
]

_SITE_DIR = Path(__file__).resolve().parent.parent
_WORKSPACE_DIR = _SITE_DIR.parent
_PROJECTS_DIR = _WORKSPACE_DIR.parent

# ═══════════════════════════════════════════════════════════════════
# Templates — ensure the consolidated assets/templates/ is in DIRS.
# The shared configs already include this path via BASE_DIR.parent, but
# we add it explicitly so it takes priority over scattered app dirs.
# ═══════════════════════════════════════════════════════════════════
_ASSETS_TEMPLATES = _WORKSPACE_DIR / "assets" / "templates"
if str(_ASSETS_TEMPLATES) not in [str(d) for d in TEMPLATES[0]["DIRS"]]:
    TEMPLATES[0]["DIRS"].insert(0, str(_ASSETS_TEMPLATES))

# Sub-paths that app templates were scattered across — now under assets/templates/.
for _sub in ("blog", "lms", "profile", "products", "pages", "accounts",
             "blocks", "emails", "events", "layout", "plugins"):
    _sub_path = _ASSETS_TEMPLATES / _sub
    if _sub_path.exists() and str(_sub_path) not in [str(d) for d in TEMPLATES[0]["DIRS"]]:
        TEMPLATES[0]["DIRS"].append(str(_sub_path))

# ═══════════════════════════════════════════════════════════════════
# Media — serve from the monorepo-shared media tree, project-named so the
# shared Nginx proxy can map ctc-research.com → /var/www/media/ctc-research
# (see application/proxy/docker-compose.nginx.yml + nginx/default.conf.template).
# The runtime container overrides this via the MEDIA_ROOT env var (/app/media).
# ═══════════════════════════════════════════════════════════════════
MEDIA_ROOT = os.environ.get(
    "MEDIA_ROOT", str(_PROJECTS_DIR / "assets" / "media" / "ctc-research")
)

# CTC archive/media pack. The attached backup is kept under the same
# project-named shared media root; ``prepare_ctc_media`` creates a clean
# ``ctc-content/`` website copy and dump-compatible ``original_images/``
# aliases without loading or mutating database data.
_CTC_MEDIA_ROOT = Path(MEDIA_ROOT)
CTC_MEDIA_SOURCE_DIR = Path(os.environ.get("CTC_MEDIA_SOURCE_DIR", str(_CTC_MEDIA_ROOT / "media")))
CTC_MEDIA_CONTENT_DIR = Path(os.environ.get("CTC_MEDIA_CONTENT_DIR", str(_CTC_MEDIA_ROOT / "ctc-content")))
CTC_MEDIA_DUMP_IMAGE_DIR = Path(os.environ.get("CTC_MEDIA_DUMP_IMAGE_DIR", str(_CTC_MEDIA_ROOT / "original_images")))
CTC_MEDIA_MANIFEST_PATH = Path(os.environ.get(
    "CTC_MEDIA_MANIFEST_PATH",
    str(_SITE_DIR / "assets" / "fixtures" / "ctc-research-media.json"),
))
CTC_MEDIA_CONTENT_URL = os.environ.get("CTC_MEDIA_CONTENT_URL", f"{MEDIA_URL}ctc-content/")

# ═══════════════════════════════════════════════════════════════════
# Bundles — webpack writes to the site-local assets/bundles/ctc-research/ dir
# (mounted at /app/assets/bundles/ctc-research in the container). Register it
# under the bundles/ctc-research/ URL namespace so collectstatic copies it into
# STATIC_ROOT and the shared proxy serves it at /static/bundles/ctc-research/
# (nginx location already aliases that path).
# ═══════════════════════════════════════════════════════════════════
_SHARED_BUNDLES = _WORKSPACE_DIR / "assets" / "bundles" / "ctc-research"
if _SHARED_BUNDLES.exists() and "STATICFILES_DIRS" in dir():
    # The runtime site root is /app/precis-ctc, while the shared asset tree is
    # mounted at /app/assets. Keep the webpack manifest and URL namespace
    # aligned with the actual shared bundle directory.
    SITE_BUNDLES_DIR = _SHARED_BUNDLES
    _bundle_entry = ("bundles/ctc-research", str(_SHARED_BUNDLES))
    if _bundle_entry not in STATICFILES_DIRS:
        STATICFILES_DIRS.append(_bundle_entry)
    if "WEBPACK_LOADER" in dir():
        _webpack_default = WEBPACK_LOADER.setdefault("DEFAULT", {})
        _webpack_default["BUNDLE_DIR_NAME"] = "bundles/ctc-research/"
        _webpack_default["STATS_FILE"] = str(_SHARED_BUNDLES / "bundles.json")
        if (_SHARED_BUNDLES / "bundles.json").is_file():
            _webpack_default["LOADER_CLASS"] = "webpack_loader.loader.WebpackLoader"
    if "FUSION_PIPELINE" in dir():
        FUSION_PIPELINE["webpack"].update(
            stats_file=str(_SHARED_BUNDLES / "bundles.json"),
            bundle_dir="bundles/ctc-research/",
        )

# ═══════════════════════════════════════════════════════════════════
# Static — ensure workspace-level assets/static is in STATICFILES_DIRS.
# Use the CTC finder so Unfold's intentional admin overrides do not produce
# duplicate-destination warnings during collectstatic.
# ═══════════════════════════════════════════════════════════════════
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "apps.core.staticfiles.CtcAppDirectoriesFinder",
]
_ASSETS_STATIC = _WORKSPACE_DIR / "assets" / "static"
if _ASSETS_STATIC.exists() and "STATICFILES_DIRS" in dir():
    # Mount the site-local assets at the root namespace (/static/...) so the
    # fusion bundles (css/fusion.css, js/app.js) resolve from this site's own
    # assets/static/ — same convention as precis-landing. The shared configs
    # also register this same directory under a ``site/precis-ctc/`` namespace;
    # drop that alias because FileSystemFinder keys storages by root path, so a
    # second entry for the same dir overwrites the root prefix and makes every
    # file collect twice (the ``site/precis-ctc/...`` collectstatic duplicates).
    _root_entry = str(_ASSETS_STATIC)
    STATICFILES_DIRS[:] = [
        d for d in STATICFILES_DIRS
        if not (isinstance(d, tuple) and str(d[1]) == _root_entry)
    ]
    if _root_entry not in STATICFILES_DIRS:
        STATICFILES_DIRS.insert(0, _root_entry)

# FUSION_PIPELINE: point component manifest at the workspace static root.
if "FUSION_PIPELINE" in dir() and "components" in FUSION_PIPELINE:
    FUSION_PIPELINE["components"]["manifest_path"] = str(
        _ASSETS_STATIC / "components" / "manifest.json"
    )

# Legacy duplicate styles dir: remove assets/styles/ from STATICFILES_DIRS
# (content was merged into assets/static/styles/).
if "STATICFILES_DIRS" in dir():
    _styles_dup = _WORKSPACE_DIR / "assets" / "styles"
    STATICFILES_DIRS[:] = [
        d for d in STATICFILES_DIRS
        if not (isinstance(d, tuple) and str(d[1]) == str(_styles_dup))
    ]

# ═══════════════════════════════════════════════════════════════════
# Component templates — the flat single-file tree under ``apps/components/``
# (contact.sections.field, contact.sections.method, blocks.partials.form_field,
# content.page_title, ...) only resolves when the apps root is a template dir,
# because django-fusion prefixes dotted names with ``components/``, ``partials/``
# or ``tags/`` when generating candidate names. Append it LAST so it never
# shadows the nested ``name/name.html`` trees already registered above.
# ═══════════════════════════════════════════════════════════════════
_APPS_TEMPLATE_ROOT = _SITE_DIR / "apps"
if str(_APPS_TEMPLATE_ROOT) not in [str(d) for d in TEMPLATES[0]["DIRS"]]:
    TEMPLATES[0]["DIRS"].append(str(_APPS_TEMPLATE_ROOT))
