"""Site discovery for the Loop-CRM configuration package.

Loop-CRM is a single-site product, so this module is intentionally smaller
than the multi-site Precis registry. It keeps the same shape — a ``site_config``
accessor and a ``configure_site_environment`` bootstrap that seeds env defaults
before ``configs.default`` is imported — while owning only Loop-CRM's
domain/allowed-hosts contract.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# backend/ = configs/site.py → parents[0]=configs, parents[1]=backend.
BACKEND_DIR = Path(__file__).resolve().parents[1]
# loop-crm/ = parents[2].
SITE_DIR = BACKEND_DIR.parent
SITE_CONFIG_FILE = Path(__file__).resolve().parent / "Env" / "sites.yml"

_DEFAULTS: dict[str, Any] = {
    "name": "loop-crm",
    "domain": "crm.structa.cloud",
    "module": "CRM",
    "port": 8074,
    "ssl_enabled": True,
    "allowed_hosts": [
        "crm.structa.cloud",
        "www.crm.structa.cloud",
        "loop-crm-backend",
        "localhost",
        "127.0.0.1",
    ],
    "csrf_trusted_origins": [
        "https://crm.structa.cloud",
        "https://www.crm.structa.cloud",
    ],
    "cors_allowed_origins": [
        "https://crm.structa.cloud",
        "https://www.crm.structa.cloud",
    ],
}


def _load_cascade() -> Any:
    """Load the project config cascade (configs/*.yml → Env/_site.yml → .env).

    Optional sugar via django-fusion's ``config.project`` loader; never raises
    so an env-only checkout behaves exactly as before.
    """
    try:
        from django_fusion.config.project import load_config

        return load_config(SITE_DIR)
    except Exception:  # pragma: no cover — cascade is optional
        return None


def site_config() -> dict[str, Any]:
    """Return Loop-CRM's site identity (single site, no registry lookup).

    Defaults come from ``_DEFAULTS`` overlaid by the project config cascade
    (``configs/site.yml`` + ``configs/admin.yml``) so the YAML files are the
    source of truth; ``configure_site_environment`` still seeds them with
    ``os.environ.setdefault``, so an explicit environment always wins.
    """
    config = dict(_DEFAULTS)
    config["allowed_hosts"] = list(_DEFAULTS["allowed_hosts"])
    config["csrf_trusted_origins"] = list(_DEFAULTS["csrf_trusted_origins"])
    config["cors_allowed_origins"] = list(_DEFAULTS["cors_allowed_origins"])

    cascade = _load_cascade()
    if cascade is not None:
        site = cascade.section("SITE")
        if site:
            if site.get("name"):
                config["name"] = site["name"]
            domain = site.get("primary_domain") or site.get("domain")
            if domain:
                config["domain"] = domain
            if site.get("allowed_hosts"):
                config["allowed_hosts"] = list(site["allowed_hosts"])
        admin = cascade.section("ADMIN")
        if admin:
            if admin.get("csrf_trusted_origins"):
                config["csrf_trusted_origins"] = list(admin["csrf_trusted_origins"])
            if admin.get("cors_allowed_origins"):
                config["cors_allowed_origins"] = list(admin["cors_allowed_origins"])
    return config


def known_websites() -> tuple[str, ...]:
    return (_DEFAULTS["name"],)


def active_website_name(default: str = "loop-crm") -> str:
    """Resolve the active website from env vars, falling back to the default."""
    return (
        os.getenv("DJANGO_WEBSITE")
        or os.getenv("WEBSITE")
        or os.getenv("WEBSITE_NAME")
        or default
    )


def active_site_dir() -> Path:
    """Return the filesystem path for the active website (loop-crm/)."""
    env_dir = os.getenv("DJANGO_WEBSITE_DIR") or os.getenv("WEBSITE_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return SITE_DIR


def configure_site_environment() -> None:
    """Seed process env defaults before importing ``configs.default``.

    Uses ``os.environ.setdefault`` so an explicit environment (docker-compose,
    CI, local shell) always wins over the site registry defaults.
    """
    config = site_config()
    env_defaults = {
        "DJANGO_WEBSITE": config["name"],
        "WEBSITE": config["name"],
        "WEBSITE_NAME": config["name"],
        "SITE_DOMAIN": config["domain"],
        "DJANGO_ALLOWED_HOSTS": ",".join(config["allowed_hosts"]),
        "CSRF_TRUSTED_ORIGINS": ",".join(config["csrf_trusted_origins"]),
        "CORS_ALLOWED_ORIGINS": ",".join(config["cors_allowed_origins"]),
    }
    for key, value in env_defaults.items():
        os.environ.setdefault(key, value)
