import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from django_rseal.content.models.newsletter import Campaign, Subscriber

logger = logging.getLogger(__name__)

def send_confirmation_email(subscriber_id: int) -> bool:
    """
    Send confirmation email to a new subscriber.
    """
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)

        if subscriber.status != "pending":
            logger.warning(f"Subscriber {subscriber_id} is not pending, skipping email")
            return False

        # Build confirmation URL
        confirm_url = f"{settings.SITE_URL}/newsletter/confirm/{subscriber.confirmation_token}/"

        # Render email
        context = {
            "subscriber": subscriber,
            "confirm_url": confirm_url,
        }

        html_content = render_to_string("newsletter/email/confirmation.html", context)

        # Send email
        email = EmailMessage(
            subject="Confirm your newsletter subscription",
            body=html_content,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            to=[subscriber.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)

        logger.info(f"Confirmation email sent to {subscriber.email}")
        return True

    except Subscriber.DoesNotExist:
        logger.error(f"Subscriber {subscriber_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")
        raise e

def send_campaign_email(campaign_id: int, subscriber_id: int) -> bool:
    """
    Send campaign email to a single subscriber.
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        subscriber = Subscriber.objects.get(id=subscriber_id)

        if not subscriber.is_active:
            logger.warning(f"Subscriber {subscriber_id} is not active, skipping")
            return False

        # Build unsubscribe URL
        unsubscribe_url = f"{settings.SITE_URL}/newsletter/unsubscribe/{subscriber.unsubscribe_token}/"

        # Render email
        context = {
            "campaign": campaign,
            "subscriber": subscriber,
            "unsubscribe_url": unsubscribe_url,
        }

        html_content = render_to_string("newsletter/email/campaign.html", context)

        # Send email
        email = EmailMessage(
            subject=campaign.subject,
            body=html_content,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            to=[subscriber.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)

        # Update campaign stats
        campaign.increment_sent()

        logger.info(f"Campaign email sent to {subscriber.email}")
        return True

    except (Campaign.DoesNotExist, Subscriber.DoesNotExist) as e:
        logger.error(f"Campaign or subscriber not found: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send campaign email: {e}")
        raise e

def send_campaign_to_all(campaign_id: int) -> dict:
    """
    Queue campaign emails to all active subscribers.
    """
    from django_rseal.services.jobs import dispatch_job

    try:
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.status not in ["scheduled", "draft"]:
            logger.warning(f"Campaign {campaign_id} cannot be sent (status: {campaign.status})")
            return {"queued": 0, "error": "Invalid campaign status"}

        # Mark as sending
        campaign.mark_sending()

        # Get all active subscribers
        subscribers = Subscriber.objects.filter(status="confirmed")
        queued = 0

        for subscriber in subscribers:
            dispatch_job(send_campaign_email, campaign_id, subscriber.id, queue_name="newsletter")
            queued += 1

        logger.info(f"Queued {queued} emails for campaign {campaign_id}")
        return {"queued": queued}

    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
        return {"queued": 0, "error": "Campaign not found"}
