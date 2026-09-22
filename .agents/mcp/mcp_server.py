"""django-bolt MCP helper routes for Structa Cloud.

Thin wrapper that delegates django-fusion, designer, and prompt-catalog logic
to the canonical django-fusion MCP routers.  Only Structa-Cloud-specific
infrastructure endpoints (Docker, Traefik, OpenRouter, ceptor-ai) remain here.

Serve with django-bolt's ``runbolt`` management command::

    PYTHONPATH=libs/ceptor-ai/src python -m django_bolt.cli run --app mcp_server:app

The module exposes a single :class:`django_bolt.BoltAPI` as ``app`` so tests
can exercise it with ``django_bolt.testing.TestClient(app)``.
"""

from __future__ import annotations

import logging
import os
import subprocess
from importlib import util
from io import StringIO
from pathlib import Path
from typing import Any

from django_bolt import BoltAPI
from django_bolt.exceptions import HTTPException
from django_bolt.params import Depends
from django_bolt.responses import Response

# ═══════════════════════════════════════════════════════════════════════════
# django-fusion MCP routers (designer, info, tasks, prompts)
# ═══════════════════════════════════════════════════════════════════════════

try:
    from django_fusion.mcp.fusion_router import register_fusion_routes
except ImportError:  # pragma: no cover
    register_fusion_routes = None  # type: ignore[assignment]

try:
    from django_fusion.plugins.designer.mcp_router import register_designer_routes
except ImportError:  # pragma: no cover
    register_designer_routes = None  # type: ignore[assignment]

try:
    from django_fusion.mcp.prompts import get_prompt as _fusion_get_prompt
    from django_fusion.mcp.prompts import list_prompt_metadata as _fusion_list_prompt_metadata
except ImportError:  # pragma: no cover
    _fusion_get_prompt = None  # type: ignore[assignment]
    _fusion_list_prompt_metadata = None  # type: ignore[assignment]

try:
    from django_fusion.tasks.mcp_router import register_task_routes
except ImportError:  # pragma: no cover
    register_task_routes = None  # type: ignore[assignment]


# ═══════════════════════════════════════════════════════════════════════════
# App
# ═══════════════════════════════════════════════════════════════════════════

def _ensure_django_settings() -> None:
    """Configure a minimal Django environment so ``BoltAPI`` can be created."""
    try:
        from django.conf import settings
        if settings.configured:
            return
        settings.configure(
            INSTALLED_APPS=[],
            SECRET_KEY="kilo-mcp-dev",
            DEBUG=True,
        )
        import django
        django.setup()
    except Exception:  # pragma: no cover - defensive
        pass


_ensure_django_settings()

app = BoltAPI()
logger = logging.getLogger(__name__)

# Mount django-fusion routers when available
if register_fusion_routes is not None:  # pragma: no cover
    register_fusion_routes(app)

if register_designer_routes is not None:  # pragma: no cover
    # api_key is resolved from FUSION_MCP_DESIGNER_API_KEY env var,
    # Django settings, or the constructor argument.  When no key is
    # configured only localhost callers are permitted (development-safe).
    register_designer_routes(app)

if register_task_routes is not None:  # pragma: no cover
    register_task_routes(app)


# ═══════════════════════════════════════════════════════════════════════════
# Structa Cloud infrastructure helpers (Kilo-only)
# ═══════════════════════════════════════════════════════════════════════════


def _find_spec(name: str) -> Any | None:
    try:
        return util.find_spec(name)
    except ModuleNotFoundError:
        return None


def _json_error(message: str, status_code: int, **details: Any) -> Response:
    return Response({"ok": False, "error": message, **details}, status_code=status_code)


def _django_status() -> dict[str, Any]:
    if _find_spec("django") is None:
        return {"available": False, "configured": False, "error": "django not installed"}
    from importlib import import_module
    django_conf = import_module("django.conf")
    configured = bool(django_conf.settings.configured)
    return {
        "available": True,
        "configured": configured,
        "settings_module": os.environ.get("DJANGO_SETTINGS_MODULE"),
        "error": None if configured else "Django not configured",
    }


