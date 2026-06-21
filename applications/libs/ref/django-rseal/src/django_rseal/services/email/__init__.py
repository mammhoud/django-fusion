"""
Email services for django_rseal.

Handles email automation, queue management, CSV parsing, and report generation.

Modules:
- email_service: Core email sending service
- queue_manager: Email queue management
- csv_parser: CSV parsing for bulk email operations
- report_generator: Email report generation
"""

from .csv_parser import CSVParser, EmailRecord
from .email_service import EmailService
from .queue_manager import EmailQueueManager
from .report_generator import ReportGenerator

__all__ = [
    "CSVParser",
    "EmailRecord",
    "EmailService",
    "EmailQueueManager",
    "ReportGenerator",
]
