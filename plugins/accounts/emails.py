"""
Email Service for Registration
================================
Sends branded HTML confirmation emails with password creation link.
Supports failover between multiple Gmail SMTP senders.

Site-specific values are read from Django settings:
    SITE_NAME              — display name used in email subjects/bodies
    DEFAULT_FROM_EMAIL     — fallback sender address
    WAGTAILADMIN_BASE_URL  — fallback site URL for links
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger("apps.registration")


def _site_name() -> str:
    """Return the site display name from settings, with a safe fallback."""
    return getattr(settings, "SITE_NAME", None) or getattr(settings, "WAGTAIL_SITE_NAME", "Platform")


def _default_from_email() -> str:
    """Return the default from-email from settings."""
    return getattr(settings, "DEFAULT_FROM_EMAIL", "support@example.com")


def _site_url() -> str:
    """Return the base site URL from settings."""
    url = (
        getattr(settings, "SITE_URL", None)
        or getattr(settings, "WAGTAILADMIN_BASE_URL", None)
        or ""
    )
    return url.rstrip("/")


def _get_sender_accounts():
    """
    Build sender accounts list dynamically from environment variables.
    Discovers EMAIL_SENDER_1, EMAIL_SENDER_2, ... until no more are found.
    """
    import os

    accounts = []
    n = 1
    while True:
        email = os.environ.get(f"EMAIL_SENDER_{n}")
        if not email:
            break
        password = os.environ.get(f"EMAIL_SENDER_{n}_PASSWORD", "")
        if email and password:
            accounts.append({"email": email, "password": password, "name": _site_name()})
        n += 1

    return accounts


def _resolve_template(template_type: str, fallback_template: str, context: dict):
    """
    Query AuthEmailTemplate for an active snippet of the given type.
    Falls back to the file-based template if none is found or on DB error.
    Returns (subject, html_content, text_content).
    """
    try:
        from .models.snippets import AuthEmailTemplate
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
    subject = context.get("subject", _site_name())
    return subject, html_content, text_content


def send_registration_email(user, confirmation_url: str) -> bool:
    """
    Send registration confirmation email with password creation link.
    Implements failover: tries configured senders, then Django backend.
    """
    site_name = _site_name()
    subject = f"Welcome to {site_name} — Create Your Password"

    full_name = getattr(user, "first_name", "") or ""
    if hasattr(user, "last_name") and user.last_name:
        full_name = f"{full_name} {user.last_name}".strip()
    if not full_name:
        full_name = user.email.split("@")[0].title()

    context = {
        "user_name": full_name,
        "user_email": user.email,
        "confirmation_url": confirmation_url,
        "site_name": site_name,
        "site_url": _site_url(),
        "expiration_hours": 24,
        "support_email": _default_from_email(),
    }

    try:
        html_content = render_to_string("registration/emails/confirmation.html", context)
        text_content = strip_tags(html_content)
    except Exception as e:
        logger.error(f"Failed to render email template: {e}")
        html_content = _get_fallback_html(context)
        text_content = strip_tags(html_content)

    sender_accounts = _get_sender_accounts()

    if not sender_accounts:
        logger.warning("No sender accounts configured, using Django default email backend")
        return _send_with_django_backend(subject, text_content, html_content, user.email)

    for i, account in enumerate(sender_accounts):
        try:
            logger.info(
                f"Attempting to send registration email to {user.email} "
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
                logger.info(f"Registration email sent to {user.email} via sender {i + 1}")
                return True
        except Exception as e:
            logger.error(f"Failed to send to {user.email} via sender {i + 1}: {e}")
            continue

    logger.warning("All sender accounts failed, trying Django default backend")
    return _send_with_django_backend(subject, text_content, html_content, user.email)


def send_signin_success_email(user) -> bool:
    """
    Send a "sign-in success" email after the user's first login.
    Uses the AuthEmailTemplate snippet if active, otherwise falls back to file template.
    """
    site_name = _site_name()

    full_name = getattr(user, "first_name", "") or ""
    if hasattr(user, "last_name") and user.last_name:
        full_name = f"{full_name} {user.last_name}".strip()
    if not full_name:
        full_name = user.email.split("@")[0].title()

    context = {
        "user_name": full_name,
        "user_email": user.email,
        "site_name": site_name,
        "site_url": _site_url(),
        "subject": f"Welcome to {site_name} — Your Account is Active",
        "support_email": _default_from_email(),
    }

    subject, html_content, text_content = _resolve_template(
        template_type="signin_success",
        fallback_template="registration/emails/signin_success.html",
        context=context,
    )

    logger.info(f"Sending sign-in success email to {user.email}")

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
                    logger.info(f"Sign-in success email sent to {user.email} via sender {i + 1}")
                    result = True
                    break
            except Exception as e:
                logger.error(
                    f"Failed to send sign-in success email to {user.email} "
                    f"via sender {i + 1}: {e}"
                )
                continue
        if not result:
            logger.warning("All senders failed for sign-in success email, trying Django backend")
            result = _send_with_django_backend(subject, text_content, html_content, user.email)

    if not result:
        logger.error(f"Sign-in success email delivery failed for user_id={user.pk}")
    return result


def _get_fallback_html(context: dict) -> str:
    """Fallback inline HTML template if file template fails to load."""
    confirmation_url = context.get("confirmation_url", "#")
    return (
        "<!DOCTYPE html><html><body>"
        f'<h1>Welcome to {context["site_name"]}!</h1>'
        f'<p>Hello {context["user_name"]},</p>'
        "<p>Please click the link below to create your password.</p>"
        f'<p><a href="{confirmation_url}">Create Your Password</a></p>'
        f'<p>This link expires in {context.get("expiration_hours", 24)} hours.</p>'
        "</body></html>"
    )


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
        from_email = _default_from_email()
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