def _traefik_status() -> dict[str, Any]:
    d = Path("/home/structa.cloud/application/proxy/configs/traefik")
    return {
        "config_dir": str(d),
        "dynamic_exists": (d / "dynamic.yml").exists(),
        "dynamic_dir_exists": (d / "dynamic").exists(),
        "ctc_research": (d / "dynamic/ctc-research.yml").exists(),
        "precis_landing": (d / "dynamic/precis-landing.yml").exists(),
        "lms_fusion": (d / "dynamic/lms-fusion.yml").exists(),
        "certs_dir_exists": (d / "../../data/certs").exists(),
    }


def _docker_status() -> dict[str, Any]:
    try:
        r = subprocess.run(["docker", "ps", "--format", "{{.Names}}|{{.Status}}|{{.Ports}}"],
                           capture_output=True, text=True, timeout=10)
        containers = []
        for line in r.stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                containers.append({"name": parts[0], "status": parts[1] if len(parts) > 1 else "",
                                   "ports": parts[2] if len(parts) > 2 else ""})
        return {"ok": True, "containers": containers}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _migration_status() -> dict[str, Any]:
    s = _django_status()
    if not s["available"] or not s["configured"]:
        return {"ok": False, "django": s}
    from importlib import import_module
    out = StringIO()
    try:
        import_module("django.core.management").call_command("showmigrations", stdout=out)
    except Exception as e:
        return {"ok": False, "django": s, "error": str(e)}
    return {"ok": True, "raw": out.getvalue(), "django": s}


def _ceptor_ai_info() -> dict[str, Any]:
    if _find_spec("ceptor_ai.cli") is None:
        return {"available": False, "error": "ceptor_ai not importable"}
    from importlib import import_module
    cli = import_module("ceptor_ai.cli")
    fn = getattr(cli, "package_info", None)
    if fn is None:
        return {"available": False, "error": "package_info unavailable"}
    return {"available": True, "package": fn()}


def _ceptor_ai_agents() -> dict[str, Any]:
    if _find_spec("ceptor_ai.agents") is None:
        return {"available": False, "agents": [], "error": "ceptor_ai.agents not importable"}
    from importlib import import_module
    mod = import_module("ceptor_ai.agents")
    registry = getattr(mod, "AGENTS", None) or getattr(mod, "agents", [])
    return {"available": True, "agents": registry}


def _website_endpoints() -> dict[str, Any]:
    return {"ok": True, "endpoints": {
        "structa_cloud": {"host": "structa.cloud", "port": 5071, "service": "lms-web"},
        "vresume": {"host": "vresume.structa.cloud", "port": 5072, "service": "vresume-web"},
        "ctc_research": {"host": "ctc-research.com", "port": 5070, "service": "precis-ctc-website"},
    }}


# ═══════════════════════════════════════════════════════════════════════════
# Kilo-only routes
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/health", tags=["kilo"])
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "status": "ok",
        "django": _django_status(),
        "optional_dependencies": {
            "ceptor_ai": _find_spec("ceptor_ai") is not None,
            "django_fusion": _find_spec("django_fusion") is not None,
            "openai": _find_spec("openai") is not None,
            "allauth": _find_spec("allauth") is not None,
            "django_bolt": _find_spec("django_bolt") is not None,
        },
        "traefik": _traefik_status(),
        "docker": _docker_status(),
        "websites": _website_endpoints(),
    }


@app.get("/migrations/status", tags=["kilo"])
def migration_status() -> Any:
    r = _migration_status()
    return r if r["ok"] else _json_error("Migrations unavailable", 503, django=r["django"])


@app.get("/traefik/status", tags=["kilo"])
def traefik_status() -> Any:
    return {"ok": True, **_traefik_status()}


