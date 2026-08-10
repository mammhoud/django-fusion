from django_fusion.comp.tags.components import register


@register.filter
def discount_price(price, discount_percentage):
    try:
        discount = (price * discount_percentage) / 100
        return price - discount
    except (TypeError, ValueError):
        return price
