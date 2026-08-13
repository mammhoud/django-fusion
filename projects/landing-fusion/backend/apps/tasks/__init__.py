"""Landing-Fusion background tasks.

Each module below uses ``@task`` from ``django_fusion.tasks`` to register
broker-agnostic background jobs.  The ``django_fusion`` autodiscovery (via
``DjangoFusionConfig.ready()``) imports this package automatically, so tasks
are registered as soon as Django starts.
"""

# The following imports ensure that every @task-decorated function is
# discovered by django_fusion.tasks.task_registry.autodiscover().
#
# DO NOT remove — these side-effect imports are how the registry finds tasks
# when scanning ``INSTALLED_APPS`` for ``.tasks`` subpackages.
from apps.tasks.email_tasks import (  # noqa: F401
    send_contact_form_notification,
    send_newsletter,
    send_weekly_site_stats,
)
from apps.tasks.content_tasks import (  # noqa: F401
    generate_blog_preview_images,
    warm_page_cache,
)
