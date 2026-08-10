"""
MCP tool definitions for background task operations.

These are registered with the django-fusion MCP endpoint and exposed
to AI agents via the Model Context Protocol.
"""

from __future__ import annotations

MCP_TASK_TOOLS = {
    "task.inspect": {
        "description": "Inspect a task by its ID or name. Returns status, logs, retry count.",
        "parameters": {
            "task_id": {"type": "string", "description": "UUID of the task log entry"},
            "task_name": {"type": "string", "description": "Registered task name (alternative to task_id)"},
        },
    },
    "task.queues": {
        "description": "List all task queues with message counts and consumer status.",
        "parameters": {},
    },
    "task.history": {
        "description": "Query task execution history with filtering.",
        "parameters": {
            "status": {"type": "string", "enum": ["queued", "started", "finished", "failed", "cancelled", "retrying"]},
            "queue": {"type": "string"},
            "task_name": {"type": "string"},
            "since": {"type": "string", "description": "ISO-8601 datetime"},
            "limit": {"type": "integer", "default": 20},
        },
    },
    "task.retry": {
        "description": "Re-enqueue a failed task with the same arguments.",
        "parameters": {
            "task_id": {"type": "string", "description": "UUID of the failed task log entry"},
        },
    },
    "task.trigger": {
        "description": "Manually trigger a registered task by name.",
        "parameters": {
            "task_name": {"type": "string", "description": "Registered task name"},
            "args": {"type": "array", "default": []},
            "kwargs": {"type": "object", "default": {}},
        },
    },
    "task.stats": {
        "description": "Aggregate task statistics: counts by status, failure rate.",
        "parameters": {
            "period": {"type": "string", "enum": ["1h", "24h", "7d"], "default": "24h"},
        },
    },
    "task.purge": {
        "description": "Purge stale completed/failed task logs older than N days.",
        "parameters": {
            "older_than_days": {"type": "integer", "default": 30},
            "status": {"type": "string", "enum": ["finished", "failed"], "default": "finished"},
        },
    },
    "task.workers": {
        "description": "Check worker health and consumer status.",
        "parameters": {},
    },
}
