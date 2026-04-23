"""
Email Service for Registration
================================
Sends branded HTML confirmation emails with password creation link.
Supports failover between multiple Gmail SMTP senders.
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("apps.registration")


def _get_sender_accounts():
    """
    Build sender accounts list dynamically from environment variables.
    Discovers EMAIL_SENDER_1, EMAIL_SENDER_2, EMAIL_SENDER_3, ... until
    no more are found. Each sender requires EMAIL_SENDER_N and
    EMAIL_SENDER_N_PASSWORD to be set.

    Defaults:
        EMAIL_SENDER_1 = e.babiker55@gmail.com
        EMAIL_SENDER_2 = yasirzaroug8@gmail.com (falls back to EMAIL_USER)
        EMAIL_SENDER_3 = dranas352002@gmail.com
    """
    import os

    _defaults = {
        1: ("e.babiker55@gmail.com", "EMAIL_SENDER_1_PASSWORD"),
        2: (os.environ.get("EMAIL_USER", "yasirzaroug8@gmail.com"), "EMAIL_SENDER_2_PASSWORD"),
        3: ("dranas352002@gmail.com", "EMAIL_SENDER_3_PASSWORD"),
    }

    accounts = []
    n = 1
    while True:
        default_email, default_pw_key = _defaults.get(n, (None, None))
        email = os.environ.get(f"EMAIL_SENDER_{n}", default_email)
        if not email:
            break
        password = os.environ.get(
            f"EMAIL_SENDER_{n}_PASSWORD",
            os.environ.get(default_pw_key, "") if default_pw_key else "",
        )
        # For sender 2, also accept legacy EMAIL_PASSWORD
        if n == 2 and not password:
            password = os.environ.get("EMAIL_PASSWORD", "")
        if email and password:
            accounts.append({"email": email, "password": password, "name": "CTC Research"})
        n += 1
        # Stop after checking beyond the last known default if no env var found
        if n > 3 and not os.environ.get(f"EMAIL_SENDER_{n}"):
            break

    return accounts


def _get_fallback_html(context: dict) -> str:
    """Fallback inline HTML template if file template fails to load."""
    confirmation_url = context.get("confirmation_url", "#")
    unsubscribe_url = context.get("unsubscribe_url", "#")
    return (
        "<!DOCTYPE html>"
        "<html>"
        '<body style="font-family: Arial, sans-serif; background: #f4f4f4; padding: 20px;">'
        '<div style="max-width: 600px; margin: auto; background: white; border-radius: 12px; padding: 40px;">'
        f'<h1 style="color: #1a1a2e;">Welcome to {context["site_name"]}!</h1>'
        f'<p>Hello {context["user_name"]},</p>'
        "<p>Your account has been created. Please click the button below to create your password"
        " and activate your account.</p>"
        '<p style="text-align: center; margin: 30px 0;">'
        f'<a href="{confirmation_url}"'
        ' style="background: #6C63FF; color: white; padding: 14px 32px;'
        ' text-decoration: none; font-weight: bold;">'
        "Create Your Password"
        "</a>"
        "</p>"
        f'<p style="font-size: 13px; color: #666;">'
        f'This link will expire in {context.get("expiration_hours", 24)} hours.'
        "</p>"
        f'<p style="font-size: 13px; color: #666;">'
        f"If the button doesn't work, copy and paste this link:<br>"
        f'<a href="{confirmation_url}">{confirmation_url}</a>'
        "</p>"
        '<hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">'
        f'<p style="font-size: 12px; color: #999; text-align: center;">'
        f'&copy; {context["site_name"]} | Need help? Contact {context.get("support_email", "")}'
        "</p>"
        f'<p style="font-size: 11px; color: #bbb; text-align: center; margin-top: 8px;">'
        f'<a href="{unsubscribe_url}" style="color: #bbb;">Unsubscribe</a>'
        "</p>"
        "</div>"
        "</body>"
        "</html>"
    )


def send_registration_email(user, confirmation_url: str) -> bool:
    """
    Send registration confirmation email with password creation link.
    Implements failover: tries primary sender, then secondary.

    Args:
        user: Django User instance
        confirmation_url: Full URL to the password creation page

    Returns:
        True if email was sent successfully, False otherwise
    """
    subject = "Welcome to CTC Research — Create Your Password"

    # Get the user's display name
    full_name = getattr(user, 'first_name', '') or ''
    if hasattr(user, 'last_name') and user.last_name:
        full_name = f"{full_name} {user.last_name}".strip()
    if not full_name:
        full_name = user.email.split("@")[0].title()

    # Render HTML email
    context = {
        "user_name": full_name,
        "user_email": user.email,
        "confirmation_url": confirmation_url,
        "site_name": "CTC Research",
        "site_url": getattr(settings, 'WAGTAILADMIN_BASE_URL', 'https://structa.cloud'),
        "expiration_hours": 24,
        "support_email": getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@structa.cloud'),
    }

    try:
        html_content = render_to_string("registration/emails/confirmation.html", context)
        text_content = strip_tags(html_content)
    except Exception as e:
        logger.error(f"Failed to render email template: {e}")
        # Fallback to inline template
        html_content = _get_fallback_html(context)
        text_content = strip_tags(html_content)

    # Try sending with failover
    sender_accounts = _get_sender_accounts()

    if not sender_accounts:
        # Fall back to Django's built-in email
        logger.warning("No sender accounts configured, using Django default email backend")
        return _send_with_django_backend(subject, text_content, html_content, user.email)

    for i, account in enumerate(sender_accounts):
        attempt_ts = datetime.utcnow().isoformat()
        try:
            logger.info(
                f"[{attempt_ts}] Attempting to send registration email to {user.email} "
                f"via sender {i + 1} ({account['email']})"
            )
            success = _send_via_smtp(
                sender_email=account["email"],
                sender_password=account["password"],
                sender_name=account["name"],
                recipient_email=user.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )
            if success:
                success_ts = datetime.utcnow().isoformat()
                logger.info(
                    f"[{success_ts}] Registration email sent successfully to {user.email} "
                    f"via sender {i + 1} ({account['email']})"
                )
                return True
        except Exception as e:
            fail_ts = datetime.utcnow().isoformat()
            logger.error(
                f"[{fail_ts}] Failed to send to {user.email} "
                f"via sender {i + 1} ({account['email']}): {e}"
            )
            continue

    # Final fallback: try Django's default email backend
    logger.warning("All sender accounts failed, trying Django default backend")
    return _send_with_django_backend(subject, text_content, html_content, user.email)


def _send_via_smtp(
    sender_email: str,
    sender_password: str,
    sender_name: str,
    recipient_email: str,
    subject: str,
    html_content: str,
    text_content: str,
) -> bool:
    """Send email directly via Gmail SMTP with TLS."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email

    msg.attach(MIMEText(text_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed for {sender_email}: {e}")
        raise
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error for {sender_email}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending via {sender_email}: {e}")
        raise


def _send_with_django_backend(
    subject: str, text_content: str, html_content: str, recipient_email: str
) -> bool:
    """Fallback: send email using Django's configured email backend."""
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@structa.cloud')
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=[recipient_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        logger.info(f"Email sent via Django backend to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"Django email backend failed: {e}")
        return False


def _resolve_template(template_type: str, fallback_template: str, context: dict):
    """
    Query AuthEmailTemplate for an active snippet of the given type.
    Falls back to the file-based template if none is found.
    Returns (subject, html_content, text_content).
    """
    try:
        from .models import AuthEmailTemplate
        snippet = AuthEmailTemplate.objects.filter(
            template_type=template_type, is_active=True
        ).first()
        if snippet:
            from django.template import Context, Template
            from django.utils.html import strip_tags as _strip_tags
            html_content = Template(snippet.body_html).render(Context(context))
            text_content = snippet.body_text or _strip_tags(html_content)
            return snippet.subject, html_content, text_content
    except Exception as exc:
        logger.warning(f"Could not load AuthEmailTemplate for {template_type}: {exc}")

    # Fallback to file template
    from django.template.loader import render_to_string as _render_to_string
    from django.utils.html import strip_tags as _strip_tags
    html_content = _render_to_string(fallback_template, context)
    text_content = _strip_tags(html_content)
    subject = context.get("subject", "CTC Research")
    return subject, html_content, text_content


def send_signin_success_email(user) -> bool:
    """
    Send a "sign-in success" email after the user's first login.
    Uses the AuthEmailTemplate snippet if an active one exists for
    template_type='signin_success', otherwise falls back to the
    file-based template.
    """
    full_name = getattr(user, 'first_name', '') or ''
    if hasattr(user, 'last_name') and user.last_name:
        full_name = f"{full_name} {user.last_name}".strip()
    if not full_name:
        full_name = user.email.split("@")[0].title()

    context = {
        "user_name": full_name,
        "user_email": user.email,
        "site_name": "CTC Research",
        "site_url": getattr(settings, 'WAGTAILADMIN_BASE_URL', 'https://structa.cloud'),
        "subject": "Welcome to CTC Research — Your Account is Active",
        "support_email": getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@structa.cloud'),
    }

    subject, html_content, text_content = _resolve_template(
        template_type="signin_success",
        fallback_template="registration/emails/signin_success.html",
        context=context,
    )

    attempt_ts = datetime.utcnow().isoformat()
    logger.info(f"[{attempt_ts}] Sending sign-in success email to {user.email}")

    sender_accounts = _get_sender_accounts()
    if not sender_accounts:
        logger.warning("No sender accounts configured, using Django default email backend")
        result = _send_with_django_backend(subject, text_content, html_content, user.email)
    else:
        result = False
        for i, account in enumerate(sender_accounts):
            try:
                success = _send_via_smtp(
                    sender_email=account["email"],
                    sender_password=account["password"],
                    sender_name=account["name"],
                    recipient_email=user.email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                )
                if success:
                    success_ts = datetime.utcnow().isoformat()
                    logger.info(
                        f"[{success_ts}] Sign-in success email sent to {user.email} "
                        f"via sender {i + 1} ({account['email']})"
                    )
                    result = True
                    break
            except Exception as e:
                fail_ts = datetime.utcnow().isoformat()
                logger.error(
                    f"[{fail_ts}] Failed to send sign-in success email to {user.email} "
                    f"via sender {i + 1}: {e}"
                )
                continue
        if not result:
            logger.warning("All senders failed for sign-in success email, trying Django backend")
            result = _send_with_django_backend(subject, text_content, html_content, user.email)

    if not result:
        logger.error(f"Sign-in success email delivery failed for user_id={user.pk}")
    return result
