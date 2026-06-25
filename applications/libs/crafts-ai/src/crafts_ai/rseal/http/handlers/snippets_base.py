"""
Base admin utilities and abstract viewset classes
for Wagtail snippets across the project.
"""

from django.contrib import messages
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from wagtail.snippets.views.snippets import SnippetViewSet

# =============================================================================
# SHARED UTILITIES
# =============================================================================

def export_to_csv(filename, headers, rows):
    """Reusable CSV export helper for snippet data exports."""
    import csv
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow([smart_str(h) for h in headers])
    for row in rows:
        writer.writerow([smart_str(v) for v in row])
    return response


# =============================================================================
# BASE SNIPPET VIEWSET
# =============================================================================

class BaseSnippetViewSet(SnippetViewSet):
    """
    Base class for Wagtail Snippet ViewSets with:
    - Common CSV export
    - Duplicate & toggle actions
    - HTML formatters
    """

    # Default export headers/fields — override in subclasses
    list_export = []
    csv_filename = "data_export.csv"

    # Optional common actions — override list_actions in subclasses
    list_actions = ["duplicate", "export_csv"]

    # --- Common Actions ---
    def duplicate(self, request, queryset):
        duplicated = 0
        for obj in queryset:
            obj.pk = None
            obj.is_active = getattr(obj, "is_active", False)
            obj.save()
            duplicated += 1

        messages.success(request, ngettext(
            "Duplicated %(count)d record",
            "Duplicated %(count)d records",
            duplicated
        ) % {"count": duplicated})

    duplicate.label = _("Duplicate")
    duplicate.icon = "copy"

    def export_csv(self, request, queryset):
        """Generic CSV exporter for snippets."""
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

    # --- Optional activate/deactivate toggle ---
    def activate(self, request, queryset):
        if not hasattr(queryset.model, "is_active"):
            messages.warning(request, _("This model does not have an 'is_active' field."))
            return

        count = queryset.update(is_active=True)
        messages.success(request, ngettext(
            "Activated %(count)d record",
            "Activated %(count)d records",
            count
        ) % {"count": count})

    activate.label = _("Activate")
    activate.icon = "view"

    def deactivate(self, request, queryset):
        if not hasattr(queryset.model, "is_active"):
            messages.warning(request, _("This model does not have an 'is_active' field."))
            return

        count = queryset.update(is_active=False)
        messages.success(request, ngettext(
            "Deactivated %(count)d record",
            "Deactivated %(count)d records",
            count
        ) % {"count": count})

    deactivate.label = _("Deactivate")
    deactivate.icon = "hidden"

    # --- Display Helpers ---
    @staticmethod
    def icon_boolean(value, true_icon="✅", false_icon="❌", true_color="#198754", false_color="#dc3545"):
        """Render a boolean field as colored icon."""
        icon = true_icon if value else false_icon
        color = true_color if value else false_color
        return format_html('<span style="color:{};font-size:16px;">{}</span>', color, icon)

    @staticmethod
    def link_display(url):
        """Render clickable link or ❌ if missing."""
        if url:
            return format_html('<a href="{}" target="_blank">🔗 {}</a>', url, url)
        return format_html('<span style="color:#dc3545">❌ No link</span>')

    @staticmethod
    def image_display(image):
        """Render camera icon if image exists."""
        return BaseSnippetViewSet.icon_boolean(bool(image), "📷", "❌")

    @staticmethod
    def safe_text(value, max_length=100):
        """Truncate long text safely for admin lists."""
        if not value:
            return ""
        return f"{value[:max_length]}..." if len(value) > max_length else value




