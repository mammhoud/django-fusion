from django.apps import AppConfig


class MCPDesignerConfig(AppConfig):
    name = 'django_rseal.mcp_designer'
    label = 'mcp_designer'
    verbose_name = "MCP Designer"

    def ready(self):
        # Import signals to register receivers
        from . import signals  # noqa
