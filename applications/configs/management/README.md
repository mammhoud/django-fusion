# Shared management configuration

The active worker package is `projects/precis/precis-main/backend/plugins/workers/`.
Dramatiq handles every queue and `django_fusion.tasks.scheduler` replaces
Celery Beat for scheduled tasks.
