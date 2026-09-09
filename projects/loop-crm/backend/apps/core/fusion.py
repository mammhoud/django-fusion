"""django-fusion Application registry for Loop-CRM.

This is the route-level counterpart to ``apps.core.navigation``: the registry
provides real URL patterns and menu metadata, while the navigation module owns
hierarchy and active-state data for every render road.
"""
from __future__ import annotations

from django.urls import path
from django.utils.translation import gettext_lazy as _
from django_fusion.routes.core.base import menu_path
from django_fusion.routes.core.sites import Application, Module

from apps.crm.views import CompanyListView, ContactListView, DealListView
from apps.finance.views import (
    FinanceDashboardView,
    InvoiceListView,
    PaymentListView,
    RevenueListView,
)
from apps.marketing.views import ApprovalsView, ChannelListView, ContentCalendarView, MediaListView

from .navigation import navigation_context
from .views import (
    AihubView,
    AuditLogView,
    CustomFieldsView,
    CustomObjectRecordsView,
    CustomObjectsView,
    DashboardView,
    EmailInboxView,
    ImportView,
    IntegrationsView,
    MemberListView,
    ModuleView,
    ReportsView,
    ResourceListView,
    SavedViewsView,
    TaskCenterView,
    WorkflowListView,
)


class LoopCrmApplication(Application):
    title = _("Loop CRM")
    icon = "hub"
    app_name = "loop_crm"

    urlpatterns = [
        menu_path("", DashboardView.as_view(), name="dashboard", icon="dashboard", title=_("Overview")),
        path("overview/", DashboardView.as_view(), name="overview"),
        menu_path("crm/", ModuleView.as_view(module_id="crm", page_title=_("CRM"), page_kicker=_("Sales"), page_description=_("The relationship graph and pipeline operating system.")), name="crm", icon="account_tree", title=_("CRM")),
        path("crm/companies/", CompanyListView.as_view(), name="crm_companies"),
        path("crm/contacts/", ContactListView.as_view(), name="crm_contacts"),
        path("crm/pipelines/", ResourceListView.as_view(resource="pipelines", module_id="crm", page_title=_("Pipelines"), page_kicker=_("CRM · pipelines"), page_description=_("Configurable stages, probabilities, and forecasting views."), empty_message=_("No pipelines yet.")), name="crm_pipelines"),
        path("crm/deals/", DealListView.as_view(), name="crm_deals"),
        path("crm/activities/", ResourceListView.as_view(resource="activities", module_id="crm", page_title=_("Activities"), page_kicker=_("CRM · activities"), page_description=_("Calls, emails, meetings, notes, tasks, and social touches across every deal."), empty_message=_("No activities yet.")), name="crm_activities"),
        menu_path("marketing/", ModuleView.as_view(module_id="marketing", page_title=_("Marketing"), page_kicker=_("Growth"), page_description=_("Plan, approve, publish, and measure every channel from one calendar.")), name="marketing", icon="campaign", title=_("Marketing")),
        path("marketing/calendar/", ContentCalendarView.as_view(), name="marketing_calendar"),
        path("marketing/campaigns/", ResourceListView.as_view(resource="campaigns", module_id="marketing", page_title=_("Campaigns"), page_kicker=_("Marketing · campaigns"), page_description=_("Group content, spend, performance, and influenced deals."), empty_message=_("No campaigns yet.")), name="marketing_campaigns"),
        path("marketing/channels/", ChannelListView.as_view(), name="marketing_channels"),
        path("marketing/media/", MediaListView.as_view(), name="marketing_media"),
        path("marketing/approvals/", ApprovalsView.as_view(), name="marketing_approvals"),
        menu_path("finance/", FinanceDashboardView.as_view(), name="finance", icon="account_balance", title=_("Finance")),
        path("finance/invoices/", InvoiceListView.as_view(), name="finance_invoices"),
        path("finance/payments/", PaymentListView.as_view(), name="finance_payments"),
        path("finance/revenue/", RevenueListView.as_view(), name="finance_revenue"),
        menu_path("attribution/", ModuleView.as_view(module_id="attribution", page_title=_("Attribution"), page_kicker=_("RevOps"), page_description=_("See which content and conversations create pipeline revenue.")), name="attribution", icon="insights", title=_("Attribution")),
        path("attribution/touchpoints/", ResourceListView.as_view(resource="touchpoints", module_id="attribution", page_title=_("Touchpoints"), page_kicker=_("Attribution · touchpoints"), page_description=_("Every social interaction credited toward a deal."), empty_message=_("No touchpoints yet.")), name="attribution_touchpoints"),
        path("attribution/reports/", ReportsView.as_view(), name="attribution_reports"),
        path("ai/", AihubView.as_view(), name="ai"),
        path("employees/", ModuleView.as_view(module_id="employees", page_title=_("People"), page_kicker=_("Workspace · people"), page_description=_("Review member activity, ownership, publishing, and performance dossiers.")), name="employees"),
        menu_path("tasks/", TaskCenterView.as_view(site_name="loop-crm", template_name="dashboard/tasks.html"), name="tasks", icon="bolt", title=_("Tasks")),
        menu_path("settings/", ModuleView.as_view(module_id="workspace", page_title=_("Workspace"), page_kicker=_("Workspace"), page_description=_("Configure people, automations, integrations, and audit history.")), name="settings", icon="settings", title=_("Workspace")),
        path("settings/members/", MemberListView.as_view(), name="settings_members"),
        path("settings/workflows/", WorkflowListView.as_view(), name="settings_workflows"),
        path("settings/integrations/", IntegrationsView.as_view(), name="settings_integrations"),
        path("settings/email/", EmailInboxView.as_view(), name="settings_email"),
        path("settings/custom-fields/", CustomFieldsView.as_view(), name="settings_custom_fields"),
        path("settings/custom-objects/", CustomObjectsView.as_view(), name="settings_custom_objects"),
        path("settings/custom-objects/<str:key>/records/", CustomObjectRecordsView.as_view(), name="settings_custom_object_records"),
        path("settings/saved-views/", SavedViewsView.as_view(), name="settings_saved_views"),
        path("settings/import/", ImportView.as_view(), name="settings_import"),
        path("settings/audit/", AuditLogView.as_view(), name="settings_audit"),
    ]

    def application_context(self, request) -> dict:
        return {
            "site_name": _("Loop CRM"),
            "navigation": navigation_context(request.path),
        }


loop_crm_application = LoopCrmApplication()


class LoopCrmModule(Module):
    """Top-level django-fusion module that owns the Loop CRM application tree.

    The module declares the ``LoopCrmApplication`` resolver (and any custom
    routes attached below) as the route root; the application carries the
    per-page ``menu_path`` / ``path`` declarations.
    """

    title = _("Loop CRM")
    icon = "hub"
    urlpatterns = loop_crm_application.urls[0]


loop_crm_module = LoopCrmModule()
