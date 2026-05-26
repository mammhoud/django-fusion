from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, CharFilter
from django_osoul.core.models import EmailTemplate
from wagtail.admin.filters import WagtailFilterSet

from ..base import BaseSnippetViewSet  # ✅ unified base class for all snippets

# =============================================================================
# FILTERSET
# =============================================================================


class EmailTemplateFilterSet(WagtailFilterSet):
    """
    Advanced filtering for EmailTemplate model.
    """

    name = CharFilter(field_name="name", lookup_expr="icontains", label=_("Template Name"))
    is_active = BooleanFilter(field_name="is_active", label=_("Is Active"))
    is_default = BooleanFilter(field_name="is_default", label=_("Is Default"))

    class Meta:
        model = EmailTemplate
        fields = ["is_default", "is_active"]


# =============================================================================
# SNIPPET VIEWSET
# =============================================================================


class EmailTemplateViewSet(BaseSnippetViewSet):
    """
    Admin interface for managing Email Templates.
    Reusable HTML templates for newsletters and campaigns.
    """

    model = EmailTemplate
    menu_label = _("Email Templates")
    icon = "mail"
    menu_order = 240

    list_display = ("name", "is_default", "is_active", "created_at")
    list_filter = ("is_default", "is_active")
    search_fields = ("name", "description")
    filterset_class = EmailTemplateFilterSet
    list_export = ("name", "is_default", "is_active", "created_at")

    # -------------------------------------------------------------------------
    # Custom Admin Actions
    # -------------------------------------------------------------------------

    list_actions = ["set_default_template", "deactivate_templates"]

    def set_default_template(self, request, queryset):
        """
        Set one selected template as the default (unsets all others).
        """
        if queryset.count() != 1:
            messages.warning(request, _("Please select exactly one template to set as default."))
            return

        template = queryset.first()
        # unset others
        EmailTemplate.objects.update(is_default=False)
        template.is_default = True
        template.save()

        messages.success(request, _(f"'{template.name}' set as the default email template."))

    set_default_template.label = _("Set as Default")
    set_default_template.icon = "star"

    def deactivate_templates(self, request, queryset):
        """
        Deactivate selected templates.
        """
        count = queryset.update(is_active=False)
        messages.success(request, _(f"Deactivated {count} email templates."))

    deactivate_templates.label = _("Deactivate")
    deactivate_templates.icon = "cross"
