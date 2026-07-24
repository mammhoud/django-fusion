"""
POS Full Server - Route modules.

Each module exports a `register_routes(app)` function that wires
route handlers to a Robyn application instance.

Usage:
    from routes import register_all

    app = Robyn(__file__)
    register_all(app)
"""

def register_all(app):
    """Register all route handlers by importing each module.
    Modules import from 'server' module which is already loaded.
    """
    from routes import info as _info
    _info.register_info_routes(app)

    from routes import nodes as _nodes
    _nodes.register_node_routes(app)

    from routes import config as _config
    _config.register_config_routes(app)

    from routes import sync as _sync
    _sync.register_sync_routes(app)

    from routes import approvals as _approvals
    _approvals.register_approval_routes(app)

    from routes import webhooks as _webhooks
    _webhooks.register_webhook_routes(app)

    from routes import crm as _crm
    _crm.register_crm_routes(app)

    from routes import reports as _reports
    _reports.register_report_routes(app)

    from routes import admin as _admin
    _admin.register_admin_routes(app)

    from routes import data as _data
    _data.register_data_routes(app)

    from routes import fusion_fragments as _fusion_fragments
    _fusion_fragments.register_fusion_fragment_routes(app)
