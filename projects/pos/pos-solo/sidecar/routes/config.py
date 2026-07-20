"""
Configuration route handlers for POS Solo - cloud links, master sync, config WebSocket.
"""

import json
from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from robyn import jsonify

from routes import state as S


def register_config_routes(app):
    """Register config-related routes."""

    @app.post("/config/cloud-links/:pk/test")
    async def test_cloud_link(request, pk: int):
        @sync_to_async
        def _get_link():
            try:
                return S.CloudLink.objects.get(id=pk, is_active=True)
            except S.CloudLink.DoesNotExist:
                return None
        link = await _get_link()
        if not link:
            return S._error(404, "Cloud link not found")
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{link.cloud_url.rstrip('/')}/health", headers={"Accept": "application/json"})
                if resp.status_code == 200:
                    @sync_to_async
                    def _mark_connected():
                        link.status = "connected"; link.last_connected_at = datetime.now(timezone.utc); link.save(update_fields=["status", "last_connected_at", "updated_at"])
                    await _mark_connected()
                    return jsonify({"status": "connected", "health": resp.json()})
                return jsonify({"status": "error", "code": resp.status_code})
        except Exception as exc:
            @sync_to_async
            def _mark_error():
                link.status = "error"; link.status_message = str(exc); link.save(update_fields=["status", "status_message", "updated_at"])
            await _mark_error()
            return jsonify({"status": "error", "error": str(exc)})

    @app.post("/config/master/:pk/sync")
    async def sync_master_config(request, pk: int):
        @sync_to_async
        def _get_master():
            try:
                return S.MasterDevice.objects.get(id=pk, is_active=True)
            except S.MasterDevice.DoesNotExist:
                return None
        master = await _get_master()
        if not master:
            return S._error(404, "Master device not found")
        managed_ids = master.managed_node_ids or []
        if not managed_ids:
            return jsonify({"status": "ok", "synced": 0, "message": "No managed nodes"})
        @sync_to_async
        def _sync_nodes():
            synced = 0
            for nid in managed_ids:
                for key, val in master.config.items():
                    S.DeviceConfig.objects.update_or_create(node_id=nid, config_key=key, defaults={"config_value": val, "category": "system"})
                    synced += 1
            return {"synced": synced, "nodes": len(managed_ids)}
        result = await _sync_nodes()
        await S._broadcast_config_event("master_synced", master.device_id, {"master_device_id": master.device_id, "nodes_synced": result["nodes"], "entries_synced": result["synced"]})
        if S.fire_config_synced:
            S.fire_config_synced(source_device_id=master.device_id, target_device_ids=managed_ids, config_keys=list(master.config.keys()), status="success")
        return jsonify({"status": "ok", **result})

    @app.websocket("/ws/config")
    async def config_stream(websocket):
        client_id = id(websocket)
        S._config_ws_clients.add(websocket)
        S._config_ws_filters[client_id] = {}
        try:
            await websocket.send_text(json.dumps({"type": "connected", "message": "Connected to configuration event stream", "client_id": client_id, "timestamp": datetime.now(timezone.utc).isoformat()}))
            while True:
                msg = await websocket.receive_text()
                if msg is None: break
                try:
                    data = json.loads(msg)
                    if "filter" in data:
                        S._config_ws_filters[client_id] = data["filter"]
                        await websocket.send_text(json.dumps({"type": "filter_updated", "filter": S._config_ws_filters[client_id]}))
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({"type": "error", "message": "Invalid JSON"}))
        except Exception:
            pass
        finally:
            S._config_ws_clients.discard(websocket)
            S._config_ws_filters.pop(client_id, None)
