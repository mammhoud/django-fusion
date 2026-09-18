from django.contrib import admin

from .models import AttributionModel, AttributionTouchpoint


@admin.register(AttributionModel)
class AttributionModelAdmin(admin.ModelAdmin):
    list_display = ("name", "workspace", "model_type", "is_active")
    list_filter = ("workspace", "model_type", "is_active")


@admin.register(AttributionTouchpoint)
class AttributionTouchpointAdmin(admin.ModelAdmin):
    list_display = ("source", "deal", "campaign", "weight", "occurred_at", "workspace")
    list_filter = ("workspace", "source")
