"""FastAPI MCP helper routes for Structa Cloud.

This module is intentionally import-safe: it does not configure Django, execute
Django management commands, or call external AI providers at import time.
FastAPI endpoints for project-local MCP helpers.

Run with the ceptor-ai source package on the import path, for example:

    PYTHONPATH=core/libs/ceptor-ai/src uvicorn mcp_server:app \
        --app-dir .kilo --host 127.0.0.1 --port 8002
"""

from __future__ import annotations

import os
import subprocess
from importlib import import_module, util
from io import StringIO
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Structa Cloud MCP")


def _find_spec(module_name: str) -> Any | None:
    """Return a module spec when an optional dependency is importable."""
    try:
        return util.find_spec(module_name)
    except ModuleNotFoundError:
        return None


def _optional_import(module_name: str) -> Any | None:
    """Import an optional dependency only when it is installed."""
    if _find_spec(module_name) is None:
        return None
    return import_module(module_name)


def _json_error(message: str, status_code: int, **details: Any) -> JSONResponse:
    """Return a structured JSON error response."""
    payload = {"ok": False, "error": message, **details}
    return JSONResponse(status_code=status_code, content=payload)


def _django_status() -> dict[str, Any]:
    """Return Django import/configuration status without configuring it."""
    if _find_spec("django") is None:
        return {
            "available": False,
            "configured": False,
            "error": "Optional dependency 'django' is not installed.",
        }

    django_conf = import_module("django.conf")
    settings = django_conf.settings
    configured = bool(settings.configured)
    return {
        "available": True,
        "configured": configured,
        "settings_module": os.environ.get("DJANGO_SETTINGS_MODULE"),
        "error": None
        if configured
        else (
            "Django is not configured. Set DJANGO_SETTINGS_MODULE before using "
            "Django routes."
        ),
    }


def get_django_fusion_info() -> dict[str, Any]:
    """Return django-fusion package metadata."""
    if _find_spec("django_fusion") is None:
        return {
            "available": False,
            "error": "Optional package 'django_fusion' is not importable.",
        }

    fusion = import_module("django_fusion")
    return {
        "available": True,
        "version": getattr(fusion, "__version__", "unknown"),
        "path": str(Path(fusion.__file__).parent),
        "modules": ["site", "wagtail", "views", "comp", "routes", "contrib", "web", "health"],
    }


def get_django_fusion_viewsets() -> dict[str, Any]:
    """Get available django-fusion viewsets."""
    if _find_spec("django_fusion") is None:
        return {"available": False, "error": "django-fusion not installed"}

    try:
        viewsets = import_module("django_fusion.site")

        component_views = getattr(viewsets, "ComponentViews", None)
        page_handler = getattr(viewsets, "PageHandler", None)
        htmx_pagination = getattr(viewsets, "HTMXPaginationMixin", None)
        model_viewset = getattr(viewsets, "ModelViewset", None)
        readonly_model_viewset = getattr(viewsets, "ReadonlyModelViewset", None)

        return {
            "available": True,
            "ComponentViews": component_views is not None,
            "PageHandler": page_handler is not None,
            "HTMXPaginationMixin": htmx_pagination is not None,
            "ModelViewset": model_viewset is not None,
            "ReadonlyModelViewset": readonly_model_viewset is not None,
        }
    except Exception as e:
        return {"available": False, "error": str(e)}


def get_traefik_status() -> dict[str, Any]:
    """Return Traefik configuration status."""
    traefik_dir = Path("/home/structa.cloud/proxy/traefik")

    return {
        "config_dir": str(traefik_dir),
        "dynamic_exists": (traefik_dir / "dynamic.yml").exists(),
        "dynamic_dir_exists": (traefik_dir / "dynamic").exists(),
        "ctc_research": (traefik_dir / "dynamic/ctc-research.yml").exists(),
        "structa_cloud": (traefik_dir / "dynamic/structa-cloud.yml").exists(),
        "vresume": (traefik_dir / "dynamic/vresume.yml").exists(),
        "certs_dir_exists": (traefik_dir / "../certs").exists(),
    }


def get_docker_status() -> dict[str, Any]:
    """Return Docker container status for the project."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        containers = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                containers.append({
                    "name": parts[0] if len(parts) > 0 else "unknown",
                    "status": parts[1] if len(parts) > 1 else "unknown",
                    "ports": parts[2] if len(parts) > 2 else "",
                })
        return {"ok": True, "containers": containers}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_migration_status() -> dict[str, Any]:
    """Run Django's showmigrations command when Django is configured."""
    status = _django_status()
    if not status["available"] or not status["configured"]:
        return {"ok": False, "django": status}

    management = import_module("django.core.management")
    out = StringIO()
    management.call_command("showmigrations", stdout=out)
    return {"ok": True, "raw": out.getvalue(), "django": status}


