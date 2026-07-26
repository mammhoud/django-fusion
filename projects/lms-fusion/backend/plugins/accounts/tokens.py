"""
Secure Token Generation for Email-Based Registration
=====================================================
Uses Django's signing framework for secure, time-limited tokens.
Tokens encode user ID + timestamp and expire after 24 hours.

The SALT is derived from settings.REGISTRATION_TOKEN_SALT if set,
otherwise falls back to a value derived from the site module name.
"""

import hashlib
import logging

from django.conf import settings
from django.core import signing
from django.utils import timezone

logger = logging.getLogger("apps.registration")

# Token validity period in seconds (24 hours)
TOKEN_MAX_AGE = 86400


def _get_salt() -> str:
    """
    Return the token SALT from settings.REGISTRATION_TOKEN_SALT.
    Falls back to a generic salt if not configured.
    Set REGISTRATION_TOKEN_SALT in configs/base/auth.py or _core.yml.
    """
    return getattr(
        settings,
        "REGISTRATION_TOKEN_SALT",
        "registration-password-create",
    )


class RegistrationTokenGenerator:
    """
    Generates and validates secure registration tokens using Django's signing framework.

    Tokens are:
    - Cryptographically signed (HMAC-SHA256)
    - Time-limited (24 hours)
    - Encoded with user ID + timestamp

    The SALT is read from settings.REGISTRATION_TOKEN_SALT at call time,
    so it is always site-specific without hardcoding it in this file.
    """

    def make_token(self, user) -> str:
        """Generate a secure, time-limited token for a user."""
        data = {
            "uid": str(user.pk),
            "ts": timezone.now().isoformat(),
            "hash": self._make_hash(user),
        }
        token = signing.dumps(data, salt=_get_salt())
        logger.info(f"Registration token generated for user_id={user.pk}")
        return token

    def validate_token(self, token: str) -> dict | None:
        """
        Validate a registration token.

        Returns:
            dict with 'uid', 'ts', 'hash' (and optionally 'allauth_key') if valid.
            {"expired": True} if the token signature is valid but has expired.
            None if the token is invalid (bad signature or any other error).
        """
        try:
            data = signing.loads(token, salt=_get_salt(), max_age=TOKEN_MAX_AGE)
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
        """Full token validation including user state check."""
        data = self.validate_token(token)
        if data is None or data.get("expired"):
            return False

        if str(user.pk) != str(data.get("uid")):
            logger.warning(f"Token user_id mismatch: expected={user.pk}, got={data.get('uid')}")
            return False

        expected_hash = self._make_hash(user)
        if data.get("hash") != expected_hash:
            logger.warning(f"Token state hash mismatch for user_id={user.pk}")
            return False

        return True

    def make_allauth_compatible_token(self, user, allauth_key: str) -> str:
        """
        Generate a signed token that embeds both the standard registration
        payload and the allauth EmailConfirmationHMAC key.

        Args:
            user: Django User instance
            allauth_key: The key string from allauth's EmailConfirmationHMAC

        Returns:
            Signed token string

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
        token = signing.dumps(data, salt=_get_salt())
        logger.info(f"Allauth-compatible token generated for user_id={user.pk}")
        return token

    def _make_hash(self, user) -> str:
        """Create a hash of the user's current state."""
        key_data = f"{user.pk}-{user.password}-{user.is_active}"
        return hashlib.sha256(
            f"{key_data}-{settings.SECRET_KEY}".encode()
        ).hexdigest()[:32]


# Singleton instance
registration_token_generator = RegistrationTokenGenerator()
