from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .viewsets import SubscriberViewSet, FormSubmissionViewSet, EmailDeliveryViewSet


class ConnectAdminGroup(SnippetViewSetGroup):
    menu_label = "Connect"
    menu_icon = "mail"
    menu_order = 220
    items = (
        SubscriberViewSet,
        FormSubmissionViewSet,
        EmailDeliveryViewSet,
    )


register_snippet(ConnectAdminGroup)
