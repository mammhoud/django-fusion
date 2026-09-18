"""Loop-CRM site-specific Django settings entrypoint.

Bootstraps the site environment, then re-exports Loop-CRM's project-local
settings from ``configs.default`` (Loop-CRM's own package, not the LMS/Wagtail
``configs``). Site-specific overrides live below the import.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure `configs` resolves to backend/configs (this package) before Django
# imports anything else.
_SITE_DIR = Path(__file__).resolve().parent
if str(_SITE_DIR) not in sys.path:
    sys.path.insert(0, str(_SITE_DIR))

from configs.site import configure_site_environment  # noqa: E402

# Seed SITE_DOMAIN / ALLOWED_HOSTS / CSRF / CORS defaults before settings load.
# ``os.environ.setdefault`` means an explicit environment always wins.
configure_site_environment()

from configs.default import *  # noqa: E402,F401,F403
