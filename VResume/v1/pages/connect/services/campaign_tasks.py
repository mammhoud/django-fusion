"""
Campaign Celery Tasks — Periodic and scheduled campaign operations
"""
import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_scheduled_campaigns(self):
    """
    Periodic task: Process campaigns scheduled for sending.
    
    Runs every 5 minutes to check for campaigns with:
    - status = "scheduled"
    - scheduled_at <= now
    
    Then queues send_campaign_to_all for each campaign.
    """
    from pages.connect.models import Campaign
    from pages.connect.services.newsletter_tasks import send_campaign_to_all
    
    try:
        now = timezone.now()
        
        # Find all scheduled campaigns that are ready to send
        campaigns = Campaign.objects.filter(
            status="scheduled",
            scheduled_at__lte=now
        )
        
        processed = 0
        for campaign in campaigns:
            try:
                # Queue the campaign send task
                send_campaign_to_all.delay(campaign.id)
                processed += 1
                logger.info(f"Queued campaign {campaign.id} ({campaign.name}) for sending")
            except Exception as e:
                logger.error(f"Failed to queue campaign {campaign.id}: {e}")
                continue
        
        logger.info(f"process_scheduled_campaigns: processed {processed} campaigns")
        return {"processed": processed}
        
    except Exception as e:
        logger.error(f"process_scheduled_campaigns failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@shared_task(bind=True, max_retries=3)
def cleanup_old_campaigns(self, days_old=30):
    """
    Periodic task: Archive or delete old campaigns.
    
    Runs daily to clean up campaigns older than `days_old` days.
    By default, campaigns older than 30 days are archived (status="archived").
    
    Args:
        days_old: Number of days to consider a campaign "old" (default: 30)
    """
    from pages.connect.models import Campaign
    
    try:
        cutoff_date = timezone.now() - timedelta(days=days_old)
        
        # Find campaigns that are old and not already archived
        old_campaigns = Campaign.objects.filter(
            created_at__lt=cutoff_date,
            status__in=["sent", "failed", "paused"]
        )
        
        count = old_campaigns.count()
        
        if count > 0:
            # Archive old campaigns instead of deleting
            old_campaigns.update(status="archived")
            logger.info(f"cleanup_old_campaigns: archived {count} campaigns older than {days_old} days")
        else:
            logger.info(f"cleanup_old_campaigns: no campaigns to archive (older than {days_old} days)")
        
        return {"archived": count}
        
    except Exception as e:
        logger.error(f"cleanup_old_campaigns failed: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@shared_task(bind=True, max_retries=3)
def update_campaign_analytics(self, campaign_id):
    """
    Async task: Update campaign analytics (open rate, click rate, etc).
    
    Called after campaign is sent to aggregate metrics.
    """
    from pages.connect.models import Campaign, EmailDelivery
    
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        
        # Get delivery stats
        deliveries = EmailDelivery.objects.filter(campaign=campaign, sent_at__isnull=False)
        total_sent = deliveries.count()
        total_opened = deliveries.filter(opened_at__isnull=False).count()
        total_clicked = deliveries.filter(clicked_at__isnull=False).count()
        total_bounced = deliveries.filter(bounced_at__isnull=False).count()
        
        # Update campaign
        campaign.total_sent = total_sent
        campaign.total_opened = total_opened
        campaign.total_clicked = total_clicked
        campaign.total_bounced = total_bounced
        campaign.save(update_fields=[
            'total_sent', 'total_opened', 'total_clicked', 'total_bounced'
        ])
        
        logger.info(
            f"Updated analytics for campaign {campaign_id}: "
            f"sent={total_sent}, opened={total_opened}, clicked={total_clicked}"
        )
        
        return {
            "campaign_id": campaign_id,
            "total_sent": total_sent,
            "total_opened": total_opened,
            "total_clicked": total_clicked,
        }
        
    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
        return {"error": "Campaign not found"}
    except Exception as e:
        logger.error(f"update_campaign_analytics failed: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
