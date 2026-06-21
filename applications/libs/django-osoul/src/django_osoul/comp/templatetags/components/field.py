from django import template

register = template.Library()


@register.filter
def get_field_value(obj, field_name):
    """
    Custom filter to get the value of a field dynamically from a model instance.

    Usage:
        {{ row|get_field_value:'field_name' }}
    """
    try:
        return getattr(obj, field_name, "")
    except AttributeError:
        return ""


@register.simple_tag
def render_field(field, label=None):
    """
    Template tag to render a form field with optional custom labels.

    Usage:
        {% render_field field %}
        {% render_field field label="Custom Label" %}
    """
    return {"field": field, "label": label if label else field.label}
