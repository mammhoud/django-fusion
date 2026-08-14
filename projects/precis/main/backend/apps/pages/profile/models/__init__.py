# Re-exports from canonical handlers/ location.
from apps.handlers.models.profiles.certificate import Certificate  # noqa: F401
from apps.handlers.models.profiles.message import Message  # noqa: F401
from apps.handlers.models.profiles.note import Note, SharedNote  # noqa: F401
from .privacy import PrivacyConsent, PrivacyPolicy, TermsConsent, TermsOfService

__all__ = [
    "Certificate",
    "Message",
    "Note",
    "SharedNote",
    "PrivacyConsent",
    "PrivacyPolicy",
    "TermsConsent",
    "TermsOfService",
]
