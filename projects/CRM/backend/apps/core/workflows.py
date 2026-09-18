"""Loop-CRM workflow catalog.

These workflow definitions are intentionally provider-neutral. They describe
triggers and actions in the same way Twenty workflow automation and Postiz
approval/publishing flows do, while Dramatiq remains the execution runtime.
Persisted workflow instances can be added without changing the navigation or
connector contracts.
"""
from __future__ import annotations

from typing import Any

from django.db import OperationalError, ProgrammingError

WORKFLOW_ACTION_CATALOG: tuple[dict[str, str], ...] = (
    {"id": "assign_owner", "label": "Assign owner", "module": "crm"},
    {"id": "create_activity", "label": "Create sales activity", "module": "crm"},
    {"id": "request_approval", "label": "Request approval", "module": "marketing"},
    {"id": "notify_sales", "label": "Notify sales", "module": "crm"},
    {"id": "notify_marketing_manager", "label": "Notify marketing manager", "module": "marketing"},
    {"id": "publish_to_channels", "label": "Publish to connected channels", "module": "marketing"},
    {"id": "record_touchpoint", "label": "Record attribution touchpoint", "module": "attribution"},
    {"id": "refresh_analytics", "label": "Refresh post analytics", "module": "marketing"},
    {"id": "recalculate_attribution", "label": "Recalculate attribution", "module": "attribution"},
    {"id": "update_campaign_roi", "label": "Update campaign revenue", "module": "finance"},
    {"id": "create_invoice", "label": "Create invoice from won deal", "module": "finance"},
    {"id": "mark_invoice_overdue", "label": "Mark invoice overdue", "module": "finance"},
    {"id": "record_payment", "label": "Record invoice payment", "module": "finance"},
    {"id": "reconcile_pos_sale", "label": "Reconcile POS sale", "module": "pos"},
    {"id": "create_follow_up_task", "label": "Create follow-up task", "module": "crm"},
    {"id": "send_email", "label": "Send email notification", "module": "workspace"},
    {"id": "send_slack", "label": "Send Slack notification", "module": "workspace"},
    {"id": "call_webhook", "label": "Call outbound webhook", "module": "workspace"},
    {"id": "notify_revops", "label": "Notify RevOps", "module": "workspace"},
)


WORKFLOW_CATALOG: tuple[dict[str, Any], ...] = (
    {
        "id": "lead-capture",
        "name": "Route a new lead",
        "module": "crm",
        "trigger": "contact.created",
        "actions": ["assign_owner", "create_activity", "notify_sales"],
        "status": "ready",
    },
    {
        "id": "content-approval",
        "name": "Approve scheduled content",
        "module": "marketing",
        "trigger": "post.submitted_for_review",
        "actions": ["request_approval", "notify_marketing_manager"],
        "status": "ready",
    },
    {
        "id": "publish-and-attribute",
        "name": "Publish and create touchpoint",
        "module": "marketing",
        "trigger": "post.published",
        "actions": ["publish_to_channels", "record_touchpoint", "refresh_analytics"],
        "status": "ready",
    },
    {
        "id": "deal-won",
        "name": "Close the revenue loop",
        "module": "attribution",
        "trigger": "deal.stage_changed:closed_won",
        "actions": ["recalculate_attribution", "update_campaign_roi", "create_invoice", "notify_revops"],
        "status": "ready",
    },
    {
        "id": "invoice-dunning",
        "name": "Chase an overdue invoice",
        "module": "finance",
        "trigger": "invoice.due_date_passed",
        "actions": ["mark_invoice_overdue", "send_email", "create_follow_up_task"],
        "status": "ready",
    },
    {
        "id": "payment-received",
        "name": "Attribute a received payment",
        "module": "finance",
        "trigger": "payment.created",
        "actions": ["update_campaign_roi", "notify_revops"],
        "status": "ready",
    },
    {
        "id": "pos-revenue-reconciled",
        "name": "Reconcile POS revenue",
        "module": "pos",
        "trigger": "pos_sale.ingested",
        "actions": ["reconcile_pos_sale", "notify_revops"],
        "status": "ready",
    },
    {
        "id": "contact-nurture",
        "name": "Welcome a new contact",
        "module": "crm",
        "trigger": "contact.created",
        "actions": ["assign_owner", "send_email"],
        "status": "ready",
    },
)


