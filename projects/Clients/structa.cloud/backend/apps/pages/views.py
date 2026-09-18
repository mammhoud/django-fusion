"""Plain Django views for the pages app (non-Wagtail routes)."""

from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views import View


class InviteAcceptView(View):
    """Invitation landing — validates the invite token from the email link.

    The invitation email links to ``/invite/<token>/`` (built by
    ``InvitationService``). Valid tokens are consumed and the recipient is
    sent to allauth's signup page with their email pre-filled (allauth's
    SignupView already honours the ``?email=`` query parameter); expired or
    unknown tokens render the shared ``pages/token_error`` template.
    """

    def get(self, request, token):
        from apps.domain.services.communication.invitation_service import (
            InvitationService,
        )

        result = InvitationService.accept_invitation(token, user=request.user)
        if result.get("success"):
            email = result.get("email", "")
            signup_url = "/accounts/signup/"
            if email:
                signup_url = "{}?{}".format(signup_url, urlencode({"email": email}))
            return HttpResponseRedirect(signup_url)

        error_type = (
            "expired"
            if result.get("error") == "Token expired or invalid"
            else "invalid"
        )
        return render(
            request,
            "pages/token_error.html",
            {
                "error_type": error_type,
                "message": _(
                    "This invitation link is invalid or has expired. "
                    "Please contact the sender for a new invitation."
                ),
            },
            status=400,
        )
