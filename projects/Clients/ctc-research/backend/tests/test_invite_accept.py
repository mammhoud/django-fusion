"""Regression tests for the invitation-accept flow.

Covers the ``/invite/<token>/`` landing route wired in ``apps/urls.py`` and
exercised by invitation emails (built by ``InvitationService`` as
``{SITE_URL}/invite/{token}/``):

* a valid, unexpired token → 302 redirect to registration with the
  recipient's email pre-filled in the ``?email=`` query param, and the token
  consumed (single-use);
* an unknown token → 400 with the shared ``token_error`` template;
* an expired token → 400 with the ``token_error`` template;
* the registration page renders the pre-filled email when arrived via the
  invite redirect.
* the invited role (persisted on the EmailLog) is assigned to the user as
  Django groups at registration, falling back to the default group.

These guard against regressions where the link 404s (unwired route), the
token is left reusable after acceptance, or the invited role never reaches
account creation.
"""

from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.domain.services.email.models import EmailLog
from apps.pages.accounts.site.views.registration import (
    get_invited_role_for_email,
    role_to_group_names,
)

User = get_user_model()

VALID_TOKEN = "valid-token-abc"
EXPIRED_TOKEN = "expired-token-xyz"
INVITED_EMAIL = "invited@example.com"


@override_settings(ROOT_URLCONF="tests.urls")
class InviteAcceptViewTests(TestCase):
    """Exercise the /invite/<token>/ landing end-to-end."""

    @classmethod
    def setUpTestData(cls):
        cls.register_url = reverse("handlers:register-account")

    def _invite_url(self, token: str = VALID_TOKEN) -> str:
        return reverse("invite-accept", kwargs={"token": token})

    def _make_invite(
        self,
        *,
        token: str = VALID_TOKEN,
        recipient: str = INVITED_EMAIL,
        token_expires_at=None,
    ):
        """Create an EmailLog row carrying a usable invitation token."""
        return EmailLog.objects.create(
            recipient=recipient,
            subject="You are invited to join CTC Research Hub",
            template_used="emails/invitation.html",
            status=EmailLog.Status.SENT,
            invitation_token=token,
            token_expires_at=token_expires_at or (timezone.now() + timedelta(days=7)),
        )

    # ── Valid token ────────────────────────────────────────────────────────

    def test_valid_token_redirects_to_registration_with_email_prefilled(self):
        """Valid token → 302 to the register page with ?email=<recipient>."""
        self._make_invite()

        response = self.client.get(self._invite_url())

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.register_url, response["Location"])
        self.assertIn("email=invited%40example.com", response["Location"])

    def test_valid_token_is_consumed_single_use(self):
        """After acceptance the token is cleared so it cannot be reused."""
        log = self._make_invite()

        self.client.get(self._invite_url())
        log.refresh_from_db()

        self.assertIsNone(log.invitation_token)
        self.assertIsNone(log.token_expires_at)

    def test_reused_token_after_accept_returns_400(self):
        """A consumed token is no longer accepted on a second visit."""
        self._make_invite()
        self.client.get(self._invite_url())

        response = self.client.get(self._invite_url())
        self.assertEqual(response.status_code, 400)

    def test_registration_page_prefills_email_from_query_param(self):
        """/auth/register/?email=… renders the email input pre-filled."""
        email = INVITED_EMAIL
        response = self.client.get(f"{self.register_url}?email={email}")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'value="{email}"')
        self.assertContains(response, 'name="email"')

    # ── Invalid / expired tokens ───────────────────────────────────────────

    def test_unknown_token_returns_400(self):
        """An unregistered token renders the token_error page (400)."""
        response = self.client.get(self._invite_url(token="never-issued-token"))

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "registration/token_error.html")
        self.assertContains(response, "invitation", status_code=400)

    def test_expired_token_returns_400(self):
        """A token past its expiry renders the token_error page (400)."""
        self._make_invite(
            token=EXPIRED_TOKEN,
            token_expires_at=timezone.now() - timedelta(hours=1),
        )

        response = self.client.get(self._invite_url(token=EXPIRED_TOKEN))

        self.assertEqual(response.status_code, 400)
        self.assertTemplateUsed(response, "registration/token_error.html")