TRIGGER_CATALOG: tuple[tuple[str, str], ...] = (
    ("contact.created", "Contact created"),
    ("deal.stage_changed:closed_won", "Deal closed won"),
    ("deal.stage_changed:closed_lost", "Deal closed lost"),
    ("post.submitted_for_review", "Post submitted for review"),
    ("post.published", "Post published"),
    ("invoice.created", "Invoice created"),
    ("invoice.due_date_passed", "Invoice due date passed"),
    ("payment.created", "Payment received"),
    ("pos_sale.ingested", "POS sale ingested"),
    ("campaign.created", "Campaign created"),
)


def trigger_catalog() -> list[dict[str, str]]:
    """Return the editor's trigger options (value + human label)."""
    return [{"id": value, "label": label} for value, label in TRIGGER_CATALOG]


def workflow_action_catalog() -> list[dict[str, str]]:
    return [dict(action) for action in WORKFLOW_ACTION_CATALOG]


def workflow_catalog() -> list[dict[str, Any]]:
    """Return the product's immutable workflow template catalog."""
    return [dict(workflow, actions=list(workflow["actions"])) for workflow in WORKFLOW_CATALOG]


def _topological_order(nodes: list[dict[str, Any]], edges: list[dict[str, str]]) -> list[str]:
    """Return node ids in topological order (Kahn's algorithm).

    Raises ``ValueError`` when the edge set contains a cycle so a canvas can
    never persist an executable graph that would loop forever.
    """
    ids = {node["id"] for node in nodes}
    indegree = {node_id: 0 for node_id in ids}
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in ids}
    for edge in edges:
        src, dst = edge["from"], edge["to"]
        adjacency[src].append(dst)
        indegree[dst] += 1

    queue = [node_id for node_id, degree in indegree.items() if degree == 0]
    order: list[str] = []
    while queue:
        node_id = queue.pop(0)
        order.append(node_id)
        for neighbour in adjacency[node_id]:
            indegree[neighbour] -= 1
            if indegree[neighbour] == 0:
                queue.append(neighbour)
    if len(order) != len(ids):
        raise ValueError("The workflow graph contains a cycle.")
    return order


