"""
Shared test setup helpers for ctc-research.com CI tests.

Provides UserFactory and EmailFactory for consistent test data creation.
"""
from __future__ import annotations

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail

from .config import Credentials

User = get_user_model()


class UserFactory:
    """
    Factory for creating test users with consistent state.

    All users created here are cleaned up by calling UserFactory.cleanup().
    """

    # Track emails created so tests can clean up
    _created_emails: list[str] = []

    @classmethod
    def create_verified(
        cls,
        email: str = Credentials.NEW_USER_EMAIL,
        password: str = Credentials.NEW_USER_PASSWORD,
        username: str | None = None,
    ) -> "User":
        """Create an active, email-verified user."""
        User.objects.filter(email=email).delete()
        username = username or email.split("@")[0].replace(".", "_")[:30]
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=True,
        )
        EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={"verified": True, "primary": True},
        )
        cls._created_emails.append(email)
        return user

    @classmethod
    def create_unverified(
        cls,
        email: str = Credentials.NEW_USER_EMAIL,
        password: str = Credentials.NEW_USER_PASSWORD,
        username: str | None = None,
    ) -> "User":
        """Create an active user whose email is NOT verified."""
        User.objects.filter(email=email).delete()
        username = username or email.split("@")[0].replace(".", "_")[:30]
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=True,
        )
        EmailAddress.objects.get_or_create(
            user=user,
            email=email,
            defaults={"verified": False, "primary": True},
        )
        cls._created_emails.append(email)
        return user

    @classmethod
    def cleanup(cls, *emails: str) -> None:
        """Delete test users by email. If no emails given, cleans all tracked."""
        targets = list(emails) if emails else cls._created_emails[:]
        User.objects.filter(email__in=targets).delete()
        for e in targets:
            if e in cls._created_emails:
                cls._created_emails.remove(e)

    @classmethod
    def exists(cls, email: str) -> bool:
        """Check if a user with the given email exists."""
        return User.objects.filter(email=email).exists()

    @classmethod
    def get(cls, email: str) -> "User | None":
        """Get a user by email."""
        return User.objects.filter(email=email).first()


class EmailFactory:
    """
    Helpers for working with Django's email outbox in tests.

    Use with @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend').
    """

    @staticmethod
    def clear() -> None:
        """Clear the email outbox."""
        mail.outbox = []

    @staticmethod
    def sent_to(email: str) -> list:
        """Return all emails sent to the given address."""
        return [m for m in mail.outbox if email in m.to]

    @staticmethod
    def count() -> int:
        """Return total number of emails in outbox."""
        return len(mail.outbox)

    @staticmethod
    def last() -> object | None:
        """Return the last email sent."""
        return mail.outbox[-1] if mail.outbox else None

    @classmethod
    def assert_sent_to(cls, email: str, test_case) -> None:
        """Assert at least one email was sent to the given address."""
        sent = cls.sent_to(email)
        test_case.assertTrue(
            len(sent) > 0,
            f"No email sent to {email}. Outbox has {cls.count()} emails total.",
        )

    @classmethod
    def body_of_first_sent_to(cls, email: str) -> str:
        """Return the body of the first email sent to the given address."""
        sent = cls.sent_to(email)
        return sent[0].body if sent else ""
