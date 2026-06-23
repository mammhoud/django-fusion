"""FastAPI MCP helper routes for Structa Cloud.

This module is intentionally import-safe: it does not configure Django, execute
Django management commands, or call external AI providers at import time.
FastAPI endpoints for project-local MCP helpers.

Run with the crafts-ai source package on the import path, for example:

    PYTHONPATH=applications/libs/crafts-ai/src uvicorn mcp_server:app \
        --app-dir .kilo --host 127.0.0.1 --port 8002
"""

from __future__ import annotations

import os
from importlib import import_module, util
from io import StringIO
from typing import Any


from django.core.management import call_command
from fastapi import FastAPI

from crafts_ai.cli import package_info

app = FastAPI(title="Structa Cloud MCP")


JSONResponse: Any | None = None


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


_fastapi = _optional_import("fastapi")
_responses = _optional_import("fastapi.responses")

if _fastapi is None:
    app = None
else:
    app = _fastapi.FastAPI(title="Structa Cloud MCP")
    JSONResponse = _responses.JSONResponse if _responses is not None else None


def _json_error(message: str, status_code: int, **details: Any) -> Any:
    """Return a structured JSON error response."""
    payload = {"ok": False, "error": message, **details}
    if JSONResponse is not None:
        return JSONResponse(status_code=status_code, content=payload)
    return payload


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


def get_crafts_ai_info() -> dict[str, Any]:
    """Return crafts-ai package metadata when the optional package is available."""
    if _find_spec("crafts_ai.cli") is None:
        return {
            "available": False,
            "error": "Optional package 'crafts_ai' is not importable.",
        }

    cli = import_module("crafts_ai.cli")
    package_info = getattr(cli, "package_info", None)
    if package_info is None:
        return {
            "available": False,
            "error": "crafts_ai.cli.package_info is not available.",
        }
    return {"available": True, "package": package_info()}


def list_crafts_ai_agents() -> dict[str, Any]:
    """Return known crafts-ai agent documentation without importing Django code."""
    agent_module = "crafts_ai.agents"
    if _find_spec(agent_module) is None:
        return {
            "available": False,
            "agents": [],
            "error": "Optional module 'crafts_ai.agents' is not importable.",
        }

    agents = import_module(agent_module)
    registry = getattr(agents, "AGENTS", None)
    if registry is None:
        registry = getattr(agents, "agents", [])
    return {"available": True, "agents": registry}


if app is not None:

    @app.get("/health")
    async def health() -> dict[str, Any]:
        """Return service health without touching optional integrations."""
        return {
            "ok": True,
            "status": "ok",
            "django": _django_status(),
            "optional_dependencies": {
                "crafts_ai": _find_spec("crafts_ai") is not None,
                "openai": _find_spec("openai") is not None,
            },
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

    @app.get("/crafts-ai/info")
    async def crafts_ai_info() -> Any:
        """Return crafts-ai metadata, or a structured dependency error."""
        result = get_crafts_ai_info()
        if not result["available"]:
            return _json_error(result["error"], 503)
        return {"ok": True, **result}

    @app.get("/crafts-ai/agents")
    async def crafts_ai_agents() -> Any:
        """Return crafts-ai agent metadata, or a structured dependency error."""
        result = list_crafts_ai_agents()
        if not result["available"]:
            return _json_error(result["error"], 503, agents=result["agents"])
        return {"ok": True, **result}

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


@app.get("/health")
async def health() -> dict[str, str]:
    """Return a lightweight health response for the MCP server."""
    return {"status": "ok"}


@app.get("/crafts-ai/info")
async def crafts_ai_info() -> dict[str, str | bool]:
    """Return framework-agnostic crafts-ai package metadata."""
    return package_info()


@app.get("/migrations/status")
async def migration_status() -> dict[str, Any]:
    """Return Django migration status from the configured project."""
    out = StringIO()
    call_command("showmigrations", stdout=out)
    output = out.getvalue()
    return {"raw": output}
