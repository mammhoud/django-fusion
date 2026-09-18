"""Canonical named API roads replacing the deprecated ``/api/v1/`` prefix.

These endpoints are the forward path for Loop-CRM's data API surface. They
live under ``/apis/core/`` and are separate from the public landing road
(``/apis/pages/``) and the billing road (``/apis/billing/``). The frontend's
``BoltApiClient`` will prefer these paths when the Bolt runtime is unavailable;
the ``/api/v1/`` copies remain accessible but carry Deprecation/Sunset headers
via ``APIV1DeprecationMiddleware``.
"""

from django.urls import path

from apps.core.api import (
    ai_catalog_api,
    ai_consent_api,
    ai_operation_api,
    badge_counts_api,
    dashboard_api,
    employee_report_api,
    employees_api,
    integrations_api,
    ledger_settings_api,
    reports_api,
    search_api,
    resource_api,
    workflows_api,
    workspace_current_api,
)
from apps.core.locale_api import locale_api
from apps.crm.views import deal_move_api, pipeline_board_api
from apps.finance.views import revenue_trend_api

urlpatterns = [
    # Workspace identity — used by the WebSocket island to discover its tenant
    # id without a hardcoded value. (was: /api/v1/workspace/current/)
    path("workspace/current/", workspace_current_api, name="workspace_current_api"),
    # Dashboard counts — RevOps KPIs. (was: /api/v1/dashboard/)
    path("dashboard/", dashboard_api, name="dashboard_api"),
    # Report catalog — /reports/ surface. (was: /apis/reports/)
    path("reports/", reports_api, name="reports_api"),
    path("workflows/", workflows_api, name="workflows_api"),
    path("integrations/", integrations_api, name="integrations_api"),
    path("ai/", ai_catalog_api, name="ai_catalog_api"),
    path("settings/ledger/", ledger_settings_api, name="ledger_settings_api"),
    path("ai/consent/", ai_consent_api, name="ai_consent_api"),
    path("ai/<str:operation>/", ai_operation_api, name="ai_operation_api"),
    path("employees/", employees_api, name="employees_api"),
    path("employees/<int:pk>/report/", employee_report_api, name="employee_report_api"),
    path("search/", search_api, name="search_api"),
    # Live sidebar badge counters (approvals/invoices/tasks). (was: /apis/badges/)
    path("badges/", badge_counts_api, name="badge_counts_api"),
    path("locale/", locale_api, name="locale_api"),
    # Pipeline kanban board payload. (was: /api/v1/board/)
    path("board/", pipeline_board_api, name="pipeline_board_api"),
    # Move a deal between stages. (was: /api/v1/deals/<pk>/stage/)
    path("deals/<int:pk>/stage/", deal_move_api, name="deal_move_api"),
    path("revenue/trend/", revenue_trend_api, name="revenue_trend_api"),
    # Canonical session-cookie CRUD road for registered resources. `/api/v1/`
    # remains compatibility-only and is not used by the Astro shell.
    path("resources/<str:resource>/", resource_api, name="resource_api"),
    path("resources/<str:resource>/<int:pk>/", resource_api, name="resource_detail_api"),
]