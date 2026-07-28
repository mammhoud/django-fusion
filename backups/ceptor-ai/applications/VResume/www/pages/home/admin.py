"""
Home App Admin — django-unfold
Registers VResumeSettings, Service, Slider, TeamMember, Testimonial.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display
from .models.snippets.vresume_settings import VResumeSettings
from .models.snippets.service import Service
from .models.snippets.slider import Slider
from .models.snippets.team import TeamMember



# ── VResumeSettings ───────────────────────────────────────────────────────────

@admin.register(VResumeSettings)
class VResumeSettingsAdmin(ModelAdmin):
    list_display = ["full_name", "job_title", "email", "phone", "location"]
    search_fields = ["full_name", "job_title", "email"]
    fieldsets = (
        (_("Identity"), {
            "fields": ("avatar", "logo", "favicon"),
        }),
        (_("Personal Info"), {
            "fields": (
                "full_name", "job_title", "email",
                "phone", "birthday", "location", "map_embed_url",
            ),
        }),
        (_("Social Links"), {
            "fields": (
                "facebook_url", "twitter_url", "linkedin_url",
                "github_url", "instagram_url",
            ),
        }),
    )


# ── Service ───────────────────────────────────────────────────────────────────

@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ["name", "icon", "is_active", "order"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    list_editable = ["is_active", "order"]
    fieldsets = (
        (_("Service"), {
            "fields": ("name", "description", "icon"),
        }),
        (_("Settings"), {
            "fields": ("is_active", "order"),
        }),
    )


# ── Slider ────────────────────────────────────────────────────────────────────

@admin.register(Slider)
class SliderAdmin(ModelAdmin):
    list_display = ["title", "subtitle", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["title", "subtitle"]
    list_editable = ["is_active"]
    fieldsets = (
        (_("Slide"), {
            "fields": ("title", "subtitle", "image", "links"),
        }),
        (_("Settings"), {
            "fields": ("is_active",),
        }),
    )


# ── TeamMember ────────────────────────────────────────────────────────────────

@admin.register(TeamMember)
class TeamMemberAdmin(ModelAdmin):
    list_display = ["name", "job_title", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "job_title"]
    list_editable = ["is_active"]
    fieldsets = (
        (_("Member"), {
            "fields": ("name", "job_title", "image"),
        }),
        (_("Social"), {
            "fields": ("facebook_url", "twitter_url", "linkedin_url"),
        }),
        (_("Settings"), {
            "fields": ("is_active",),
        }),
    )

