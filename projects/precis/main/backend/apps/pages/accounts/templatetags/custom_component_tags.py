from django import template

from apps.pages.accounts.management.renderers import dynamic_renderer

register = template.Library()

@register.simple_tag(takes_context=True)
def render_dynamic_html(context, html_file):
    """
    Renders an uploaded HTML file using the DynamicComponentRenderer.
    """
    return dynamic_renderer.render(html_file, context)
