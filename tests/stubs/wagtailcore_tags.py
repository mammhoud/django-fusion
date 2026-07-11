"""Stub tag library for wagtailcore_tags in the django-fusion test environment.

The canonical django_fusion/comp/templates/components/form/form_block.html
template loads wagtailcore_tags for production use (Wagtail richtext rendering).
The test environment doesn't have Wagtail installed, so this stub provides
an empty Library plus a pass-through `richtext` filter so get_template()
can still parse the template.
"""
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.filter
def richtext(value):
    """Pass-through richtext filter for the test environment.

    In production this would render Wagtail rich-text fields as HTML.
    In tests we just return the value as a safe string so the template
    can be parsed and rendered without Wagtail installed.
    """
    if value is None:
        return ""
    return mark_safe(str(value))
