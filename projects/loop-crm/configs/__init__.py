"""Loop-CRM project-level configuration contract.

This package is the canonical, documentation-first description of Loop-CRM's
environment configuration. It is deliberately dependency-free (stdlib only) so
that the Makefiles, CI, and the container entrypoint can read and validate the
environment without booting Django.

Layout:

* ``env.py``       — the env-var catalog (name, default, purpose). Single
                     source of truth for ``.env.example`` and the Makefile
                     ``validate-env`` target.
* ``validate.py``  — ``validate_environment()`` that checks a loaded env dict
                     against the catalog and reports missing/invalid values.

How the pieces fit together (architecture):

* ``backend/settings.py``        — Django entrypoint; seeds site env defaults
                                   via ``configs.site.configure_site_environment``
                                   then re-exports ``configs.default``.
* ``backend/configs/default``    — the actual Django settings module (cache,
                                   channels, database, middleware, …).
* ``Env/_site.yml``              — site identity + per-environment overrides
                                   (documented YAML; not loaded at runtime).
* ``.env.example``               — copy-paste template of every variable the
                                   project reads, generated from ``env.py``.
* ``frontend/.env.example``      — Astro-side variables (port, API prefixes).

The runtime always reads through ``os.environ``: compose/.env set the values,
``configure_site_environment`` seeds safe defaults with ``setdefault``, and the
Django settings consume plain environment variables. Nothing here is Dynaconf.
"""

from .env import ENV_VARS, REQUIRED_ENV_VARS, env_defaults
from .validate import validate_environment

__all__ = ["ENV_VARS", "REQUIRED_ENV_VARS", "env_defaults", "validate_environment"]
