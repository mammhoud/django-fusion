"""
Newsletter Celery Tasks moved to Connect app
"""
import logging
import secrets

from bs4 import BeautifulSoup
from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


def _wrap_links_with_tracking(html_content: str, tracking_token: str) -> str:
    """
    Wrap all links in HTML with click-tracking redirect.
    """
    from pages.connect.models import TrackedURL

    soup = BeautifulSoup(html_content, "html.parser")

    # Find all links
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and href.startswith(("http://", "https://")):
            # Create or get tracked URL
            tracked_url, _ = TrackedURL.objects.get_or_create(
                url=href,
                defaults={"url_hash": TrackedURL.generate_hash(href)},
            )

            # Build tracking redirect URL
            track_url = f"{settings.SITE_URL}/newsletter/track/click/{tracking_token}/{tracked_url.url_hash}/"
            link["href"] = track_url

    return str(soup)


def _embed_tracking_pixel(html_content: str, tracking_token: str) -> str:
    """
    Embed tracking pixel in email HTML.
    """
    pixel_url = f"{settings.SITE_URL}/newsletter/track/open/{tracking_token}/"
    pixel_html = f'<img src="{pixel_url}" width="1" height="1" alt="" style="display: none;" />'

    # Insert pixel before closing body tag if present, otherwise at end
    if "</body>" in html_content:
        html_content = html_content.replace("</body>", f"{pixel_html}</body>")
    else:
        html_content += pixel_html

    return html_content


