from django import template

register = template.Library()


@register.inclusion_tag("table.html")
def generate_table(columns, rows):
    """
    Template tag to generate a table with dynamic columns and rows.

    Usage:
        {% generate_table columns=columns rows=rows %}
    """
    return {"columns": columns, "rows": rows}


@register.inclusion_tag("table.html")
def generate_table_rows(fields, qs, *args, **kwargs):
    """
    Template tag to generate table rows based on the provided fields and queryset.

    Usage:
        {% generate_table_rows fields qs %}
    """
    context = {"fields": fields, "qs": qs}
    return context
