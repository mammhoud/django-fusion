"""
Custom Django test assertions for django-grep.
"""
from typing import Optional

from django.core import mail


class AssertEmailMixin:
    """
    Email assertion helpers for Django test cases.

    Mix into any TestCase subclass:

        class MyTest(AssertEmailMixin, TestCase):
            def test_email(self):
                send_welcome_email("user@example.com")
                self.assertEmailSent("user@example.com", subject="Welcome")
    """

    def assertEmailSent(
        self,
        recipient: Optional[str] = None,
        subject: Optional[str] = None,
        body_contains: Optional[str] = None,
    ) -> None:
        """Assert that at least one email was sent matching the given criteria."""
        self.assertTrue(len(mail.outbox) > 0, "No emails were sent")

        matching = mail.outbox
        if recipient:
            matching = [m for m in matching if recipient in m.to]
            self.assertTrue(
                len(matching) > 0,
                f"No email sent to {recipient!r}. Recipients: {[m.to for m in mail.outbox]}",
            )
        if subject:
            matching = [m for m in matching if subject in m.subject]
            self.assertTrue(
                len(matching) > 0,
                f"No email with subject containing {subject!r}. Subjects: {[m.subject for m in mail.outbox]}",
            )
        if body_contains:
            matching = [m for m in matching if body_contains in m.body]
            self.assertTrue(
                len(matching) > 0,
                f"No email with body containing {body_contains!r}",
            )

    def assertEmailCount(self, count: int) -> None:
        """Assert exactly `count` emails were sent."""
        self.assertEqual(
            len(mail.outbox),
            count,
            f"Expected {count} email(s), got {len(mail.outbox)}",
        )

    def assertNoEmailSent(self) -> None:
        """Assert no emails were sent."""
        self.assertEqual(len(mail.outbox), 0, f"Expected no emails, got {len(mail.outbox)}")

    def get_last_email(self):
        """Return the most recently sent email."""
        self.assertTrue(len(mail.outbox) > 0, "No emails were sent")
        return mail.outbox[-1]
