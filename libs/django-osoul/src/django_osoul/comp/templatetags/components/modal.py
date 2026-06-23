from django import template

register = template.Library()


@register.inclusion_tag("modal.html")
def generate_modal(modal_id, modal_title, modal_body):
    """
    Template tag to generate a modal dialog.

    Usage:
        {% generate_modal modal_id="myModal" modal_title="Modal Title" modal_body="This is the body of the modal" %}
    """
    return {"modal_id": modal_id, "modal_title": modal_title, "modal_body": modal_body}
