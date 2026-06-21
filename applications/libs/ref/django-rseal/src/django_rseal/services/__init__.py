"""
Services module for django-rseal.

Organized by use case into categories:
- email: Email automation services
- communication: User communication services
- commerce: Payment and certificate services
- content: Content search and form handling
- infrastructure: Core service infrastructure

Email Services:
- CSVParser, EmailRecord
- EmailService
- EmailQueueManager
- ReportGenerator

Communication Services:
- InvitationService
- MessageServiceBase
- send_confirmation_email

Commerce Services:
- CertificateServiceBase
- PayPalGateway, StripeGateway

Content Services:
- SearchService
- FormSubmissionService

Infrastructure Services:
- BaseService
- TokenService, TokenProtectedService
- dispatch_job

Generic services are imported from django_osoul.services:
- BaseService, ServiceRegistry, ModelService
- CRUDService, BatchCRUDService
- CartServiceBase, PersonServiceBase
"""

# Email services
# Generic services from osoul
from django_osoul.core.services import (
    BatchCRUDService,
    CartServiceBase,
    CRUDService,
    ModelService,
    PersonServiceBase,
    ServiceRegistry,
)

# Commerce services
from .commerce import (
    CertificateServiceBase,
    PayPalGateway,
    StripeGateway,
)

# Communication services
from .communication import (
    InvitationService,
    MessageServiceBase,
    send_confirmation_email,
)

# Content services
from .content import (
    FormSubmissionService,
    SearchService,
)
from .email import (
    CSVParser,
    EmailQueueManager,
    EmailRecord,
    EmailService,
    ReportGenerator,
)

# Infrastructure services
from .infrastructure import (
    BaseService,
    TokenProtectedService,
    TokenService,
    dispatch_job,
)

__all__ = [
    # Email services
    'CSVParser',
    'EmailRecord',
    'EmailService',
    'EmailQueueManager',
    'ReportGenerator',
    # Communication services
    'InvitationService',
    'MessageServiceBase',
    'send_confirmation_email',
    # Commerce services
    "CertificateServiceBase",
    "PayPalGateway",
    "StripeGateway",
    # Content services
    "FormSubmissionService",
    "SearchService",
    # Infrastructure services
    "BaseService",
    "dispatch_job",
    "TokenService",
    "TokenProtectedService",
    # Generic (from osoul)
    "ServiceRegistry",
    "ModelService",
    "CRUDService",
    "BatchCRUDService",
    "CartServiceBase",
    "PersonServiceBase",
]
