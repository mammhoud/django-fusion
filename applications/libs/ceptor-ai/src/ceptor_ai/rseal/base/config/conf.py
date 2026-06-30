from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models

from ceptor_ai.contrib.utils import unique_ordered
from ceptor_ai.typing import override

# ------------------------------------------------------------------
# CONSTANTS
# ------------------------------------------------------------------
COMPONENTS_SETTINGS_NAME = "COMPONENTS"
COMPONENTS_BUILTINS = "django_osoul.comp.templatetags.components"
COMPONENTS_FINDER = "django_osoul.comp.staticfiles.BlockAssetFinder"


# ------------------------------------------------------------------
# ENUMS
# ------------------------------------------------------------------
class EmailSendingStrategy(str, Enum):
    """Email sending strategies"""

    LOCAL = "local"
    CONSOLE = "console"
    SMTP = "smtp"
    SENDGRID = "sendgrid"
    MAILGUN = "mailgun"
    MAILTRAP = "mailtrap"
    MAILPIT = "mailpit"
    VIRTUAL = "virtual"
    AWS_SES = "aws_ses"


class TemplateSource(str, Enum):
    """Email template source strategies"""

    INLINE = "inline"
    FILE = "file"
    PATH = "path"
    EXTERNAL = "external"


class EmailPriority(str, Enum):
    """Email sending priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailStatus(str, Enum):
    """Email delivery statuses"""

    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    COMPLAINED = "complained"
    DEFERRED = "deferred"
    OPENED = "opened"
    CLICKED = "clicked"


class ImportStrategy(str, Enum):
    """Strategies for importing modules"""

    STANDARD = "standard"
    DJANGO = "django"
    LAZY = "lazy"
    CACHED = "cached"


# ------------------------------------------------------------------
# DJANGO BLOCK SETTINGS
# ------------------------------------------------------------------
@dataclass
class DjangoComponentsSettings:
    """Django Block component framework settings"""

    COMPONENT_DIRS: list[Path | str] = field(default_factory=list)
    ENABLE_BLOCK_ATTRS: bool = False
    ADD_ASSET_PREFIX: bool | None = None
    COMPONENT_CACHE_TIMEOUT: int = 3600  # 1 hour
    ENABLE_HOT_RELOAD: bool = settings.DEBUG
    MINIFY_COMPONENTS: bool = not settings.DEBUG
    DEFAULT_COMPONENT_THEME: str = "default"

    # Component registration
    AUTO_DISCOVER_COMPONENTS: bool = False

    # Asset settings
    ASSET_VERSIONING: bool = not settings.DEBUG
    ASSET_CACHE_BUSTING: bool = True
    BUNDLE_ASSETS: bool = not settings.DEBUG

    # Import settings
    IMPORT_STRATEGY: ImportStrategy = ImportStrategy.DJANGO
    ENABLE_LAZY_LOADING: bool = True
    CACHE_IMPORTS: bool = True

    @override
    def __getattribute__(self, __name: str) -> object:
        user_settings = getattr(settings, COMPONENTS_SETTINGS_NAME, {})
        return user_settings.get(__name, super().__getattribute__(__name))

    def get_component_directory_names(self):
        return unique_ordered([*self.COMPONENT_DIRS, "components"])

    def should_add_asset_prefix(self) -> bool:
        """Determine if the app label prefix should be added to asset URLs."""
        if self.ADD_ASSET_PREFIX is not None:
            return self.ADD_ASSET_PREFIX
        # Fall back to the DEBUG setting (add prefix in production)
        return not settings.DEBUG

    def get_component_cache_key(self, component_name: str) -> str:
        """Generate cache key for component."""
        return f"block_component_{component_name}_{self.DEFAULT_COMPONENT_THEME}"

    def get_import_strategy(self) -> ImportStrategy:
        """Get the import strategy to use."""
        return self.IMPORT_STRATEGY


# ------------------------------------------------------------------
# UTILITY FUNCTIONS
# ------------------------------------------------------------------
def import_attribute(path: str, strategy: ImportStrategy = ImportStrategy.DJANGO) -> Any:
    """
    Import an attribute from a module path.

    Args:
        path: Full path to attribute (e.g., "module.submodule.ClassName")
        strategy: Import strategy to use

    Returns:
        The imported attribute
    """
    assert isinstance(path, str), "Path must be a string"

    if strategy == ImportStrategy.LAZY:
        return _lazy_import_attribute(path)
    elif strategy == ImportStrategy.CACHED:
        return _cached_import_attribute(path)
    else:
        return _standard_import_attribute(path)


def _standard_import_attribute(path: str) -> Any:
    """Standard import using importlib."""
    try:
        import importlib
    except ImportError:
        from django.utils import importlib

    pkg, attr = path.rsplit(".", 1)
    module = importlib.import_module(pkg)
    return getattr(module, attr)


def _lazy_import_attribute(path: str) -> Any:
    """Lazy import that only imports when accessed."""
    from django.utils.functional import SimpleLazyObject

    def _import():
        return _standard_import_attribute(path)

    return SimpleLazyObject(_import)


def _cached_import_attribute(path: str) -> Any:
    """Cached import that stores result in module cache."""
    import hashlib

    from django.core.cache import cache

    cache_key = f"import_attribute_{hashlib.md5(path.encode()).hexdigest()}"
    cached = cache.get(cache_key)

    if cached is None:
        cached = _standard_import_attribute(path)
        cache.set(cache_key, cached, 3600)  # Cache for 1 hour

    return cached


def import_model(model_path: str) -> Type[models.Model]:
    """
    Import a Django model from a string path.

    Args:
        model_path: Model path in format "app_label.model_name"

    Returns:
        The model class

    Raises:
        ImproperlyConfigured: If model path is invalid or model not found
    """
    try:
        return django_apps.get_model(model_path)
    except ValueError:
        raise ImproperlyConfigured("Model path must be of the form 'app_label.model_name'")  # noqa: B904
    except LookupError:
        raise ImproperlyConfigured(f"Model '{model_path}' has not been installed or does not exist")  # noqa: B904


def import_form(form_path: str) -> Type:
    """
    Import a form class from a string path.

    Args:
        form_path: Full path to form class

    Returns:
        The form class
    """
    return import_attribute(form_path)


def import_adapter(adapter_path: str) -> Any:
    """
    Import an adapter class from a string path.

    Args:
        adapter_path: Full path to adapter class

    Returns:
        The adapter class or instance
    """
    return import_attribute(adapter_path)


# ------------------------------------------------------------------
# DYNAMIC IMPORT FUNCTIONS
# ------------------------------------------------------------------
def get_invite_form() -> Type:
    """
    Returns the form for sending an invite.

    Returns:
        The invite form class
    """
    return import_form(app_settings.INVITE_FORM)


def get_invitation_admin_add_form() -> Type:
    """
    Returns the form for creating a new invitation in admin.

    Returns:
        The admin add form class
    """
    return import_form(app_settings.ADMIN_ADD_FORM)


def get_invitation_admin_change_form() -> Type:
    """
    Returns the form for changing invitations in admin.

    Returns:
        The admin change form class
    """
    return import_form(app_settings.ADMIN_CHANGE_FORM)


def get_invitation_model() -> Type[models.Model]:
    """
    Returns the Invitation model that is active in this installation.

    Returns:
        The invitation model class

    Raises:
        ImproperlyConfigured: If model not found
    """
    return import_model(app_settings.INVITATION_MODEL)


def get_email_template_model() -> Type[models.Model]:
    """
    Returns the EmailTemplate model.

    Returns:
        The email template model class or None if not configured
    """
    model_path = getattr(app_settings, "EMAIL_TEMPLATE_MODEL", "core.CI.models.EmailTemplate")
    try:
        return import_model(model_path)
    except ImproperlyConfigured:
        return None


def get_email_handler() -> Any:
    """
    Returns the email handler for sending invitation emails.

    Returns:
        Email handler class or instance
    """
    email_handler_path = getattr(
        app_settings, "EMAIL_HANDLER", "core.CI.email_utils.InvitationEmailHandler"
    )
    return import_attribute(email_handler_path)


def get_adapter() -> Any:
    """
    Returns the adapter configured for invitations.

    Returns:
        Adapter class or instance
    """
    return import_adapter(app_settings.ADAPTER)


def get_confirmation_url_name() -> str:
    """
    Returns the confirmation URL name for invitations.

    Returns:
        URL name string
    """
    return app_settings.CONFIRMATION_URL_NAME


def get_email_strategy() -> EmailSendingStrategy:
    """
    Returns the email sending strategy.

    Returns:
        EmailSendingStrategy enum
    """
    return app_settings.EMAIL_STRATEGY


# ------------------------------------------------------------------
# FACTORY FUNCTIONS
# ------------------------------------------------------------------
def create_invitation_form(*args, **kwargs) -> Any:
    """
    Create an instance of the invitation form.

    Returns:
        Form instance
    """
    form_class = get_invite_form()
    return form_class(*args, **kwargs)


def create_invitation_admin_add_form(*args, **kwargs) -> Any:
    """
    Create an instance of the admin add form.

    Returns:
        Form instance
    """
    form_class = get_invitation_admin_add_form()
    return form_class(*args, **kwargs)


def create_invitation_admin_change_form(*args, **kwargs) -> Any:
    """
    Create an instance of the admin change form.

    Returns:
        Form instance
    """
    form_class = get_invitation_admin_change_form()
    return form_class(*args, **kwargs)


def create_invitation(**kwargs) -> models.Model:
    """
    Create a new invitation instance.

    Returns:
        Invitation model instance
    """
    model_class = get_invitation_model()
    return model_class.objects.create(**kwargs)


def get_invitation_by_key(key: str) -> Optional[models.Model]:
    """
    Get invitation by its key.

    Args:
        key: Invitation key

    Returns:
        Invitation instance or None
    """
    model_class = get_invitation_model()
    try:
        return model_class.objects.get(key=key)
    except model_class.DoesNotExist:
        return None


# ------------------------------------------------------------------
# VALIDATION FUNCTIONS
# ------------------------------------------------------------------
def validate_invitation_key(key: str) -> bool:
    """
    Validate an invitation key.

    Args:
        key: Invitation key to validate

    Returns:
        True if key is valid, False otherwise
    """
    invitation = get_invitation_by_key(key)
    if not invitation:
        return False

    # Check if accepted
    if invitation.accepted:
        return False

    # Check if expired
    if invitation.key_expired():
        return False

    # Check if active
    if hasattr(invitation, "is_active") and not invitation.is_active:
        return False

    return True


def validate_email_for_invitation(email: str) -> bool:
    """
    Validate if an email can receive an invitation.

    Args:
        email: Email to validate

    Returns:
        True if email can receive invitation, False otherwise
    """
    # Validate email format
    if not app_settings.validate_email_address(email):
        return False

    # Check if email already has a pending invitation
    model_class = get_invitation_model()
    existing = model_class.objects.filter(email=email, accepted=False, is_active=True).exists()

    return not existing


# ------------------------------------------------------------------
# INVITATIONS & EMAIL SETTINGS
# ------------------------------------------------------------------
class AppSettings:
    """Unified application settings for invitations and email system"""

    def __init__(self, prefix=""):
        self.prefix = prefix

    def _setting(self, name: str, dflt: Any) -> Any:
        """Get setting with prefix or from Django settings."""
        return getattr(settings, self.prefix + name, dflt)

    # ------------------------------------------------------------------
    # CORE APPLICATION SETTINGS
    # ------------------------------------------------------------------
    @property
    def APP_NAME(self) -> str:
        """Application name"""
        return self._setting("APP_NAME", "Core Application")

    @property
    def APP_VERSION(self) -> str:
        """Application version"""
        return self._setting("APP_VERSION", "1.0.0")

    @property
    def ENVIRONMENT(self) -> str:
        """Current environment (development, staging, production)"""
        return self._setting("ENVIRONMENT", "development" if settings.DEBUG else "production")

    @property
    def DEBUG(self) -> bool:
        """Debug mode"""
        return self._setting("DEBUG", settings.DEBUG)

    # ------------------------------------------------------------------
    # IMPORT SETTINGS
    # ------------------------------------------------------------------
    @property
    def IMPORT_STRATEGY(self) -> ImportStrategy:
        """Import strategy for dynamic imports"""
        return ImportStrategy(self._setting("IMPORT_STRATEGY", "django"))

    @property
    def ENABLE_IMPORT_CACHE(self) -> bool:
        """Enable caching for imported modules"""
        return self._setting("ENABLE_IMPORT_CACHE", True)

    @property
    def IMPORT_CACHE_TIMEOUT(self) -> int:
        """Cache timeout for imports in seconds"""
        return self._setting("IMPORT_CACHE_TIMEOUT", 3600)

    # ------------------------------------------------------------------
    # INVITATION SETTINGS
    # ------------------------------------------------------------------
    @property
    def INVITATION_EXPIRY(self) -> int:
        """How long before the invitation expires (in days)"""
        return self._setting("INVITATION_EXPIRY", 3)

    @property
    def INVITATION_ONLY(self) -> bool:
        """Signup is invite only"""
        return self._setting("INVITATION_ONLY", False)

    @property
    def CONFIRM_INVITE_ON_GET(self) -> bool:
        """Simple get request confirms invite"""
        return self._setting("CONFIRM_INVITE_ON_GET", True)

    @property
    def ACCEPT_INVITE_AFTER_SIGNUP(self) -> bool:
        """Accept the invitation after the user finished signup."""
        return self._setting("ACCEPT_INVITE_AFTER_SIGNUP", False)

    @property
    def GONE_ON_ACCEPT_ERROR(self) -> bool:
        """If an invalid/expired/previously accepted key is provided, return HTTP 410 GONE."""
        return self._setting("GONE_ON_ACCEPT_ERROR", True)

    @property
    def ALLOW_JSON_INVITES(self) -> bool:
        """Exposes json endpoint for mass invite creation"""
        return self._setting("ALLOW_JSON_INVITES", False)

    @property
    def SIGNUP_REDIRECT(self) -> str:
        """Where to redirect on email confirm of invite"""
        return self._setting("SIGNUP_REDIRECT", "account_signup")

    @property
    def LOGIN_REDIRECT(self) -> str:
        """Where to redirect on an expired or already accepted invite"""
        return self._setting("LOGIN_REDIRECT", getattr(settings, "LOGIN_URL", "/accounts/login/"))

    @property
    def ADAPTER(self) -> str:
        """The adapter, setting ACCOUNT_ADAPTER overrides this default"""
        return self._setting("ADAPTER", "django_osoul.adapters.AccountAdapter")

    @property
    def EMAIL_MAX_LENGTH(self) -> int:
        """Adjust max_length of e-mail addresses"""
        return self._setting("EMAIL_MAX_LENGTH", 254)

    @property
    def EMAIL_SUBJECT_PREFIX(self) -> Optional[str]:
        """Subject-line prefix to use for email messages sent"""
        return self._setting("EMAIL_SUBJECT_PREFIX", None)

    @property
    def INVITATION_MODEL(self) -> str:
        """Invitation model setup"""
        return self._setting("INVITATION_MODEL", "core.CI.models.Invitation")

    @property
    def INVITE_FORM(self) -> str:
        """Form class used for sending invites outside admin."""
        return self._setting("INVITE_FORM", "core.CI.forms.InviteForm")

    @property
    def ADMIN_ADD_FORM(self) -> str:
        """Form class used for sending invites in admin."""
        return self._setting("ADMIN_ADD_FORM", "core.CI.forms.InvitationAdminAddForm")

    @property
    def ADMIN_CHANGE_FORM(self) -> str:
        """Form class used for updating invitations in admin."""
        return self._setting("ADMIN_CHANGE_FORM", "core.CI.forms.InvitationAdminChangeForm")

    @property
    def CONFIRMATION_URL_NAME(self) -> str:
        return self._setting("CONFIRMATION_URL_NAME", "invitations:accept-invite")

    # ------------------------------------------------------------------
    # EMAIL CONFIGURATION SETTINGS
    # ------------------------------------------------------------------
    @property
    def EMAIL_STRATEGY(self) -> EmailSendingStrategy:
        """Default email sending strategy"""
        return EmailSendingStrategy(self._setting("EMAIL_STRATEGY", "console"))

    @property
    def DEFAULT_FROM_EMAIL(self) -> str:
        """Default sender email address"""
        return self._setting("DEFAULT_FROM_EMAIL", "noreply@example.com")

    @property
    def DEFAULT_REPLY_TO(self) -> Optional[str]:
        """Default reply-to email address"""
        return self._setting("DEFAULT_REPLY_TO", None)

    @property
    def DEFAULT_BCC(self) -> List[str]:
        """Default BCC recipients for all emails"""
        return self._setting("DEFAULT_BCC", [])

    @property
    def INVITATION_FROM_EMAIL(self) -> str:
        """Specific from email for invitation emails"""
        return self._setting("INVITATION_FROM_EMAIL", self.DEFAULT_FROM_EMAIL)

    @property
    def INVITATION_REPLY_TO(self) -> Optional[str]:
        """Specific reply-to for invitation emails"""
        return self._setting("INVITATION_REPLY_TO", self.DEFAULT_REPLY_TO)

    @property
    def INVITATION_BCC(self) -> List[str]:
        """Specific BCC for invitation emails"""
        return self._setting("INVITATION_BCC", self.DEFAULT_BCC)

    @property
    def EMAIL_TEMPLATE_PREFIX(self) -> str:
        """Prefix for email template paths"""
        return self._setting("EMAIL_TEMPLATE_PREFIX", "email/")

    @property
    def INVITATION_EMAIL_TEMPLATE(self) -> str:
        """Template for invitation emails"""
        return self._setting("INVITATION_EMAIL_TEMPLATE", "invitation/invitation_email")

    @property
    def INVITATION_EMAIL_SUBJECT(self) -> str:
        """Subject for invitation emails"""
        return self._setting("INVITATION_EMAIL_SUBJECT", "You're invited!")

    @property
    def SEND_INVITATION_EMAIL(self) -> bool:
        """Whether to send invitation emails"""
        return self._setting("SEND_INVITATION_EMAIL", True)

    @property
    def EMAIL_AS_BACKGROUND_TASK(self) -> bool:
        """Send emails as background tasks"""
        return self._setting("EMAIL_AS_BACKGROUND_TASK", False)

    @property
    def EMAIL_RETRY_ATTEMPTS(self) -> int:
        """Number of retry attempts for failed emails"""
        return self._setting("EMAIL_RETRY_ATTEMPTS", 3)

    @property
    def EMAIL_RETRY_DELAY(self) -> int:
        """Delay between retry attempts in seconds"""
        return self._setting("EMAIL_RETRY_DELAY", 60)

    @property
    def EMAIL_MAX_RETRY_DELAY(self) -> int:
        """Maximum delay between retry attempts in seconds"""
        return self._setting("EMAIL_MAX_RETRY_DELAY", 3600)

    @property
    def EMAIL_QUEUE_NAME(self) -> str:
        """Celery queue name for email tasks"""
        return self._setting("EMAIL_QUEUE_NAME", "emails")

    @property
    def EMAIL_PRIORITY_DEFAULT(self) -> EmailPriority:
        """Default email priority"""
        return EmailPriority(self._setting("EMAIL_PRIORITY_DEFAULT", "normal"))

    # ------------------------------------------------------------------
    # SMTP CONFIGURATION
    # ------------------------------------------------------------------
    @property
    def SMTP_HOST(self) -> str:
        """SMTP server host"""
        return self._setting("SMTP_HOST", "localhost")

    @property
    def SMTP_PORT(self) -> int:
        """SMTP server port"""
        return self._setting("SMTP_PORT", 25)

    @property
    def SMTP_USE_TLS(self) -> bool:
        """Use TLS for SMTP connection"""
        return self._setting("SMTP_USE_TLS", False)

    @property
    def SMTP_USE_SSL(self) -> bool:
        """Use SSL for SMTP connection"""
        return self._setting("SMTP_USE_SSL", False)

    @property
    def SMTP_USERNAME(self) -> str:
        """SMTP username"""
        return self._setting("SMTP_USERNAME", "")

    @property
    def SMTP_PASSWORD(self) -> str:
        """SMTP password"""
        return self._setting("SMTP_PASSWORD", "")

    @property
    def SMTP_TIMEOUT(self) -> int:
        """SMTP connection timeout in seconds"""
        return self._setting("SMTP_TIMEOUT", 30)

    # ------------------------------------------------------------------
    # SENDGRID CONFIGURATION
    # ------------------------------------------------------------------
    @property
    def SENDGRID_API_KEY(self) -> str:
        """SendGrid API key"""
        return self._setting("SENDGRID_API_KEY", "")

    @property
    def SENDGRID_SANDBOX_MODE(self) -> bool:
        """SendGrid sandbox mode for testing"""
        return self._setting("SENDGRID_SANDBOX_MODE", False)

    # ------------------------------------------------------------------
    # AWS SES CONFIGURATION
    # ------------------------------------------------------------------
    @property
    def AWS_SES_REGION(self) -> str:
        """AWS SES region"""
        return self._setting("AWS_SES_REGION", "us-east-1")

    @property
    def AWS_SES_CONFIG_SET(self) -> str:
        """AWS SES configuration set"""
        return self._setting("AWS_SES_CONFIG_SET", "")

    @property
    def AWS_SES_SOURCE_ARN(self) -> Optional[str]:
        """AWS SES source ARN for verified identity"""
        return self._setting("AWS_SES_SOURCE_ARN", None)

    # ------------------------------------------------------------------
    # MAILGUN CONFIGURATION
    # ------------------------------------------------------------------
    @property
    def MAILGUN_API_KEY(self) -> str:
        """Mailgun API key"""
        return self._setting("MAILGUN_API_KEY", "")

    @property
    def MAILGUN_DOMAIN(self) -> str:
        """Mailgun domain"""
        return self._setting("MAILGUN_DOMAIN", "")

    @property
    def MAILGUN_EU_REGION(self) -> bool:
        """Use Mailgun EU region"""
        return self._setting("MAILGUN_EU_REGION", False)

    # ------------------------------------------------------------------
    # EMAIL TEMPLATE SETTINGS
    # ------------------------------------------------------------------
    @property
    def EMAIL_LOGO_URL(self) -> str:
        """URL for logo in email templates"""
        return self._setting("EMAIL_LOGO_URL", "")

    @property
    def EMAIL_COMPANY_NAME(self) -> str:
        """Company name for email templates"""
        return self._setting("EMAIL_COMPANY_NAME", "")

    @property
    def EMAIL_COMPANY_ADDRESS(self) -> str:
        """Company address for email templates"""
        return self._setting("EMAIL_COMPANY_ADDRESS", "")

    @property
    def EMAIL_PRIMARY_COLOR(self) -> str:
        """Primary color for email templates"""
        return self._setting("EMAIL_PRIMARY_COLOR", "#007bff")

    @property
    def EMAIL_SECONDARY_COLOR(self) -> str:
        """Secondary color for email templates"""
        return self._setting("EMAIL_SECONDARY_COLOR", "#6c757d")

    @property
    def EMAIL_BACKGROUND_COLOR(self) -> str:
        """Background color for email templates"""
        return self._setting("EMAIL_BACKGROUND_COLOR", "#f8f9fa")

    @property
    def EMAIL_FONT_FAMILY(self) -> str:
        """Font family for email templates"""
        return self._setting("EMAIL_FONT_FAMILY", "Arial, sans-serif")

    # ------------------------------------------------------------------
    # EMAIL FEATURES
    # ------------------------------------------------------------------
    @property
    def EMAIL_TRACK_OPENS(self) -> bool:
        """Track email opens"""
        return self._setting("EMAIL_TRACK_OPENS", False)

    @property
    def EMAIL_TRACK_CLICKS(self) -> bool:
        """Track email link clicks"""
        return self._setting("EMAIL_TRACK_CLICKS", False)

    @property
    def EMAIL_UNSUBSCRIBE_LINK(self) -> bool:
        """Include unsubscribe link in emails"""
        return self._setting("EMAIL_UNSUBSCRIBE_LINK", True)

    @property
    def EMAIL_PREVIEW_TEXT(self) -> bool:
        """Include preview text in emails"""
        return self._setting("EMAIL_PREVIEW_TEXT", True)

    @property
    def EMAIL_SPAM_TEST(self) -> bool:
        """Run spam tests before sending"""
        return self._setting("EMAIL_SPAM_TEST", False)

    @property
    def EMAIL_VALIDATE_BEFORE_SEND(self) -> bool:
        """Validate email before sending"""
        return self._setting("EMAIL_VALIDATE_BEFORE_SEND", True)

    # ------------------------------------------------------------------
    # VALIDATION SETTINGS
    # ------------------------------------------------------------------
    @property
    def VALIDATE_EMAIL_DELIVERABILITY(self) -> bool:
        """Validate email deliverability before sending"""
        return self._setting("VALIDATE_EMAIL_DELIVERABILITY", False)

    @property
    def EMAIL_BLACKLIST(self) -> List[str]:
        """List of email domains/addresses to block"""
        return self._setting("EMAIL_BLACKLIST", [])

    @property
    def EMAIL_WHITELIST(self) -> List[str]:
        """List of allowed email domains/addresses (if set, only these are allowed)"""
        return self._setting("EMAIL_WHITELIST", [])

    @property
    def EMAIL_DOMAIN_BLOCKLIST(self) -> List[str]:
        """List of blocked email domains"""
        return self._setting("EMAIL_DOMAIN_BLOCKLIST", [])

    @property
    def EMAIL_DOMAIN_ALLOWLIST(self) -> List[str]:
        """List of allowed email domains"""
        return self._setting("EMAIL_DOMAIN_ALLOWLIST", [])

    # ------------------------------------------------------------------
    # TEMPLATE SETTINGS
    # ------------------------------------------------------------------
    @property
    def DEFAULT_TEMPLATE_SOURCE(self) -> TemplateSource:
        """Default template source"""
        return TemplateSource(self._setting("DEFAULT_TEMPLATE_SOURCE", "inline"))

    @property
    def TEMPLATE_CACHE_TIMEOUT(self) -> int:
        """Template cache timeout in seconds"""
        return self._setting("TEMPLATE_CACHE_TIMEOUT", 3600)

    @property
    def ENABLE_TEMPLATE_PREVIEW(self) -> bool:
        """Enable template preview in admin"""
        return self._setting("ENABLE_TEMPLATE_PREVIEW", True)

    @property
    def TEMPLATE_AUTO_UPDATE_FROM_FILES(self) -> bool:
        """Automatically update template content from uploaded files"""
        return self._setting("TEMPLATE_AUTO_UPDATE_FROM_FILES", True)

    # ------------------------------------------------------------------
    # PERFORMANCE SETTINGS
    # ------------------------------------------------------------------
    @property
    def EMAIL_BATCH_SIZE(self) -> int:
        """Batch size for bulk email sending"""
        return self._setting("EMAIL_BATCH_SIZE", 50)

    @property
    def EMAIL_CONCURRENT_SENDERS(self) -> int:
        """Number of concurrent email senders"""
        return self._setting("EMAIL_CONCURRENT_SENDERS", 5)

    @property
    def EMAIL_RATE_LIMIT(self) -> int:
        """Emails per minute rate limit"""
        return self._setting("EMAIL_RATE_LIMIT", 100)

    @property
    def ENABLE_EMAIL_LOGGING(self) -> bool:
        """Enable detailed email logging"""
        return self._setting("ENABLE_EMAIL_LOGGING", True)

    @property
    def EMAIL_LOG_RETENTION_DAYS(self) -> int:
        """Days to retain email logs"""
        return self._setting("EMAIL_LOG_RETENTION_DAYS", 90)

    # ------------------------------------------------------------------
    # HELPER METHODS
    # ------------------------------------------------------------------
    def get_email_context(self, extra_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get default email context with template variables"""
        context = {
            "logo_url": self.EMAIL_LOGO_URL,
            "company_name": self.EMAIL_COMPANY_NAME,
            "company_address": self.EMAIL_COMPANY_ADDRESS,
            "primary_color": self.EMAIL_PRIMARY_COLOR,
            "secondary_color": self.EMAIL_SECONDARY_COLOR,
            "background_color": self.EMAIL_BACKGROUND_COLOR,
            "font_family": self.EMAIL_FONT_FAMILY,
            "site_url": getattr(settings, "SITE_URL", ""),
            "site_name": getattr(settings, "SITE_NAME", ""),
            "site_domain": getattr(settings, "SITE_DOMAIN", ""),
            "track_opens": self.EMAIL_TRACK_OPENS,
            "track_clicks": self.EMAIL_TRACK_CLICKS,
            "include_unsubscribe": self.EMAIL_UNSUBSCRIBE_LINK,
            "year": self._get_current_year(),
            "app_name": self.APP_NAME,
            "app_version": self.APP_VERSION,
        }
        if extra_context:
            context.update(extra_context)
        return context

    def get_invitation_email_context(self, invitation=None) -> Dict[str, Any]:
        """Get context specific for invitation emails"""
        context = self.get_email_context()
        context.update(
            {
                "invitation": invitation,
                "expiry_days": self.INVITATION_EXPIRY,
                "subject": self.INVITATION_EMAIL_SUBJECT,
            }
        )
        return context

    def get_email_backend_config(self) -> Dict[str, Any]:
        """Get configuration for Django email backend based on strategy"""
        strategy = self.EMAIL_STRATEGY

        if strategy == EmailSendingStrategy.SMTP:
            return {
                "EMAIL_BACKEND": "django.core.mail.backends.smtp.EmailBackend",
                "EMAIL_HOST": self.SMTP_HOST,
                "EMAIL_PORT": self.SMTP_PORT,
                "EMAIL_USE_TLS": self.SMTP_USE_TLS,
                "EMAIL_USE_SSL": self.SMTP_USE_SSL,
                "EMAIL_HOST_USER": self.SMTP_USERNAME,
                "EMAIL_HOST_PASSWORD": self.SMTP_PASSWORD,
                "EMAIL_TIMEOUT": self.SMTP_TIMEOUT,
            }
        elif strategy == EmailSendingStrategy.CONSOLE:
            return {
                "EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
            }
        elif strategy == EmailSendingStrategy.LOCAL:
            return {
                "EMAIL_BACKEND": "django.core.mail.backends.locmem.EmailBackend",
            }
        elif strategy == EmailSendingStrategy.FILEBASED:
            return {
                "EMAIL_BACKEND": "django.core.mail.backends.filebased.EmailBackend",
                "EMAIL_FILE_PATH": "/tmp/app-messages",
            }
        else:
            # Default to console for other strategies that use custom handlers
            return {
                "EMAIL_BACKEND": "django.core.mail.backends.console.EmailBackend",
            }

    def _get_current_year(self) -> int:
        """Get current year for templates."""
        from datetime import datetime

        return datetime.now().year

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    def is_staging(self) -> bool:
        """Check if running in staging environment."""
        return self.ENVIRONMENT == "staging"

    def should_use_background_tasks(self) -> bool:
        """Determine if background tasks should be used."""
        return self.EMAIL_AS_BACKGROUND_TASK and self.is_production()

    def get_email_queue_config(self) -> Dict[str, Any]:
        """Get email queue configuration."""
        return {
            "queue": self.EMAIL_QUEUE_NAME,
            "priority": self.EMAIL_PRIORITY_DEFAULT.value,
            "retry": self.EMAIL_RETRY_ATTEMPTS > 0,
            "retry_policy": {
                "max_retries": self.EMAIL_RETRY_ATTEMPTS,
                "interval_start": self.EMAIL_RETRY_DELAY,
                "interval_step": self.EMAIL_RETRY_DELAY * 2,
                "interval_max": self.EMAIL_MAX_RETRY_DELAY,
            },
        }

    def validate_email_address(self, email: str) -> bool:
        """Validate email address against blocklist/whitelist."""
        import re

        # Basic email format validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False

        # Check blocklist
        if email in self.EMAIL_BLACKLIST:
            return False

        # Extract domain
        domain = email.split("@")[-1].lower()

        # Check domain blocklist
        if domain in self.EMAIL_DOMAIN_BLOCKLIST:
            return False

        # Check whitelist if set
        if self.EMAIL_WHITELIST and email not in self.EMAIL_WHITELIST:
            return False

        # Check domain allowlist if set
        if self.EMAIL_DOMAIN_ALLOWLIST and domain not in self.EMAIL_DOMAIN_ALLOWLIST:
            return False

        return True

    def get_template_settings(self) -> Dict[str, Any]:
        """Get template-related settings."""
        return {
            "cache_timeout": self.TEMPLATE_CACHE_TIMEOUT,
            "auto_update_from_files": self.TEMPLATE_AUTO_UPDATE_FROM_FILES,
            "enable_preview": self.ENABLE_TEMPLATE_PREVIEW,
            "default_source": self.DEFAULT_TEMPLATE_SOURCE.value,
        }


