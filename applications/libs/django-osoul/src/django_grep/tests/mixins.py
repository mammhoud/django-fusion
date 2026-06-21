"""Test assertion mixins."""
import re  # noqa: F401


class AssertHTMLMixin:
    """Mixin for HTML content assertions."""

    def assertHTMLContains(self, response, text):
        """Assert response HTML contains the given text."""
        self.assertContains(response, text)

    def assertHTMLNotContains(self, response, text):
        """Assert response HTML does not contain the given text."""
        self.assertNotContains(response, text)

    def assertTemplateUsed(self, response, template_name):
        """Assert a specific template was used."""
        super().assertTemplateUsed(response, template_name)

    def assertRedirectsTo(self, response, url):
        """Assert response redirects to the given URL."""
        self.assertRedirects(response, url)


class AssertEmailMixin:
    """Mixin for email assertion helpers."""

    def assertEmailSent(self, to_email, subject=None, body_contains=None):
        """Assert an email was sent to the given address."""
        from django.core import mail

        matching = [
            m for m in mail.outbox
            if to_email in m.to
        ]
        self.assertTrue(
            len(matching) > 0,
            f"No email sent to {to_email}. Outbox: {[m.to for m in mail.outbox]}"
        )

        if subject:
            subjects = [m.subject for m in matching]
            self.assertIn(subject, subjects, f"Subject '{subject}' not found in {subjects}")

        if body_contains:
            bodies = [m.body for m in matching]
            self.assertTrue(
                any(body_contains in b for b in bodies),
                f"'{body_contains}' not found in email bodies"
            )

        return matching

    def assertNoEmailSent(self):
        """Assert no emails were sent."""
        from django.core import mail
        self.assertEqual(len(mail.outbox), 0, f"Expected no emails but got {len(mail.outbox)}")

    def clearEmailOutbox(self):
        """Clear the email outbox."""
        from django.core import mail
        mail.outbox = []
