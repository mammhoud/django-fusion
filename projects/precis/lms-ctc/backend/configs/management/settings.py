"""Settings entrypoint for the shared sentinel site.

The `tools` package (renamed from `projects/www/`) provides the shared
worker and CI infrastructure used across all websites. It serves as the
sentinel site for the shared-task worker stack (shared-worker +
shared-scheduler). The sentinel site is named `www` in the CLI config
and the Docker image path for the baked worker is `/app/www/` regardless
of the source directory name.

Mirrors the per-site settings.py pattern (see `projects/precis/ctc-research/settings.py`)
but with two differences:

1. No `_SITE_APP_DIR = _SITE_DIR / "www"`. The shared stack runs the
   `plugins.workers` package globally — registered once via
   `projects/configs/base/apps.py` — so no per-site `www/` override is
   needed. Adding `_SITE_APP_DIR` here would *block* `www.core` and
   `plugins.workers` imports because the shared stack doesn't ship a
   per-site `www/` directory of its own.

2. Calls `configure_site_environment("www", module="CMS",
   default_port=5080)` instead of a tenant site. This seeds the
   `DJANGO_WEBSITE`, `WEBSITE`, `SITE_DOMAIN`, `MODULE`, `PORT`, etc.
   env vars that `projects/configs/settings/conf.py:MainSettings` reads
   via `default_factory=active_website_name` at import time.

Once this module is importable from runtime `sys.path`, it loads as
`settings` when `DJANGO_SETTINGS_MODULE=settings` is the default
(resolves to /app/www/settings.py under the `PROJECT_PATH=tools` bake
which copies into /app/www/) and as `www.settings` when both
`PROJECT_PATH=tools` and `DJANGO_SETTINGS_MODULE=www.settings` are
set. With either path resolvable, the Dramatiq scheduler and shared-worker's
`python manage.py rundramatiq` calls resolve cleanly without the
historical `Unknown site 'shared'` rejection.

DEV-TIME ONLY:
Product workers run with their product backend baked at build time; the
shared worker mounts only explicitly selected product `plugins/workers` paths.
The retired Temporal campaign worker is no longer a runtime entrypoint.

Production web workers run with their product backend baked at build time;
in `projects/compose/Dockerfile` (override-able via the
`TASKS_PROJECT_PATH=tools` build arg passed from
`applications/compose/docker-compose.tasks.yml`). Under the default
PROJECT_PATH=ctc-research, `python manage.py rundramatiq` is invoked with
DJANGO_SETTINGS_MODULE=settings resolving to
`projects/precis/ctc-research/settings.py` (bind-mounted at runtime) — NOT this module.

Setting TASKS_PROJECT_PATH=tools IS the runtime wiring: the
Dockerfile's `COPY projects/${PROJECT_PATH}` step bakes tools/ contents
into /app/www/, which the runtime loads as the default `settings`
module (DJANGO_SETTINGS_MODULE=settings resolves to
/app/www/settings.py when /app/www/ is on sys.path). Under the
default bake, this file is loaded by:
  - ad-hoc dev invocations: `python projects/tools/__main__.py check`
  - unit tests under `tests/unit/` that patch `www.settings` (or
    `DJANGO_SETTINGS_MODULE=www.settings`)
  - any future tooling that explicitly sets DJANGO_SETTINGS_MODULE=www.settings
"""

import os
import sys
from pathlib import Path

# ── Site dir layout ──────────────────────────────────────────────────────
_SITE_DIR = Path(__file__).resolve().parent          # = projects/tools/
_WORKSPACE_DIR = _SITE_DIR.parent                    # = projects/

# Same REVERSED iteration pattern as per-site settings.py: put the
# per-site directory (here, `projects/tools/`) at sys.path[0] so a
# subsequent `import www.xxx` resolves to THIS directory rather
# than any sibling `www/` package on the workspace path.
for _path in reversed((str(_WORKSPACE_DIR), str(_SITE_DIR))):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

# ── Site tracker ─────────────────────────────────────────────────────────
from configs.site import configure_site_environment

# The shared worker uses the infrastructure-only `shared` sentinel. Keep
# `www` as a compatibility alias for older local invocations.
configure_site_environment(
    os.environ.get("DJANGO_SITE") or os.environ.get("WEBSITE") or "shared",
    module="CMS",
    default_port=5080,
)

# ── Shared Django settings ──────────────────────────────────────────────
from configs.settings import *  # noqa: E402,F401,F403

# Explicit override of the per-app site identifier. `configs.settings`
# already arrived with these defaults filled in via the configs layer,
# but we re-assert them to make the intent visible in this file —
# future readers shouldn't have to chase down the registry to verify
# which site "www" identifies as.
WEBSITE_NAME = os.environ.get("DJANGO_SITE") or os.environ.get("WEBSITE") or "shared"

# No product-local apps are appended here on purpose. The `plugins.workers` Dramatiq app
# is registered globally in
# `projects/configs/base/apps.py:INSTALLED_APPS`. Site-specific apps that
# `projects/<site>/settings.py` append (wagtail pages, plugins, etc.) are
# intentionally NOT added — the shared stack is site-agnostic and
# task dispatches it performs cross sites via the explicit queue
# routing inside `plugins.workers`.

# Background-only sentinel: never import the site `apps.urls` tree. That tree
# instantiates ``LMSApp`` and pulls in per-site models (apps.learning, etc.)
# that are absent from this site-agnostic INSTALLED_APPS, which crashes
# ``rundramatiq`` during Django's system checks (check_url_config).
ROOT_URLCONF = "configs.management.urls"
