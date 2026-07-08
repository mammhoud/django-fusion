"""
Django admin registration for EmailConfiguration model.

Provides a management interface for email settings with test email functionality.

Classes:
    EmailConfigurationAdmin: Admin class for EmailConfiguration model with
        test email functionality and activation/deactivation actions.

Usage in Django admin::

    from django.contrib import admin
    from django_fusion.contrib.admin.email_admin import EmailConfigurationAdmin
    from django_fusion.contrib.admin.email_config import EmailConfiguration

    admin.site.register(EmailConfiguration, EmailConfigurationAdmin)
"""

import logging

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from .email_config import EmailConfiguration

logger = logging.getLogger(__name__)


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        "email_host_user",
        "email_host",
        "email_port",
        "email_use_tls",
        "is_active",
        "updated_at",
    )
    list_filter = ("is_active", "email_use_tls", "email_use_ssl", "email_backend")
    search_fields = ("email_host_user", "email_host", "notes")
    readonly_fields = ("created_at", "updated_at")
    actions = ["send_test_email_action", "activate_config", "deactivate_config"]

    fieldsets = (
        (
            _("Connection"),
            {
                "fields": (
                    "email_backend",
                    "email_host",
                    "email_port",
                    "email_use_tls",
                    "email_use_ssl",
                ),
            },
        ),
        (
            _("Authentication"),
            {
                "fields": ("email_host_user", "email_host_password"),
            },
        ),
        (
            _("Sender"),
            {
                "fields": ("default_from_email",),
            },
        ),
        (
            _("Status"),
            {
                "fields": ("is_active", "notes", "created_at", "updated_at"),
            },
        ),
    )

    def get_form(self, request, obj=None, **kwargs):
        """Override password widget to use PasswordInput."""
        from django import forms

        form = super().get_form(request, obj, **kwargs)
        if "email_host_password" in form.base_fields:
            form.base_fields["email_host_password"].widget = forms.PasswordInput(
                render_value=True,
                attrs={"class": "vTextField", "autocomplete": "new-password"},
            )
        return form

    @admin.action(description=_("📧 Send test email to admin"))
    def send_test_email_action(self, request, queryset):
        for config in queryset:
            try:
                to_email = request.user.email or config.email_host_user
                config.send_test_email(to_email)
                messages.success(
                    request,
                    _(f"✅ Test email sent to {to_email} via {config.email_host}"),
                )
            except Exception as e:
                logger.error(f"[Email] Test email failed: {e}", exc_info=True)
                messages.error(
                    request,
                    _(f"❌ Failed to send test email: {e}"),
                )

    @admin.action(description=_("✅ Activate selected config"))
    def activate_config(self, request, queryset):
        if queryset.count() > 1:
            messages.warning(request, _("Please select only one configuration to activate."))
            return
        EmailConfiguration.objects.filter(is_active=True).update(is_active=False)
        queryset.update(is_active=True)
        messages.success(request, _("Configuration activated."))

    @admin.action(description=_("❌ Deactivate selected config"))
    def deactivate_config(self, request, queryset):
        queryset.update(is_active=False)
        messages.success(request, _("Configuration deactivated."))
