"""POS Cloud — Django-Fusion skeleton loading fragments.

Skeleton/placeholder components shown during HTMX data loads.

Usage:
    {% comp "core.skeletons.table_skeleton" rows=5 cols=4 / %}
    {% comp "core.skeletons.card_skeleton" / %}
    {% comp "core.skeletons.report_skeleton" / %}
"""

from django_fusion.comp.routes import FragmentComponent


class TableSkeleton(FragmentComponent):
    """Skeleton loader for data tables with configurable rows and columns."""

    fragment_name = "core.skeletons.table_skeleton"

    def get_context(self, **kwargs):
        return {
            "rows": kwargs.get("rows", 5),
            "cols": kwargs.get("cols", 4),
        }


class CardSkeleton(FragmentComponent):
    """Skeleton loader for KPI / stat cards."""

    fragment_name = "core.skeletons.card_skeleton"

    def get_context(self, **kwargs):
        return {
            "count": kwargs.get("count", 4),
        }


class ReportSkeleton(FragmentComponent):
    """Skeleton loader for report page (filter bar + chart + table placeholders)."""

    fragment_name = "core.skeletons.report_skeleton"

    def get_context(self, **kwargs):
        return {
            "show_chart": kwargs.get("show_chart", True),
            "row_count": kwargs.get("row_count", 6),
        }


class ModalSkeleton(FragmentComponent):
    """Skeleton loader for modal forms."""

    fragment_name = "core.skeletons.modal_skeleton"

    def get_context(self, **kwargs):
        return {
            "field_count": kwargs.get("field_count", 4),
        }
