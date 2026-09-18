"""
Node registry route handlers - register, heartbeat, CRUD, WebSocket streams, events, history.
"""

import json
import uuid
import socket as _socket
from datetime import datetime, timezone
from typing import Any

from asgiref.sync import sync_to_async
from robyn import jsonify, Response

from routes import state as S


def register_node_routes(app):
    """Register all node-related routes on the given Robyn app."""

    # ── Config-specific endpoints (per-node config) ──

    @app.get("/nodes/:node_id/config")
    async def get_node_config(request, node_id: str):
        @sync_to_async
        def _q():
            entries = S.DeviceConfig.objects.filter(node_id=node_id, is_active=True)
            return {
                "node_id": node_id,
                "configs": {e.config_key: e.config_value for e in entries},
                "count": entries.count(),
            }
        return jsonify(await _q())

    @app.post("/nodes/:node_id/config")
    async def set_node_config(request, node_id: str):
        body = request.json() or {}
        config_key = body.get("config_key", "")
        if not config_key:
            return S._error(400, "config_key is required")

        @sync_to_async
        def _upsert():
            obj, created = S.DeviceConfig.objects.update_or_create(
                node_id=node_id, config_key=config_key,
                defaults={
                    "config_value": body.get("config_value", {}),
                    "category": body.get("category", "system"),
                    "description": body.get("description", ""),
                },
            )
            action = "created" if created else "updated"
            S.NodeEvent.objects.create(
                node_id=node_id, event_type="config_change",
                description=f"Config {config_key} {action}",
                metadata={"config_key": config_key, "action": action},
            )
            return {
                "node_id": node_id, "config_key": config_key,
                "config_value": obj.config_value, "action": action, "version": obj.version,
            }

        result = await _upsert()
        await S._broadcast_config_event("config_" + result["action"], node_id, {
            "config_key": config_key, "category": result.get("category", "system"),
        })
        if S.fire_config_changed:
            S.fire_config_changed(
                node_id=node_id, config_key=config_key,
                action=result["action"], new_value=body.get("config_value", {}),
                category=body.get("category", "system"),
            )
        return jsonify(result)

    @app.delete("/nodes/:node_id/config/:config_key")
    async def delete_node_config(request, node_id: str, config_key: str):
        @sync_to_async
        def _del():
            deleted, _ = S.DeviceConfig.objects.filter(
                node_id=node_id, config_key=config_key,
            ).delete()
            if deleted:
                S.NodeEvent.objects.create(
                    node_id=node_id, event_type="config_change",
                    description=f"Config {config_key} deleted",
                    metadata={"config_key": config_key, "action": "deleted"},
                )
            return {"deleted": deleted > 0}
        result = await _del()
        await S._broadcast_config_event("config_deleted", node_id, {"config_key": config_key})
        if result.get("deleted") and S.fire_config_changed:
            S.fire_config_changed(node_id=node_id, config_key=config_key, action="deleted")
        return jsonify(result)

    # ── Device history ──

    @app.get("/nodes/:node_id/history")
    async def node_history(request, node_id: str):
        limit = min(int(str(request.query_params.get("limit", "100"))), 500)

        @sync_to_async
        def _q():
            return {
                "node_id": node_id,
                "events": list(S.NodeEvent.objects.filter(node_id=node_id)
                    .order_by("-created_at")[:limit]
                    .values("id", "event_type", "description", "metadata", "created_at")),
                "heartbeats": list(S.Heartbeat.objects.filter(node_id=node_id)
                    .order_by("-received_at")[:limit]
                    .values("id", "status", "latency_ms", "received_at")),
                "configs": list(S.DeviceConfig.objects.filter(node_id=node_id, is_active=True)
                    .values("config_key", "category", "version", "updated_at")),
                "syncs": list(S.SyncLog.objects.filter(node_id=node_id)
                    .order_by("-created_at")[:50]
                    .values("entity_type", "entity_id", "direction", "status", "created_at")),
                "total_events": S.NodeEvent.objects.filter(node_id=node_id).count(),
            }
        return jsonify(await _q())

    # ── Node CRUD ──

    @app.get("/nodes")
    async def list_nodes(request):
        return jsonify(await S._list(S.Node, request))

    @app.get("/nodes/:node_id")
    async def get_node(request, node_id: str):
        @sync_to_async
        def _q():
            try:
                return S._ser_node(S.Node.objects.get(node_id=node_id))
            except S.Node.DoesNotExist:
                return None
        obj = await _q()
        if not obj:
            return S._error(404, "Node not found")
        return jsonify(obj)

    @app.post("/nodes/register")
    async def register_node(request):
        body = request.json() or {}
        if S._PYDANTIC_READY and S.NodeRegisterRequest:
            try:
                validated = S.NodeRegisterRequest(**body)
                body = validated.model_dump(exclude_none=True)
            except Exception as exc:
                return S._error(400, str(exc))

        @sync_to_async
        def _reg():
            nid = body.get("node_id") or f"NODE-{uuid.uuid4().hex[:8].upper()}"
            hst = body.get("hostname") or _socket.gethostname()
            node, created = S.Node.objects.update_or_create(
                node_id=nid,
                defaults={
                    "hostname": hst, "version": body.get("version", "unknown"),
                    "api_version": body.get("api_version", "1.0"),
                    "status": body.get("status", "online"),
                    "node_type": body.get("node_type", "pos-full"),
                    "product_count": body.get("product_count", 0),
                    "transaction_count": body.get("transaction_count", 0),
                    "customer_count": body.get("customer_count", 0),
                    "ip_address": body.get("ip_address"), "port": body.get("port"),
                    "capabilities": body.get("capabilities", {}),
                    "metadata": body.get("metadata", {}),
                },
            )
            S.Heartbeat.objects.create(
                node_id=nid, status=node.status,
                payload={"version": node.version, "product_count": node.product_count},
            )
            if created:
                S.NodeEvent.objects.create(
                    node_id=nid, event_type="registered",
                    description=f"Node {nid} registered ({node.node_type})",
                    metadata={"hostname": hst, "version": node.version},
                )
            return S._ser_node(node)

        node = await _reg()
        if S.fire_device_status_changed:
            S.fire_device_status_changed(
                node_id=node["node_id"], old_status="",
                new_status=node["status"], reason="node_registered",
            )
        await S._broadcast_node_event("registered", node["node_id"], node)
        return Response(
            status_code=201,
            headers={"Content-Type": "application/json"},
            description=json.dumps({"status": "registered", "node": node}),
        )

    @app.post("/nodes/heartbeat")
    async def heartbeat_node(request):
        body = request.json() or {}
        node_id = body.pop("node_id", None)
        if not node_id:
            return S._error(400, "node_id is required")

        if S._PYDANTIC_READY and S.HeartbeatRequest:
            try:
                validated = S.HeartbeatRequest(node_id=node_id, **body)
                body = validated.model_dump(exclude_none=True)
                node_id = body.pop("node_id", node_id)
            except Exception as exc:
                return S._error(400, str(exc))

        @sync_to_async
        def _hb():
            try:
                node = S.Node.objects.get(node_id=node_id)
            except S.Node.DoesNotExist:
                return None
            was_offline = node.status == "offline"
            node.status = body.get("status", "online")
            if "version" in body:
                node.version = body["version"]
            if "product_count" in body:
                node.product_count = body["product_count"]
            if "transaction_count" in body:
                node.transaction_count = body["transaction_count"]
            node.save()
            S.Heartbeat.objects.create(node_id=node_id, status=node.status, payload=body)
            if was_offline:
                S.NodeEvent.objects.create(
                    node_id=node_id, event_type="heartbeat_restored",
                    description=f"Node {node_id} restored to online",
                )
                if S.fire_device_status_changed:
                    S.fire_device_status_changed(
                        node_id=node_id, old_status="offline",
                        new_status=node.status, reason="heartbeat_restored",
                    )
            return S._ser_node(node)

        node = await _hb()
        if not node:
            return S._error(404, f"node '{node_id}' not found. Register first.")
        await S._broadcast_node_event("heartbeat", node["node_id"], node)
        return jsonify({"status": "ok", "node": node})

    @app.patch("/nodes/:node_id")
    async def update_node(request, node_id: str):
        body = request.json() or {}

        @sync_to_async
        def _upd():
            try:
                node = S.Node.objects.get(node_id=node_id)
            except S.Node.DoesNotExist:
                return None
            allowed = {"hostname", "version", "api_version", "status", "status_message",
                       "product_count", "transaction_count", "customer_count",
                       "ip_address", "port", "node_type", "is_active",
                       "capabilities", "metadata"}
            changed = [k for k in body if k in allowed and hasattr(node, k)]
            for k in changed:
                setattr(node, k, body[k])
            if changed:
                node.save(update_fields=changed + ["updated_at"])
                S.NodeEvent.objects.create(
                    node_id=node_id, event_type="config_change",
                    description=f"Node updated: {', '.join(changed)}",
                    metadata={"changed_fields": changed},
                )
            return S._ser_node(node)

        node = await _upd()
        if not node:
            return S._error(404, "node not found")
        await S._broadcast_node_event("config_change", node["node_id"], node)
        return jsonify(node)

    @app.delete("/nodes/:node_id")
    async def delete_node(request, node_id: str):
        @sync_to_async
        def _del():
            try:
                n = S.Node.objects.get(node_id=node_id)
                n.delete()
                S.NodeEvent.objects.create(
                    node_id=node_id, event_type="deleted",
                    description=f"Node {node_id} deleted",
                )
                return True
            except S.Node.DoesNotExist:
                return False
        if not await _del():
            return S._error(404, "node not found")
        await S._broadcast_node_event("deleted", node_id, {"node_id": node_id, "status": "deleted"})
        return jsonify({"status": "deleted"})

    # ── WebSocket: Node event stream (Full edition only) ──

    @app.websocket("/ws/nodes")
    async def node_stream(websocket):
        client_id = id(websocket)
        S._ws_clients.add(websocket)
        S._ws_filters[client_id] = {}
        try:
            await websocket.send_text(json.dumps({
                "type": "connected",
                "message": "Connected to POS Full node event stream",
                "client_id": client_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }))
            while True:
                msg = await websocket.receive_text()
                if msg is None:
                    break
                try:
                    data = json.loads(msg)
                    if "filter" in data:
                        S._ws_filters[client_id] = data["filter"]
                        await websocket.send_text(json.dumps({
                            "type": "filter_updated",
                            "filter": S._ws_filters[client_id],
                        }))
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({"type": "error", "message": "Invalid JSON"}))
        except Exception:
            pass
        finally:
            S._ws_clients.discard(websocket)
            S._ws_filters.pop(client_id, None)

    # ── Events API ──

    @app.get("/events")
    async def list_events(request):
        node_id_filter = request.query_params.get("node_id", None)
        event_type_filter = request.query_params.get("event_type", None)
        limit = min(int(str(request.query_params.get("limit", "50"))), 500)

        @sync_to_async
        def _q():
            qs = S.NodeEvent.objects.all()
            if node_id_filter:
                qs = qs.filter(node_id=node_id_filter)
            if event_type_filter:
                qs = qs.filter(event_type=event_type_filter)
            qs = qs.order_by("-created_at")[:limit]
            return [{
                "id": e.id, "node_id": e.node_id,
                "event_type": e.event_type, "description": e.description,
                "metadata": e.metadata,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            } for e in qs]
        return jsonify({"events": await _q(), "total": 0})
