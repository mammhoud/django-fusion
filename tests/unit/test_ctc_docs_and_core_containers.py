"""
Property-based tests for ctc-docs-and-core-containers spec.

Tests validate the four correctness properties defined in the design document:
  Property 1: Container name matches Traefik service URL hostname
  Property 2: Redis DB index and DB name uniqueness across Django services
  Property 3: Service configuration completeness
  Property 4: Traefik config routing completeness

NOTE: All four tests are currently skipped because they were written for a
planned `ctc-core` service that does not yet exist in
`structa.cloud/docker-compose.yml`. The actual services are `website`,
`website-media`, and `website-worker`. Re-enable these tests when the
`ctc-core` service is added to the compose file.

See: docs/specs/pending/README.md — ctc-docs-and-core-containers spec
"""
from pathlib import Path
from urllib.parse import urlparse

import pytest

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    yaml = None  # type: ignore[assignment]
    _YAML_AVAILABLE = False
from hypothesis import given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Paths (relative to workspace root)
# ---------------------------------------------------------------------------
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
COMPOSE_FILE = WORKSPACE_ROOT / "structa.cloud" / "docker-compose.yml"
TRAEFIK_CORE_FILE = WORKSPACE_ROOT / "compose" / "traefik" / "dynamic" / "ctc-core.yml"
NGINX_CONF_FILE = WORKSPACE_ROOT / "compose" / "nginx" / "docsify.conf"

_SKIP_REASON = (
    "ctc-core service not yet in structa.cloud/docker-compose.yml "
    "(actual services: website, website-media, website-worker). "
    "Re-enable when ctc-core is added. "
    "See docs/specs/pending/README.md — ctc-docs-and-core-containers spec."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_compose() -> dict:
    with open(COMPOSE_FILE) as f:
        return yaml.safe_load(f)


def load_traefik_config(filename: str = "ctc-core.yml") -> dict:
    path = WORKSPACE_ROOT / "compose" / "traefik" / "dynamic" / filename
    with open(path) as f:
        return yaml.safe_load(f)


def extract_redis_db_index(redis_url: str) -> str:
    """Extract the /N database index from a Redis URL."""
    parsed = urlparse(redis_url)
    return parsed.path.lstrip("/")


def extract_hostname(url: str) -> str:
    """Extract the hostname from a URL like http://ctc-core:5080."""
    return urlparse(url).hostname


def get_env_dict(service: dict) -> dict:
    """Convert a list of 'KEY=VALUE' env strings to a dict."""
    env = {}
    for item in service.get("environment", []):
        if "=" in item:
            k, v = item.split("=", 1)
            env[k] = v
    return env


# ---------------------------------------------------------------------------
# Property 1: Container name matches Traefik service URL hostname
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason=_SKIP_REASON)
@given(st.just(None))
@settings(max_examples=1)
def test_container_name_matches_traefik_url(_):
    """
    For docs and ctc-core, the container_name in docker-compose.yml must equal
    the hostname used in the corresponding Traefik loadBalancer server URL.
    """
    compose = load_compose()
    traefik = load_traefik_config("ctc-core.yml")

    services = compose["services"]
    lb_services = traefik["http"]["services"]

    ctc_core_url = lb_services["ctc-core-service"]["loadBalancer"]["servers"][0]["url"]
    assert extract_hostname(ctc_core_url) == services["ctc-core"]["container_name"]

    nginx_url = lb_services["ctc-nginx-service"]["loadBalancer"]["servers"][0]["url"]
    assert extract_hostname(nginx_url) == services["ctc-nginx"]["container_name"]


