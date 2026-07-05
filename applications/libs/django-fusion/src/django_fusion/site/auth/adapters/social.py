"""
Social account adapter for ceptor_ai.

Provides a minimal SocialAccountAdapter that delegates to allauth's default.

Canonical import: from ceptor_ai.adapters import SocialAccountAdapter
"""
try:
    from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

    class SocialAccountAdapter(DefaultSocialAccountAdapter):
        """Custom social account adapter — extends allauth default."""
        pass

except ImportError:
    class SocialAccountAdapter:  # type: ignore[no-redef]
        """Fallback stub when allauth is not installed."""
        pass
