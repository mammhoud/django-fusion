"""django_rseal.pipelines.conf — compatibility shim."""
import enum


class EmailPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class EmailSendingStrategy(str, enum.Enum):
    SMTP = "smtp"
    ASYNC = "async"
    QUEUE = "queue"


class EmailStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class TemplateSource(str, enum.Enum):
    FILE = "file"
    DATABASE = "database"


class AppSettings:
    """Stub AppSettings."""
    pass


def get_email_strategy():
    return EmailSendingStrategy.SMTP


def get_invitation_model():
    return None


def create_invitation(*args, **kwargs):
    return None
