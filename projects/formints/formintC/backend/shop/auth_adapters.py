"""Shop allauth adapters — guest-cart merge on login + logout redirect."""
from allauth.account.adapter import DefaultAccountAdapter


class FormintCPurchaseAccountAdapter(DefaultAccountAdapter):
    """Merges the session guest cart into the user's account after login and
    sends customers back to the storefront after logout."""

    def get_logout_redirect_url(self, request):
        return "/"

    def login(self, request, user):
        super().login(request, user)
        # Adopt the guest cart under the authenticated user.
        from .services import merge_session_cart_to_user

        merge_session_cart_to_user(request)
