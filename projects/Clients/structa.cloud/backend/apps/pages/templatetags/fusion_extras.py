"""Precis Landing template filters for the backend render road."""

from django import template

register = template.Library()


@register.filter
def class_name(value):
    """Return the model class name of a page (e.g. ``PhasePage``).

    Django templates cannot resolve ``__class__`` directly; the HTMX fragment
    template uses this filter to pick the phase/prompt fragment road.
    """
    return value.__class__.__name__
