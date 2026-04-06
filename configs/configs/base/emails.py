# ====================================
# 📧 Email Configuration
# ====================================
from enum import Enum

from ..settings.conf import Environment, settings
from .apps import INSTALLED_APPS


# -------------------------------
# Email Strategy Enum
# -------------------------------
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


# -------------------------------
# Email Strategy Configuration
# -------------------------------
def get_email_strategy():
    """Get email strategy based on environment"""
    if settings.is_production:
        return settings.get("EMAIL_STRATEGY", EmailSendingStrategy.SMTP)
    else:
        return settings.get("EMAIL_STRATEGY", EmailSendingStrategy.CONSOLE)


EMAIL_SENDING_STRATEGY = get_email_strategy()

# -------------------------------
# Email Timeout Configuration
# -------------------------------
EMAIL_TIMEOUT = settings.get("EMAIL_TIMEOUT", 30)
EMAIL_USE_SSL = settings.get("EMAIL_USE_SSL", False)
EMAIL_USE_TLS = settings.get("EMAIL_USE_TLS", True)

# -------------------------------
# Email Failure Simulation (for testing)
# -------------------------------
EMAIL_SENDING_FAILURE_TRIGGER = settings.get("EMAIL_FAILURE_TRIGGER", False)
EMAIL_SENDING_FAILURE_RATE = settings.get("EMAIL_FAILURE_RATE", 0.2)
EMAIL_HOST_USER = None

# -------------------------------
# Email Backend Configuration
# -------------------------------
if EMAIL_SENDING_STRATEGY == EmailSendingStrategy.CONSOLE:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

elif EMAIL_SENDING_STRATEGY == EmailSendingStrategy.MAILTRAP:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = settings.get("MAILTRAP_HOST", "smtp.mailtrap.io")
    EMAIL_HOST_USER = settings.get("EMAIL_USER", settings.get("MAILTRAP_USER", ""))
    EMAIL_HOST_PASSWORD = settings.get("EMAIL_PASSWORD", settings.get("MAILTRAP_PASSWORD", ""))
    EMAIL_PORT = settings.get("MAILTRAP_PORT", 2525)
    EMAIL_USE_TLS = True

elif EMAIL_SENDING_STRATEGY in [
    EmailSendingStrategy.MAILPIT,
    EmailSendingStrategy.VIRTUAL,
]:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = settings.get("MAILPIT_HOST", "localhost")
    EMAIL_PORT = settings.get("MAILPIT_PORT", 1025)
    EMAIL_USE_TLS = False

elif EMAIL_SENDING_STRATEGY == EmailSendingStrategy.SENDGRID:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = settings.get("SENDGRID_HOST", "smtp.sendgrid.net")
    EMAIL_PORT = settings.get("SENDGRID_PORT", 587)
    EMAIL_HOST_USER = settings.get("EMAIL_USER", settings.get("SENDGRID_USER", "apikey"))
    EMAIL_HOST_PASSWORD = settings.get("EMAIL_PASSWORD", settings.get("SENDGRID_PASSWORD", ""))
    EMAIL_USE_TLS = True

elif EMAIL_SENDING_STRATEGY == EmailSendingStrategy.MAILGUN:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = settings.get("MAILGUN_HOST", "smtp.mailgun.org")
    EMAIL_PORT = settings.get("MAILGUN_PORT", 587)
    EMAIL_HOST_USER = settings.get("EMAIL_USER", settings.get("MAILGUN_USER", ""))
    EMAIL_HOST_PASSWORD = settings.get("EMAIL_PASSWORD", settings.get("MAILGUN_PASSWORD", ""))
    EMAIL_USE_TLS = True

elif EMAIL_SENDING_STRATEGY == EmailSendingStrategy.AWS_SES:
    EMAIL_BACKEND = "django_ses.SESBackend"
    AWS_SES_ACCESS_KEY_ID = settings.get(
        "AWS_ACCESS_KEY_ID", settings.get("AWS_SES_ACCESS_KEY_ID", "")
    )
    AWS_SES_SECRET_ACCESS_KEY = settings.get(
        "AWS_SECRET_ACCESS_KEY", settings.get("AWS_SES_SECRET_ACCESS_KEY", "")
    )
    AWS_SES_REGION_NAME = settings.get("AWS_SES_REGION_NAME", "us-east-1")
    AWS_SES_REGION_ENDPOINT = settings.get(
        "AWS_SES_REGION_ENDPOINT", f"email.{AWS_SES_REGION_NAME}.amazonaws.com"
    )

else:  # SMTP (default)
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = settings.get("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = settings.get("EMAIL_PORT", 587)
    EMAIL_HOST_USER = settings.get("EMAIL_USER", settings.get("EMAIL_USERNAME", ""))
    EMAIL_HOST_PASSWORD = settings.get("EMAIL_PASSWORD", settings.get("EMAIL_PASSWORD", ""))
    EMAIL_USE_TLS = settings.get("EMAIL_USE_TLS", True)
    EMAIL_USE_SSL = settings.get("EMAIL_USE_SSL", False)

# -------------------------------
# Email Content Configuration
# -------------------------------
EMAIL_SUBJECT_PREFIX = settings.get("EMAIL_SUBJECT_PREFIX", f"[{settings.MODULE}] ")
ACCOUNT_EMAIL_SUBJECT_PREFIX = EMAIL_SUBJECT_PREFIX

# Email addresses
DEFAULT_FROM_EMAIL = settings.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "noreply@example.com")
SERVER_EMAIL = settings.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)
EMAIL_FROM = settings.get("EMAIL_FROM", DEFAULT_FROM_EMAIL)

