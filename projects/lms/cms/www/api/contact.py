"""
Contact API — form submission endpoint (bolt-pattern adapter).

Matches the RTK Query slice at: store/api/endpoints/contact.ts
"""

import json
import logging

from www.api.bolt_adapter import bolt_view, parse_body

logger = logging.getLogger(__name__)


@bolt_view
def contact_submit(request):
    """POST /api/contact/ — Submit a contact form inquiry."""
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    name = body.get("name", "").strip()
    email = body.get("email", "").strip()
    subject = body.get("subject", "").strip()
    message = body.get("message", "").strip()

    # Validation
    errors = {}
    if not name:
        errors["name"] = "Name is required"
    if not email:
        errors["email"] = "Email is required"
    elif "@" not in email:
        errors["email"] = "Invalid email address"
    if not subject:
        errors["subject"] = "Subject is required"
    if not message:
        errors["message"] = "Message is required"

    if errors:
        return {"status": "error", "errors": errors}, 400

    # Save the contact submission
    try:
        from plugins.accounts.models.forms.submission import FormSubmission
        submission = FormSubmission.objects.create(
            form_type="contact",
            data=json.dumps({
                "name": name, "email": email,
                "subject": subject, "message": message,
            }),
        )
        logger.info("Contact submission saved: %s", submission.id)
    except Exception:
        logger.info(
            "Contact form submission: name=%s, email=%s, subject=%s, message=%.100s",
            name, email, subject, message,
        )

    return {
        "status": "success",
        "message": "Thank you for your message. We'll get back to you soon.",
    }
