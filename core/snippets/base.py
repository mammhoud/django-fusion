"""
Base Snippet ViewSet
Shared utilities for all snippet viewsets across the application
"""
from django.contrib import messages
from django.http import HttpResponse
from django.utils.encoding import smart_str
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from wagtail.snippets.views.snippets import SnippetViewSet


def export_to_csv(filename, headers, rows):
    """
    Reusable CSV export helper for snippet data exports.
    
    Args:
        filename: Name of the CSV file to download
        headers: List of column headers
        rows: List of rows (each row is a list of values)
    
    Returns:
        HttpResponse with CSV content
    """
    import csv
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow([smart_str(h) for h in headers])
    for row in rows:
        writer.writerow([smart_str(v) for v in row])
    return response


class BaseSnippetViewSet(SnippetViewSet):
    """
    Base class for Wagtail Snippet ViewSets with:
    - Common CSV export functionality
    - Duplicate & toggle actions
    - HTML formatters for display
    - Organized menu grouping
    
    Usage:
        class MySnippetViewSet(BaseSnippetViewSet):
            model = MyModel
            icon = "folder"
            menu_label = _("My Snippets")
            menu_group = "content"  # Groups snippets in admin menu
    """

    # Default export headers/fields — override in subclasses
    list_export = []
    csv_filename = "data_export.csv"

    # Optional common actions — override list_actions in subclasses
    list_actions = ["duplicate", "export_csv"]

    # Menu grouping for organization
    menu_group = None  # Override in subclasses: "content", "settings", "portfolio", etc.

    # --- Common Actions ---
    def duplicate(self, request, queryset):
        """Duplicate selected snippets"""
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
        """Generic CSV exporter for snippets"""
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

    # --- Display Helpers ---
    @staticmethod
    def icon_boolean(value, true_icon="✅", false_icon="❌", true_color="#198754", false_color="#dc3545"):
        """
        Render a boolean field as colored icon.
        
        Args:
            value: Boolean value
            true_icon: Icon to show when True
            false_icon: Icon to show when False
            true_color: Color for True state
            false_color: Color for False state
        
        Returns:
            HTML formatted icon
        """
        icon = true_icon if value else false_icon
        color = true_color if value else false_color
        return format_html('<span style="color:{};font-size:16px;">{}</span>', color, icon)

    @staticmethod
    def link_display(url):
        """
        Render clickable link or ❌ if missing.
        
        Args:
            url: URL to display
        
        Returns:
            HTML formatted link or error icon
        """
        if url:
            return format_html('<a href="{}" target="_blank">🔗 {}</a>', url, url)
        return format_html('<span style="color:#dc3545">❌ No link</span>')

    @staticmethod
    def image_display(image):
        """
        Render camera icon if image exists.
        
        Args:
            image: Image object or None
        
        Returns:
            HTML formatted icon
        """
        return BaseSnippetViewSet.icon_boolean(bool(image), "📷", "❌")