def get_openrouter_client() -> Any:
    """Build an OpenRouter client from environment configuration on demand."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")

    if _find_spec("openai") is None:
        raise RuntimeError("Optional dependency 'openai' is not installed.")

    openai = import_module("openai")
    return openai.OpenAI(
        base_url=os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        api_key=api_key,
    )


def get_ceptor_ai_info() -> dict[str, Any]:
    """Return ceptor-ai package metadata when the optional package is available."""
    if _find_spec("ceptor_ai.cli") is None:
        return {
            "available": False,
            "error": "Optional package 'ceptor_ai' is not importable.",
        }

    cli = import_module("ceptor_ai.cli")
    package_info_fn = getattr(cli, "package_info", None)
    if package_info_fn is None:
        return {
            "available": False,
            "error": "ceptor_ai.cli.package_info is not available.",
        }
    return {"available": True, "package": package_info_fn()}


def list_ceptor_ai_agents() -> dict[str, Any]:
    """Return known ceptor-ai agent documentation without importing Django code."""
    agent_module = "ceptor_ai.agents"
    if _find_spec(agent_module) is None:
        return {
            "available": False,
            "agents": [],
            "error": "Optional module 'ceptor_ai.agents' is not importable.",
        }

    agents = import_module(agent_module)
    registry = getattr(agents, "AGENTS", None)
    if registry is None:
        registry = getattr(agents, "agents", [])
    return {"available": True, "agents": registry}


def get_website_endpoints() -> dict[str, Any]:
    """Return configured website endpoints from Traefik dynamic config."""
    endpoints = {
        "structa_cloud": {"host": "structa.cloud", "port": 5071, "service": "lms-web"},
        "vresume": {"host": "vresume.structa.cloud", "port": 5072, "service": "vresume-web"},
        "ctc_research": {"host": "ctc-research.com", "port": 5070, "service": "ctc-research-website"},
    }
    return {"ok": True, "endpoints": endpoints}


def get_auth_features() -> dict[str, Any]:
    """Return auth feature availability across the project."""
    features = {
        "allauth": _find_spec("allauth") is not None,
        "django_fusion_auth": _find_spec("django_fusion.site.auth") is not None,
        "social_auth": _find_spec("allauth.socialaccount") is not None,
        "mfa": _find_spec("allauth.mfa") is not None,
        "oauth2_provider": _find_spec("oauth2_provider") is not None,
    }
    return {"ok": True, "features": features}


@app.get("/health")
async def health() -> dict[str, Any]:
    """Return service health with all integrations."""
    return {
        "ok": True,
        "status": "ok",
        "django": _django_status(),
        "optional_dependencies": {
            "ceptor_ai": _find_spec("ceptor_ai") is not None,
            "django_fusion": _find_spec("django_fusion") is not None,
            "openai": _find_spec("openai") is not None,
            "allauth": _find_spec("allauth") is not None,
        },
        "traefik": get_traefik_status(),
        "docker": get_docker_status(),
        "auth": get_auth_features(),
        "websites": get_website_endpoints(),
    }


@app.get("/migrations/status")
async def migration_status() -> Any:
    """Return Django migration status, or a structured configuration error."""
    result = get_migration_status()
    if not result["ok"]:
        return _json_error(
            "Django migrations are unavailable.",
            503,
            django=result["django"],
        )
    return result


@app.get("/ceptor-ai/info")
async def ceptor_ai_info() -> Any:
    """Return ceptor-ai metadata, or a structured dependency error."""
    result = get_ceptor_ai_info()
    if not result["available"]:
        return _json_error(result["error"], 503)
    return {"ok": True, **result}


@app.get("/ceptor-ai/agents")
async def ceptor_ai_agents() -> Any:
    """Return ceptor-ai agent metadata, or a structured dependency error."""
    result = list_ceptor_ai_agents()
    if not result["available"]:
        return _json_error(result["error"], 503, agents=result["agents"])
    return {"ok": True, **result}


@app.get("/django-fusion/info")
async def django_fusion_info() -> Any:
    """Return django-fusion metadata."""
    result = get_django_fusion_info()
    if not result["available"]:
        return _json_error(result["error"], 503)
    return {"ok": True, **result}


@app.get("/django-fusion/viewsets")
async def django_fusion_viewsets() -> Any:
    """Return django-fusion viewsets info."""
    result = get_django_fusion_viewsets()
    if not result["available"]:
        return _json_error(result["error"], 503)
    return {"ok": True, **result}


@app.get("/traefik/status")
async def traefik_status() -> Any:
    """Return Traefik configuration status."""
    return {"ok": True, **get_traefik_status()}


@app.get("/docker/status")
async def docker_status() -> Any:
    """Return Docker container status."""
    return get_docker_status()


@app.get("/auth/features")
async def auth_features() -> Any:
    """Return auth feature availability."""
    return get_auth_features()


@app.get("/websites/endpoints")
async def websites_endpoints() -> Any:
    """Return configured website endpoints."""
    return get_website_endpoints()


@app.get("/openrouter/status")
async def openrouter_status() -> Any:
    """Report OpenRouter readiness without making an external request."""
    missing = []
    if not os.environ.get("OPENROUTER_API_KEY"):
        missing.append("OPENROUTER_API_KEY")
    if _find_spec("openai") is None:
        return _json_error(
            "Optional dependency 'openai' is not installed.",
            503,
            missing_dependencies=["openai"],
        )
    if missing:
        return _json_error(
            "OpenRouter is not configured.",
            503,
            missing_environment=missing,
        )
    return {"ok": True, "configured": True}
