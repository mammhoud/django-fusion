from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def render_bundle(bundle_name, *args, **kwargs):
    """Render bundle - returns empty string to skip webpack errors"""
    return mark_safe('')

@register.simple_tag
def render_js(bundle_name):
    """Render JS bundle - returns empty string"""
    return mark_safe('')

@register.simple_tag
def render_css(bundle_name):
    """Render CSS bundle - returns empty string"""
    return mark_safe('')
