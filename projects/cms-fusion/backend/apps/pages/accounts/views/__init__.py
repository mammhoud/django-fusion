"""Views for the accounts app."""

from .auth import AllauthLoginView, AllauthSignupView  # noqa: F401
from .notes import *  # noqa: F401, F403
from .privacy import *  # noqa: F401, F403
from .registration import (  # noqa: F401
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
from .tags import *  # noqa: F401, F403
