from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.models import DraftStateMixin, LockableMixin, RevisionMixin

from .base import DefaultBase


class ContactSubmission(DefaultBase, DraftStateMixin, RevisionMixin, LockableMixin):
    """
    Stores form submissions from ContactFormBlock.
    Integrates with Wagtail's form submission system.
    """

    form_id = models.CharField(
        max_length=100,
        verbose_name=_("Form ID"),
        help_text=_("Identifier for the form that was submitted"),
    )
    page_id = models.IntegerField(
        verbose_name=_("Page ID"),
        help_text=_("ID of the page containing the form"),
    )
    page_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Page Title"),
        help_text=_("Title of the page containing the form"),
    )
    page_url = models.URLField(
        blank=True,
        verbose_name=_("Page URL"),
        help_text=_("URL of the page containing the form"),
    )
    submitted_data = models.JSONField(
        verbose_name=_("Submitted Data"),
        help_text=_("Form data as JSON"),
    )
    files_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Files Data"),
        help_text=_("Information about uploaded files"),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP Address"),
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("User Agent"),
    )
    referrer = models.URLField(
        blank=True,
        verbose_name=_("Referrer"),
        help_text=_("URL of the page that referred the user"),
    )
    submission_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Submission Date"),
    )
    processed = models.BooleanField(
        default=False,
        verbose_name=_("Processed"),
        help_text=_("Whether this submission has been processed"),
    )
    processed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Processed Date"),
        help_text=_("When this submission was processed"),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Internal notes about this submission"),
    )

    class Meta:
        verbose_name = _("Contact Submission")
        verbose_name_plural = _("Contact Submissions")
        ordering = ["-submission_date"]
        indexes = [
            models.Index(fields=["form_id"]),
            models.Index(fields=["page_id"]),
            models.Index(fields=["submission_date"]),
            models.Index(fields=["processed"]),
            models.Index(fields=["page_title"]),
            models.Index(fields=["live"]),
        ]
        permissions = [
            ("can_export", _("Can export submissions")),
            ("can_bulk_delete", _("Can bulk delete submissions")),
            ("can_change_status", _("Can change submission status")),
        ]

    # Panels configuration
    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("form_id", read_only=True),
                FieldPanel("page_id", read_only=True),
                FieldPanel("page_title", read_only=True),
                FieldPanel("page_url", read_only=True),
            ],
            heading=_("Form Information"),
        ),
        FieldPanel("submitted_data", read_only=True),
        FieldPanel("files_data", read_only=True),
    ]

    metadata_panels = [
        MultiFieldPanel(
            [
                FieldPanel("ip_address", read_only=True),
                FieldPanel("user_agent", read_only=True),
                FieldPanel("referrer", read_only=True),
                FieldPanel("submission_date", read_only=True),
            ],
            heading=_("Submission Details"),
        ),
    ]

    status_panels = [
        MultiFieldPanel(
            [
                FieldPanel("processed"),
                FieldPanel("processed_date"),
                FieldPanel("notes"),
            ],
            heading=_("Processing Status"),
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(metadata_panels, heading=_("Metadata")),
            ObjectList(status_panels, heading=_("Status")),
            # ObjectList(DraftStateMixin.publish_panel, heading=_("Publishing"),
            #           classname="publishing"),
        ]
    )

    def __str__(self):
        name = self.get_name()
        email = self.get_email()
        identifier = f"{name} ({email})" if email else name
        return f"{identifier} - {self.form_id} ({self.submission_date.strftime('%Y-%m-%d %H:%M')})"

    def get_field_value(self, field_name):
        """Get a specific field value from submitted data."""
        return self.submitted_data.get(field_name)

    def get_email(self):
        """Get email from submitted data."""
        # Try common email field names
        email_fields = ["email", "e_mail", "mail", "contact_email", "e-mail",
                       "Email", "E-Mail", "EMAIL"]
        for field in email_fields:
            if email := self.submitted_data.get(field):
                return str(email).strip()
        return None

    def get_name(self):
        """Get name from submitted data."""
        # Try to construct full name from various fields
        name_fields = ["name", "full_name", "fullname", "Full Name"]
        for field in name_fields:
            if name := self.submitted_data.get(field):
                return str(name).strip()

        # Try combining first and last name
        first_name = self.submitted_data.get("first_name", "").strip()
        last_name = self.submitted_data.get("last_name", "").strip()
        if first_name or last_name:
            return f"{first_name} {last_name}".strip()

        return _("Anonymous")

    def get_phone(self):
        """Get phone number from submitted data."""
        phone_fields = ["phone", "telephone", "mobile", "phone_number",
                       "Phone", "Telephone", "Mobile"]
        for field in phone_fields:
            if phone := self.submitted_data.get(field):
                return str(phone).strip()
        return None

    def mark_as_processed(self):
        """Mark this submission as processed."""
        from django.utils import timezone
        self.processed = True
        self.processed_date = timezone.now()
        self.save(update_fields=["processed", "processed_date", "updated_at"])

    def mark_as_unprocessed(self):
        """Mark this submission as unprocessed."""
        self.processed = False
        self.processed_date = None
        self.save(update_fields=["processed", "processed_date", "updated_at"])

    def export_as_dict(self):
        """Export submission data as dictionary."""
        return {
            "id": self.id,
            "form_id": self.form_id,
            "page_id": self.page_id,
            "page_title": self.page_title,
            "page_url": self.page_url,
            "data": self.submitted_data,
            "files": self.files_data,
            "ip_address": str(self.ip_address) if self.ip_address else None,
            "user_agent": self.user_agent,
            "referrer": self.referrer,
            "submission_date": self.submission_date.isoformat(),
            "processed": self.processed,
            "processed_date": self.processed_date.isoformat() if self.processed_date else None,
            "notes": self.notes,
            "name": self.get_name(),
            "email": self.get_email(),
            "phone": self.get_phone(),
        }

    def export_as_csv_row(self):
        """Export submission data as CSV row."""
        import csv
        from io import StringIO

        data = self.export_as_dict()
        # Flatten nested JSON data
        flattened = {}
        for key, value in data.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    flattened[f"{key}_{subkey}"] = str(subvalue)
            else:
                flattened[key] = str(value) if value is not None else ""

        return flattened

    @property
    def status(self):
        """Get human-readable status."""
        if self.processed:
            return _("Processed")
        return _("Pending")

    @property
    def status_color(self):
        """Get status color for admin display."""
        if self.processed:
            return "success"
        return "warning"

    # Wagtail-specific methods
    def get_admin_url(self):
        """Get admin URL for this submission."""
        from django.urls import reverse
        return reverse('contact_contactsubmission_modeladmin_edit', args=[self.id])

    def get_preview_url(self):
        """Get preview URL if page exists."""
        if self.page_id:
            from wagtail.models import Page
            try:
                page = Page.objects.get(id=self.page_id)
                return page.get_full_url()
            except Page.DoesNotExist:
                return None
        return None
