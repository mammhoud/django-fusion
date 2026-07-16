"""Compatibility imports for shared email background tasks."""

from www.worker.email import send_bulk_email_task, send_email_raw, send_email_task

__all__ = ["send_email_task", "send_bulk_email_task", "send_email_raw"]
