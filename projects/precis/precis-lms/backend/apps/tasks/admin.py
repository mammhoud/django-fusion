from django.contrib import admin

from .models import TaskExecution


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    list_display = ("task_name", "queue_name", "site_name", "status", "created_at")
    list_filter = ("status", "site_name", "queue_name")
    search_fields = ("task_name", "job_id", "error_message")
    readonly_fields = [f.name for f in TaskExecution._meta.fields]
