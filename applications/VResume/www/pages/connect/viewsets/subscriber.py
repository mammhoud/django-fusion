"""
Subscriber Snippet ViewSet
Manages newsletter subscribers
"""
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn

from core.snippets import BaseSnippetViewSet
from pages.connect.models import Subscriber


class SubscriberViewSet(BaseSnippetViewSet):
    """
    Subscriber Snippet ViewSet
    Manages newsletter subscribers
    
    Menu: Communications > Subscribers
    """
    model = Subscriber
    icon = "mail"
    menu_label = _("Subscribers")
    menu_name = "subscribers"
    menu_group = "communications"
    menu_order = 100

    list_display = [
        "email",
        "name",
        "status",
        BooleanColumn("blog_notifications", label=_("Blog")),
        BooleanColumn("newsletter_notifications", label=_("Newsletter")),
        BooleanColumn("project_updates", label=_("Projects")),
    ]
    list_filter = ["status", "blog_notifications", "newsletter_notifications", "project_updates"]
    search_fields = ["email", "name"]
    ordering = ["-created_at"]
