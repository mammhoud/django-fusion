"""Regression tests for the /invite/<token>/ accept flow.

The invitation email links to ``/invite/<token>/`` (built by
``InvitationService``). These tests guard against the two regressions we hit
in precis-ctc: the link 404ing (no consuming route) and the token staying
reusable after acceptance.
"""

from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.domain.services.email.models import EmailLog


class InviteAcceptFlowTests(TestCase):
    """Valid token → redirect to signup with prefilled email; invalid → 400."""

    def setUp(self):
        self.log = EmailLog.objects.create(
            recipient="invited@example.com",
            subject="You are invited to join",
            status=EmailLog.Status.SENT,
            template_used="emails/invitation.html",
        )
        self.log.generate_invitation_token(expires_in_days=7)

    def _invite_url(self, token):
        return reverse("invite_accept", kwargs={"token": token})

    def test_valid_token_redirects_to_signup_with_email_prefilled(self):
        response = self.client.get(self._invite_url(self.log.invitation_token))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/signup/", response["Location"])
        self.assertIn("email=invited%40example.com", response["Location"])

    def test_valid_token_is_consumed_single_use(self):
        self.client.get(self._invite_url(self.log.invitation_token))
        self.log.refresh_from_db()
        self.assertIsNone(self.log.invitation_token)
        self.assertIsNone(self.log.token_expires_at)

    def test_reused_token_after_accept_returns_400(self):
        self.client.get(self._invite_url(self.log.invitation_token))
        response = self.client.get(self._invite_url(self.log.invitation_token))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "pages/token_error.html")

    def test_unknown_token_returns_400(self):
        response = self.client.get(self._invite_url("not-a-real-token"))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "pages/token_error.html")

    def test_expired_token_returns_400(self):
        self.log.token_expires_at = timezone.now() - timedelta(hours=1)
        self.log.save(update_fields=["token_expires_at"])
        response = self.client.get(self._invite_url(self.log.invitation_token))
        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "pages/token_error.html")

    def test_signup_page_prefills_email_from_query_param(self):
        # allauth's SignupView reads ?email= for its initial value; assert the
        # redirect target contract survives (invite → signup?email=…).
        response = self.client.get(self._invite_url(self.log.invitation_token))
        self.assertEqual(response.status_code, 302)
        location = response["Location"]
        self.assertTrue(location.startswith("/accounts/signup/"))
        self.assertIn("email=", location)
