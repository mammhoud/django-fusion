# Shim: re-export from django_osoul.middlewares
from django_osoul.core.middlewares import (  # noqa: F401
    SiteMiddleware,
    ReadonlyExceptionHandlerMiddleware,
    DefaultLanguageMiddleware,
)
from .privacy_consent import PrivacyConsentMiddleware  # noqa: F401
