"""
Breadcrumb template tag for django-fusion.

Usage::

    {% load components.breadcrumbs %}

    {% breadcrumbs component %}
"""

from __future__ import annotations

from typing import Any

from django_fusion.comp.tags.components import register


@register.inclusion_tag("fusion/components/breadcrumbs.html")
def breadcrumbs(component: Any) -> dict[str, Any]:
    """
    Render breadcrumb trail for a routable component.

    Usage::

        {% breadcrumbs component %}

    Template: ``fusion/components/breadcrumbs.html``
    """
    crumbs = []
    if hasattr(component, "get_breadcrumbs"):
        crumbs = component.get_breadcrumbs()
    return {"breadcrumbs": crumbs}
