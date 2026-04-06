from contrib.sites.admin import register
from unfold.admin import ModelAdmin

from ..preloads.invitation import (
	get_invitation_admin_add_form,
	get_invitation_admin_change_form,
	get_invitation_model,
)

Invitation = get_invitation_model()
InvitationAdminAddForm = get_invitation_admin_add_form()
InvitationAdminChangeForm = get_invitation_admin_change_form()


@register(Invitation)
class InvitationAdmin(ModelAdmin):
	list_display = ("email", "sent", "accepted")
	# autocomplete_fields = ["inviter"]

	def get_form(self, request, obj=None, **kwargs):
		if obj:
			kwargs["form"] = InvitationAdminChangeForm
		else:
			kwargs["form"] = InvitationAdminAddForm
			kwargs["form"].user = request.user
			kwargs["form"].request = request
		return super().get_form(request, obj, **kwargs)
