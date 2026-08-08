"""POS Cloud — Django-Fusion table fragments.

Table components for rendering sortable, filterable data tables.

Usage:
    {% comp "core.tables.branches_table" branches=branches / %}
    {% comp "core.tables.leads_table" leads=leads filters=filters / %}
    {% comp "core.tables.reports_table" reports=reports / %}
"""

from django_fusion.routes.components.fragments import FragmentComponent


class BranchesTable(FragmentComponent):
    """Sortable, filterable branches table with organization grouping."""

    fragment_name = "core.tables.branches_table"

    def get_context(self, **kwargs):
        branches = kwargs.get("branches", [])
        return {
            "branches": branches,
            "columns": [
                {"key": "code", "label": "Code", "sortable": True},
                {"key": "name", "label": "Branch Name", "sortable": True},
                {"key": "organization", "label": "Organization", "sortable": True},
                {"key": "city", "label": "City", "sortable": True},
                {"key": "pos_type", "label": "POS Type", "sortable": True},
                {"key": "is_active", "label": "Status", "sortable": True},
            ],
        }


class LeadsTable(FragmentComponent):
    """Sortable, filterable leads table with status badges."""

    fragment_name = "core.tables.leads_table"

    def get_context(self, **kwargs):
        leads = kwargs.get("leads", [])
        filters = kwargs.get("filters", {})
        return {
            "leads": leads,
            "filters": filters,
            "columns": [
                {"key": "name", "label": "Name", "sortable": True},
                {"key": "email", "label": "Email", "sortable": True},
                {"key": "phone", "label": "Phone"},
                {"key": "organization", "label": "Org"},
                {"key": "status", "label": "Status", "sortable": True},
                {"key": "source", "label": "Source"},
                {"key": "assigned_to", "label": "Assignee"},
                {"key": "created_at", "label": "Created", "sortable": True},
            ],
        }


class ReportsTable(FragmentComponent):
    """Sortable reports table for both inventory and branch reports."""

    fragment_name = "core.tables.reports_table"

    def get_context(self, **kwargs):
        reports = kwargs.get("reports", [])
        report_type = kwargs.get("report_type", "inventory")
        return {
            "reports": reports,
            "report_type": report_type,
            "columns": [
                {"key": "title", "label": "Title", "sortable": True},
                {"key": "report_type", "label": "Type"},
                {"key": "branch", "label": "Branch"} if report_type == "branch" else {"key": "organization", "label": "Org"},
                {"key": "date_range", "label": "Date Range"},
                {"key": "created_at", "label": "Generated", "sortable": True},
            ],
        }
