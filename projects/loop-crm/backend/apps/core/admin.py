from django.contrib import admin

from apps.crm.models import CustomFieldDefinition

from .models import AuditLog, TaskExecution, UserProfile, WorkflowDefinition, WorkflowRun, Workspace


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "currency", "is_active")
    search_fields = ("name", "slug")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "workspace", "role")
    list_filter = ("workspace", "role")
    search_fields = ("user__email", "user__username", "title")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "workspace", "user", "action", "model_name", "object_id")
    list_filter = ("workspace", "action")
    readonly_fields = [f.name for f in AuditLog._meta.fields]


@admin.register(CustomFieldDefinition)
class CustomFieldDefinitionAdmin(admin.ModelAdmin):
    list_display = ("label", "object_type", "field_type", "workspace", "required", "is_active", "position")
    list_filter = ("object_type", "field_type", "required", "is_active", "workspace")
    search_fields = ("label", "key", "description")
    ordering = ("workspace", "object_type", "position", "label")


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ("name", "module", "trigger", "status", "workspace", "updated_at")
    list_filter = ("module", "status", "workspace")
    search_fields = ("name", "slug", "trigger")
    readonly_fields = ("created_at", "updated_at")


@admin.register(WorkflowRun)
class WorkflowRunAdmin(admin.ModelAdmin):
    list_display = ("definition", "status", "workspace", "queued_at", "finished_at")
    list_filter = ("status", "workspace")
    search_fields = ("definition__name", "error")
    readonly_fields = [f.name for f in WorkflowRun._meta.fields]


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    list_display = ("task_name", "queue_name", "site_name", "status", "created_at")
    list_filter = ("status", "site_name", "queue_name")
    search_fields = ("task_name", "job_id", "error_message")
    readonly_fields = [f.name for f in TaskExecution._meta.fields]
