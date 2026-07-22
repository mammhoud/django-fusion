"""
POS Server (Solo) - Route modules.

Each module exports a `register_routes(app)` function that wires
route handlers to a Robyn application instance.
"""

from routes.info import register_info_routes
from routes.nodes import register_node_routes
from routes.config import register_config_routes
from routes.sync import register_sync_routes
from routes.approvals import register_approval_routes


def register_all(app):
    """Register all route handlers on the given Robyn app."""
    register_info_routes(app)
    register_node_routes(app)
    register_config_routes(app)
    register_sync_routes(app)
    register_approval_routes(app)

    from routes import admin as _admin
    _admin.register_admin_routes(app)
