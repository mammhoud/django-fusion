from django import template

register = template.Library()


@register.inclusion_tag("notification.html")
def generate_notification(message, notification_type="info"):
    """
    Template tag to generate a notification message.

    Usage:
        {% generate_notification message="Data saved successfully" notification_type="success" %}
        {% generate_notification message="Error occurred!" notification_type="error" %}
    """
    return {"message": message, "notification_type": notification_type}
