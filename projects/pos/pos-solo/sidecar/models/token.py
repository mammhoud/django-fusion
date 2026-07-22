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

    Only defines ``Meta`` (app_label, db_table, indexes).  Everything
    else — fields, auth methods, sync cascade — comes from the base.
    """

    class Meta(BaseDeviceToken.Meta):
        abstract = False
        app_label = "pos_full"
        db_table = "cloud_device_tokens"
        indexes = [
            Index(fields=["token_hash"]),
            Index(fields=["device_id", "is_active"]),
            Index(fields=["role"]),
            Index(fields=["expires_at"]),
            Index(fields=["sync_status"]),
            Index(fields=["app_type", "sync_status"]),
        ]
