from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django_filters import BooleanFilter, CharFilter, ChoiceFilter
from crafts_ai.rseal.models import Newsletter
from wagtail.admin.filters import WagtailFilterSet

from ..base import BaseSnippetViewSet

# =============================================================================
# FILTERSET
# =============================================================================

class NewsletterFilterSet(WagtailFilterSet):
    """
    Advanced filtering for the Newsletter model.
    """

    title = CharFilter(
        field_name='title',
        lookup_expr='icontains',
        label=_('Title contains')
    )
    audience_type = ChoiceFilter(
        field_name='audience_type',
        choices=Newsletter.AUDIENCE_CHOICES,
        label=_('Audience Type')
    )
    is_sent = BooleanFilter(
        method='filter_is_sent',
        label=_('Has been sent')
    )

    class Meta:
        model = Newsletter
        fields = {
            "live": ["exact"],
            "audience_type": ["exact"],
            "important_announcement": ["exact"],
        }

    def filter_is_sent(self, queryset, name, value):
        """Filter newsletters that have or haven't been sent."""
        if value:
            return queryset.filter(sent_date__isnull=False)
        return queryset.filter(sent_date__isnull=True)


# =============================================================================
# NEWSLETTER SNIPPET VIEWSET
# =============================================================================

class NewsletterViewSet(BaseSnippetViewSet):
    """
    Admin interface for managing Newsletters.
    Extends BaseSnippetViewSet to maintain consistent UX and shared logic.
    """

    model = Newsletter
    menu_label = _("Newsletters")
    icon = "mail"
    menu_order = 230

    search_fields = ("title", "subject", "preview_text")
    filterset_class = NewsletterFilterSet

    list_display = (
        "title",
        "subject",
        "audience_type",
        "schedule_type",
        "status",
        "sent_date",
    )
    list_filter = ("audience_type", "schedule_type", "important_announcement", "live")
    list_export = ("title", "subject", "audience_type", "schedule_type", "status", "sent_date")

    # -------------------------------------------------------------------------
    # Custom Admin Actions
    # -------------------------------------------------------------------------

    list_actions = ["send_test_email_action", "duplicate_newsletter_action"]

    def send_test_email_action(self, request, queryset):
        """Send test emails for selected newsletters."""
        success_count = 0
        for newsletter in queryset:
            success, message = newsletter.send_test_email()
            if success:
                success_count += 1
                messages.success(request, f"✅ Test email sent for '{newsletter.title}'")
            else:
                messages.warning(request, f"⚠️ Failed to send test email for '{newsletter.title}'")

        if success_count:
            messages.success(request, f"📨 Test emails sent for {success_count} newsletters")

    send_test_email_action.label = _("Send test email")
    send_test_email_action.icon = "mail"

    def duplicate_newsletter_action(self, request, queryset):
        """Duplicate selected newsletters."""
        duplicated = 0
        for newsletter in queryset:
            newsletter.pk = None
            newsletter.title = f"{newsletter.title} (Copy)"
            newsletter.live = False
            newsletter.save()
            duplicated += 1

        messages.success(
            request,
            f"🧩 Successfully duplicated {duplicated} newsletters."
        )

    duplicate_newsletter_action.label = _("Duplicate")
    duplicate_newsletter_action.icon = "copy"
