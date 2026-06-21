from django.utils.translation import gettext_lazy as _
from django_osoul.wagtail.viewsets import BaseSnippetViewSet
from pages.home.models import TeamMember


class TeamMemberViewSet(BaseSnippetViewSet):
    model = TeamMember
    icon = "group"
    menu_label = _("Team Members")
    menu_order = 200