# ---------------------------------------------------------------------------
# Property 2: Redis DB index and DB name uniqueness
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason=_SKIP_REASON)
@given(st.just(None))
@settings(max_examples=1)
def test_redis_db_index_and_db_name_uniqueness(_):
    """
    All Django services must use distinct Redis DB indices.
    ctc-core DB_NAME (db_precis_lms) must differ from ctc-django-main DB_NAME (db_precis_ctc).
    """
    compose = load_compose()
    services = compose["services"]

    primary_app_services = {"ctc-django-main", "ctc-django-demo", "ctc-core"}
    django_services = {
        name: svc
        for name, svc in services.items()
        if name in primary_app_services
    }

    db_indices = []
    for name, svc in django_services.items():
        env = get_env_dict(svc)
        redis_url = env.get("REDIS_URL", "")
        if redis_url:
            db_indices.append(extract_redis_db_index(redis_url))

    assert len(db_indices) == len(set(db_indices)), (
        f"Duplicate Redis DB indices found: {db_indices}"
    )

    core_env = get_env_dict(services["ctc-core"])
    main_env = get_env_dict(services["ctc-django-main"])
    assert core_env["DB_NAME"] == "db_precis_lms"
    assert main_env["DB_NAME"] == "db_precis_ctc"
    assert core_env["DB_NAME"] != main_env["DB_NAME"]


# ---------------------------------------------------------------------------
# Property 3: Service configuration completeness
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason=_SKIP_REASON)
@given(st.just(None))
@settings(max_examples=1)
def test_service_config_completeness(_):
    """
    docs service: image=nginx:alpine, container_name=docs, traefik-net network.
    ctc-core service: PORT=5080, DB_NAME=db_precis_lms, REDIS_URL ending in /5.
    """
    compose = load_compose()
    services = compose["services"]

    docs = services["docs"]
    assert docs["image"] == "nginx:alpine"
    assert docs["container_name"] == "docs"
    assert "traefik-net" in docs["networks"]
    assert docs["restart"] == "unless-stopped"
    assert docs["healthcheck"]["retries"] == 3
    volumes = docs["volumes"]
    assert any("./docs:/usr/share/nginx/html:ro" in v for v in volumes)
    assert any("docsify.conf" in v for v in volumes)
    assert "ports" not in docs

    core = services["ctc-core"]
    assert core["container_name"] == "ctc-core"
    core_env = get_env_dict(core)
    assert core_env["PORT"] == "5080"
    assert core_env["DB_NAME"] == "db_precis_lms"
    assert core_env["REDIS_URL"].endswith("/5")
    assert core_env["RUN_SETUP"] == "true"
    assert core_env["APP_MODULE"] == "core.asgi:application"
    assert core_env["WORKERS"] == "4"
    assert core_env["DB_HOST"] == "postgres"
    assert "traefik-net" in core["networks"]
    assert core["restart"] == "unless-stopped"
    assert core["healthcheck"]["retries"] == 3
    assert "ports" not in core
    assert "core_static" in compose["volumes"]
    assert "core_media" in compose["volumes"]


# ---------------------------------------------------------------------------
# Property 4: Traefik config routing completeness
# ---------------------------------------------------------------------------

@pytest.mark.skip(reason=_SKIP_REASON)
@given(st.just(None))
@settings(max_examples=1)
def test_traefik_config_completeness(_):
    """
    ctc-core.yml must have HTTP/HTTPS routers, assets router, letsencrypt TLS.
    """
    config = load_traefik_config("ctc-core.yml")
    routers = config["http"]["routers"]
    lb_services = config["http"]["services"]

    assert "ctc-core-http" in routers
    assert "redirect-to-https" in routers["ctc-core-http"]["middlewares"]

    assert "ctc-core-https" in routers
    https_router = routers["ctc-core-https"]
    assert "compress" in https_router["middlewares"]
    assert "security-headers" in https_router["middlewares"]
    assert https_router["tls"]["certResolver"] == "letsencrypt"
    assert https_router["service"] == "ctc-core-service"

    core_url = lb_services["ctc-core-service"]["loadBalancer"]["servers"][0]["url"]
    assert core_url == "http://ctc-core:5080"

    assert "ctc-core-assets" in routers
    assets_router = routers["ctc-core-assets"]
    assert assets_router["service"] == "ctc-nginx-service"

    nginx_url = lb_services["ctc-nginx-service"]["loadBalancer"]["servers"][0]["url"]
    assert nginx_url == "http://ctc-nginx:80"

    assert "tls" in assets_router
    assert assets_router["tls"]["certResolver"] == "letsencrypt"
