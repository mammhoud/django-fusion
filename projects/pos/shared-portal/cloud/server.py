"""
Cloud CRM Server — standalone HTTP API for POS Full Edition CRM.

Runs as an independent Sanic server (default port 8766) alongside
the POS sidecar (port 8765). Provides:

  - CRM entity CRUD (contacts, companies, deals, pipelines, activities, notes)
  - Search, pagination, and filtering on all list endpoints
  - Dashboard statistics (pipeline summary, deal counts, activity timeline)
  - Data export (CSV/JSON) and bulk import (JSON array)
  - Cloud sync management (status, trigger, log)
  - Health check endpoint

Architecture:

   sidecar (port 8765)  ───HTTP──→  cloud server (port 8766)
    (local POS)                    (CRM + sync logic)

Environment variables:
    CLOUD_HOST      (default: 127.0.0.1)
    CLOUD_PORT      (default: 8766)
    CLOUD_DATA_DIR  (default: ./cloud_data)
    CLOUD_API_KEY   (optional, for request authentication)

Usage:
    python server.py                          # Default config
    python server.py --port 8766 --data-dir ./cloud_data
    python server.py --host 0.0.0.0 --api-key mysecret

Related Names: cloud, crm, server, api, sidecar
Tags: #cloud #crm #server #api #pos-full
"""

from __future__ import annotations

import os
import sys
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

from sanic import Sanic, Request
from sanic.response import json as sanic_json, text as sanic_text

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("cloud_crm")

# ---------------------------------------------------------------------------
# App & configuration
# ---------------------------------------------------------------------------

app = Sanic("cloud_crm")
app.config.ACCESS_LOG = False

HOST = os.environ.get("CLOUD_HOST", "127.0.0.1")
PORT = int(os.environ.get("CLOUD_PORT", "8766"))
DATA_DIR: Path = Path(os.environ.get("CLOUD_DATA_DIR", "./cloud_data"))
API_KEY: str | None = os.environ.get("CLOUD_API_KEY", None)

# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="POS Cloud CRM Server",
        epilog="Run alongside sidecar for full cloud sync capabilities.",
    )
    parser.add_argument("--host", default=HOST, help="Bind address")
    parser.add_argument("--port", type=int, default=PORT, help="Bind port")
    parser.add_argument(
        "--data-dir", type=Path, default=DATA_DIR,
        help="Data directory for CRM JSON storage",
    )
    parser.add_argument(
        "--api-key", default=API_KEY,
        help="API key for request authentication (optional)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Enable verbose debug logging",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Middleware: API key auth (optional)
# ---------------------------------------------------------------------------

@app.middleware("request")
async def auth_middleware(request: Request):
    """Optional API key authentication.

    If CLOUD_API_KEY is set, all requests (except /health and /)
    must include an X-API-Key header matching the configured key.
    """
    if not API_KEY:
        return  # Auth disabled

    # Allow unauthenticated access to health/ping endpoints
    if request.path in ("/", "/health"):
        return

    req_key = request.headers.get("X-API-Key") or request.args.get("api_key")
    if req_key != API_KEY:
        return sanic_json(
            {"error": "Unauthorized: invalid or missing API key"},
            status=401,
        )


# ---------------------------------------------------------------------------
# Middleware: CORS
# ---------------------------------------------------------------------------

@app.middleware("request")
async def cors_middleware(request: Request):
    """Handle CORS preflight requests."""
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-API-Key, Authorization",
            "Access-Control-Max-Age": "86400",
        }
        return sanic_text("", headers=headers)


@app.middleware("response")
async def cors_response_middleware(request: Request, response):
    """Add CORS headers to all responses."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key, Authorization"


# ---------------------------------------------------------------------------
# Health & info
# ---------------------------------------------------------------------------

@app.get("/")
async def index(request: Request):
    """Server info and available endpoints."""
    return sanic_json({
        "service": "POS Cloud CRM Server",
        "version": "1.0.0",
        "status": "ok",
        "docs": "/health — health check",
        "endpoints": {
            "crm": "/api/crm/* — CRM REST API",
            "dashboard": "/api/crm/dashboard — CRM statistics",
            "export": "/api/crm/export/<type> — CSV/JSON export",
            "import": "/api/crm/import/<type> — Bulk import",
            "sync": "/api/crm/sync/* — Sync management",
        },
    })


@app.get("/health")
async def health(request: Request):
    """Health check endpoint."""
    return sanic_json({
        "status": "healthy",
        "service": "cloud_crm",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - _start_time).total_seconds()
        if "_start_time" in globals() else 0,
        "version": "1.0.0",
    })


_start_time = datetime.utcnow()


# ---------------------------------------------------------------------------
# CRM Blueprint
# ---------------------------------------------------------------------------

# Set data dir before importing blueprint
os.environ["CLOUD_DATA_DIR"] = str(DATA_DIR)

from .crm_api import crm_bp, init_default_pipeline  # noqa: E402
app.blueprint(crm_bp)

# Sync proxy — accepts generic pushes from pos-solo edition
from .sync_proxy import sync_proxy_bp  # noqa: E402
app.blueprint(sync_proxy_bp)

# Webhook receiver — accepts webhooks from Solo/Minimal nodes
from .webhook_receiver import webhook_bp  # noqa: E402
app.blueprint(webhook_bp)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = _parse_args()

    if args.verbose:
        logging.getLogger("cloud_crm").setLevel(logging.DEBUG)

    DATA_DIR = args.data_dir
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    os.environ["CLOUD_DATA_DIR"] = str(DATA_DIR)

    if args.api_key:
        API_KEY = args.api_key

    logger.info(
        "Starting Cloud CRM Server on %s:%s (data: %s)",
        args.host, args.port, DATA_DIR,
    )
    if API_KEY:
        logger.info("API key authentication enabled")

    # Initialize default pipeline
    init_default_pipeline()

    app.run(host=args.host, port=args.port, single_process=True, auto_reload=False)
@tested shared-portal/cloud - POS-KO → POS, POSKO-* → POS-* rename verified
