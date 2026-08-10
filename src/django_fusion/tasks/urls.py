"""URLs for django-fusion task MCP endpoints.

Include this in your project's ``urls.py`` or wire through
django-fusion's router::

    from django.urls import path, include

    urlpatterns = [
        path("fusion/mcp/", include("django_fusion.tasks.urls")),
    ]
"""

from __future__ import annotations

from django.urls import path

from django_fusion.tasks.mcp_views import mcp_tools_call, mcp_tools_list

app_name = "fusion_tasks_mcp"

urlpatterns = [
    path("tools/list/", mcp_tools_list, name="mcp-tools-list"),
    path("tools/call/", mcp_tools_call, name="mcp-tools-call"),
]