# Reply-to address
EMAIL_REPLY_TO = settings.get("EMAIL_REPLY_TO", None)

# -------------------------------
# Email Templates Configuration
# -------------------------------
EMAIL_TEMPLATES = {
    "WELCOME": "emails/welcome.html",
    "PASSWORD_RESET": "emails/password_reset.html",
    "VERIFICATION": "emails/verification.html",
    "NOTIFICATION": "emails/notification.html",
}

# -------------------------------
# Email Queue Configuration
# -------------------------------
EMAIL_QUEUE_ENABLED = settings.get("EMAIL_QUEUE_ENABLED", settings.is_production)
EMAIL_QUEUE_BATCH_SIZE = settings.get("EMAIL_QUEUE_BATCH_SIZE", 10)
EMAIL_QUEUE_MAX_RETRIES = settings.get("EMAIL_QUEUE_MAX_RETRIES", 3)
EMAIL_QUEUE_RETRY_DELAY = settings.get("EMAIL_QUEUE_RETRY_DELAY", 60)  # seconds

# -------------------------------
# Email Tracking Configuration
# -------------------------------
EMAIL_TRACKING = {
    "ENABLED": settings.get("EMAIL_TRACKING_ENABLED", settings.is_production),
    "OPEN_TRACKING": settings.get("EMAIL_OPEN_TRACKING", True),
    "CLICK_TRACKING": settings.get("EMAIL_CLICK_TRACKING", True),
    "UNSUBSCRIBE_LINK": settings.get("EMAIL_UNSUBSCRIBE_LINK", True),
}

# -------------------------------
# Email Rate Limiting
# -------------------------------
EMAIL_RATE_LIMIT = {
    "ENABLED": settings.get("EMAIL_RATE_LIMIT_ENABLED", settings.is_production),
    "REQUESTS_PER_HOUR": settings.get("EMAIL_RATE_LIMIT_REQUESTS", 100),
    "BURST_LIMIT": settings.get("EMAIL_RATE_LIMIT_BURST", 10),
}

# -------------------------------
# Email Validation
# -------------------------------
EMAIL_VALIDATION = {
    "ENABLED": settings.get("EMAIL_VALIDATION_ENABLED", True),
    "BLACKLIST": settings.get("EMAIL_BLACKLIST", []),
    "WHITELIST": settings.get("EMAIL_WHITELIST", []),
    "DOMAIN_BLACKLIST": settings.get("EMAIL_DOMAIN_BLACKLIST", []),
    "DOMAIN_WHITELIST": settings.get("EMAIL_DOMAIN_WHITELIST", []),
}

# -------------------------------
# Email Security
# -------------------------------
EMAIL_SECURITY = {
    "ENCRYPTION": settings.get("EMAIL_ENCRYPTION", "TLS"),
    "CERT_FILE": settings.get("EMAIL_CERT_FILE", None),
    "KEY_FILE": settings.get("EMAIL_KEY_FILE", None),
    "VERIFY_CERT": settings.get("EMAIL_VERIFY_CERT", True),
}

# -------------------------------
# Django-AnyMail Configuration
# -------------------------------
if EMAIL_SENDING_STRATEGY in [
    EmailSendingStrategy.SENDGRID,
    EmailSendingStrategy.MAILGUN,
    EmailSendingStrategy.AWS_SES,
]:
    INSTALLED_APPS.append("anymail")

    if EMAIL_SENDING_STRATEGY == EmailSendingStrategy.SENDGRID:
        ANYMAIL = {
            "SENDGRID_API_KEY": settings.get("EMAIL_PASSWORD", ""),
            "WEBHOOK_SECRET": settings.get("SENDGRID_WEBHOOK_SECRET", ""),
        }
        EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"

    elif EMAIL_SENDING_STRATEGY == EmailSendingStrategy.MAILGUN:
        ANYMAIL = {
            "MAILGUN_API_KEY": settings.get("EMAIL_PASSWORD", ""),
            "MAILGUN_SENDER_DOMAIN": settings.get("MAILGUN_DOMAIN", ""),
        }
        EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

    elif EMAIL_SENDING_STRATEGY == EmailSendingStrategy.AWS_SES:
        ANYMAIL = {
            "AMAZON_SES_CLIENT_PARAMS": {
                "aws_access_key_id": settings.get("AWS_ACCESS_KEY_ID", ""),
                "aws_secret_access_key": settings.get("AWS_SECRET_ACCESS_KEY", ""),
                "region_name": settings.get("AWS_SES_REGION_NAME", "us-east-1"),
            }
        }