# ------------------------------------------------------------------
# INSTANCES
# ------------------------------------------------------------------
# Django Block settings instance
_settings = DjangoComponentsSettings()

# Application settings instance (with prefix for backward compatibility)
app_settings = AppSettings("INVITATIONS_")

# Global settings instance (without prefix for new code)
global_settings = AppSettings()


# ------------------------------------------------------------------
# SETTINGS VALIDATION
# ------------------------------------------------------------------
def validate_settings():
    """Validate all settings and log warnings for misconfigurations."""
    import logging

    logger = logging.getLogger(__name__)

    # Validate email strategy
    try:
        strategy = app_settings.EMAIL_STRATEGY
        if strategy == EmailSendingStrategy.SMTP:
            if not app_settings.SMTP_HOST:
                logger.warning("SMTP strategy selected but SMTP_HOST not configured")
        elif strategy == EmailSendingStrategy.SENDGRID:
            if not app_settings.SENDGRID_API_KEY:
                logger.warning("SendGrid strategy selected but SENDGRID_API_KEY not configured")
        elif strategy == EmailSendingStrategy.MAILGUN:
            if not app_settings.MAILGUN_API_KEY or not app_settings.MAILGUN_DOMAIN:
                logger.warning(
                    "Mailgun strategy selected but MAILGUN_API_KEY or MAILGUN_DOMAIN not configured"
                )
        elif strategy == EmailSendingStrategy.AWS_SES:
            if not app_settings.AWS_SES_REGION:
                logger.warning("AWS SES strategy selected but AWS_SES_REGION not configured")
    except Exception as e:
        logger.error(f"Error validating email strategy: {str(e)}")

    # Validate template settings
    if (
        app_settings.ENVIRONMENT == "production"
        and app_settings.EMAIL_STRATEGY == EmailSendingStrategy.CONSOLE
    ):
        logger.warning("Using console email strategy in production environment")

    # Validate import paths
    try:
        get_invitation_model()
    except ImproperlyConfigured as e:
        logger.error(f"Invalid invitation model configuration: {str(e)}")

    # Log settings summary
    if settings.DEBUG:
        logger.debug(f"App settings loaded: {app_settings.APP_NAME} v{app_settings.APP_VERSION}")
        logger.debug(f"Email strategy: {app_settings.EMAIL_STRATEGY}")
        logger.debug(f"Environment: {app_settings.ENVIRONMENT}")
        logger.debug(f"Import strategy: {app_settings.IMPORT_STRATEGY}")


# ------------------------------------------------------------------
# SETTINGS EXPORT
# ------------------------------------------------------------------
__all__ = [  # noqa: RUF022
    # Enums
    "EmailSendingStrategy",
    "TemplateSource",
    "EmailPriority",
    "EmailStatus",
    "ImportStrategy",
    # Settings classes
    "DjangoBlockSettings",
    "AppSettings",
    # Settings instances
    "block_settings",
    "app_settings",
    "global_settings",
    # Import functions
    "import_attribute",
    "import_model",
    "import_form",
    "import_adapter",
    # Dynamic import functions
    "get_invite_form",
    "get_invitation_admin_add_form",
    "get_invitation_admin_change_form",
    "get_invitation_model",
    "get_email_template_model",
    "get_email_handler",
    "get_adapter",
    "get_confirmation_url_name",
    "get_email_strategy",
    # Factory functions
    "create_invitation_form",
    "create_invitation_admin_add_form",
    "create_invitation_admin_change_form",
    "create_invitation",
    "get_invitation_by_key",
    # Validation functions
    "validate_invitation_key",
    "validate_email_for_invitation",
    # Validation
    "validate_settings",
]

