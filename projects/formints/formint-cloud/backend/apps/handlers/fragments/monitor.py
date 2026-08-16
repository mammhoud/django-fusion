"""POS Cloud — django-fusion monitor tile fragment.

Cloud backup + sync monitor tile. Consumed via the ``{% comp %}`` tag or
rendered directly at ``/fusion/monitor``.

Usage:
    {% comp "core.monitor.tile" / %}
"""

from django_fusion.routes.components.fragments import FragmentComponent

from apps.core.models import BackupRun, SyncQueueItem


class MonitorTileView(FragmentComponent):
    """Display the latest backup status and pending sync queue depth."""

    fragment_name = "core.monitor.tile"

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["latest_backup"] = BackupRun.objects.order_by("-started_at").first()
        context["sync_queue_depth"] = SyncQueueItem.objects.count()
        return context
