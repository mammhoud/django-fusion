"""FastAPI MCP integration points for ceptor-ai with django-osoul integrations.

Provides endpoints for health, package info, features, file structure,
auth feature detection, django-osoul component registry introspection,
SSL certificate status, proxy health, and website endpoint discovery.
"""

from __future__ import annotations

import subprocess
from importlib import import_module, util
from pathlib import Path
from typing import Any

from .cli import package_info

MCP_FEATURES: tuple[dict[str, str], ...] = (
    {
        "name": "health",
        "path": "/health",
        "summary": "Lightweight readiness response for local MCP clients.",
    },
    {
        "name": "package_info",
        "path": "/info",
        "summary": "Package metadata shared with CLI and documentation workflows.",
    },
    {
        "name": "latest_features",
        "path": "/features",
        "summary": "Current AI/customizer/MCP feature inventory for docs and agents.",
    },
    {
        "name": "file_structure",
        "path": "/file-structure",
        "summary": "Canonical package and documentation paths agents should inspect.",
    },
    {
        "name": "auth_features",
        "path": "/auth/features",
        "summary": "Auth feature availability (allauth, MFA, social auth, oauth2, passkeys).",
    },
    {
        "name": "django_osoul_info",
        "path": "/django-osoul/info",
        "summary": "django-osoul package metadata and module inventory.",
    },
    {
        "name": "django_osoul_components",
        "path": "/django-osoul/components",
        "summary": "django-osoul component registry introspection.",
    },
    {
        "name": "django_osoul_viewsets",
        "path": "/django-osoul/viewsets",
        "summary": "django-osoul viewset availability.",
    },
    {
        "name": "website_endpoints",
        "path": "/websites/endpoints",
        "summary": "Configured website host/port/service mappings.",
    },
    {
        "name": "ssl_status",
        "path": "/ssl/status",
        "summary": "SSL certificate status for all configured domains.",
    },
    {
        "name": "proxy_status",
        "path": "/proxy/status",
        "summary": "Traefik and nginx proxy configuration status.",
    },
)

MCP_FILE_STRUCTURE: dict[str, tuple[str, ...]] = {
    "package": (
        "applications/libs/ceptor-ai/src/ceptor_ai/",
        "applications/libs/ceptor-ai/src/ceptor_ai/customizer/",
        "applications/libs/ceptor-ai/src/ceptor_ai/mcp_server.py",
    ),
    "docs": (
        "applications/libs/ceptor-ai/docs/agents.md",
        "docs/ai/START_HERE.md",
        "docs/ai/latest_features.md",
        "docs/ai/mcp_reference.md",
    ),
    "kilo": (
        ".kilo/config.json",
        ".kilo/commands/",
        ".kilo/skills/",
    ),
}


def _find_spec(module_name: str) -> Any | None:
    try:
        return util.find_spec(module_name)
    except ModuleNotFoundError:
        return None


def latest_features() -> dict[str, Any]:
    """Return framework-agnostic MCP feature metadata for docs and agents."""
    return {
        "package": "ceptor-ai",
        "features": list(MCP_FEATURES),
        "file_structure": {
            key: list(paths) for key, paths in MCP_FILE_STRUCTURE.items()
        },
    }


def get_django_osoul_info() -> dict[str, Any]:
    """Return django-osoul package metadata."""
    if _find_spec("django_osoul") is None:
        return {
            "available": False,
            "error": "Optional package 'django_osoul' is not importable.",
        }
    osoul = import_module("django_osoul")
    return {
        "available": True,
        "version": getattr(osoul, "__version__", "unknown"),
        "path": str(Path(osoul.__file__).parent),
        "modules": ["site", "wagtail", "views", "comp", "routes", "contrib", "web", "health"],
    }


