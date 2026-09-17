"""Precis Landing email background tasks.

Uses ``@task`` from ``django_fusion.tasks`` for broker-agnostic enqueue.
Configure in settings.py::

    FUSION_TASKS = {
        "BACKEND": "django_fusion.tasks.backends.dramatiq.DramatiqBackend",
        "BROKER_URL": "redis://localhost:6379/1",
    }
"""

from __future__ import annotations

import logging

from django_fusion.tasks import task

logger = logging.getLogger(__name__)


@task(queue="email", max_retries=5, min_backoff=30_000)
def send_newsletter(campaign_id: int):
    """Send a newsletter campaign to all active subscribers.

    Fetches the campaign from the database, resolves its audience
    (NewsletterSubscriber with ``is_active=True``), and dispatches
    individual email messages through the configured email backend.

    ``campaign_id`` is the primary key of a NewsletterCampaign snippet
    (wagtail.contrib.settings or a shared snippet model).
    """
    try:
        from apps.pages.models import NewsletterSubscriber  # noqa: PLC0415
    except ImportError:
        logger.warning("NewsletterSubscriber model not available — skipping.")
        return

    # Resolve campaign (snippet or page)
    try:
        from wagtail.models import Page  # noqa: PLC0415
        campaign = Page.objects.filter(id=campaign_id).specific().first()
    except Exception:
        logger.exception("Could not resolve newsletter campaign %d", campaign_id)
        return

    if campaign is None:
        logger.warning("Newsletter campaign %d not found.", campaign_id)
        return

    subscribers = NewsletterSubscriber.objects.filter(is_active=True)
    subject = getattr(campaign, "subject", "Newsletter")
    body = getattr(campaign, "body", "")
    from_email = getattr(campaign, "from_email", None)

    count = 0
    for subscriber in subscribers.iterator():
        try:
            campaign.send_email(
                to=subscriber.email,
                subject=subject,
                body=body,
                from_email=from_email,
            )
            count += 1
        except Exception:
            logger.exception(
                "Failed to send newsletter to %s", subscriber.email
            )

    logger.info("Newsletter campaign %d sent to %d subscribers.", campaign_id, count)


@task(queue="email", max_retries=3)
def send_contact_form_notification(contact_id: int):
    """Notify site admins about a new contact-form submission.

    Fetches the FormSubmission record, composes an admin notification
    email, and sends it via the default email backend.
    """
    try:
        from wagtail.contrib.forms.models import FormSubmission  # noqa: PLC0415
        sub = FormSubmission.objects.select_related("page").filter(
            id=contact_id
        ).first()
    except ImportError:
        logger.warning("FormSubmission model not available — skipping.")
        return

    if sub is None:
        logger.warning("Contact submission %d not found.", contact_id)
        return

    from django.conf import settings
    from django.core.mail import send_mail

    page_title = getattr(sub.page, "title", "Contact Form")
    field_data = sub.get_data()

    send_mail(
        subject=f"New submission: {page_title}",
        message=(
            f"A new form submission was received on '{page_title}'.\n\n"
            + "\n".join(
                f"{key}: {value}" for key, value in field_data.items()
            )
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[
            addr.strip()
            for addr in settings.ADMINS or []
            if "@" in addr
        ],
        fail_silently=True,
    )


@task(queue="email", schedule="0 8 * * 1")
def send_weekly_site_stats():
    """Compile and email weekly site analytics to administrators.

    Runs every Monday at 08:00 UTC.  Gathers page views, new subscribers,
    form submissions, and any other relevant metrics from the past 7 days.
    """
    from datetime import timedelta

    from django.conf import settings
    from django.core.mail import send_mail
    from django.utils import timezone

    since = timezone.now() - timedelta(days=7)

    # Gather stats from the Wagtail page tree
    from wagtail.models import Page  # noqa: PLC0415

    new_pages = Page.objects.filter(live=True, first_published_at__gte=since).count()

    # Subscriber growth
    try:
        from apps.pages.models import NewsletterSubscriber  # noqa: PLC0415
        new_subscribers = NewsletterSubscriber.objects.filter(
            created_at__gte=since
        ).count()
    except ImportError:
        new_subscribers = 0

    # Form submissions
    try:
        from wagtail.contrib.forms.models import FormSubmission  # noqa: PLC0415
        new_submissions = FormSubmission.objects.filter(
            submit_time__gte=since
        ).count()
    except ImportError:
        new_submissions = 0

    body = (
        f"Weekly Site Stats\n"
        f"─────────────────\n"
        f"Period: {since.date()} → {timezone.now().date()}\n\n"
        f"New pages published: {new_pages}\n"
        f"New newsletter subscribers: {new_subscribers}\n"
        f"New form submissions: {new_submissions}\n"
    )

    admin_emails = [
        addr.strip()
        for name, addr in settings.ADMINS or []
        if "@" in addr
    ]
    if not admin_emails:
        logger.info("No admin recipients configured — skipping weekly stats email.")
        return

    send_mail(
        subject=f"Weekly Stats — {timezone.now().date()}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=admin_emails,
        fail_silently=True,
    )
