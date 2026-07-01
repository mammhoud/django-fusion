"""Request/response middleware for transport layer.

Modules
-------
privacy_consent     Checks that visiting users have accepted the privacy policy
                    before accessing protected views.
"""

from .privacy_consent import PrivacyConsentMiddleware

__all__ = ["PrivacyConsentMiddleware"]
