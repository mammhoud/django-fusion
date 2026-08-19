"""Site-specific Django settings for ctc-research (package form).

Follows the shared ``configs`` technique: the package ``__init__`` bootstraps
path resolution and the site environment, imports the shared Fusion defaults
from ``configs.default``, then layers the site-specific modules below in a
fixed order. Each module exposes only its own overrides via ``__all__`` and
resolves every value through the ``cfg()`` helper (env var → Dynaconf YAML →
Python fallback), so the whole tree stays extendable with defaults.

Module layering order (later modules may depend on earlier ones):
  1. base   — ALLOWED_HOSTS/testserver + TLS (security defaults)
  2. auth   — django-allauth headless configuration
  3. site   — identity, branding, render mode, languages, task center
  4. api    — CORS origins + FUSION_BOLT
  5. assets — media/static/templates/bundles consolidation
"""

import os
import sys
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# Path Configuration — ensure correct import resolution
# ═══════════════════════════════════════════════════════════════════
_SITE_DIR = Path(__file__).resolve().parent.parent
_WORKSPACE_DIR = _SITE_DIR.parent
_PROJECTS_DIR = _WORKSPACE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"
_APPS_DIR = _SITE_DIR / "apps"

for _path in (str(_PROJECTS_DIR), str(_WORKSPACE_DIR), str(_SITE_DIR),
              str(_SITE_APP_DIR), str(_APPS_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# The canonical shared settings package lives at projects/precis/configs (not
# backend/configs). Prefer projects/precis for `import configs` so every site
# resolves one shared source; the site-local backend dir stays on the path for
# `apps`, `settings`, and `manage.py`.
sys.path.insert(0, str(_PROJECTS_DIR))


# ═══════════════════════════════════════════════════════════════════
# Site Environment — seed env vars before importing shared settings
# ═══════════════════════════════════════════════════════════════════
from configs.site import configure_site_environment  # noqa: E402

configure_site_environment("precis-ctc", module="FUSION", default_port=5070)


# ═══════════════════════════════════════════════════════════════════
# Shared Fusion Settings — CD layer, base Django, common FUSION_*
# Also provides the ``cfg()`` helper for resolving site settings
# from env vars, Dynaconf YAML (Env/_site.yml), or Python fallback.
# ═══════════════════════════════════════════════════════════════════
from configs.default import *  # noqa: E402,F401,F403

# ═══════════════════════════════════════════════════════════════════
# Site-specific layers — each exports only its overrides via __all__.
# Import order matters (site depends on auth/base; assets depends on
# the shared assets config + site paths).
# ═══════════════════════════════════════════════════════════════════
from .base import *   # noqa: E402,F401,F403
from .auth import *   # noqa: E402,F401,F403
from .site import *   # noqa: E402,F401,F403
from .api import *    # noqa: E402,F401,F403
from .assets import *  # noqa: E402,F401,F403
