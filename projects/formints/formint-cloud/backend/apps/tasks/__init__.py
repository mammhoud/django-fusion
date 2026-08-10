"""Formint Cloud background tasks.

Each module uses ``@task`` from ``django_fusion.tasks`` to register
broker-agnostic background jobs.  Discovered automatically by django-fusion
via ``DjangoFusionConfig.ready()``.
"""

from apps.tasks.backup_tasks import run_backup  # noqa: F401
