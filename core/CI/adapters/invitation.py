


from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest

from .account import AccountAdapter

# ------------------------------------------------------------------
# BACKWARDS COMPATIBILITY
# ------------------------------------------------------------------

# Legacy adapter for backwards compatibility
class InvitationsAdapter(AccountAdapter):
    """
    Legacy adapter for backwards compatibility.
    Alias of AccountAdapter with deprecation warning.
    """
    
    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn(
            "InvitationsAdapter is deprecated and will be removed in a future version. "
            "Use AccountAdapter instead.",
            DeprecationWarning,
            stacklevel=2
        )
        super().__init__(*args, **kwargs)


# Handle legacy ACCOUNT_ADAPTER setting
if hasattr(settings, "ACCOUNT_ADAPTER"):
    if settings.ACCOUNT_ADAPTER.endswith("InvitationsAdapter"):
        # Update to use the new adapter while maintaining compatibility
        import warnings
        warnings.warn(
            f"The ACCOUNT_ADAPTER setting '{settings.ACCOUNT_ADAPTER}' is deprecated. "
            "Update to 'core.CI.adapters.AccountAdapter'.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Map old adapter to new one
        old_path = settings.ACCOUNT_ADAPTER
        new_path = "core.CI.adapters.AccountAdapter"
        
        # Only update if the old path matches the expected pattern
        if "invitation" in old_path.lower():
            settings.ACCOUNT_ADAPTER = new_path