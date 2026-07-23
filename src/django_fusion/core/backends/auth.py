"""
Custom authentication backend that extends Allauth's AuthenticationBackend.

Allows authentication via:
- Email
- Username
- User ID
- Custom code field (e.g., employee or reference code)

Prefetches related profile, groups, and permissions for performance.
"""

import logging

from allauth.account.auth_backends import AuthenticationBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db.models import Prefetch, Q

logger = logging.getLogger("core")


class EmailOrUsernameModelBackend(AuthenticationBackend):
    """
    A flexible authentication backend supporting multiple identifiers.
    Inherits Allauth’s backend for password timing mitigation and security.
    """

    def authenticate(self, request, **credentials):
        """
        Authenticate user by email, username, ID, or code.
        Integrates with django-allauth’s secure password checking.
        """
        username = credentials.get("username")
        password = credentials.get("password")

        if not username or not password:
            return None

        User = get_user_model()
        user = None
        self._did_check_password = False

        try:
            # Search across multiple identifiers
            user = (
                User.objects.select_related("profile")
                .prefetch_related(
                    "groups",
                    Prefetch("user_permissions", queryset=Permission.objects.all()),
                )
                .filter(
                    Q(email__iexact=username)
                    | Q(username__iexact=username)
                    | Q(id__iexact=username)
                    | Q(code__iexact=username)
                )
                .distinct()
                .first()
            )

        except Exception as e:
            logger.error("Authentication query failed: %s", e)
            return None

        if user:
            self._did_check_password = True
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        # Perform timing attack mitigation if password wasn’t checked
        if not self._did_check_password:
            self._mitigate_timing_attack(password)

        return None

    def get_user(self, user_id):
        """
        Retrieve user instance with related profile and permissions.
        """
        User = get_user_model()
        try:
            return (
                User.objects.select_related("profile")
                .prefetch_related("groups", "user_permissions")
                .get(pk=user_id)
            )
        except User.DoesNotExist:
            return None
