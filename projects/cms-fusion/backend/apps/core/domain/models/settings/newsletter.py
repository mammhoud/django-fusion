from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fusion.models import DefaultBase
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import (
    DraftStateMixin,
    PreviewableMixin,
    RevisionMixin,
    TranslatableMixin,
)
from wagtail.search import index

from apps.core.domain.blocks.content.overview import OverviewBlock


class Newsletter(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    TranslatableMixin,
    ClusterableModel,
    DefaultBase,
    index.Indexed,
):
    """
    Advanced Newsletter model supporting:
    - Custom templates and content blocks
    - Targeted audiences
    - Scheduling (immediate, delayed, or test)
    - Open and click tracking
    - Integrated analytics and API exposure
    """

    # ------------------------------------------------------------------
    # BASIC INFO
    # ------------------------------------------------------------------
    title = models.CharField(max_length=255, verbose_name=_("Newsletter Title"))
    subject = models.CharField(max_length=255, verbose_name=_("Email Subject"))
    preview_text = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_("Preview Text"),
        help_text=_("Short summary text displayed in some email clients."),
    )
    header_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Header Image"),
    )
    body = StreamField(
        OverviewBlock(template="shared/comp/blocks/content/heading_block.html"),
        blank=True,
        use_json_field=True,
        verbose_name=_("Newsletter Content"),
    )

    # ------------------------------------------------------------------
    # TEMPLATE
    # ------------------------------------------------------------------
    template = models.ForeignKey(
        "shared.EmailTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Email Template"),
        help_text=_("HTML template for rendering this newsletter."),
    )

    # ------------------------------------------------------------------
    # AUDIENCE
    # ------------------------------------------------------------------
    AUDIENCE_CHOICES = [
        ("ALL", _("All Users")),
        ("STUDENTS", _("Students Only")),
        ("INSTRUCTORS", _("Instructors Only")),
        ("ADMINS", _("Administrators Only")),
        ("SPECIFIC", _("Specific Users/Groups")),
    ]
    audience_type = models.CharField(max_length=15, choices=AUDIENCE_CHOICES, default="ALL")
    target_user_levels = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Target User Levels"),
        help_text=_("Comma-separated user levels, e.g. UNDERGRAD,GRADUATE"),
    )

    # ------------------------------------------------------------------
    # SCHEDULING
    # ------------------------------------------------------------------
    SCHEDULE_CHOICES = [
        ("DRAFT", _("Save as Draft")),
        ("IMMEDIATE", _("Send Immediately")),
        ("SCHEDULED", _("Schedule for Later")),
        ("TEST", _("Send Test Email")),
    ]
    schedule_type = models.CharField(max_length=15, choices=SCHEDULE_CHOICES, default="DRAFT")
    scheduled_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Scheduled Date"))

    # ------------------------------------------------------------------
    # TRACKING
    # ------------------------------------------------------------------
    sent_date = models.DateTimeField(null=True, blank=True, editable=False)
    total_recipients = models.PositiveIntegerField(default=0, editable=False)
    open_count = models.PositiveIntegerField(default=0, editable=False)
    click_count = models.PositiveIntegerField(default=0, editable=False)

    track_opens = models.BooleanField(default=True, verbose_name=_("Track Opens"))
    track_clicks = models.BooleanField(default=True, verbose_name=_("Track Clicks"))
    include_unsubscribe = models.BooleanField(
        default=True, verbose_name=_("Include Unsubscribe Link")
    )
    important_announcement = models.BooleanField(default=False)
    show_in_portal = models.BooleanField(default=True)

    # ------------------------------------------------------------------
    # TESTING & METADATA
    # ------------------------------------------------------------------
    test_email_addresses = models.TextField(
        blank=True, help_text=_("Comma-separated test email addresses")
    )
    newsletter_id = models.CharField(max_length=50, unique=True, editable=False)

    revisions = GenericRelation(
        "wagtailcore.Revision",
        content_type_field="base_content_type",
        object_id_field="object_id",
        related_query_name="newsletter",
        for_concrete_model=False,
    )

    # ------------------------------------------------------------------
    # PANELS
    # ------------------------------------------------------------------
    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("subject"),
                FieldPanel("preview_text"),
                FieldPanel("header_image"),
                FieldPanel("body"),
            ],
            heading=_("Content"),
        ),
    ]

    template_panels = [
        MultiFieldPanel([FieldPanel("template")], heading=_("Template Configuration")),
    ]

    audience_panels = [
        MultiFieldPanel(
            [
                FieldPanel("audience_type"),
                FieldPanel("target_user_levels"),
            ],
            heading=_("Audience Targeting"),
        ),
    ]

    settings_panels = [
        MultiFieldPanel(
            [
                FieldPanel("schedule_type"),
                FieldRowPanel([FieldPanel("scheduled_date")]),
                FieldRowPanel([FieldPanel("track_opens"), FieldPanel("track_clicks")]),
                FieldPanel("include_unsubscribe"),
                FieldPanel("important_announcement"),
                FieldPanel("show_in_portal"),
                FieldPanel("test_email_addresses"),
            ],
            heading=_("Settings"),
        ),
    ]

    analytics_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("sent_date", read_only=True),
                        FieldPanel("total_recipients", read_only=True),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("open_count", read_only=True),
                        FieldPanel("click_count", read_only=True),
                    ]
                ),
            ],
            heading=_("Delivery Analytics"),
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(template_panels, heading=_("Template")),
            ObjectList(audience_panels, heading=_("Audience")),
            ObjectList(settings_panels, heading=_("Settings")),
            ObjectList(analytics_panels, heading=_("Analytics")),
        ]
    )

    # ------------------------------------------------------------------
    # SEARCH & API
    # ------------------------------------------------------------------
    search_fields = [
        index.SearchField("title"),
        index.AutocompleteField("title"),
        index.SearchField("subject"),
        index.FilterField("audience_type"),
        index.FilterField("schedule_type"),
        index.FilterField("sent_date"),
    ]
    api_fields = [
        APIField("title"),
        APIField("subject"),
        APIField("body"),
        APIField("audience_type"),
        APIField("sent_date"),
    ]

    # ------------------------------------------------------------------
    # MODEL METHODS
    # ------------------------------------------------------------------
    def save(self, *args, **kwargs):
        import uuid

        if not self.newsletter_id:
            self.newsletter_id = f"NL-{uuid.uuid4().hex[:8].upper()}"
        if not self.template:
            from apps.core.domain.services.email.models import EmailTemplate
            self.template = EmailTemplate.objects.filter(is_default=True, is_active=True).first()
        if self.live and not self.sent_date and self.schedule_type == "IMMEDIATE":
            self.sent_date = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_sent(self):
        return bool(self.sent_date)

    @property
    def open_rate(self):
        return (self.open_count / self.total_recipients) * 100 if self.total_recipients else 0

    @property
    def click_rate(self):
        return (self.click_count / self.total_recipients) * 100 if self.total_recipients else 0

    @property
    def status(self):
        if not self.live:
            return _("Draft")
        elif self.sent_date:
            return _("Sent")
        elif self.scheduled_date and self.scheduled_date > timezone.now():
            return _("Scheduled")
        return _("Published")

    class Meta(TranslatableMixin.Meta):
        verbose_name = _("Newsletter")
        verbose_name_plural = _("Newsletters")
        ordering = ["-created_at"]