@override_settings(ROOT_URLCONF="tests.urls")
class InvitedRoleGroupTests(TestCase):
    """Verify the invited role flows into Django group assignment."""

    @classmethod
    def setUpTestData(cls):
        cls.register_url = reverse("handlers:register-account")

    # ── role_to_group_names ────────────────────────────────────────────────

    def test_single_role_maps_to_one_group(self):
        """content_manager → [Content Manager]."""
        self.assertEqual(role_to_group_names("content_manager"), ["Content Manager"])

    def test_compound_role_maps_to_multiple_groups(self):
        """instructor/manager → [Instructor, Manager]."""
        self.assertEqual(
            role_to_group_names("instructor/manager"),
            ["Instructor", "Manager"],
        )

    def test_supervisor_role_maps_to_group(self):
        """supervisor → [Supervisor]."""
        self.assertEqual(role_to_group_names("supervisor"), ["Supervisor"])

    def test_empty_role_maps_to_nothing(self):
        """Empty role produces no groups."""
        self.assertEqual(role_to_group_names(""), [])

    # ── get_invited_role_for_email ─────────────────────────────────────────

    def test_returns_latest_invited_role_for_email(self):
        """The most recent invitation's role is returned."""
        EmailLog.objects.create(
            recipient=INVITED_EMAIL,
            subject="older",
            template_used="emails/invitation.html",
            status=EmailLog.Status.SENT,
            group_name="content_manager",
        )
        EmailLog.objects.create(
            recipient=INVITED_EMAIL,
            subject="newer",
            template_used="emails/invitation.html",
            status=EmailLog.Status.SENT,
            group_name="supervisor",
        )

        self.assertEqual(get_invited_role_for_email(INVITED_EMAIL), "supervisor")

    def test_returns_empty_when_no_invite(self):
        """No invitation for the address → empty role."""
        self.assertEqual(get_invited_role_for_email("nobody@example.com"), "")

    def test_ignores_roles_on_other_emails(self):
        """Another address's invite does not leak across."""
        EmailLog.objects.create(
            recipient="other@example.com",
            subject="x",
            template_used="emails/invitation.html",
            status=EmailLog.Status.SENT,
            group_name="supervisor",
        )

        self.assertEqual(get_invited_role_for_email(INVITED_EMAIL), "")

    # ── Registration assigns invited groups ────────────────────────────────

    def test_registration_assigns_invited_role_groups(self):
        """Registering with an invited email lands the user in role groups."""
        self._make_invite(role="instructor/manager")

        response = self.client.post(
            self.register_url,
            {
                "full_name": "Invited User",
                "email": INVITED_EMAIL,
            },
        )

        self.assertIn(response.status_code, (200, 302))
        user = User.objects.get(email=INVITED_EMAIL)
        group_names = set(user.groups.values_list("name", flat=True))
        self.assertIn("Instructor", group_names)
        self.assertIn("Manager", group_names)

    def test_registration_falls_back_to_default_group_without_invite(self):
        """No invite → user lands in the default Content Manager group."""
        response = self.client.post(
            self.register_url,
            {
                "full_name": "Plain User",
                "email": "plain@example.com",
            },
        )

        self.assertIn(response.status_code, (200, 302))
        user = User.objects.get(email="plain@example.com")
        group_names = set(user.groups.values_list("name", flat=True))
        self.assertIn("Content Manager", group_names)

    def _make_invite(self, *, role: str = "supervisor", token: str = "role-tok-1"):
        """Create an invitation EmailLog carrying a role."""
        return EmailLog.objects.create(
            recipient=INVITED_EMAIL,
            subject="You are invited to join CTC Research Hub",
            template_used="emails/invitation.html",
            status=EmailLog.Status.SENT,
            group_name=role,
            invitation_token=token,
            token_expires_at=timezone.now() + timedelta(days=7),
        )
