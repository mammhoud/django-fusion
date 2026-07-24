"""
Template tags and filters for django-fusion.
Provides reusable template functionality for Django projects.

Removed in Phase 2 cleanup (unused by both sites, duplicated Django builtins):
  - truncate_words  → use Django's built-in {{ text|truncatewords:N }}
  - file_size       → rarely needed, easy to inline
  - add_class       → use django-widget-tweaks instead
  - placeholder     → use django-widget-tweaks instead

Retained tags are documented in docs/templatetags.md.
"""
from django import template
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()


# ---------------------------------------------------------------------------
# Filters — time & duration
# ---------------------------------------------------------------------------

@register.filter
def format_duration(seconds):
    """
    Format seconds as human-readable duration.

    Usage:  {{ video.duration|format_duration }}
    Output: 3665 → "1h 1m 5s" | 125 → "2m 5s" | 45 → "45s"
    """
    if not seconds:
        return "0s"
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes, secs = divmod(seconds, 60)
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        parts = [f"{hours}h"]
        if minutes:
            parts.append(f"{minutes}m")
        if secs:
            parts.append(f"{secs}s")
        return " ".join(parts)


@register.filter
def relative_time(dt):
    """
    Format datetime as relative time string.

    Usage:  {{ post.created_at|relative_time }}
    Output: "2 hours ago" | "3 days ago" | "just now"
    """
    if not dt:
        return ""
    now = timezone.now()
    diff = now - dt
    if diff.days > 365:
        n = diff.days // 365
        return f"{n} year{'s' if n > 1 else ''} ago"
    elif diff.days > 30:
        n = diff.days // 30
        return f"{n} month{'s' if n > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        n = diff.seconds // 3600
        return f"{n} hour{'s' if n > 1 else ''} ago"
    elif diff.seconds > 60:
        n = diff.seconds // 60
        return f"{n} minute{'s' if n > 1 else ''} ago"
    return "just now"


# ---------------------------------------------------------------------------
# Filters — text
# ---------------------------------------------------------------------------

@register.filter
def truncate_chars(text, num_chars=100):
    """
    Truncate text to N characters (adds "...").

    Usage:  {{ description|truncate_chars:50 }}
    Note:   For word-boundary truncation use Django's built-in truncatewords.
    """
    if not text:
        return ""
    if len(text) <= num_chars:
        return text
    return text[:num_chars] + "..."


@register.filter
def highlight(text, search_term):
    """
    Wrap occurrences of search_term in <mark> tags.

    Usage:  {{ content|highlight:search_query }}
    Output: "Hello <mark>world</mark>"
    """
    if not text or not search_term:
        return text
    import re
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    highlighted = pattern.sub(f"<mark>{search_term}</mark>", escape(text))
    return mark_safe(highlighted)


# ---------------------------------------------------------------------------
# Filters — numbers & math
# ---------------------------------------------------------------------------

@register.filter
def percentage(value, total):
    """
    Calculate percentage of value relative to total.

    Usage:  {{ completed|percentage:total }}
    Output: 75 / 100 → "75%"
    """
    if not total or total == 0:
        return "0%"
    try:
        return f"{(float(value) / float(total)) * 100:.0f}%"
    except (ValueError, TypeError):
        return "0%"


@register.filter
def format_currency(value, currency="USD"):
    """
    Format a number as currency.

    Usage:  {{ price|format_currency }}  or  {{ price|format_currency:"EUR" }}
    Output: 1234.56 → "$1,234.56"
    """
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    try:
        v = float(value)
        sym = symbols.get(currency, "")
        return f"{sym}{v:,.2f}" if sym else f"{v:,.2f} {currency}"
    except (ValueError, TypeError):
        return f"0.00 {currency}"


@register.filter
def multiply(value, arg):
    """Multiply value by arg.  Usage: {{ price|multiply:quantity }}"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def divide(value, arg):
    """Divide value by arg.  Usage: {{ total|divide:count }}"""
    try:
        a = float(arg)
        return 0 if a == 0 else float(value) / a
    except (ValueError, TypeError):
        return 0


@register.filter
def get_item(dictionary, key):
    """Get dict item by key.  Usage: {{ my_dict|get_item:"key_name" }}"""
    if not dictionary:
        return None
    return dictionary.get(key)


# ---------------------------------------------------------------------------
# Simple tags — rendering
# ---------------------------------------------------------------------------

@register.simple_tag
def render_widget(obj, template_name=None):
    """
    Render object using its widget template.

    Usage:  {% render_widget article %}
    Looks for: templates/widgets/<model_name>.html
    """
    if template_name is None:
        template_name = f"widgets/{obj._meta.model_name}.html"
    return render_to_string(template_name, {"object": obj})


@register.simple_tag
def render_card(obj, card_type="default"):
    """
    Render object as a card component.

    Usage:  {% render_card article "featured" %}
    Looks for: templates/cards/<model_name>_<card_type>.html
    """
    template_name = f"cards/{obj._meta.model_name}_{card_type}.html"
    return render_to_string(template_name, {"object": obj})


@register.simple_tag
def query_string(request, **kwargs):
    """
    Build a query string with updated parameters.

    Usage:  {% query_string request page=2 sort="name" %}
    Output: ?page=2&sort=name&existing=value
    """
    query_dict = request.GET.copy()
    for key, value in kwargs.items():
        if value is None:
            query_dict.pop(key, None)
        else:
            query_dict[key] = value
    return f"?{query_dict.urlencode()}" if query_dict else ""


