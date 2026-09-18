"""Course Center admin — Django admin for the shared public schema."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import CenterPlan, CenterRegistration, CourseCenter, CourseDomain


class CourseDomainInline(admin.TabularInline):
    model = CourseDomain
    extra = 0
    fields = ("domain", "is_primary")


@admin.register(CourseCenter)
class CourseCenterAdmin(admin.ModelAdmin):
    list_display = [
        "organization_name",
        "slug",
        "plan",
        "status",
        "primary_domain",
        "created_at",
    ]
    list_filter = ["status", "plan"]
    search_fields = ["organization_name", "slug", "tagline"]
    readonly_fields = ["auto_create_schema", "created_at"]
    inlines = [CourseDomainInline]
    fieldsets = (
        (_("Identity"), {"fields": ("organization_name", "slug", "tagline", "plan", "status")}),
        (_("Settings"), {"fields": ("settings", "subscription_id", "trial_ends_at")}),
        (_("Schema"), {"fields": ("auto_create_schema", "created_at")}),
    )


@admin.register(CenterPlan)
class CenterPlanAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "max_courses",
        "max_instructors",
        "max_students",
        "custom_domain",
        "trial_days",
        "is_active",
    ]
    list_filter = ["is_active", "custom_domain", "custom_branding"]
    search_fields = ["name", "slug"]


@admin.register(CenterRegistration)
class CenterRegistrationAdmin(admin.ModelAdmin):
    list_display = [
        "organization_name",
        "email",
        "plan",
        "subdomain",
        "status",
        "created_at",
    ]
    list_filter = ["status", "plan"]
    search_fields = ["organization_name", "email", "subdomain", "tagline"]
    readonly_fields = ["verification_token", "created_at"]
    actions = ["approve_registrations", "reject_registrations"]

    @admin.action(description=_("Approve selected registrations"))
    def approve_registrations(self, request, queryset):
        for reg in queryset.filter(status=CenterRegistration.Status.VERIFIED):
            reg.status = CenterRegistration.Status.APPROVED
            reg.save(update_fields=["status"])
        self.message_user(request, _("Selected registrations approved."))

    @admin.action(description=_("Reject selected registrations"))
    def reject_registrations(self, request, queryset):
        updated = queryset.filter(
            status__in=[
                CenterRegistration.Status.PENDING,
                CenterRegistration.Status.VERIFIED,
            ]
        ).update(status=CenterRegistration.Status.REJECTED)
        self.message_user(request, _(f"{updated} registration(s) rejected."))