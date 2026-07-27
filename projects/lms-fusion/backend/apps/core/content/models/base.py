# Re-exports from django_fusion.models.base for backward compatibility.
from django_fusion.models.base import AuditableBaseModel as DefaultBase  # noqa: F401

# The canonical ``DefaultBase`` is now ``django_fusion.models.base.AuditableBaseModel``.
# Projects using ``apps.core.content.models.base.DefaultBase`` will continue to work;
# new code should import from ``django_fusion.models.base`` directly.
