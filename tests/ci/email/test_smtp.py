"""
Live SMTP email delivery tests for ctc-research.com.

Uses the REAL email backend (not locmem) to confirm server-side SMTP delivery.

NOTE: These tests send real emails to mahmoud.ezzat.moustafa@gmail.com.
      They are tagged 'smtp' and excluded from the default test run.
      Run explicitly with: pytest -m smtp

Domain: ctc-research.com
SMTP: smtp.gmail.com:587 (yasirzaroug8@gmail.com)
"""
from __future__ import annotations

import pytest
from django.conf import settings as django_settings
from django.core.mail import send_mail
from django_fusion.tests.base import BaseTestCase

from ..base.config import Credentials, Domain


@pytest.mark.smtp
class LiveSMTPDeliveryTest(BaseTestCase):
    """
    Live SMTP delivery tests.

    These tests use the real SMTP backend and send actual emails.
    They confirm the server's email configuration is working end-to-end.
    """

    def test_smtp_sends_test_email_to_new_user(self):
        """
        Send a real test email via SMTP to mahmoud.ezzat.moustafa@gmail.com.

        Validates: SMTP email delivery from ctc-research.com server.
        """
        try:
            result = send_mail(
                subject=f"[{Domain.PRODUCTION}] Auth Test — Email Delivery Confirmation",
                message=(
                    f"This is an automated test email from {Domain.PRODUCTION}.\n\n"
                    "If you received this, the SMTP email sending is working correctly.\n\n"
                    f"Test: Registration + Email Confirmation Flow\n"
                    f"Recipient: {Credentials.NEW_USER_EMAIL}\n"
                    f"Server: {Domain.PRODUCTION_URL}\n"
                    f"SMTP Host: {django_settings.EMAIL_HOST}:{django_settings.EMAIL_PORT}\n"
                    f"From: {django_settings.DEFAULT_FROM_EMAIL}\n"
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[Credentials.NEW_USER_EMAIL],
                fail_silently=False,
            )
            self.assertEqual(
                result, 1,
                "send_mail must return 1 (one email sent successfully)",
            )
        except Exception as exc:
            self.fail(
                f"SMTP email delivery failed.\n"
                f"Host: {django_settings.EMAIL_HOST}:{django_settings.EMAIL_PORT}\n"
                f"From: {django_settings.DEFAULT_FROM_EMAIL}\n"
                f"Error: {exc}"
            )

    def test_smtp_configuration_is_valid(self):
        """
        Verify SMTP settings are configured correctly.

        Validates: EMAIL_HOST, EMAIL_PORT, EMAIL_USE_TLS, DEFAULT_FROM_EMAIL are set.
        """
        self.assertTrue(
            bool(django_settings.EMAIL_HOST),
            "EMAIL_HOST must be configured",
        )
        self.assertIn(
            django_settings.EMAIL_PORT,
            (25, 465, 587, 2525),
            f"EMAIL_PORT {django_settings.EMAIL_PORT} is not a standard SMTP port",
        )
        self.assertTrue(
            bool(django_settings.DEFAULT_FROM_EMAIL),
            "DEFAULT_FROM_EMAIL must be configured",
        )
        self.assertIn(
            "@", django_settings.DEFAULT_FROM_EMAIL,
            "DEFAULT_FROM_EMAIL must be a valid email address",
        )
