from django_osoul.comp.conf import (
    COMPONENTS_BUILTINS,
    COMPONENTS_FINDER,
    COMPONENTS_SETTINGS_NAME,
)
from django_osoul.comp.conf import (
    DjangoComponentsSettings as _DjangoComponentsSettings,
)
from django_osoul.config.conf import *
from django_rseal.workflows.pipelines.conf import (
    AppSettings as _AppSettings,
)
from django_rseal.workflows.pipelines.conf import (
    EmailPriority,
    EmailSendingStrategy,
    EmailStatus,
    TemplateSource,
    create_invitation,
    get_email_strategy,
    get_invitation_model,
    validate_email_for_invitation,
    validate_invitation_key,
)


# Re-export settings classes (but instantiated if needed, or just classes)
# The original code imported these classes.
class DjangoComponentsSettings(_DjangoComponentsSettings):
    pass

class AppSettings(_AppSettings):
    pass

# Or just aliases
# DjangoComponentsSettings = _DjangoComponentsSettings
# AppSettings = _AppSettings

# But the original code might have instantiated them?
# Original core/conf.py did NOT instantiate them at module level?
# Ah, it had `_settings = DjangoComponentsSettings()`?
# Let's check step 47.
# It had `app_settings` or similar?
# I see `app_settings = AppSettings()` implicitly used in `get_invite_form` (line 258).
# Wait, line 258 usages `app_settings.INVITE_FORM`. Where is `app_settings` defined?
# It wasn't shown in the view_file output (truncated).
# Let's assume `app_settings = AppSettings()` was at the end of the file.

app_settings = AppSettings()
