"""
Newsletter subscribers — managed as a Wagtail snippet.

Signups flow through ``POST /api/newsletter/subscribe/`` (see
``apps/pages/api.py``) which upserts rows here and fires the post-subscribe
side effects (branded welcome email + provider sync — see
``apps/content/services/newsletter.py``). The snippet list in the Wagtail
admin shows every subscriber with status, source and sync state so the team
can review, export (CSV), broadcast an email to everyone, or pause signups.
"""

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn, Column, DateColumn
from wagtail.admin.widgets.button import HeaderButton
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import IndexView, SnippetViewSet


class NewsletterSubscriber(models.Model):
    """A single email subscribed to the Structa Cloud newsletter."""

    email = models.EmailField(
        _("email"), unique=True, db_index=True,
        help_text=_("Subscribed email address (unique)."),
    )
    is_active = models.BooleanField(
        _("active"), default=True, db_index=True,
        help_text=_("Uncheck to pause this subscription (unsubscribe)."),
    )
    source = models.CharField(
        _("source"), max_length=40, blank=True, default="footer",
        choices=[
            ("footer", _("Footer signup")),
            ("contact", _("Contact form")),
            ("product", _("Product page")),
            ("other", _("Other")),
        ],
        help_text=_("Where this address subscribed from."),
    )
    welcome_sent_at = models.DateTimeField(
        _("welcome email sent"), null=True, blank=True, editable=False,
        help_text=_("When the branded welcome email was last sent. Unset if "
                    "the send failed or this address was imported."),
    )
    provider_synced_at = models.DateTimeField(
        _("provider synced"), null=True, blank=True, editable=False,
        help_text=_("When the row was last pushed to the configured email "
                    "provider (Mailchimp / Brevo / webhook). Unset when no "
                    "provider is configured or the sync failed."),
    )
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    panels = [
        MultiFieldPanel([
            FieldPanel("email"),
            FieldPanel("is_active"),
            FieldPanel("source"),
        ], heading=_("Subscriber")),
        MultiFieldPanel([
            FieldPanel("welcome_sent_at", read_only=True),
            FieldPanel("provider_synced_at", read_only=True),
            FieldPanel("created_at", read_only=True),
            FieldPanel("updated_at", read_only=True),
        ], heading=_("Delivery state")),
    ]

    class Meta:
        app_label = "content"
        verbose_name = _("newsletter subscriber")
        verbose_name_plural = _("newsletter subscribers")
        ordering = ["-created_at"]

    def __str__(self):
        status = "active" if self.is_active else "paused"
        return f"{self.email} ({status})"


class NewsletterSubscriberIndexView(IndexView):
    """Snippet index with an ``Email subscribers`` action in the header.

    Opens the broadcast page (/admin/newsletter/broadcast/) — a Wagtail
    admin view that batch-emails every active subscriber through the branded
    newsletter shell.
    """

    @cached_property
    def header_buttons(self):
        buttons = super().header_buttons
        buttons.append(HeaderButton(
            _("Email subscribers"),
            url=reverse("wagtailadmin_newsletter_broadcast"),
            icon_name="mail",
        ))
        return buttons


class NewsletterSubscriberViewSet(SnippetViewSet):
    """Wagtail snippet viewset — the admin home for the subscriber list.

    Converts the model from a bare ``@register_snippet`` into a full viewset:
    list columns, filters, search, the built-in CSV export (the team can pull
    a Mailchimp/Brevo-ready file without leaving the admin), and the header
    broadcast action.
    """

    model = NewsletterSubscriber
    menu_label = _("Newsletter subscribers")
    icon = "mail"
    add_to_admin_menu = True

    list_display = [
        Column("email", label=_("Email")),
        BooleanColumn("is_active", label=_("Active")),
        Column("source", label=_("Source")),
        DateColumn("created_at", label=_("Signed up"), sort_key="created_at"),
        DateColumn("welcome_sent_at", label=_("Welcome sent"), sort_key="welcome_sent_at"),
        DateColumn("provider_synced_at", label=_("Provider synced"), sort_key="provider_synced_at"),
    ]
    list_filter = ["is_active", "source"]
    search_fields = ["email"]
    index_view_class = NewsletterSubscriberIndexView

    # Built-in CSV export (list view → Export) — the same row set the
    # provider sync management command pushes via the API.
    list_export = [
        "email", "is_active", "source", "welcome_sent_at", "provider_synced_at", "created_at",
    ]
    export_headings = {
        "email": _("Email"),
        "is_active": _("Active"),
        "source": _("Source"),
        "welcome_sent_at": _("Welcome sent"),
        "provider_synced_at": _("Provider synced"),
        "created_at": _("Signed up"),
    }


register_snippet(NewsletterSubscriberViewSet)
