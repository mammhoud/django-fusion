"""
Backward-compatibility shim — import from shared.handlers.signal instead.
"""
from shared.handlers.signal import (  # noqa: F401
    _send_webhook, _persist_audit, _log_signal,
    WEBHOOK_URLS, WEBHOOK_TIMEOUT,
    handle_config_changed, handle_master_device_changed,
    handle_cloud_link_changed, handle_config_synced,
    handle_device_status_changed,
)
