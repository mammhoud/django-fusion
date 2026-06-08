#!/usr/bin/env python3
"""Send an invitation email to a user.

Usage:
    python send_invite.py --email <address>

The script boots the Django environment using the project's settings and sends an email
using Django's email utilities. In development the email backend is typically set to
`django.core.mail.backends.console.EmailBackend`, so the email will appear in the
container's stdout.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def bootstrap_workspace() -> Path:
    """Prepare sys.path and environment for Django utilities.

    This mirrors the logic used in other utility scripts in the repository.
    """
    repo_root = Path(__file__).resolve().parents[4]
    os.chdir(repo_root)
    # Ensure the repository root is first in sys.path
    repo_str = str(repo_root)
    if repo_str in sys.path:
        sys.path.remove(repo_str)
    sys.path.insert(0, repo_str)
    return repo_root


def send_invite(email: str) -> None:
    """Send a simple invitation email.

    The function relies on Django's email configuration. In production you would
    configure `EMAIL_HOST`, `EMAIL_HOST_USER`, etc. For the current development
    setup the console backend is used, which prints the email to stdout.
    """
    from django.core.mail import send_mail
    from django.conf import settings

    # Ensure Django settings are configured – already done by bootstrap_workspace
    subject = "You’re invited to join CTC Research"
    message = (
        "Hello,\n\n"
        "You have been invited to join the CTC Research platform. "
        "Please follow the link below to complete your registration:\n"
        "https://ctc-research.com/register/\n\n"
        "If you did not expect this email, you can safely ignore it.\n\n"
        "Best regards,\nCTC Research Team"
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@ctc-research.com")
    send_mail(subject, message, from_email, [email])
    print(f"✅ Invitation email sent to {email}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True, help="Recipient email address")
    args = parser.parse_args()

    bootstrap_workspace()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    import django

    django.setup()
    send_invite(args.email)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
