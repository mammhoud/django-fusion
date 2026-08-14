from django.contrib import admin

from .models import Campaign, Media, Post, PostAnalytics, SocialChannel


@admin.register(SocialChannel)
class SocialChannelAdmin(admin.ModelAdmin):
    list_display = ("account_name", "platform", "workspace", "is_active")
    list_filter = ("workspace", "platform", "is_active")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "budget", "start_date", "end_date", "owner")
    list_filter = ("workspace",)
    search_fields = ("name",)


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("id", "workspace", "file", "created_at")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("content", "channel", "campaign", "status", "scheduled_at", "workspace")
    list_filter = ("workspace", "status", "channel__platform")
    search_fields = ("content",)


@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("post", "impressions", "clicks", "engagement", "spend", "fetched_at")
