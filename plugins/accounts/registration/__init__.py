"""
plugins.accounts.registration — compatibility shim.

All business logic has been merged into plugins.accounts.
This module re-exports everything so existing imports continue to work
without modification.

Deprecated: import directly from plugins.accounts.* instead.
"""

# Re-export from new locations so old imports keep working
from plugins.accounts.allauth_views import (  # noqa: F401
    AllauthLoginView,
    AllauthSignupView,
)
from plugins.accounts.emails import (  # noqa: F401
    _get_fallback_html,
    _get_sender_accounts,
    _resolve_template,
    _send_via_smtp,
    _send_with_django_backend,
    send_registration_email,
    send_signin_success_email,
)
from plugins.accounts.registration_adapter import RegistrationAdapter  # noqa: F401
from plugins.accounts.registration_forms import (  # noqa: F401
    PasswordCreationForm,
    RegistrationForm,
)
from plugins.accounts.registration_views import (  # noqa: F401
    CreatePasswordView,
    RegisterView,
    RegistrationSuccessView,
    _ensure_profile_exists,
    assign_default_group,
    ensure_groups_exist,
    get_client_ip,
    get_site_url,
    rate_limit_check,
    rate_limit_increment,
    trigger_notification,
)
from plugins.accounts.signals import on_user_logged_in  # noqa: F401
from plugins.accounts.tokens import (  # noqa: F401
    RegistrationTokenGenerator,
    registration_token_generator,
)
