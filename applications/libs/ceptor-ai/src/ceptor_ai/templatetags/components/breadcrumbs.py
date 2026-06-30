import logging

from django import template
from django.template.context import Context

# Viewset belongs to rseal (routing concept) — keep pointing to ceptor_ai
from wagtail.models import Page

logger = logging.getLogger(__name__)

register = template.Library()


@register.inclusion_tag("tags/breadcrumbs.html", takes_context=True)
def breadcrumbs(context: Context):
    """
    Render breadcrumbs for current Wagtail page.
    """
    self = context.get("self")
    if not self or self.depth <= 2:
        ancestors = ()
    else:
        ancestors = Page.objects.ancestor_of(self, inclusive=True).filter(depth__gt=1)
    return {
        "ancestors": ancestors,
        "request": context["request"],
    }
