"""Async email backend for django-fusion.

Usage in settings.py::

    EMAIL_BACKEND = "django_fusion.tasks.email_backend.AsyncEmailBackend"
"""

from __future__ import annotations

from django.core.mail.backends.base import BaseEmailBackend


class AsyncEmailBackend(BaseEmailBackend):
    """Email backend that enqueues all messages as background tasks.

    Requires ``django_fusion.tasks`` to be configured with a broker
    backend (Dramatiq, RQ, or in-process).

    Configure with::

        FUSION_EMAIL_TASK_QUEUE = "email"   # default
        FUSION_EMAIL_MAX_RETRIES = 5        # default
    """

    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        from django.conf import settings

        self.queue = getattr(settings, "FUSION_EMAIL_TASK_QUEUE", "email")
        self.max_retries = getattr(
            settings, "FUSION_EMAIL_MAX_RETRIES", 5
        )
        self.real_backend = getattr(
            settings,
            "FUSION_REAL_EMAIL_BACKEND",
            "django.core.mail.backends.smtp.EmailBackend",
        )

    def send_messages(self, email_messages):
        """Enqueue each message as a background task."""
        from django_fusion.tasks.decorators import task

        @task(
            queue=self.queue,
            max_retries=self.max_retries,
            actor_name="fusion.email.send",
        )
        def _send_email_task(subject, body, from_email, recipient_list, html_message=None):
            from django.core.mail import EmailMultiAlternatives
            from django.core.mail import get_connection
            from django.conf import settings

            connection = get_connection(
                backend=getattr(
                    settings,
                    "FUSION_REAL_EMAIL_BACKEND",
                    "django.core.mail.backends.smtp.EmailBackend",
                )
            )
            msg = EmailMultiAlternatives(
                subject=subject,
                body=body,
                from_email=from_email,
                to=recipient_list,
                connection=connection,
            )
            if html_message:
                for alt_content, alt_type in html_message:
                    msg.attach_alternative(alt_content, alt_type)
            msg.send()

        task_ids = []
        for message in email_messages:
            html_message = (
                getattr(message, "alternatives", None) or None
            )
            msg_id = _send_email_task.send(
                subject=message.subject,
                body=message.body,
                from_email=message.from_email,
                recipient_list=message.recipients(),
                html_message=html_message,
            )
            task_ids.append(msg_id)
        return len(task_ids)
