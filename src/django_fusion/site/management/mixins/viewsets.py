"""Reusable Wagtail snippet viewset helpers."""

import csv
from collections.abc import Iterable, Sequence
from typing import Any

from django.contrib import messages
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from wagtail.snippets.views.snippets import SnippetViewSet


def export_to_csv(
    filename: str, headers: Sequence[Any], rows: Iterable[Sequence[Any]]
) -> HttpResponse:
    """Return a CSV download response for snippet data exports."""

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow([smart_str(header) for header in headers])
    for row in rows:
        writer.writerow([smart_str(value) for value in row])
    return response


class BaseSnippetViewSet(SnippetViewSet):
    """Base class for snippets with CSV export and display helpers."""

    list_export: Sequence[str] = []
    csv_filename = "data_export.csv"
    list_actions = ["duplicate", "export_csv"]
    menu_group = None

    def duplicate(self, request, queryset):
        """Duplicate selected snippets."""

        duplicated = 0
        for obj in queryset:
            obj.pk = None
            if hasattr(obj, "is_active"):
                obj.is_active = False
            obj.save()
            duplicated += 1

        messages.success(
            request,
            ngettext(
                "Duplicated %(count)d record",
                "Duplicated %(count)d records",
                duplicated,
            )
            % {"count": duplicated},
        )

    duplicate.label = _("Duplicate")
    duplicate.icon = "copy"

    def export_csv(self, request, queryset):
        """Export configured fields from selected snippets as CSV."""

        if not self.list_export:
            messages.warning(request, _("No export fields defined."))
            return None

        headers = [_(field.replace("_", " ").title()) for field in self.list_export]
        rows = []
        for obj in queryset:
            row = []
            for field in self.list_export:
                value = getattr(obj, field, "")
                if callable(value):
                    value = value()
                row.append(value or "")
            rows.append(row)

        return export_to_csv(self.csv_filename, headers, rows)

    export_csv.label = _("Export CSV")
    export_csv.icon = "download"

    @staticmethod
    def icon_boolean(
        value: bool,
        true_icon: str = "✅",
        false_icon: str = "❌",
        true_color: str = "#198754",
        false_color: str = "#dc3545",
    ):
        """Render a boolean value as a colored icon."""

        icon = true_icon if value else false_icon
        color = true_color if value else false_color
        return format_html('<span style="color:{};font-size:16px;">{}</span>', color, icon)

    @staticmethod
    def link_display(url: str | None):
        """Render a clickable link or a missing-link indicator."""

        if url:
            return format_html('<a href="{}" target="_blank">🔗 {}</a>', url, url)
        return format_html('<span style="color:#dc3545">❌ No link</span>')

    @staticmethod
    def image_display(image: Any):
        """Render an image-present indicator."""

        return BaseSnippetViewSet.icon_boolean(bool(image), "📷", "❌")
