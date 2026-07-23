"""POS Cloud — Django-Fusion page layout fragments.

Layout components for consistent page structure across the platform.

Usage:
    {% comp "core.layouts.dashboard_layout" cards=cards / %}
    {% comp "core.layouts.report_page_layout" title="Report" report=report / %}
    {% comp "core.layouts.crm_page_layout" title="CRM" / %}
"""

from django_fusion.routes import FragmentComponent


class DashboardLayout(FragmentComponent):
    """Dashboard page layout with KPI cards grid and quick-action sections."""

    fragment_name = "core.layouts.dashboard_layout"

    def get_context(self, **kwargs):
        return {
            "cards": kwargs.get("cards", []),
            "recent_leads": kwargs.get("recent_leads", []),
            "recent_reports": kwargs.get("recent_reports", []),
        }


class ReportPageLayout(FragmentComponent):
    """Report page layout — filter bar → chart → data table → export controls."""

    fragment_name = "core.layouts.report_page_layout"

    def get_context(self, **kwargs):
        return {
            "title": kwargs.get("title", "Report"),
            "report": kwargs.get("report"),
            "report_type": kwargs.get("report_type", "inventory"),
            "filter_bar": kwargs.get("filter_bar", True),
            "chart_section": kwargs.get("chart_section", True),
            "table_section": kwargs.get("table_section", True),
            "export_enabled": kwargs.get("export_enabled", True),
        }


class CRMPageLayout(FragmentComponent):
    """CRM page layout — sidebar filters → kanban/table → modal actions."""

    fragment_name = "core.layouts.crm_page_layout"

    def get_context(self, **kwargs):
        return {
            "title": kwargs.get("title", "CRM"),
            "view_mode": kwargs.get("view_mode", "table"),  # table | kanban
            "entity_type": kwargs.get("entity_type", "leads"),  # leads | contacts | deals
        }
