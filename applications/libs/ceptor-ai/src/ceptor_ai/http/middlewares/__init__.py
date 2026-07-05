# Re-export canonical middleware classes from django_fusion
from django_fusion.core.middlewares import (  # noqa: F401
    SiteMiddleware,
    ReadonlyExceptionHandlerMiddleware,
    DefaultLanguageMiddleware,
)
from .privacy_consent import PrivacyConsentMiddleware  # noqa: F401
