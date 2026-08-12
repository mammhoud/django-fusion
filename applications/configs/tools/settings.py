"""Settings entrypoint for the merged `www` sentinel site.

The `www` site (created from the merge of `projects/shared/` and
`projects/www/`) provides the shared/core Django application code
used across all websites. It serves as the sentinel site for the
shared-task worker stack (shared-worker + shared-scheduler).

Mirrors the per-site settings.py pattern (see `projects/precis/backend/settings.py`)
but with two differences:

1. No `_SITE_APP_DIR = _SITE_DIR / "www"`. The shared stack runs the
   `www.worker` package globally — registered once via
   `projects/configs/base/apps.py` — so no per-site `www/` override is
   needed. Adding `_SITE_APP_DIR` here would *block* `www.core` and
   `www.worker` imports because the shared stack doesn't ship a
   per-site `www/` directory of its own.

2. Calls `configure_site_environment("www", module="CMS",
   default_port=5080)` instead of a tenant site. This seeds the
   `DJANGO_WEBSITE`, `WEBSITE`, `SITE_DOMAIN`, `MODULE`, `PORT`, etc.
   env vars that `projects/configs/settings/conf.py:MainSettings` reads
   via `default_factory=active_website_name` at import time.

Once this module is importable from runtime `sys.path`, it loads as
`settings` when `DJANGO_SETTINGS_MODULE=settings` is the default
(resolves to /app/www/settings.py under the `PROJECT_PATH=www` bake)
and as `www.settings` when both `PROJECT_PATH=www` (which COPY-bakes
`/app/www/__init__.py`) and `DJANGO_SETTINGS_MODULE=www.settings` are
set. With either path resolvable, celery-beat and shared-worker's
`python manage.py rundramatiq` calls resolve cleanly without the
historical `Unknown site 'shared'` rejection.

DEV-TIME ONLY:
Production workers run with PROJECT_PATH=lms-fusion baked at build time
in `projects/precis/compose/Dockerfile.backend` (override-able via the
`TASKS_PROJECT_PATH=www` build arg passed from
`applications/docker-compose.tasks.yml`). Under the default
PROJECT_PATH=lms-fusion, `python manage.py rundramatiq` is invoked with
DJANGO_SETTINGS_MODULE=settings resolving to
`projects/precis/backend/settings.py` (bind-mounted at runtime) — NOT this module.

Setting TASKS_PROJECT_PATH=www IS the runtime wiring: the
Dockerfile's `COPY projects/${PROJECT_PATH}` step bakes www/ contents
into /app/www/, which the runtime loads as the default `settings`
module (DJANGO_SETTINGS_MODULE=settings resolves to
/app/www/settings.py when /app/www/ is on sys.path). Under the
default bake, this file is loaded by:
  - ad-hoc dev invocations: `python projects/www/__main__.py check`
  - unit tests under `tests/unit/` that patch `www.settings` (or
    `DJANGO_SETTINGS_MODULE=www.settings`)
  - any future tooling that explicitly sets DJANGO_SETTINGS_MODULE=www.settings
"""

import sys
from pathlib import Path

# ── Site dir layout ──────────────────────────────────────────────────────
_SITE_DIR = Path(__file__).resolve().parent          # = projects/configs/tools/
_WORKSPACE_DIR = _SITE_DIR.parent.parent             # = projects/

# Same REVERSED iteration pattern as per-site settings.py: put
# projects/ at sys.path[0] so subsequent imports resolve
# correctly. The tools/ directory is a shared configs package,
# not a standalone site directory.
for _path in reversed((str(_WORKSPACE_DIR), str(_SITE_DIR))):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ── Site tracker ─────────────────────────────────────────────────────────
from configs.site import configure_site_environment

configure_site_environment("www", module="CMS", default_port=5080)

# ── Shared Django settings ──────────────────────────────────────────────
from configs.settings import *  # noqa: E402,F401,F403

# Explicit override of the per-app site identifier. `configs.settings`
# already arrived with these defaults filled in via the configs layer,
# but we re-assert them to make the intent visible in this file —
# future readers shouldn't have to chase down the registry to verify
# which site "www" identifies as.
WEBSITE_NAME = "www"

# No LOCAL_APPS appended here on purpose. The `www.worker` Celery /
# Dramatiq app is registered globally in
# `projects/configs/base/apps.py:INSTALLED_APPS`. Site-specific apps that
# `projects/<site>/settings.py` append (wagtail pages, plugins, etc.) are
# intentionally NOT added — the shared stack is site-agnostic and
# task dispatches it performs cross sites via the explicit queue
# routing inside `www.worker.tasks`.