@shared_task(bind=True, max_retries=5)
def send_confirmation_email(self, subscriber_id: int) -> bool:
    """
    Send confirmation email to a new subscriber with tracking.
    """
    from pages.connect.models import EmailDelivery, Subscriber

    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)

        if subscriber.status != "pending":
            logger.warning(f"Subscriber {subscriber_id} is not pending, skipping email")
            return False

        # Create EmailDelivery record for confirmation email
        delivery, _ = EmailDelivery.objects.get_or_create(
            campaign=None,
            subscriber=subscriber,
            defaults={"tracking_token": secrets.token_urlsafe(32)},
        )

        # Build confirmation URL
        confirm_url = f"{settings.SITE_URL}/newsletter/confirm/{subscriber.confirmation_token}/"

        # Render email
        context = {
            "subscriber": subscriber,
            "confirm_url": confirm_url,
        }

        html_content = render_to_string("connect/newsletter/email/confirmation.html", context)

        # Embed tracking pixel
        html_content = _embed_tracking_pixel(html_content, delivery.tracking_token)

        # Send email
        email = EmailMessage(
            subject="Confirm your newsletter subscription",
            body=html_content,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            to=[subscriber.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)

        # Mark as sent
        delivery.sent_at = timezone.now()
        delivery.save(update_fields=["sent_at"])

        logger.info(f"Confirmation email sent to {subscriber.email}")
        return True

    except Subscriber.DoesNotExist:
        logger.error(f"Subscriber {subscriber_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to send confirmation email: {e}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@shared_task(bind=True, max_retries=5)
def send_campaign_email(self, campaign_id: int, subscriber_id: int) -> bool:
    """
    Send campaign email to a single subscriber with tracking.
    """
    from pages.connect.models import Campaign, EmailDelivery, Subscriber

    try:
        campaign = Campaign.objects.get(id=campaign_id)
        subscriber = Subscriber.objects.get(id=subscriber_id)

        if not subscriber.is_active:
            logger.warning(f"Subscriber {subscriber_id} is not active, skipping")
            return False

        # Create EmailDelivery record before sending
        delivery, _ = EmailDelivery.objects.get_or_create(
            campaign=campaign,
            subscriber=subscriber,
            defaults={"tracking_token": secrets.token_urlsafe(32)},
        )

        # Build unsubscribe URL
        unsubscribe_url = f"{settings.SITE_URL}/newsletter/unsubscribe/{subscriber.unsubscribe_token}/"

        # Render email
        context = {
            "campaign": campaign,
            "subscriber": subscriber,
            "unsubscribe_url": unsubscribe_url,
        }

        html_content = render_to_string("connect/newsletter/email/campaign.html", context)

        # Wrap links with click-tracking redirect
        html_content = _wrap_links_with_tracking(html_content, delivery.tracking_token)

        # Embed tracking pixel in email HTML
        html_content = _embed_tracking_pixel(html_content, delivery.tracking_token)

        # Send email
        email = EmailMessage(
            subject=campaign.subject,
            body=html_content,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            to=[subscriber.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)

        # Set delivery.sent_at after successful send
        delivery.sent_at = timezone.now()
        delivery.save(update_fields=["sent_at"])

        logger.info(f"Campaign email sent to {subscriber.email}")
        return True

    except (Campaign.DoesNotExist, Subscriber.DoesNotExist) as e:
        logger.error(f"Campaign or subscriber not found: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send campaign email: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


@shared_task
def send_campaign_to_all(campaign_id: int) -> dict:
    """
    Queue campaign emails to all active subscribers.
    """
    from pages.connect.models import Campaign, Subscriber

    try:
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.status not in ["scheduled", "draft"]:
            logger.warning(f"Campaign {campaign_id} cannot be sent (status: {campaign.status})")
            return {"queued": 0, "error": "Invalid campaign status"}

        # Mark campaign as sending before queuing
        campaign.mark_sending()

        # Get all active subscribers
        subscribers = Subscriber.objects.filter(status="confirmed")
        queued = 0

        for subscriber in subscribers:
            send_campaign_email.delay(campaign_id, subscriber.id)
            queued += 1

        # Mark campaign as sent after all tasks queued
        campaign.mark_sent()

        logger.info(f"Queued {queued} emails for campaign {campaign_id}")
        return {"queued": queued}

    except Campaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found")
        return {"queued": 0, "error": "Campaign not found"}

@shared_task
def trigger_blog_newsletter(blog_page_id: int):
    """
    Generate and send a newsletter campaign for a newly published blog post.
    """
    from wagtail.models import Site

    from pages.blog.models import BlogPage
    from pages.connect.models import Campaign
    from pages.home.models import VResumeSettings

    try:
        post = BlogPage.objects.get(pk=blog_page_id)
        site = Site.objects.first()
        site_settings = VResumeSettings.for_site(site) if site else None
        author_name = site_settings.full_name if site_settings else "VResume"

        # Extract an image URL
        image_url = ""
        if post.featured_image:
            base = getattr(settings, "SITE_URL", "")
            image_url = f"{base}{post.featured_image.file.url}"

        post_url = post.full_url or f"/blog/{post.slug}/"

        html_body = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <h2 style="color: #004250;">New Blog Post Published!</h2>
            <p>Hi there,</p>
            <p>I just published a new article that you might find interesting:</p>

            <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0; color: #d98c00;">{post.title}</h3>
                {f'<img src="{image_url}" alt="{post.title}" style="max-width: 100%; border-radius: 4px; margin-bottom: 15px;" />' if image_url else ''}
                <p style="color: #666; font-size: 14px;">
                    {post.introduction or post.short_description}
                </p>
                <a href="{post_url}" style="display: inline-block; background: #004250; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 4px; font-weight: bold;">
                    Read Full Article
                </a>
            </div>

            <p>Thanks for subscribing!</p>
            <p>Best regards,<br>{author_name}</p>
        </div>
        """

        campaign = Campaign.objects.create(
            name=f"Auto-Newsletter: {post.title[:50]}",
            subject=f"New Post: {post.title}",
            preview_text=post.introduction[:250] if post.introduction else "Read my latest blog post.",
            body=html_body,
            blog_post=post,
            status="draft"
        )

        # Link all active subscribers
        from pages.connect.models import Subscriber
        active_subs = Subscriber.objects.filter(status="confirmed")
        campaign.subscribers.set(active_subs)

        # Trigger sending
        send_campaign_to_all.delay(campaign.id)
        return {"campaign_id": campaign.id, "status": "queued"}

    except Exception as e:
        logger.error(f"Failed to trigger blog newsletter for page {blog_page_id}: {e}")
        return {"error": str(e)}

@shared_task
def trigger_project_newsletter(project_id: int):
    """
    Generate and send a newsletter campaign for a newly published portfolio project.
    """
    from wagtail.models import Site

    from pages.connect.models import Campaign
    from pages.home.models import VResumeSettings
    from pages.portfolio.models.snippets import Project

    try:
        project = Project.objects.get(pk=project_id)
        site = Site.objects.first()
        site_settings = VResumeSettings.for_site(site) if site else None
        author_name = site_settings.full_name if site_settings else "VResume"

        image_url = ""
        if project.image:
            base = getattr(settings, "SITE_URL", "")
            image_url = f"{base}{project.image.file.url}"

        # Since project is a snippet, we assume there's a generic portfolio link or an anchor
        project_url = f"/portfolio/#project-{project.slug}"

        html_body = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto; color: #333;">
            <h2 style="color: #087e81;">New Portfolio Project Added!</h2>
            <p>Hi there,</p>
            <p>I just added a new project to my portfolio. Check it out:</p>

            <div style="background: #f0f8fa; padding: 20px; border-radius: 8px; margin: 20px 0; border: 1px solid #cde4ec;">
                <h3 style="margin-top: 0; color: #004250;">{project.title}</h3>
                <p style="color: #087e81; font-size: 12px; text-transform: uppercase; font-weight: bold; margin-bottom: 15px;">
                    {project.category}
                </p>
                {f'<img src="{image_url}" alt="{project.title}" style="max-width: 100%; border-radius: 4px; margin-bottom: 15px;" />' if image_url else ''}
                <p style="color: #164152; font-size: 14px;">
                    {project.description}
                </p>
                <a href="{project_url}" style="display: inline-block; background: #d98c00; color: #fff; text-decoration: none; padding: 10px 20px; border-radius: 4px; font-weight: bold;">
                    View Project Details
                </a>
            </div>

            <p>Thanks for subscribing and following my work!</p>
            <p>Best regards,<br>{author_name}</p>
        </div>
        """

        campaign = Campaign.objects.create(
            name=f"Auto-Newsletter: {project.title[:50]}",
            subject=f"New Project: {project.title}",
            preview_text=project.description[:250],
            body=html_body,
            status="draft"
        )

        # Link all active subscribers
        from pages.connect.models import Subscriber
        active_subs = Subscriber.objects.filter(status="confirmed")
        campaign.subscribers.set(active_subs)

        # Trigger sending
        send_campaign_to_all.delay(campaign.id)
        return {"campaign_id": campaign.id, "status": "queued"}

    except Exception as e:
        logger.error(f"Failed to trigger project newsletter for project {project_id}: {e}")
        return {"error": str(e)}