def normalize_workflow_graph(
    payload: dict[str, Any],
    allowed_actions: set[str],
    *,
    trigger: str,
) -> tuple[dict[str, Any], list[str]]:
    """Validate a canvas graph and return ``(graph, actions)``.

    The accepted shape is::

        {"nodes": [{"id", "action", "x", "y"}], "edges": [{"from", "to"}]}

    * exactly one ``trigger`` node (id ``"trigger"``) anchors the graph;
    * every action node must reference a known action id and be reachable from
      the trigger (no orphan nodes);
    * the edge set must be acyclic.

    ``actions`` is the derived topological execution order so the executor and
    the step editor keep consuming the same flat contract.
    """
    nodes = payload.get("nodes")
    edges = payload.get("edges")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("A workflow needs at least a trigger node.")
    if not isinstance(edges, list):
        raise ValueError("Edges must be an array.")

    normalized_nodes: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    trigger_count = 0
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("Each node must be an object.")
        node_id = str(node.get("id") or "").strip()
        action = node.get("action")
        if not node_id:
            raise ValueError("Every node needs an id.")
        if node_id in seen_ids:
            raise ValueError(f"Duplicate node id: {node_id}.")
        seen_ids.add(node_id)
        if node_id == "trigger":
            trigger_count += 1
            action = None
        else:
            if not isinstance(action, str) or action.strip() not in allowed_actions:
                raise ValueError(f"Unknown action for node {node_id}.")
            action = action.strip()
        try:
            x = float(node.get("x") or 0)
            y = float(node.get("y") or 0)
        except (TypeError, ValueError):
            x, y = 0.0, 0.0
        normalized_nodes.append({"id": node_id, "action": action, "x": x, "y": y})

    if trigger_count != 1:
        raise ValueError("The graph needs exactly one trigger node.")

    normalized_edges: list[dict[str, str]] = []
    seen_edges: set[tuple[str, str]] = set()
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("Each edge must be an object.")
        src = str(edge.get("from") or "").strip()
        dst = str(edge.get("to") or "").strip()
        if src not in seen_ids or dst not in seen_ids:
            raise ValueError("Every edge must reference existing nodes.")
        if src == dst:
            raise ValueError("A node cannot connect to itself.")
        if (src, dst) in seen_edges:
            raise ValueError("Duplicate edge.")
        seen_edges.add((src, dst))
        normalized_edges.append({"from": src, "to": dst})

    order = _topological_order(normalized_nodes, normalized_edges)

    # Reachability check: every action node must be reachable from the trigger.
    reachable = {"trigger"}
    changed = True
    while changed:
        changed = False
        for edge in normalized_edges:
            if edge["from"] in reachable and edge["to"] not in reachable:
                reachable.add(edge["to"])
                changed = True
    orphans = [node["id"] for node in normalized_nodes if node["id"] not in reachable]
    if orphans:
        raise ValueError(f"Nodes not connected to the trigger: {', '.join(orphans)}.")

    actions = [
        next(node["action"] for node in normalized_nodes if node["id"] == node_id)
        for node_id in order
        if node_id != "trigger"
    ]
    graph = {"trigger": trigger, "nodes": normalized_nodes, "edges": normalized_edges}
    return graph, actions


def graph_from_actions(trigger: str, actions: list[str]) -> dict[str, Any]:
    """Derive a linear-chain canvas graph from a flat action list.

    Used to backfill the DAG view for workflows created before the canvas
    existed (or edited via the step editor / form).
    """
    nodes: list[dict[str, Any]] = [{"id": "trigger", "action": None, "x": 32, "y": 48}]
    edges: list[dict[str, str]] = []
    previous = "trigger"
    for index, action in enumerate(actions):
        node_id = f"step-{index + 1}"
        nodes.append({"id": node_id, "action": action, "x": 32 + (index + 1) * 200, "y": 48})
        edges.append({"from": previous, "to": node_id})
        previous = node_id
    return {"trigger": trigger, "nodes": nodes, "edges": edges}


def persisted_workflow_catalog(workspace_id: int | None = None) -> list[dict[str, Any]]:
    """Return workflow records scoped to global templates + one workspace.

    ``workspace_id=None`` returns only the product's global templates
    (``workspace__isnull=True``). Passing a workspace adds that tenant's own
    definitions on top, so a member never sees another tenant's automations.
    """
    from django.db.models import Q

    from .models import WorkflowDefinition

    try:
        definitions = WorkflowDefinition.objects.exclude(status="archived")
        if workspace_id is None:
            definitions = definitions.filter(workspace__isnull=True)
        else:
            definitions = definitions.filter(
                Q(workspace__isnull=True) | Q(workspace_id=workspace_id)
            )
        definitions = definitions.order_by("name")
        return [
            {
                "id": definition.slug,
                "name": definition.name,
                "module": definition.module,
                "description": definition.description,
                "trigger": definition.trigger,
                "actions": list(definition.actions or []),
                "status": definition.status,
                "graph": definition.graph
                or graph_from_actions(definition.trigger, list(definition.actions or [])),
            }
            for definition in definitions
        ]
    except (OperationalError, ProgrammingError):
        return []
