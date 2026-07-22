"""CI (Core Integration) models — re-exports from django_fusion.core.models.

These models use ``app_label = "CI"`` in their Meta class.  Django's migration
autodetector discovers them through this module so that ``makemigrations CI``
creates migrations in ``django_fusion/ci/migrations/``.
"""

from django_fusion.core.models.datatoken import DataToken  # noqa: F401
from django_fusion.core.models.integrations import Integration  # noqa: F401

# NOTE: Call and Notification are imported by django_fusion.core.models.__init__.py
# and therefore appear in the generated CI migration.  They are NOT re-exported
# here to avoid hard-failing when twilio is absent — but the migration tables
# (ci_call, ci_notification) will still be created and can be used once
# twilio is installed.
