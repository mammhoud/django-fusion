import calendar

from django import template
from django.utils.timezone import now

register = template.Library()


@register.simple_tag
def generate_calendar(year=None, month=None):
    """
    Template tag to generate a calendar view for the specified month and year.

    Usage:
        {% generate_calendar year=2024 month=5 %}
    """
    if not year or not month:
        year, month = now().year, now().month
    cal = calendar.monthcalendar(year, month)
    return {"year": year, "month": month, "calendar": cal}
