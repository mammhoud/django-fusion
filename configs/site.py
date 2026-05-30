"""Site discovery helpers for the shared Django configuration stack.

The repository hosts more than one Django website.  These helpers keep the
shared ``configs`` package pointed at the active website while still allowing
site-local ``settings.py`` files to be tiny entrypoints.
"""

from __future__ import annotations

import os
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parents[1]
KNOWN_WEBSITES = ("structa.cloud", "ctc-research.com")

SITE_DOMAINS = {
    "structa.cloud": "structa.cloud",
    "ctc-research.com": "ctc-research.com",
}

SITE_PORTS = {
    "structa.cloud": 5071,
    "ctc-research.com": 5070,
}


def _normalise_website(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    aliases = {
        "structa": "structa.cloud",
        "core": "structa.cloud",
        "ctc": "ctc-research.com",
        "ctc-research": "ctc-research.com",
    }
    return aliases.get(value, value)


def active_website_name(default: str = "structa.cloud") -> str:
    """Return the active website name from env vars, cwd, or a safe default."""
    env_name = _normalise_website(
        os.getenv("DJANGO_WEBSITE")
        or os.getenv("WEBSITE")
        or os.getenv("WEBSITE_NAME")
        or os.getenv("SITE_NAME")
    )
    if env_name in KNOWN_WEBSITES:
        return env_name

    cwd = Path.cwd().resolve()
    for website in KNOWN_WEBSITES:
        website_dir = WORKSPACE_DIR / website
        try:
            cwd.relative_to(website_dir)
        except ValueError:
            continue
        return website

    default = _normalise_website(default) or "structa.cloud"
    return default if default in KNOWN_WEBSITES else "structa.cloud"


def active_site_dir(default: str = "structa.cloud") -> Path:
    """Return the filesystem path for the active website."""
    env_dir = os.getenv("DJANGO_WEBSITE_DIR") or os.getenv("WEBSITE_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return WORKSPACE_DIR / active_website_name(default)


def configure_site_environment(website: str, *, module: str, default_port: int | None = None) -> None:
    """Seed process env vars before importing shared settings."""
    website = active_website_name(website)
    site_dir = WORKSPACE_DIR / website
    domain = SITE_DOMAINS.get(website, website)
    port = default_port or SITE_PORTS.get(website, 5080)

    os.environ.setdefault("DJANGO_WEBSITE", website)
    os.environ.setdefault("WEBSITE", website)
    os.environ.setdefault("WEBSITE_NAME", website)
    os.environ.setdefault("DJANGO_WEBSITE_DIR", str(site_dir))
    os.environ.setdefault("WEBSITE_DIR", str(site_dir))
    os.environ.setdefault("SITE_DOMAIN", domain)
    os.environ.setdefault("DOMAIN", domain)
    os.environ.setdefault("DOMAIN_NAME", domain)
    os.environ.setdefault("MODULE", module)
    os.environ.setdefault("PORT", str(port))
