"""POS Cloud — Django-Fusion report fragments.

Report components for displaying generated reports with filters.

Usage:
    {% comp "core.reports.inventory_report" report=report / %}
    {% comp "core.reports.branch_report" report=report / %}
    {% comp "core.reports.report_filter_bar" report_type=type / %}
"""

from django_fusion.routes.components.fragments import FragmentComponent


class InventoryReportView(FragmentComponent):
    """Display a generated inventory report with summary and data section."""

    fragment_name = "core.reports.inventory_report"

    def get_context(self, **kwargs):
        report = kwargs.get("report")
        return {
            "report": report,
            "report_type_choices": [
                ("stock_level", "Stock Level"),
                ("low_stock", "Low Stock Alert"),
                ("movement", "Stock Movement"),
                ("valuation", "Inventory Valuation"),
                ("turnover", "Inventory Turnover"),
            ],
        }


class BranchReportView(FragmentComponent):
    """Display a generated branch performance report."""

    fragment_name = "core.reports.branch_report"

    def get_context(self, **kwargs):
        report = kwargs.get("report")
        return {
            "report": report,
            "report_type_choices": [
                ("daily_sales", "Daily Sales"),
                ("weekly_summary", "Weekly Summary"),
                ("monthly_summary", "Monthly Summary"),
                ("product_performance", "Product Performance"),
                ("employee_performance", "Employee Performance"),
                ("revenue_trend", "Revenue Trend"),
                ("profit_loss", "Profit & Loss"),
            ],
        }


class ReportFilterBar(FragmentComponent):
    """Filter bar for report generation with date pickers and dropdowns."""

    fragment_name = "core.reports.report_filter_bar"

    def get_context(self, **kwargs):
        report_type = kwargs.get("report_type", "inventory")
        branches = kwargs.get("branches", [])
        organizations = kwargs.get("organizations", [])
        return {
            "report_type": report_type,
            "branches": branches,
            "organizations": organizations,
        }
