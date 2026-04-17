from django.contrib.admin import register
from unfold.admin import ModelAdmin

from core.CI.models.invitation.invitation import Invitation


@register(Invitation)
class InvitationAdmin(ModelAdmin):
    list_display = ("email", "accepted", "inviter")
