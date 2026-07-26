"""
Notification Service for handling HTMX-triggered notifications.
"""
import json
from typing import TYPE_CHECKING

from django.http import HttpResponse

if TYPE_CHECKING:
    from django.http import HttpResponseBase


def trigger_notification(
    response: "HttpResponseBase",
    message: str,
    notification_type: str = "success",
) -> "HttpResponseBase":
    """
    Add HX-Trigger header to response for client-side notification display.

    Sets: HX-Trigger: {"showNotification": {"message": "...", "type": "..."}}

    The existing notification bundle (assets/static/js/modules/notifications/notification.js)
    listens for HTMX trigger headers and handles the "showNotification" event via
    `processTriggerHeader()`, reading `value.message` and `value.type` fields to
    display toast notifications. Supported types: "success", "error", "warning", "info".

    Args:
        response: Django HttpResponse to modify
        message: Notification message text
        notification_type: One of "success", "error", "warning", "info"

    Returns:
        Modified response with HX-Trigger header set
    """
    response["HX-Trigger"] = json.dumps({
        "showNotification": {
            "message": message,
            "type": notification_type,
        }
    })
    return response
