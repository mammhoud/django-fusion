from django import template

register = template.Library()


@register.inclusion_tag("card.html")
def generate_card(title, content, image=None):
    """
    Template tag to generate a card component with a title, content, and optional image.

    Usage:
        {% generate_card title="Card Title" content="Card content here" %}
        {% generate_card title="Card Title" content="Card content here" image="image_url.jpg" %}
    """
    return {"title": title, "content": content, "image": image}