@app.get("/docker/status", tags=["kilo"])
def docker_status() -> Any:
    return _docker_status()


@app.get("/websites/endpoints", tags=["kilo"])
def websites_endpoints() -> Any:
    return _website_endpoints()


@app.get("/openrouter/status", tags=["kilo"])
def openrouter_status() -> Any:
    missing = []
    if not os.environ.get("OPENROUTER_API_KEY"):
        missing.append("OPENROUTER_API_KEY")
    if _find_spec("openai") is None:
        return _json_error("openai not installed", 503, missing_dependencies=["openai"])
    if missing:
        return _json_error("OpenRouter not configured", 503, missing_environment=missing)
    return {"ok": True, "configured": True}


@app.get("/ceptor-ai/info", tags=["kilo"])
def ceptor_ai_info() -> Any:
    r = _ceptor_ai_info()
    return _json_error(r["error"], 503) if not r["available"] else {"ok": True, **r}


@app.get("/ceptor-ai/agents", tags=["kilo"])
def ceptor_ai_agents() -> Any:
    r = _ceptor_ai_agents()
    return _json_error(r["error"], 503, agents=r["agents"]) if not r["available"] else {"ok": True, **r}


# ═══════════════════════════════════════════════════════════════════════════
# Shared auth for sensitive endpoints (prompts)
# ═══════════════════════════════════════════════════════════════════════════


def _resolve_mcp_api_key() -> str | None:
    """Resolve the MCP API key from env or Django settings."""
    env_key = os.environ.get("FUSION_MCP_DESIGNER_API_KEY", "").strip()
    if env_key:
        return env_key
    try:
        from django.conf import settings
        key = getattr(settings, "FUSION_MCP_DESIGNER_API_KEY", None)
        if key:
            return str(key).strip()
    except Exception:
        pass
    return None


def _make_mcp_auth():
    """django-bolt dependency: API-key or localhost-only access."""
    api_key = _resolve_mcp_api_key()

    def _require_auth(request: dict[str, Any]) -> None:
        headers = request.get("headers", {}) or {}
        if api_key:
            provided = headers.get("x-api-key", "")
            if provided != api_key:
                raise HTTPException(status_code=403, detail="Invalid or missing X-API-Key header")
            return
        host = (headers.get("host") or "").split(":", 1)[0].strip().lower()
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise HTTPException(
                status_code=403,
                detail=(
                    "Access requires API-key authentication. "
                    "Set FUSION_MCP_DESIGNER_API_KEY and provide it via X-API-Key header."
                ),
            )

    return _require_auth


_mcp_auth = _make_mcp_auth()


# ═══════════════════════════════════════════════════════════════════════════
# Prompt catalog (delegated to django-fusion)
# ═══════════════════════════════════════════════════════════════════════════


@app.get("/prompts", tags=["prompts"])
def prompts_catalog(_auth: None = Depends(_mcp_auth)) -> Any:
    if _fusion_list_prompt_metadata is None:
        return _json_error("django-fusion prompt catalog is not available", 503)
    try:
        return {"ok": True, **_fusion_list_prompt_metadata()}
    except Exception:
        logger.exception("Prompt catalog listing failed")
        return _json_error("Prompt catalog is unavailable", 503)


@app.get("/prompts/{prompt_id}", tags=["prompts"])
def prompt_detail(prompt_id: str, _auth: None = Depends(_mcp_auth)) -> Any:
    if _fusion_get_prompt is None:
        return _json_error("django-fusion prompt catalog is not available", 503)
    try:
        prompt = _fusion_get_prompt(prompt_id)
    except Exception:
        logger.exception("Prompt detail failed", extra={"prompt_id": prompt_id})
        return _json_error("Prompt catalog is unavailable", 503)
    if prompt is None:
        return _json_error("Prompt not found", 404, prompt_id=prompt_id)
    return {"ok": True, "prompt": prompt}
