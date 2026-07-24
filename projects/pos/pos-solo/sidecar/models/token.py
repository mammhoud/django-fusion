"""POS Solo Edition — DeviceToken (thin wrapper over BaseDeviceToken).

See :class:`django_fusion.core.models.BaseDeviceToken` for full documentation
(token lifecycle, security model, auth methods, sync cascade).
"""

from __future__ import annotations

from django.db.models import Index
from django_fusion.core.models import BaseDeviceToken

__all__ = ["DeviceToken"]


class DeviceToken(BaseDeviceToken):
    """POS Solo edition device token — inherits all behaviour from BaseDeviceToken.

    Keeps only sidecar-specific indexes.  ``token_hash`` is already
    ``unique=True`` on the base model, so no extra index is needed.
    """

    class Meta(BaseDeviceToken.Meta):
        abstract = False
        app_label = "pos_solo"
        db_table = "cloud_device_tokens"
        indexes = [
            Index(fields=["device_id", "is_active"]),
            Index(fields=["node_id_link", "is_active"]),
            Index(fields=["expires_at"]),
            Index(fields=["sync_status"]),
            Index(fields=["app_type", "sync_status"]),
        ]
