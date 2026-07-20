"""
Approval workflow route handlers for POS Solo.
"""

from robyn import jsonify
from routes import state as S


def register_approval_routes(app):
    """Register approval-related routes."""

    @app.post("/approvals/:pk/approve")
    async def approve_change(request, pk: int):
        body = request.json() or {}
        result = await S.sync_engine.approve_changes([pk], reviewer=body.get("reviewer", ""), notes=body.get("notes", ""))
        await S._broadcast_config_event("approval_approved", "__approval__", {"approval_id": pk, "reviewer": body.get("reviewer", ""), "result": result.message})
        if S.fire_config_changed:
            S.fire_config_changed(node_id="__approval__", config_key=f"approval_{pk}", action="approved", new_value={"reviewer": body.get("reviewer", ""), "notes": body.get("notes", "")})
        return jsonify({"status": result.status if result.errors == 0 else "partial", **result.__dict__})

    @app.post("/approvals/:pk/reject")
    async def reject_change(request, pk: int):
        body = request.json() or {}
        result = await S.sync_engine.reject_changes([pk], reviewer=body.get("reviewer", ""), notes=body.get("notes", ""))
        await S._broadcast_config_event("approval_rejected", "__approval__", {"approval_id": pk, "reviewer": body.get("reviewer", ""), "reason": body.get("notes", "")})
        if S.fire_config_changed:
            S.fire_config_changed(node_id="__approval__", config_key=f"approval_{pk}", action="rejected", new_value={"reviewer": body.get("reviewer", ""), "reason": body.get("notes", "")})
        return jsonify(result.__dict__)

    @app.get("/approvals/stats")
    async def approval_stats(request):
        return jsonify(await S.sync_engine.get_approval_stats())

    @app.get("/approvals/pending")
    async def pending_approvals(request):
        entity_type = request.query_params.get("entity_type")
        node_id = request.query_params.get("node_id")
        limit = min(int(str(request.query_params.get("limit", "50"))), 200)
        result = await S.sync_engine.get_pending_approvals(entity_type=entity_type, node_id=node_id, limit=limit)
        return jsonify({"pending": result, "total": len(result)})
