"""
Sync route handlers - status, config, trigger, push/receive, product sync, sales with items.
"""

import json
import logging
from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from robyn import jsonify, Response

from routes import state as S

logger = logging.getLogger("pos_full_server")


def register_sync_routes(app):
    """Register sync-related routes."""

    # ── Sales with items ──

    @app.post("/sales/with-items")
    async def create_sale_with_items(request):
        body = request.json() or {}
        @sync_to_async
        def _create():
            items_data = body.pop("items", [])
            sale = S.pos_models.Sale.objects.create(**body)
            for item in items_data:
                S.pos_models.SaleItem.objects.create(sale=sale, **item)
            return S._ser(sale)
        sale = await _create()
        return Response(
            status_code=201,
            headers={"Content-Type": "application/json"},
            description=json.dumps(sale),
        )

    # ── Sync status ──

    @app.get("/sync/status")
    async def sync_status(request):
        state = S._load_sync_state()
        cloud = S.SyncClient()
        cloud_health = await cloud.health()

        @sync_to_async
        def _stats():
            return {
                "total_logs": S.SyncLog.objects.count(),
                "pending": S.SyncLog.objects.filter(status="pending").count(),
                "failed": S.SyncLog.objects.filter(status="failed").count(),
                "success": S.SyncLog.objects.filter(status="success").count(),
            }

        local = await _stats()
        return jsonify({
            "config": {
                "enabled": state.get("enabled", True),
                "cloud_url": state.get("cloud_url", S.CLOUD_CRM_URL),
                "status": state.get("status", "idle"),
                "last_sync": state.get("last_sync"),
                "items_synced": state.get("items_synced", 0),
                "errors": state.get("errors", 0),
            },
            "local_logs": local,
            "cloud_crm": cloud_health,
        })

    # ── Sync config ──

    @app.patch("/sync/config")
    async def sync_config(request):
        body = request.json() or {}
        state = S._load_sync_state()
        if "cloud_url" in body:
            state["cloud_url"] = body["cloud_url"]
        if "api_key" in body:
            state["api_key"] = body["api_key"]
        if "enabled" in body:
            state["enabled"] = bool(body["enabled"])
        S._save_sync_state(state)
        return jsonify({"status": "ok", "config": state})

    # ── Sync log ──

    @app.get("/sync/log")
    async def sync_log(request):
        limit = min(int(str(request.query_params.get("limit", "50"))), 200)
        @sync_to_async
        def _q():
            qs = S.SyncLog.objects.all().order_by("-created_at")[:limit]
            return [{
                "id": log.id, "node_id": log.node_id,
                "entity_type": log.entity_type, "entity_id": log.entity_id,
                "direction": log.direction, "status": log.status,
                "error_message": log.error_message,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            } for log in qs]

        state = S._load_sync_state()
        entries = await _q()
        return jsonify({
            "entries": entries, "total": len(entries),
            "sync_config": {
                "last_sync": state.get("last_sync"),
                "status": state.get("status", "idle"),
                "items_synced": state.get("items_synced", 0),
                "errors": state.get("errors", 0),
            },
        })

    # ── Sync trigger ──

    @app.post("/sync/trigger")
    async def sync_trigger(request):
        state = S._load_sync_state()
        cloud = S.SyncClient()
        if not cloud.is_enabled:
            return jsonify({"error": "Sync is disabled. Enable via PATCH /sync/config", "config": state})

        @sync_to_async
        def _get_active():
            return [S._ser_node(n) for n in S.Node.objects.filter(is_active=True)]

        nodes = await _get_active()
        state["status"] = "syncing"
        S._save_sync_state(state)

        results = []
        for node_data in nodes:
            result = await cloud.push_node(node_data)
            status = result.get("status", "failed")
            await S._log_sync(
                node_data["node_id"], "node", node_data["node_id"],
                status, result.get("error", ""),
            )
            if status == "success":
                @sync_to_async
                def _mark(nid: str):
                    S.Node.objects.filter(node_id=nid).update(last_synced_at=datetime.now(timezone.utc))
                await _mark(node_data["node_id"])
            results.append({"node_id": node_data["node_id"], "status": status})

        succeeded = sum(1 for r in results if r["status"] == "success")
        state["status"] = "idle"
        state["last_sync"] = datetime.now(timezone.utc).isoformat()
        state["items_synced"] = state.get("items_synced", 0) + succeeded
        S._save_sync_state(state)

        await S._broadcast_node_event("sync_complete", "__cluster__", {
            "total_nodes": len(nodes), "succeeded": succeeded,
            "failed": len(results) - succeeded, "results": results,
        })
        return jsonify({"triggered": True, "total": len(results), "results": results})

    # ── Cloud push proxy ──

    @app.post("/cloud/push/:entity_type")
    async def cloud_push(request, entity_type: str):
        valid = {"nodes", "heartbeats", "events", "products", "sales", "customers", "inventory"}
        if entity_type not in valid:
            return jsonify({"error": f"invalid type: {entity_type}", "valid": list(valid)})
        body = request.json() or {}
        cloud = S.SyncClient()
        result = await cloud._push(entity_type, body)
        return jsonify(result)

    # ── API sync push receive ──

    @app.post("/api/sync/push/:entity_type")
    async def receive_push(request, entity_type: str):
        valid = {"nodes", "heartbeats", "events", "products", "sales", "customers", "inventory"}
        if entity_type not in valid:
            return jsonify({"error": f"invalid type: {entity_type}", "valid": list(valid)})
        body = request.json() or {}

        @sync_to_async
        def _record():
            S.SyncLog.objects.create(
                node_id=body.get("node_id", "unknown"),
                entity_type=entity_type, entity_id=body.get("id", ""),
                direction="push", status="success",
                payload_size=len(json.dumps(body)),
            )
        await _record()
        await S._broadcast_node_event("sync_push", body.get("node_id", "unknown"), {
            "entity_type": entity_type, "payload_size": len(json.dumps(body)),
            "node_id": body.get("node_id"),
            "data_preview": {k: body[k] for k in list(body)[:5]},
        })
        return jsonify({
            "status": "received", "entity_type": entity_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    # ── Product sync endpoints ──

    @app.post("/sync/receive/sales")
    async def receive_sales(request):
        body = request.json() or {}
        node_id = body.get("node_id", "unknown")
        sales = body.get("sales", [])
        require_approval = body.get("require_approval", True)
        result = await S.sync_engine.receive_sales_from_node(
            node_id, sales, require_approval=require_approval,
        )
        @sync_to_async
        def _log():
            S.SyncLog.objects.create(
                node_id=node_id, entity_type="sale",
                entity_id="batch", direction="push",
                status="pending" if require_approval else "success",
            )
        await _log()
        if S.fire_device_status_changed:
            S.fire_device_status_changed(
                node_id=node_id, old_status="idle",
                new_status="syncing_sales",
                reason=f"Received {len(sales)} sales from {node_id}",
            )
        return jsonify(result.__dict__)

    @app.post("/sync/receive/reports")
    async def receive_reports(request):
        body = request.json() or {}
        result = await S.sync_engine.receive_reports_from_node(
            body.get("node_id", "unknown"), body,
            require_approval=body.get("require_approval", True),
        )
        return jsonify(result.__dict__)

    @app.post("/sync/receive/inventory")
    async def receive_inventory(request):
        body = request.json() or {}
        result = await S.sync_engine.receive_inventory_changes(
            body.get("node_id", "unknown"), body.get("transactions", []),
            require_approval=body.get("require_approval", True),
        )
        return jsonify(result.__dict__)

    @app.post("/sync/push/products")
    async def push_products(request):
        body = request.json() or {}
        target_node = body.get("target_node_id", "")
        if not target_node:
            return S._error(400, "target_node_id is required")
        result = await S.sync_engine.push_products_to_node(
            body.get("master_node_id", "master"), target_node,
            body.get("products", []),
            create_approval=body.get("create_approval", False),
        )
        await S._broadcast_config_event("products_pushed", target_node, {
            "product_count": len(body.get("products", [])), "synced": result.synced,
        })
        if S.fire_config_synced:
            S.fire_config_synced(
                source_device_id=body.get("master_node_id", "master"),
                target_device_ids=[target_node],
                config_keys=[f"product_{p.get('id', '?')}" for p in body.get("products", [])],
                status="success" if result.errors == 0 else "partial",
            )
        return jsonify(result.__dict__)

    @app.post("/sync/push/configs")
    async def push_configs(request):
        body = request.json() or {}
        target = body.get("target_node_id", "")
        if not target:
            return S._error(400, "target_node_id is required")
        result = await S.sync_engine.push_config_to_node(
            body.get("master_node_id", "master"), target,
            body.get("configs", {}), category=body.get("category", "system"),
        )
        await S._broadcast_config_event("configs_pushed", target, {
            "config_count": len(body.get("configs", {})), "synced": result.synced,
        })
        if S.fire_config_synced:
            S.fire_config_synced(
                source_device_id=body.get("master_node_id", "master"),
                target_device_ids=[target],
                config_keys=list(body.get("configs", {}).keys()),
                status="success" if result.errors == 0 else "partial",
            )
        return jsonify(result.__dict__)

    @app.post("/sync/push/catalog")
    async def push_catalog(request):
        body = request.json() or {}
        target = body.get("target_node_id", "")
        if not target:
            return S._error(400, "target_node_id is required")
        result = await S.sync_engine.push_catalog_to_node(
            body.get("master_node_id", "master"), target,
            body.get("products", []),
            category_data=body.get("categories"), settings=body.get("settings"),
        )
        await S._broadcast_config_event("catalog_pushed", target, {
            "product_count": len(body.get("products", [])), "synced": result.synced,
        })
        return jsonify(result.__dict__)
