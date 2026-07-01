"""Service layer — domain service implementations across commerce, communication, content.

Sub-packages
------------
services.commerce           Certificate issuance, payment processing.
services.communication      Invitation service, message dispatch, newsletter delivery.
services.content            Form submission processing, full-text search service.
services.email              Email send service, queue manager, CSV parser, report gen.
  .email_service            EmailService, BulkEmailService — primary send interface.
  .queue_manager            Background queue management for bulk sends.
  .csv_parser               CSV address-list parser for bulk campaigns.
  .report_generator         Send-result report generation.
services.infrastructure     Base service class, job runner, token service.

Flat compat aliases (legacy ``services.email_service`` path still works)::

    from ceptor_ai.services.email_service import EmailService  # legacy
    from ceptor_ai.services.email.email_service import EmailService  # canonical

Usage::

    from ceptor_ai.services.email.email_service import EmailService, BulkEmailService
    from ceptor_ai.services.commerce.payments import PaymentService
    from ceptor_ai.services.infrastructure.base import BaseService
"""
from __future__ import annotations
import importlib
import sys

# Expose services.email sub-modules as flat attributes for legacy patch paths
# e.g.  patch('ceptor_ai.services.email_service.render_to_string')
for _sub in ("email_service", "queue_manager", "csv_parser", "report_generator"):
    _compat_name = f"{__name__}.{_sub}"
    _canonical_name = f"ceptor_ai.services.email.{_sub}"
    if _compat_name not in sys.modules:
        try:
            _mod = importlib.import_module(_canonical_name)
            sys.modules[_compat_name] = _mod
        except ImportError:
            pass
