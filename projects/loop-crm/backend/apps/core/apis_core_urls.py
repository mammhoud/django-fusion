"""Canonical named API roads replacing the deprecated ``/api/v1/`` prefix.

These endpoints are the forward path for Loop-CRM's data API surface. They
live under ``/apis/core/`` and are separate from the public landing road
(``/apis/pages/``) and the billing road (``/apis/billing/``). The frontend's
``BoltApiClient`` will prefer these paths when the Bolt runtime is unavailable;
the ``/api/v1/`` copies remain accessible but carry Deprecation/Sunset headers
via ``APIV1DeprecationMiddleware``.
"""

from django.urls import path

from apps.core.api import dashboard_api, reports_api, workspace_current_api
from apps.crm.views import deal_move_api, pipeline_board_api

urlpatterns = [
    # Workspace identity — used by the WebSocket island to discover its tenant
    # id without a hardcoded value. (was: /api/v1/workspace/current/)
    path("workspace/current/", workspace_current_api, name="workspace_current_api"),
    # Dashboard counts — RevOps KPIs. (was: /api/v1/dashboard/)
    path("dashboard/", dashboard_api, name="dashboard_api"),
    # Report catalog — /reports/ surface. (was: /apis/reports/)
    path("reports/", reports_api, name="reports_api"),
    # Pipeline kanban board payload. (was: /api/v1/board/)
    path("board/", pipeline_board_api, name="pipeline_board_api"),
    # Move a deal between stages. (was: /api/v1/deals/<pk>/stage/)
    path("deals/<int:pk>/stage/", deal_move_api, name="deal_move_api"),
]