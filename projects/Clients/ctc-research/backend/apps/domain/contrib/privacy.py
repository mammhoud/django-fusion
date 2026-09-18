"""Privacy content helpers for the domain layer.

`get_privacy_html()` returns the rendered HTML of the active PrivacyPolicy
record (or an empty string when none is configured), consumed by the auth
mixins and the HTMX privacy modal view.
"""


def get_privacy_html():
    """Return the active privacy policy HTML, or '' when unavailable."""
    try:
        from apps.pages.accounts.models.profiles.privacy import PrivacyPolicy

        policy = PrivacyPolicy.objects.filter(is_active=True).first()
        if policy is None:
            return ""
        return policy.content or ""
    except Exception:
        # Never block auth pages on privacy content.
        return ""
