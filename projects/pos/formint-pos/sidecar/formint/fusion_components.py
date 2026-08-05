from typing import Any

from django_fusion.routes.components.dual_mode import FusionDualModeMixin
from django_fusion.routes.components.fragments import FragmentComponent


class BranchSummaryFragment(FusionDualModeMixin, FragmentComponent):
    """The first Formint render-first fragment.

    The component is intentionally small: it proves django-fusion rendering
    before the same domain section is consumed as a lean HTMX data fragment.
    Django owns the values and the fragment template; Astro owns the shell,
    skeleton, and target lifecycle.
    """

    fragment_name = "formint.branch_summary"
    template_name = "formint/branch_summary.html"
    fusion_render_first = True
    htmx_only = True

    def get_fragment_context(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_fragment_context(**kwargs)
        context.update(
            {
                "branches": 0,
                "orders_today": 0,
                "sync_status": "Planned",
            }
        )
        return context

    def get_fragment_data(self) -> dict[str, Any]:
        return {
            "branches": 0,
            "orders_today": 0,
            "sync_status": "Planned",
        }
