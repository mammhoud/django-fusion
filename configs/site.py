"""Site discovery helpers for the shared Django configuration stack."""

from __future__ import annotations

import ast
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

WORKSPACE_DIR = Path(__file__).resolve().parents[1]
WEBSITES_DIR = WORKSPACE_DIR / "websites"
SITE_CONFIG_FILE = WORKSPACE_DIR / "configs" / "settings" / "ENV" / "sites.yml"


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "None", "~"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError):
            inner = value[1:-1].strip()
            return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
    if value.isdigit():
        return int(value)
    return value.strip("'\"")


def _read_simple_yaml(path: Path) -> dict[str, Any]:
    """Read the small site YAML file without requiring PyYAML at bootstrap."""
    if not path.exists():
        return {}

    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in path.read_text().splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key, _, raw_value = raw_line.strip().partition(":")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if raw_value.strip() == "":
            node: dict[str, Any] = {}
            parent[key] = node
            stack.append((indent, node))
        else:
            parent[key] = _parse_scalar(raw_value)
    return root


@lru_cache(maxsize=1)
def sites_settings() -> dict[str, Any]:
    data = _read_simple_yaml(SITE_CONFIG_FILE)
    default = data.get("default", {}) if isinstance(data.get("default"), dict) else {}
    websites = default.get("websites", {}) if isinstance(default.get("websites"), dict) else {}
    return {
        "default": default.get("default", "structa.cloud"),
        "websites": websites,
    }


@lru_cache(maxsize=1)
def site_configs() -> dict[str, dict[str, Any]]:
    return dict(sites_settings().get("websites", {}))


def known_websites() -> tuple[str, ...]:
    return tuple(site_configs().keys()) or ("structa.cloud", "ctc-research.com")


KNOWN_WEBSITES = known_websites()
SITE_DOMAINS = {name: config.get("domain", name) for name, config in site_configs().items()}
SITE_PORTS = {name: int(config.get("port", 5080)) for name, config in site_configs().items()}


def _normalise_website(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    configs = site_configs()
    if value in configs:
        return value
    for website, config in configs.items():
        aliases = config.get("aliases", [])
        if value in aliases:
            return website
    return value


def site_config(website: str | None = None) -> dict[str, Any]:
    website = _normalise_website(website) or sites_settings().get("default", "structa.cloud")
    config = dict(site_configs().get(website, {}))
    config.setdefault("name", website)
    config.setdefault("domain", website)
    config.setdefault("port", 5080)
    config.setdefault("module", "CMS")
    return config


def _origin_list(domain: str) -> list[str]:
    hosts = [domain]
    if not domain.startswith("www."):
        hosts.append(f"www.{domain}")
    return [f"http://{host}" for host in hosts] + [f"https://{host}" for host in hosts]


def site_security_defaults(website: str | None = None) -> dict[str, Any]:
    config = site_config(website)
    domain = config.get("domain", config["name"])
    allowed_hosts = config.get("allowed_hosts") or [domain, f"www.{domain}", "localhost", "127.0.0.1"]
    origins = _origin_list(domain)
    return {
        "ALLOWED_HOSTS": allowed_hosts,
        "CSRF_TRUSTED_ORIGINS": config.get("csrf_trusted_origins") or origins,
        "CORS_ALLOWED_ORIGINS": config.get("cors_allowed_origins") or origins,
    }


def active_website_name(default: str = "structa.cloud") -> str:
    """Return the active website name from env vars, cwd, or a safe default."""
    configured_default = str(sites_settings().get("default") or default)
    env_name = _normalise_website(
        os.getenv("DJANGO_WEBSITE")
        or os.getenv("WEBSITE")
        or os.getenv("WEBSITE_NAME")
        or os.getenv("SITE_NAME")
    )
    if env_name in known_websites():
        return env_name

    cwd = Path.cwd().resolve()
    for website in known_websites():
        website_dir = WORKSPACE_DIR / website
        try:
            cwd.relative_to(website_dir)
        except ValueError:
            continue
        return website

    selected = _normalise_website(default) or _normalise_website(configured_default) or "structa.cloud"
    return selected if selected in known_websites() else configured_default


def site_dir_for(website: str) -> Path:
    """Return the preferred filesystem path for a known website."""
    website = _normalise_website(website) or active_website_name()
    root_site = WORKSPACE_DIR / website
    if root_site.exists():
        return root_site
    return WEBSITES_DIR / website


def active_site_dir(default: str = "structa.cloud") -> Path:
    """Return the filesystem path for the active website."""
    env_dir = os.getenv("DJANGO_WEBSITE_DIR") or os.getenv("WEBSITE_DIR")
    if env_dir:
        return Path(env_dir).expanduser().resolve()
    return site_dir_for(active_website_name(default))


def configure_site_environment(website: str, *, module: str | None = None, default_port: int | None = None) -> None:
    """Seed process env vars before importing shared settings."""
    website = active_website_name(website)
    config = site_config(website)
    site_dir = site_dir_for(website)
    domain = str(config.get("domain", website))
    port = int(default_port or config.get("port", 5080))
    selected_module = module or str(config.get("module", "CMS"))
    security = site_security_defaults(website)

    env_defaults = {
        "DJANGO_WEBSITE": website,
        "WEBSITE": website,
        "WEBSITE_NAME": website,
        "DJANGO_WEBSITE_DIR": str(site_dir),
        "WEBSITE_DIR": str(site_dir),
        "SITE_DOMAIN": domain,
        "DOMAIN": domain,
        "DOMAIN_NAME": domain,
        "MODULE": selected_module,
        "PORT": str(port),
        "SSL_ENABLED": str(config.get("ssl_enabled", False)).lower(),
        "ALLOWED_HOSTS": ",".join(security["ALLOWED_HOSTS"]),
        "CSRF_TRUSTED_ORIGINS": ",".join(security["CSRF_TRUSTED_ORIGINS"]),
        "CORS_ALLOWED_ORIGINS": ",".join(security["CORS_ALLOWED_ORIGINS"]),
    }
    for key, value in env_defaults.items():
        os.environ.setdefault(key, value)
