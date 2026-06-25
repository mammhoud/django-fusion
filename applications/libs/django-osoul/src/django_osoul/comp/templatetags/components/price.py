from django import template

register = template.Library()


@register.filter
def discount_price(price, discount_percentage):
    try:
        discount = (price * discount_percentage) / 100
        return price - discount
    except (TypeError, ValueError):
        return price
