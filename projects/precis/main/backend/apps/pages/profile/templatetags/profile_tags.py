"""
Template filters for the profile app.

``split`` splits a string on a separator and returns the parts — used by
``profile/settings/notifications.html`` to build the quiet-hours dropdown
from a ``"00|01|..."`` literal.
"""

from __future__ import annotations

from django import template

register = template.Library()


@register.filter
def split(value, separator="|"):
    """Split ``value`` on ``separator`` and return the list of parts."""
    if value is None:
        return []
    return str(value).split(separator)
