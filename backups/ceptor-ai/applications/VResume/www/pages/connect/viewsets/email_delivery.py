from django_fusion.wagtail.viewsets import BaseSnippetViewSet
from django.utils.translation import gettext_lazy as _

from pages.connect.models import EmailDelivery


class EmailDeliveryViewSet(BaseSnippetViewSet):
    model = EmailDelivery
    icon = "mail"
    menu_label = _("Integrated Emails")
    menu_name = "integrated_emails"
    menu_group = "communications"
    menu_order = 120

    list_display = [
        "campaign",
        "subscriber",
        "status",
        "sent_at",
        "open_count",
        "click_count",
        "progress",
    ]
    list_filter = ["status", "sent_at", "opened_at", "clicked_at", "bounced_at"]
    search_fields = ["campaign__name", "subscriber__email", "tracking_token"]
    ordering = ["-created_at"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if queryset is None:
            return self.model.objects.none()
        return queryset.select_related("campaign", "subscriber")

    def progress(self, obj):
        if obj.status == "pending":
            return "0%"
        if obj.status in {"sent", "failed", "bounced"}:
            return "50%"
        return "100%"
    progress.short_description = _("Progress")
