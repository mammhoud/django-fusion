from django import template

register = template.Library()


@register.filter
def filter_by_url(submenu, url):
    """
    Recursively filters a submenu structure to determine if the URL matches any item's URL.

    Usage:
        {% if submenu|filter_by_url:request %}
    """
    if submenu:
        for subitem in submenu:
            subitem_url = subitem.get("url")
            if subitem_url in [url.path, url.resolver_match.url_name]:
                return True
            if subitem.get("submenu") and filter_by_url(subitem["submenu"], url):
                return True
    return False
