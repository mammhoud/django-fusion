from crafts_ai.content.models.tasks import BackgroundTaskLog
from wagtail.snippets.views.snippets import SnippetViewSet


class BackgroundTaskLogViewSet(SnippetViewSet):
    model = BackgroundTaskLog
    icon = "tasks"
    menu_label = "Background Tasks"
    menu_name = "background_tasks"
    menu_order = 900
    add_to_admin_menu = True
    list_display = ["task_name", "status", "queue_name", "created_at", "retry_count"]
    list_filter = ["status", "queue_name", "task_name"]
    search_fields = ["task_name", "job_id", "error_message"]
    inspect_view_enabled = True
