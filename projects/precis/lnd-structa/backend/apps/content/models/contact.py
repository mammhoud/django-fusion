"""
Contact form submissions — managed as a Wagtail snippet.

``POST /fragment/contact/`` (see ``apps/pages/api.py``) validates the payload
and persists a row here so every inquiry has an audit trail in the Wagtail
admin, mirroring the archived ctc-research ``ContactSubmission`` enhancement
(also present in the Precis LMS backend). Editors review, mark-processed and
export submissions without digging through server logs or email boxes.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.admin.ui.tables import BooleanColumn, Column, DateColumn
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


class ContactSubmission(models.Model):
    """A single inquiry submitted through the public contact form."""

    form_id = models.CharField(
        max_length=100,
        verbose_name=_("Form ID"),
        help_text=_("Identifier for the form that was submitted."),
    )
    page_id = models.IntegerField(
        default=0,
        verbose_name=_("Page ID"),
        help_text=_("ID of the page containing the form."),
    )
    page_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Page Title"),
        help_text=_("Title of the page containing the form."),
    )
    page_url = models.URLField(
        blank=True,
        verbose_name=_("Page URL"),
        help_text=_("URL of the page containing the form."),
    )
    submitted_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Submitted Data"),
        help_text=_("Form data as JSON."),
    )
    files_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Files Data"),
        help_text=_("Information about uploaded files."),
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
        help_text=_("URL of the page that referred the user."),
    )
    submission_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Submission Date"),
    )
    processed = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Processed"),
        help_text=_("Whether this submission has been reviewed."),
    )
    processed_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Processed Date"),
        help_text=_("When this submission was processed."),
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Notes"),
        help_text=_("Internal notes about this submission."),
    )

    panels = [
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
        MultiFieldPanel(
            [
                FieldPanel("ip_address", read_only=True),
                FieldPanel("user_agent", read_only=True),
                FieldPanel("referrer", read_only=True),
                FieldPanel("submission_date", read_only=True),
            ],
            heading=_("Submission Details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("processed"),
                FieldPanel("processed_date"),
                FieldPanel("notes"),
            ],
            heading=_("Processing Status"),
        ),
    ]

    class Meta:
        app_label = "content"
        verbose_name = _("contact submission")
        verbose_name_plural = _("contact submissions")
        ordering = ["-submission_date"]
        indexes = [
            models.Index(fields=["form_id"]),
            models.Index(fields=["page_id"]),
            models.Index(fields=["submission_date"]),
            models.Index(fields=["processed"]),
        ]

    def __str__(self):
        name = self.get_name()
        email = self.get_email()
        identifier = f"{name} ({email})" if email else name
        return f"{identifier} — {self.form_id} ({self.submission_date:%Y-%m-%d %H:%M})"

    # ── Field helpers ──────────────────────────────────────────────

    def get_field_value(self, field_name):
        """Get a specific field value from the submitted data."""
        return self.submitted_data.get(field_name)

    def get_email(self):
        """Best-effort email from the submitted data (any common key)."""
        for field in ("email", "e_mail", "mail", "contact_email", "e-mail", "Email"):
            value = self.submitted_data.get(field)
            if value:
                return str(value).strip()
        return None

    def get_name(self):
        """Best-effort name from the submitted data."""
        for field in ("name", "full_name", "fullname", "Full Name"):
            value = self.submitted_data.get(field)
            if value:
                return str(value).strip()
        first_name = str(self.submitted_data.get("first_name", "")).strip()
        last_name = str(self.submitted_data.get("last_name", "")).strip()
        if first_name or last_name:
            return f"{first_name} {last_name}".strip()
        return _("Anonymous")

    def get_phone(self):
        """Best-effort phone number from the submitted data."""
        for field in ("phone", "telephone", "mobile", "phone_number", "Phone"):
            value = self.submitted_data.get(field)
            if value:
                return str(value).strip()
        return None

    # ── Processing helpers ─────────────────────────────────────────

    def mark_as_processed(self):
        from django.utils import timezone

        self.processed = True
        self.processed_date = timezone.now()
        self.save(update_fields=["processed", "processed_date"])

    def mark_as_unprocessed(self):
        self.processed = False
        self.processed_date = None
        self.save(update_fields=["processed", "processed_date"])

    @property
    def status(self):
        """Human-readable processing status."""
        return _("Processed") if self.processed else _("Pending")

    @property
    def status_color(self):
        """Wagtail-admin status color."""
        return "success" if self.processed else "warning"

    def export_as_dict(self):
        """Export the submission as a flat, JSON-safe dict."""
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
        """Flatten the submission into a CSV-friendly row dict."""
        row = {}
        for key, value in self.export_as_dict().items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    row[f"{key}_{subkey}"] = str(subvalue)
            else:
                row[key] = str(value) if value is not None else ""
        return row


class ContactSubmissionViewSet(SnippetViewSet):
    """Wagtail snippet viewset — the admin home for contact submissions.

    Lists every inquiry with its form, page, email, date and processing
    state, with filtering + search and the built-in CSV export.
    """

    model = ContactSubmission
    menu_label = _("Contact submissions")
    icon = "mail"
    add_to_admin_menu = True

    list_display = [
        Column("form_id", label=_("Form")),
        Column("page_title", label=_("Page")),
        Column("get_email", label=_("Email"), sort_key="submission_date"),
        DateColumn("submission_date", label=_("Date"), sort_key="submission_date"),
        BooleanColumn("processed", label=_("Processed")),
    ]
    list_filter = ["processed", "form_id"]
    search_fields = ["submitted_data", "page_title", "form_id", "notes"]
    list_export = [
        "form_id", "page_title", "page_url", "submission_date",
        "processed", "processed_date", "ip_address", "user_agent",
        "referrer", "notes", "get_name", "get_email", "get_phone",
    ]
    export_headings = {
        "form_id": _("Form"),
        "page_title": _("Page"),
        "page_url": _("Page URL"),
        "submission_date": _("Date"),
        "processed": _("Processed"),
        "processed_date": _("Processed date"),
        "ip_address": _("IP address"),
        "user_agent": _("User agent"),
        "referrer": _("Referrer"),
        "notes": _("Notes"),
        "get_name": _("Name"),
        "get_email": _("Email"),
        "get_phone": _("Phone"),
    }


register_snippet(ContactSubmissionViewSet)
