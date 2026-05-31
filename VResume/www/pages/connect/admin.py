"""
Connect Admin — django-unfold
Registers Campaign, Subscriber, EmailDelivery, TrackedURL, URLClick, FormSubmission.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display, action

from .models import (
    Campaign,
    EmailDelivery,
    Subscriber,
    TrackedURL,
    URLClick,
    FormSubmission,
)


class EmailDeliveryInline(TabularInline):
    model = EmailDelivery
    extra = 0
    readonly_fields = [
        "subscriber",
        "tracking_token",
        "status",
        "sent_at",
        "opened_at",
        "open_count",
        "clicked_at",
        "click_count",
    ]
    can_delete = False
    verbose_name = _("Email Delivery")
    verbose_name_plural = _("Email Deliveries")


class TrackedURLInline(TabularInline):
    model = TrackedURL
    extra = 0
    readonly_fields = ["url_hash", "click_count", "unique_clicks", "created_at"]
    can_delete = False
    verbose_name = _("Tracked URL")
    verbose_name_plural = _("Tracked URLs")


class URLClickInline(TabularInline):
    model = URLClick
    extra = 0
    readonly_fields = ["email_delivery", "ip_address", "device_type", "clicked_at"]
    can_delete = False
    verbose_name = _("URL Click")
    verbose_name_plural = _("URL Clicks")


@admin.register(Subscriber)
class SubscriberAdmin(ModelAdmin):
    list_display = [
        "email",
        "name",
        "status",
        "confirmed_at",
        "source",
        "display_open_rate",
        "display_click_rate",
        "created_at",
    ]
    list_filter = ["status", "source", "created_at", "confirmed_at"]
    search_fields = ["email", "name"]
    readonly_fields = [
        "confirmation_token",
        "unsubscribe_token",
        "confirmed_at",
        "unsubscribed_at",
        "created_at",
        "updated_at",
    ]
    inlines = [EmailDeliveryInline]

    @display(description=_("Open Rate"), label=True)
    def display_open_rate(self, obj):
        total = obj.deliveries.filter(sent_at__isnull=False).count()
        opened = obj.deliveries.filter(opened_at__isnull=False).count()
        return f"{round(opened / total * 100, 1)}%" if total else "—"

    @display(description=_("Click Rate"), label=True)
    def display_click_rate(self, obj):
        total = obj.deliveries.filter(sent_at__isnull=False).count()
        clicked = obj.deliveries.filter(clicked_at__isnull=False).count()
        return f"{round(clicked / total * 100, 1)}%" if total else "—"


@admin.register(Campaign)
class CampaignAdmin(ModelAdmin):
    list_display = [
        "name",
        "subject",
        "status",
        "subscriber_count",
        "total_sent",
        "display_open_rate",
        "display_click_rate",
        "created_at",
    ]
    list_filter = ["status", "sent_at", "created_at", "scheduled_at"]
    search_fields = ["name", "subject", "body"]
    inlines = [TrackedURLInline]
    fieldsets = [
        (_("Campaign Details"), {
            "fields": ["name", "subject", "preview_text", "body"]
        }),
        (_("Status & Scheduling"), {
            "fields": ["status", "scheduled_at", "sent_at"]
        }),
        (_("Subscribers"), {
            "fields": ["subscribers", "blog_post"]
        }),
        (_("Analytics"), {
            "fields": ["total_sent", "total_opened", "total_clicked", "total_bounced"],
            "classes": ["collapse"]
        }),
        (_("Audit"), {
            "fields": ["created_by", "created_at", "updated_at"],
            "classes": ["collapse"]
        }),
    ]

    @display(description=_("Subscribers"), label=True)
    def subscriber_count(self, obj):
        return obj.subscriber_count

    @display(description=_("Open Rate"), label=True)
    def display_open_rate(self, obj):
        if obj.total_sent:
            return f"{round(obj.total_opened / obj.total_sent * 100, 1)}%"
        return "—"

    @display(description=_("Click Rate"), label=True)
    def display_click_rate(self, obj):
        if obj.total_sent:
            return f"{round(obj.total_clicked / obj.total_sent * 100, 1)}%"
        return "—"


@admin.register(EmailDelivery)
class EmailDeliveryAdmin(ModelAdmin):
    list_display = [
        "subscriber",
        "campaign",
        "status",
        "sent_at",
        "opened_at",
        "clicked_at",
        "open_count",
        "click_count",
    ]
    list_filter = ["status", "sent_at", "opened_at", "clicked_at", "bounced_at"]
    search_fields = ["subscriber__email", "campaign__name", "tracking_token"]
    readonly_fields = [
        "tracking_token",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["campaign", "subscriber"]


@admin.register(TrackedURL)
class TrackedURLAdmin(ModelAdmin):
    list_display = [
        "original_url",
        "campaign",
        "click_count",
        "unique_clicks",
        "created_at",
    ]
    list_filter = ["campaign", "created_at"]
    search_fields = ["original_url", "url_hash"]
    readonly_fields = ["url_hash", "created_at", "updated_at"]
    raw_id_fields = ["campaign"]


@admin.register(URLClick)
class URLClickAdmin(ModelAdmin):
    list_display = [
        "tracked_url",
        "email_delivery",
        "ip_address",
        "device_type",
        "clicked_at",
    ]
    list_filter = ["device_type", "clicked_at"]
    search_fields = ["ip_address", "user_agent"]
    readonly_fields = ["clicked_at"]