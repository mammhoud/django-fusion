from django.db import models
from django.db.models import JSONField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page


class FormSubmission(ClusterableModel):
    """
    Stores all form submissions from across the site.
    """
    page = models.ForeignKey(
        Page,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Submitted from page"),
        related_name="grep_form_submissions",
    )
    form_name = models.CharField(
        max_length=100,
        verbose_name=_("Form name"),
        help_text=_("Identifier for the form (e.g., 'contact', 'newsletter')"),
        blank=True,
        default="contact",
    )
    submitted_at = models.DateTimeField(
        default=timezone.now,
        verbose_name=_("Submission date"),
        editable=False,
    )
    form_data = JSONField(
        verbose_name=_("Form data"),
        help_text=_("Structured form submission data"),
        default=dict,
        blank=True,
    )
    ip_address = models.GenericIPAddressField(
        verbose_name=_("IP address"),
        blank=True,
        null=True,
    )
    user_agent = models.TextField(
        verbose_name=_("User agent"),
        blank=True,
    )

    panels = [
        FieldPanel("page"),
        FieldPanel("form_name"),

        FieldPanel("form_data"),
        FieldPanel("ip_address"),
        FieldPanel("user_agent"),
    ]

    class Meta:
        app_label = "shared"
        verbose_name = _("Form Submission")
        verbose_name_plural = _("Form Submissions")
        ordering = ["-submitted_at"]

    @property
    def page_title(self):
        return self.page.title if self.page else "-"

    @property
    def summary(self):
        """Show a quick preview of the first few fields."""
        if not self.form_data:
            return "-"
        items = list(self.form_data.items())[:3]
        return ", ".join(f"{k}: {v}" for k, v in items)

    def __str__(self):
        return f"{self.form_name} – {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"
