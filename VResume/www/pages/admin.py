"""
Pages Admin — django-unfold
Registers ContactSubmission (FormSubmission) with full Unfold ModelAdmin.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display

from pages.connect.models import FormSubmission as ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(ModelAdmin):
    """Admin for contact form submissions."""
    
    list_display = [
        "get_name",
        "get_email",
        "form_id",
        "submitted_at",
        "email_sent",
        "is_read",
    ]
    list_filter = [
        "form_id",
        "email_sent",
        "is_read",
        "submitted_at",
    ]
    search_fields = [
        "form_id",
        "data",
        "ip_address",
    ]
    readonly_fields = [
        "form_id",
        "data",
        "submitted_at",
        "ip_address",
        "user_agent",
        "email_sent",
        "email_sent_at",
        "is_read",
        "read_at",
    ]
    date_hierarchy = "submitted_at"
    actions = [
        "mark_as_read",
        "mark_as_unread",
    ]

    fieldsets = (
        (_("Form Information"), {
            "fields": ("form_id", "data"),
        }),
        (_("Submission Details"), {
            "fields": ("ip_address", "user_agent", "submitted_at"),
        }),
        (_("Email Status"), {
            "fields": ("email_sent", "email_sent_at"),
        }),
        (_("Processing Status"), {
            "fields": ("is_read", "read_at"),
        }),
    )

    @display(description=_("Name"), label=True)
    def get_name(self, obj):
        return obj.get_name() or "—"

    @display(description=_("Email"), label=True)
    def get_email(self, obj):
        return obj.get_email() or "—"

    def mark_as_read(self, request, queryset):
        """Mark selected submissions as read."""
        count = 0
        for submission in queryset:
            submission.mark_as_read()
            count += 1
        self.message_user(request, f"{count} submissions marked as read")
    mark_as_read.short_description = _("Mark selected as read")

    def mark_as_unread(self, request, queryset):
        """Mark selected submissions as unread."""
        count = 0
        for submission in queryset:
            submission.is_read = False
            submission.read_at = None
            submission.save(update_fields=["is_read", "read_at"])
            count += 1
        self.message_user(request, f"{count} submissions marked as unread")
    mark_as_unread.short_description = _("Mark selected as unread")