def get_django_osoul_components() -> dict[str, Any]:
    """Return django-osoul component registry info."""
    if _find_spec("django_osoul.comp.core") is None:
        return {"available": False, "error": "django-osoul comp not available"}
    try:
        from django_osoul.comp.core._init import components
        from django_osoul.comp.registry import register_default_partials
        return {
            "available": True,
            "registered_count": len(components._components),
            "render_history_count": len(components._render_history),
            "default_partials_registered": bool(register_default_partials()),
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


def get_auth_features() -> dict[str, Any]:
    """Return auth feature availability."""
    return {
        "ok": True,
        "features": {
            "allauth": _find_spec("allauth") is not None,
            "django_osoul_auth": _find_spec("django_osoul.site.auth") is not None,
            "social_auth": _find_spec("allauth.socialaccount") is not None,
            "mfa": _find_spec("allauth.mfa") is not None,
            "oauth2_provider": _find_spec("oauth2_provider") is not None,
        },
    }


def get_website_endpoints() -> dict[str, Any]:
    """Return configured website endpoints."""
    return {
        "ok": True,
        "endpoints": {
            "structa_cloud": {
                "host": "structa.cloud",
                "port": 5071,
                "service": "lms-web",
                "media_host": "media.structa.cloud",
            },
            "vresume": {
                "host": "vresume.structa.cloud",
                "port": 5072,
                "service": "vresume-web",
                "media_host": "media.vresume.structa.cloud",
            },
            "ctc_research": {
                "host": "ctc-research.com",
                "port": 5070,
                "service": "ctc-research-website",
                "media_host": "media.ctc-research.com",
            },
            "lms_demo": {
                "host": "lms-demo.com",
                "port": 5071,
                "service": "lms-web",
                "media_host": "media.lms-demo.com",
            },
        },
    }


def get_ssl_status() -> dict[str, Any]:
    """Return SSL certificate status for all domains."""
    certs_dir = Path("/home/structa.cloud/proxy/certs")
    domains = [
        ("ctc-research", "ctc-research.com"),
        ("structa-cloud", "structa.cloud"),
        ("vresume", "vresume.structa.cloud"),
    ]
    results = []
    all_valid = True
    for cert_name, domain in domains:
        crt = certs_dir / f"{cert_name}.crt"
        key = certs_dir / f"{cert_name}.key"
        status: dict[str, Any] = {
            "domain": domain,
            "cert_name": cert_name,
            "cert_exists": crt.exists(),
            "key_exists": key.exists(),
        }
        if crt.exists() and key.exists():
            try:
                cert_md5 = subprocess.run(
                    ["openssl", "x509", "-noout", "-modulus", "-in", str(crt)],
                    capture_output=True, text=True,
                )
                key_md5 = subprocess.run(
                    ["openssl", "rsa", "-noout", "-modulus", "-in", str(key)],
                    capture_output=True, text=True,
                )
                status["match"] = cert_md5.stdout == key_md5.stdout
                if not status["match"]:
                    all_valid = False

                expiry = subprocess.run(
                    ["openssl", "x509", "-in", str(crt), "-noout", "-enddate"],
                    capture_output=True, text=True,
                )
                status["expiry"] = expiry.stdout.strip().split("=", 1)[1] if "=" in expiry.stdout else "unknown"
            except Exception as e:
                status["error"] = str(e)
                all_valid = False
        else:
            all_valid = False
        results.append(status)
    return {"ok": all_valid, "certificates": results}


def get_proxy_status() -> dict[str, Any]:
    """Return Traefik and nginx proxy configuration status."""
    traefik_dir = Path("/home/structa.cloud/proxy/traefik/dynamic")
    nginx_conf = Path("/home/structa.cloud/proxy/nginx/default.conf")
    required_configs = [
        "ctc-research.yml",
        "structa-cloud.yml",
        "vresume.yml",
        "middlewares.yml",
        "certs.yml",
        "catchall.yml",
        "media-servers.yml",
    ]
    config_status = {name: (traefik_dir / name).exists() for name in required_configs}
    return {
        "ok": all(config_status.values()) and nginx_conf.exists(),
        "traefik_configs": config_status,
        "nginx_config_exists": nginx_conf.exists(),
        "traefik_dir": str(traefik_dir),
    }


FastAPI: Any = None
if util.find_spec("fastapi") is not None:
    FastAPI = import_module("fastapi").FastAPI

if FastAPI is not None:
    app = FastAPI(title="ceptor-ai MCP")

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Return a health response for Kilo MCP checks."""
        return {"status": "ok", "package": "ceptor-ai"}

    @app.get("/info")
    async def info() -> dict[str, str | bool]:
        """Return package metadata for MCP clients."""
        return package_info()

    @app.get("/features")
    async def features() -> dict[str, Any]:
        """Return current ceptor-ai feature metadata for MCP clients."""
        return latest_features()

    @app.get("/file-structure")
    async def file_structure() -> dict[str, list[str]]:
        """Return canonical package, docs, and Kilo file locations."""
        return {key: list(paths) for key, paths in MCP_FILE_STRUCTURE.items()}

    @app.get("/auth/features")
    async def auth_features() -> dict[str, Any]:
        """Return auth feature availability."""
        return get_auth_features()

    @app.get("/django-osoul/info")
    async def django_osoul_info() -> dict[str, Any]:
        """Return django-osoul metadata."""
        return get_django_osoul_info()

    @app.get("/django-osoul/components")
    async def django_osoul_components() -> dict[str, Any]:
        """Return django-osoul component registry info."""
        return get_django_osoul_components()

    @app.get("/websites/endpoints")
    async def websites_endpoints() -> dict[str, Any]:
        """Return configured website endpoints."""
        return get_website_endpoints()

    @app.get("/ssl/status")
    async def ssl_status() -> dict[str, Any]:
        """Return SSL certificate status for all domains."""
        return get_ssl_status()

    @app.get("/proxy/status")
    async def proxy_status() -> dict[str, Any]:
        """Return Traefik and nginx proxy configuration status."""
        return get_proxy_status()

    @app.get("/django-osoul/viewsets")
    async def django_osoul_viewsets() -> dict[str, Any]:
        """Return django-osoul viewsets availability."""
        if _find_spec("django_osoul") is None:
            return {"available": False, "error": "django-osoul not installed"}
        try:
            viewsets = import_module("django_osoul.site")
            return {
                "available": True,
                "ComponentViews": getattr(viewsets, "ComponentViews", None) is not None,
                "PageHandler": getattr(viewsets, "PageHandler", None) is not None,
                "HTMXPaginationMixin": getattr(viewsets, "HTMXPaginationMixin", None) is not None,
                "ModelViewset": getattr(viewsets, "ModelViewset", None) is not None,
                "ReadonlyModelViewset": getattr(viewsets, "ReadonlyModelViewset", None) is not None,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
else:
    app = None
