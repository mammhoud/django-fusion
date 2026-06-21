from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Base and reusable block imports
from django_osoul.core.models import BaseModel as DefaultBase
from crafts_ai.content.blocks.pages.event import EventSectionBlock
from taggit.managers import TaggableManager
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField

# ===================================================================
# 🗓️ EVENT MODEL
# ===================================================================

class Event(DefaultBase):
    """
    Represents a flexible event with dynamic, StreamField-powered sections.
    """

    class EventType(models.TextChoices):
        WORKSHOP = "workshop", _("Workshop")
        SEMINAR = "seminar", _("Seminar")
        CONFERENCE = "conference", _("Conference")
        WEBINAR = "webinar", _("Webinar")
        MEETUP = "meetup", _("Meetup")
        OTHER = "other", _("Other")

    # Core info
    title = models.CharField(_("Event Title"), max_length=200)

    description = models.TextField(
        _("Description"),
        blank=True,
        help_text=_("A short introduction or summary of the event."),
    )

    event_type = models.CharField(
        _("Event Type"),
        choices=EventType.choices,
        max_length=50,
        default=EventType.OTHER,
    )

    # Dates and location
    start_date = models.DateTimeField(_("Start Date"), null=True, blank=True)
    end_date = models.DateTimeField(_("End Date"), null=True, blank=True)
    location = models.CharField(
        _("Location"),
        max_length=250,
        blank=True,
        help_text=_("Specify venue or online meeting link."),
    )

    # Content blocks
    content = StreamField(
        [("event_section", EventSectionBlock())],
        use_json_field=True,
        blank=True,
        verbose_name=_("Event Content"),
        help_text=_("Flexible content layout for this event."),
    )

    # Status & tags
    is_visible = models.BooleanField(
        _("Is Visible"),
        default=True,
        help_text=_("Controls whether this event is visible on the site."),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Mark this event as active or archived."),
    )

    tags = TaggableManager(blank=True, verbose_name=_("Tags"))

    # Admin configuration
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("description"),
                FieldPanel("event_type"),
            ],
            heading=_("Event Information"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
                FieldPanel("location"),
                FieldPanel("is_active"),
                FieldPanel("tags"),
            ],
            heading=_("Event Details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("content"),
                FieldPanel("is_visible"),
            ],
            heading=_("Event Content"),
        ),
    ]

    class Meta:
        verbose_name = _("Event")
        verbose_name_plural = _("Events")
        ordering = ["-start_date", "title"]

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"

    def get_absolute_url(self):
        return reverse("event-detail", kwargs={"pk": self.pk})
