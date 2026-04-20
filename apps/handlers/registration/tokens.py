"""
Secure Token Generation for Email-Based Registration
=====================================================
Uses Django's signing framework for secure, time-limited tokens.
Tokens encode user ID + timestamp and expire after 24 hours.
"""

import hashlib
import logging

from django.conf import settings
from django.core import signing
from django.utils import timezone

logger = logging.getLogger("apps.registration")

# Token validity period in seconds (24 hours)
TOKEN_MAX_AGE = 86400  # 24 hours


class RegistrationTokenGenerator:
    """
    Generates and validates secure registration tokens using Django's signing framework.

    Tokens are:
    - Cryptographically signed (HMAC-SHA256)
    - Time-limited (24 hours)
    - Encoded with user ID + timestamp
    - Single-use (validated against user state)
    """

    SALT = "ctc-registration-password-create"

    def make_token(self, user) -> str:
        """
        Generate a secure, time-limited token for a user.

        The token encodes:
        - User's primary key
        - Creation timestamp
        - A hash of user state (so token is invalidated after password set)
        """
        data = {
            "uid": str(user.pk),
            "ts": timezone.now().isoformat(),
            "hash": self._make_hash(user),
        }
        token = signing.dumps(data, salt=self.SALT)
        logger.info(f"Registration token generated for user_id={user.pk}")
        return token

    def validate_token(self, token: str) -> dict | None:
        """
        Validate a registration token.

        Returns:
            dict with 'uid', 'ts', 'hash' if valid.
            {"expired": True} if the token signature is valid but has expired.
            None if the token is invalid (bad signature or any other error).
        """
        try:
            data = signing.loads(token, salt=self.SALT, max_age=TOKEN_MAX_AGE)
            logger.info(f"Token validated successfully for user_id={data.get('uid')}")
            return data
        except signing.SignatureExpired:
            logger.warning("Registration token expired")
            return {"expired": True}
        except signing.BadSignature:
            logger.warning("Registration token has invalid signature")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    def check_token(self, user, token: str) -> bool:
        """
        Full token validation including user state check.
        Prevents token replay after password has been set.
        """
        data = self.validate_token(token)
        if data is None or data.get("expired"):
            return False

        # Verify user ID matches
        if str(user.pk) != str(data.get("uid")):
            logger.warning(f"Token user_id mismatch: expected={user.pk}, got={data.get('uid')}")
            return False

        # Verify user state hasn't changed (password not already set)
        expected_hash = self._make_hash(user)
        if data.get("hash") != expected_hash:
            logger.warning(f"Token state hash mismatch for user_id={user.pk} (password may already be set)")
            return False

        return True

    def make_allauth_compatible_token(self, user, allauth_key: str) -> str:
        """
        Generate a signed token that embeds both the standard registration
        payload and the allauth EmailConfirmationHMAC key.

        The resulting token can be validated with validate_token(), which
        will return a dict containing 'uid', 'ts', 'hash', and 'allauth_key'.

        Args:
            user: Django User instance
            allauth_key: The key string from allauth's EmailConfirmationHMAC

        Returns:
            Signed token string (same format as make_token, with extra field)

        Raises:
            ValueError: If allauth_key is empty
        """
        if not allauth_key:
            raise ValueError("allauth_key must not be empty")
        data = {
            "uid": str(user.pk),
            "ts": timezone.now().isoformat(),
            "hash": self._make_hash(user),
            "allauth_key": allauth_key,
        }
        token = signing.dumps(data, salt=self.SALT)
        logger.info(f"Allauth-compatible token generated for user_id={user.pk}")
        return token

    def _make_hash(self, user) -> str:
        """
        Create a hash of the user's current state.
        This ensures the token is invalidated once the password is set.
        """
        key_data = f"{user.pk}-{user.password}-{user.is_active}"
        return hashlib.sha256(
            f"{key_data}-{settings.SECRET_KEY}".encode()
        ).hexdigest()[:32]


# Singleton instance
registration_token_generator = RegistrationTokenGenerator()
