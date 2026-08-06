"""Bulk-export all newsletter subscribers to the configured provider.

Usage::

    python manage.py sync_newsletter_provider [--all]

Pushes every active subscriber to the provider named by ``NEWSLETTER_PROVIDER``
(Mailchimp / Brevo / webhook) — the same idempotent per-subscriber sync the
subscribe API performs, run over the whole list. ``--all`` also pushes paused
subscribers (as unsubscribed), for the rare full-list reconcile.

The SnippetViewSet's built-in CSV export covers the manual pull; this command
is the automated push.
"""

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Push newsletter subscribers to the configured provider (Mailchimp/Brevo/webhook)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all", action="store_true",
            help="Also push paused subscribers (as unsubscribed).",
        )

    def handle(self, *args, **options):
        from apps.content.models.newsletter import NewsletterSubscriber
        from apps.content.services.newsletter import sync_subscriber_to_provider

        provider = (getattr(settings, "NEWSLETTER_PROVIDER", "") or "").strip().lower()
        if not provider:
            self.stderr.write(self.style.WARNING(
                "No NEWSLETTER_PROVIDER configured — nothing to sync."
            ))
            return

        queryset = NewsletterSubscriber.objects.all() if options["all"] else (
            NewsletterSubscriber.objects.filter(is_active=True)
        )
        subscribers = list(queryset)
        if not subscribers:
            self.stdout.write("No subscribers to sync.")
            return

        synced = 0
        for subscriber in subscribers:
            if sync_subscriber_to_provider(subscriber):
                synced += 1
        self.stdout.write(self.style.SUCCESS(
            f"Synced {synced}/{len(subscribers)} subscribers to '{provider}'."
        ))
