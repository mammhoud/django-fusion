"""
Admin configuration for registration models.
Merged from plugins.accounts.registration.admin.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin as BaseImportExportModelAdmin
from unfold.admin import ModelAdmin, TabularInline


class ImportExportModelAdmin(BaseImportExportModelAdmin, ModelAdmin):
    """Combines django-import-export with Unfold styling."""
    pass


from plugins.accounts.models.snippets import AuthEmailTemplate

try:
    from plugins.accounts.registration.models import CSVEmailTest, CSVEmailTestBatch

    @admin.register(CSVEmailTest)
    class CSVEmailTestAdmin(ImportExportModelAdmin):
        """Admin interface for CSVEmailTest model."""

        compressed_fields = True
        warn_unsaved_changes = True
        list_filter_submit = True
        list_display = (
            "recipient_email", "test_name", "recipient_role",
            "status", "created_at", "sent_at",
        )
        list_filter = ("status", "recipient_role", "created_at")
        search_fields = ("recipient_email", "test_name", "recipient_role")
        readonly_fields = ("created_at", "sent_at", "completed_at", "send_duration_ms")

        fieldsets = (
            (_("Test Information"), {
                "fields": ("test_name", "csv_file", "template_dir")
            }),
            (_("Email Details"), {
                "fields": (
                    "recipient_email", "recipient_role",
                    "email_subject", "template_used",
                )
            }),
            (_("Status"), {
                "fields": ("status", "error_message")
            }),
            (_("Timestamps & Performance"), {
                "fields": ("created_at", "sent_at", "completed_at", "send_duration_ms"),
                "classes": ("collapse",)
            }),
        )

    @admin.register(CSVEmailTestBatch)
    class CSVEmailTestBatchAdmin(ModelAdmin):
        """Admin interface for CSVEmailTestBatch model."""

        compressed_fields = True
        warn_unsaved_changes = True
        list_filter_submit = True
        list_display = (
            "batch_id", "csv_file", "total_emails",
            "sent_count", "failed_count", "skipped_count", "started_at",
        )
        list_filter = ("started_at",)
        search_fields = ("batch_id", "csv_file")
        readonly_fields = ("started_at", "completed_at")

        fieldsets = (
            (_("Batch Information"), {
                "fields": ("batch_id", "csv_file", "results_file")
            }),
            (_("Counts"), {
                "fields": ("total_emails", "sent_count", "failed_count", "skipped_count")
            }),
            (_("Timestamps"), {
                "fields": ("started_at", "completed_at"),
                "classes": ("collapse",)
            }),
        )

except ImportError:
    pass


@admin.register(AuthEmailTemplate)
class AuthEmailTemplateAdmin(ModelAdmin):
    """Admin interface for AuthEmailTemplate model."""

    compressed_fields = True
    warn_unsaved_changes = True
    list_filter_submit = True
    list_display = ("template_type", "subject", "is_active")
    list_filter = ("template_type", "is_active")
    search_fields = ("subject", "body_text")

    fieldsets = (
        (_("Template"), {
            "fields": ("template_type", "subject", "is_active")
        }),
        (_("Content"), {
            "fields": ("body_html", "body_text")
        }),
    )


try:
    from allauth.socialaccount.models import SocialAccount

    class SocialAccountInline(TabularInline):
        model = SocialAccount
        extra = 0
        readonly_fields = ["provider", "uid", "extra_data", "date_joined", "last_login"]
        verbose_name = _("Social Account")
        verbose_name_plural = _("Social Accounts")

    class UserAdmin(ModelAdmin):
        compressed_fields = True
        warn_unsaved_changes = True
        inlines = [SocialAccountInline]

except ImportError:
    class UserAdmin(ModelAdmin):  # type: ignore[no-redef]
        compressed_fields = True
        warn_unsaved_changes = True


def register_user_admin():
    """
    Called from AppConfig.ready() — after all apps are loaded.
    Replaces Django's default UserAdmin with our Unfold-based one.
    """
    User = get_user_model()
    if User in admin.site._registry:
        admin.site.unregister(User)
    admin.site.register(User, UserAdmin)
