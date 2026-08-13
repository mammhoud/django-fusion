"""Precis LMS background tasks.

Each module uses ``@task`` from ``django_fusion.tasks`` to register
broker-agnostic background jobs.  Discovered automatically by django-fusion
via ``DjangoFusionConfig.ready()``.
"""

from apps.tasks.email_tasks import (  # noqa: F401
    send_certificate,
    send_enrollment_confirmation,
    send_password_reset,
)
from apps.tasks.course_tasks import (  # noqa: F401
    generate_course_progress_report,
    send_weekly_learning_digest,
    sync_course_completion_rates,
)
from apps.tasks.content_tasks import (  # noqa: F401
    generate_ai_course_description,
    process_uploaded_video,
)
