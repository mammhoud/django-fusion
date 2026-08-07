from datetime import timedelta
from typing import Any

from django.utils import timezone

from django_fusion.routes.components.dual_mode import FusionDualModeMixin
from django_fusion.routes.components.fragments import FragmentComponent

from models.node import Node
from models.pos import Sale
from models.sync import SyncLog


class BranchSummaryFragment(FusionDualModeMixin, FragmentComponent):
    """The first Formint render-first fragment.

    The component is intentionally small: it proves django-fusion rendering
    before the same domain section is consumed as a lean HTMX data fragment.
    Django owns the values and the fragment template; Astro owns the shell,
    skeleton, and target lifecycle.

    The summary values are computed from the live database so the fragment
    renders real rows once demo data is seeded:

    * ``branches``      — active ``Node`` count (registered POS branches)
    * ``orders_today``  — ``Sale`` rows created today
    * ``sync_status``   — healthy if any successful sync happened recently
    """

    fragment_name = "formint.branch_summary"
    template_name = "formint/branch_summary.html"
    fusion_render_first = True
    htmx_only = True

    def get_branch_summary(self) -> dict[str, Any]:
        branches = Node.objects.filter(is_active=True).count()
        orders_today = Sale.objects.filter(
            sale_date__date=timezone.localdate()
        ).count()
        recent_ok = SyncLog.objects.filter(
            status="success",
            created_at__gte=timezone.now() - timedelta(hours=24),
        ).exists()
        sync_status = "Synced" if recent_ok else ("Pending" if branches else "Planned")
        return {
            "branches": branches,
            "orders_today": orders_today,
            "sync_status": sync_status,
        }

    def get_fragment_context(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_fragment_context(**kwargs)
        context.update(self.get_branch_summary())
        return context

    def get_fragment_data(self) -> dict[str, Any]:
        return self.get_branch_summary()
