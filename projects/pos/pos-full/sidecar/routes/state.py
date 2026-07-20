"""
POS Full Server — shared server state for route modules.

Holds references to all models, helpers, configuration, and
service objects that route handlers need. Initialized by
server.py via init_state() after Django bootstrap.

This avoids circular imports between server.py and routes/*.py.

Handler utilities are in handlers.py; WebSocket state is in streams.py.
Both are re-exported here so route modules only need `from routes.state import ...`.
"""

from typing import Any
from pathlib import Path
from datetime import datetime, timezone
import logging

logger = logging.getLogger("pos_full_server")

# ── State placeholders (set by init_state) ──

_ALL_MODELS: list = []
_POS_MODELS: list = []
_REGISTRY_MODELS: list = []
_CONFIG_MODELS: list = []
pos_models = None
Node = None
Heartbeat = None
NodeEvent = None
SyncLog = None
DeviceConfig = None
MasterDevice = None
CloudLink = None
SyncApproval = None
DeviceToken = None
SignalEvent = None

sync_engine = None

DB_PATH: Path = None  # type: ignore[assignment]
CLOUD_CRM_URL = ""
CLOUD_API_KEY = ""
SYNC_STATE_PATH: Path = None  # type: ignore[assignment]
_start_time: datetime = None  # type: ignore[assignment]
BASE_DIR: Path = None  # type: ignore[assignment]
_DJANGO_READY = False
_PYDANTIC_READY = False

NodeRegisterRequest = None
HeartbeatRequest = None

fire_config_changed = None
fire_config_synced = None
fire_device_status_changed = None


def init_state(**kwargs):
    """Initialize shared state with values from server.py after Django bootstrap."""
    for key, value in kwargs.items():
        globals()[key] = value
    global logger
    logger = logging.getLogger("pos_full_server")


# ===========================================================================
# Re-export handler utilities from handlers.py
# ===========================================================================

from handlers import (  # noqa: E402, F401
    # Serialization
    _ser, _ser_node, _paginate, _error,
    # CRUD async helpers
    _list, _get, _create, _update, _delete, _count,
    # Sync state and client
    _load_sync_state, _save_sync_state, SyncClient, _log_sync,
    # CRUD router factory
    _register_crud,
)

# ===========================================================================
# Re-export WebSocket state from streams.py
# ===========================================================================

from streams import (  # noqa: E402, F401
    _ws_clients, _ws_filters, _broadcast_node_event,
    _config_ws_clients, _config_ws_filters, _broadcast_config_event,
)
