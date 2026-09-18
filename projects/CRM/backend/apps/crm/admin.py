from django.contrib import admin

from .models import Activity, Company, Contact, Deal, Pipeline, PipelineStage


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "industry", "owner")
    list_filter = ("workspace", "industry")
    search_fields = ("name",)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company", "workspace", "email", "owner")
    list_filter = ("workspace", "company")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "is_default", "order")


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ("name", "pipeline", "stage_type", "probability", "order")


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "stage", "value", "owner", "campaign")
    list_filter = ("workspace", "stage", "pipeline")
    search_fields = ("name", "company__name")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("subject", "deal", "activity_type", "status", "created_at")
    list_filter = ("workspace", "activity_type", "status")
