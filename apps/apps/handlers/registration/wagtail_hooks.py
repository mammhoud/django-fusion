from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from .models import AuthEmailTemplate


class AuthEmailTemplateViewSet(SnippetViewSet):
    model = AuthEmailTemplate
    icon = "mail"
    menu_label = _("Email Templates")
    list_display = ["template_type", "subject", "is_active"]
    list_filter = ["template_type", "is_active"]
    search_fields = ["subject"]


class AuthEmailSnippetGroup(SnippetViewSetGroup):
    menu_label = _("Auth & Email")
    menu_icon = "lock"
    menu_order = 300
    items = (AuthEmailTemplateViewSet,)


register_snippet(AuthEmailSnippetGroup)
