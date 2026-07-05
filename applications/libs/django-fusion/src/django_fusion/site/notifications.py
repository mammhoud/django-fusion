"""
Enhanced Unified Notification System with SSE Support
====================================================
Combines the original NotificationMixin with the NotificationMixin
into a single, consistent API without conflicts.
"""

import json
import logging
import time
from collections.abc import Generator
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union

from django.contrib import messages as django_messages
from django.http import HttpRequest, HttpResponse, StreamingHttpResponse
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


class NotificationLevel(Enum):
    """Notification severity levels."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class UnifiedNotification:
    """Enhanced notification object with unified features."""

    def __init__(
        self,
        message: str,
        level: Union[str, NotificationLevel] = "info",
        title: str = "",
        icon: str = "",
        duration: int = 5000,
        dismissible: bool = True,
        position: str = "top-right",
        data: dict | None = None,
        tags: list[str] | None = None,
        source: str = "system",
        redirect_url: str | None = None,
        replace_form: bool = False,
        target: str | None = None,
        swap: str = "innerHTML",
    ):
        self.message = message
        self.level = NotificationLevel(level) if isinstance(level, str) else level
        self.title = title
        self.icon = icon
        self.duration = duration
        self.dismissible = dismissible
        self.position = position
        self.data = data or {}
        self.tags = tags or []
        self.source = source
        self.redirect_url = redirect_url
        self.replace_form = replace_form
        self.target = target
        self.swap = swap
        self.timestamp = time.time()
        self.id = f"notif_{int(self.timestamp)}_{hash(message) % 10000}"

    def to_dict(self) -> dict[str, Any]:
        """Convert notification to dictionary."""
        return {
            "id": self.id,
            "message": self.message,
            "level": self.level.value,
            "title": self.title,
            "icon": self.icon,
            "duration": self.duration,
            "dismissible": self.dismissible,
            "position": self.position,
            "data": self.data,
            "tags": self.tags,
            "source": self.source,
            "timestamp": self.timestamp,
            "redirect_url": self.redirect_url,
            "replace_form": self.replace_form,
            "target": self.target,
            "swap": self.swap,
        }

    def to_sse_format(self) -> str:
        """Convert to SSE format."""
        data = self.to_dict()
        return f"event: notification\ndata: {json.dumps(data)}\n\n"

    def to_htmx_trigger(self) -> dict[str, Any]:
        """Convert to HTMX trigger format."""
        return {
            "showNotification": self.to_dict()
        }


class SSENotificationStream:
    """
    Server-Sent Events (SSE) notification stream generator.
    Provides real-time notifications via text/event-stream.
    """

    def __init__(self, request: HttpRequest):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None
        self.connected_at = datetime.now()
        self.heartbeat_interval = 15  # seconds
        self.max_connection_time = 3600  # 1 hour

    def stream(self) -> Generator[str, None, None]:
        """Generate SSE stream."""
        try:
            # Send initial connection event
            yield self.format_sse_event("connection", {
                "status": "connected",
                "user": self.user.username if self.user else "anonymous",
                "timestamp": self.connected_at.isoformat(),
                "message": "SSE notification stream connected"
            })

            # Send any pending notifications
            pending_notifications = self.get_pending_notifications()
            for notification in pending_notifications:
                yield notification.to_sse_format()

            # Send heartbeat loop
            start_time = time.time()
            heartbeat_count = 0

            while True:
                # Check connection timeout
                if time.time() - start_time > self.max_connection_time:
                    yield self.format_sse_event("connection", {
                        "status": "timeout",
                        "message": "Connection timeout"
                    })
                    break

                # Check if client disconnected
                if self.request.META.get('wsgi.disconnect', False):
                    logger.info("Client disconnected from SSE stream")
                    break

                # Send heartbeat
                if heartbeat_count % self.heartbeat_interval == 0:
                    yield self.format_sse_event("heartbeat", {
                        "timestamp": datetime.now().isoformat(),
                        "count": heartbeat_count
                    })

                # Check for new notifications
                new_notifications = self.check_new_notifications()
                for notification in new_notifications:
                    yield notification.to_sse_format()

                # Small sleep to prevent CPU spinning
                time.sleep(1)
                heartbeat_count += 1

        except GeneratorExit:
            logger.info("SSE stream generator exited")
        except Exception as e:
            logger.error(f"Error in SSE stream: {e}")
            yield self.format_sse_event("error", {
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })

    def format_sse_event(self, event_type: str, data: dict) -> str:
        """Format data as SSE event."""
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"

    def get_pending_notifications(self) -> list[UnifiedNotification]:
        """Get pending notifications for user."""
        if not self.user:
            return []

        # Get from notification store
        from . import notification_store
        return notification_store.get(self.user.id)

    def check_new_notifications(self) -> list[UnifiedNotification]:
        """Check for new notifications (placeholder implementation)."""
        # In production, this would check a message queue or database
        return []


class NotificationMixin:
    """
    Unified notification system that works across all request types:
    - Traditional Django requests
    - HTMX requests
    - SSE streams
    - Both Django messages and custom notifications
    """

    # Default configuration
    DEFAULT_DURATION = 5000
    DEFAULT_POSITION = "top-right"
    DEFAULT_TARGET = ".notifications-init"
    DEFAULT_SWAP = "none"

    def _get_request(self) -> Optional[HttpRequest]:
        """Get request from self if available."""
        return getattr(self, 'request', None)

    def is_htmx(self, request: Optional[HttpRequest] = None) -> bool:
        """Check if request is HTMX."""
        request = request or self._get_request()
        return hasattr(request, 'htmx') and request.htmx if request else False

    def _create_notification_object(
        self,
        message: str,
        level: Union[str, NotificationLevel] = "info",
        **kwargs
    ) -> UnifiedNotification:
        """Create a UnifiedNotification object."""
        return UnifiedNotification(
            message=message,
            level=level,
            **kwargs
        )

    def _create_htmx_redirect_response(self, redirect_url: str, notification: UnifiedNotification) -> HttpResponse:
        """Create an HTMX response with redirect and notification."""
        from django_fusion.site.response import HttpResponseClientRedirect

        response = HttpResponseClientRedirect(redirect_url)
        response["HX-Trigger"] = json.dumps(notification.to_htmx_trigger(), default=str)
        return response

    def _create_htmx_notification_response(self, notification: UnifiedNotification) -> HttpResponse:
        """Create HTMX response with notification trigger."""
        response = HttpResponse(status=200)

        # Set HTMX headers
        response["HX-Reswap"] = "none"
        response["HX-Swap"] = "none"

        # Set notification trigger
        response["HX-Trigger"] = json.dumps(notification.to_htmx_trigger(), default=str)

        # Set target if provided
        if notification.target:
            response["HX-Target"] = notification.target
            response["HX-Swap"] = notification.swap

        return response

    def _create_sse_stream_response(self, request: HttpRequest) -> StreamingHttpResponse:
        """Create SSE stream response."""
        sse_stream = SSENotificationStream(request)

        response = StreamingHttpResponse(
            sse_stream.stream(),
            content_type='text/event-stream'
        )

        # Add SSE headers
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # Disable buffering for nginx

        return response

    def _send_django_notification(self, notification: UnifiedNotification, request: HttpRequest):
        """Send notification via Django messages framework."""
        level_map = {
            NotificationLevel.SUCCESS: django_messages.SUCCESS,
            NotificationLevel.ERROR: django_messages.ERROR,
            NotificationLevel.WARNING: django_messages.WARNING,
            NotificationLevel.INFO: django_messages.INFO,
            NotificationLevel.DEBUG: django_messages.DEBUG,
        }

        level = level_map.get(notification.level, django_messages.INFO)

        # Store extra data in message tags
        extra_data = {
            "title": notification.title,
            "icon": notification.icon,
            "duration": notification.duration,
            "data": notification.data,
            "source": notification.source,
            "id": notification.id,
            "position": notification.position,
            "redirect_url": notification.redirect_url,
            "replace_form": notification.replace_form,
            "target": notification.target,
            "swap": notification.swap,
        }

        django_messages.add_message(
            request,
            level,
            notification.message,
            extra_tags=json.dumps(extra_data, default=str)
        )

    def show_notification(
        self,
        message: str,
        level: Union[str, NotificationLevel] = "info",
        title: str = "",
        duration: int = None,
        redirect_url: str = None,
        replace_form: bool = False,
        target: str = None,
        swap: str = "none",
        request: HttpRequest = None,
        sse_stream: bool = False,
        **kwargs
    ) -> Optional[Union[HttpResponse, StreamingHttpResponse]]:
        """
        Unified notification method that works with all request types.
        """
        request = request or self._get_request()
        if not request:
            logger.warning("No request available for notification")
            return None

        # Handle SSE stream request
        if sse_stream:
            return self._create_sse_stream_response(request)

        # Create notification object
        notification = self._create_notification_object(
            message=message,
            level=level,
            title=title,
            duration=duration or self.DEFAULT_DURATION,
            redirect_url=redirect_url,
            replace_form=replace_form,
            target=target or self.DEFAULT_TARGET,
            swap=swap or self.DEFAULT_SWAP,
            **kwargs
        )

        # Handle HTMX requests
        if self.is_htmx(request):
            if hasattr(request, 'accept') and 'text/event-stream' in request.headers.get('Accept', ''):
                return HttpResponse(
                    notification.to_sse_format(),
                    content_type='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'}
                )

            if replace_form:
                notification.target = target or ".fragment--form"
                notification.swap = "innerHTML"

            if redirect_url:
                return self._create_htmx_redirect_response(redirect_url, notification)

            return self._create_htmx_notification_response(notification)

        # Handle traditional Django requests
        self._send_django_notification(notification, request)

        if redirect_url:
            return redirect(redirect_url)

        return None

    # Alias for compatibility
    def send_notification(self, **kwargs):
        """Alias for show_notification for backward compatibility."""
        return self.show_notification(**kwargs)

    def send_notification_stream(self, request: HttpRequest, **kwargs) -> StreamingHttpResponse:
        """Start SSE notification stream."""
        return self._create_sse_stream_response(request)

    def broadcast_notification(
        self,
        message: str,
        level: Union[str, NotificationLevel] = "info",
        title: str = "",
        user_ids: list[int | str] | None = None,
        **kwargs
    ):
        """Broadcast notification to multiple users."""
        notification = self._create_notification_object(
            message=message,
            level=level,
            title=title,
            **kwargs
        )

        from . import notification_store

        if user_ids is None:
            logger.info(f"Broadcasting notification to all users: {message}")
        else:
            for user_id in user_ids:
                notification_store.add(user_id, notification)
                logger.info(f"Added notification for user {user_id}: {message}")

    # Convenience methods
    def add_success(self, message: str, **kwargs) -> Optional[Union[HttpResponse, StreamingHttpResponse]]:
        """Show success notification."""
        return self.show_notification(message, "success", **kwargs)

    def add_error(self, message: str, **kwargs) -> Optional[Union[HttpResponse, StreamingHttpResponse]]:
        """Show error notification."""
        return self.show_notification(message, "error", **kwargs)

    def add_warning(self, message: str, **kwargs) -> Optional[Union[HttpResponse, StreamingHttpResponse]]:
        """Show warning notification."""
        return self.show_notification(message, "warning", **kwargs)

    def add_info(self, message: str, **kwargs) -> Optional[Union[HttpResponse, StreamingHttpResponse]]:
        """Show info notification."""
        return self.show_notification(message, "info", **kwargs)

    def add_debug(self, message: str, **kwargs) -> Optional[Union[HttpResponse, StreamingHttpResponse]]:
        """Show debug notification."""
        return self.show_notification(message, "debug", **kwargs)

    def get_notifications(self, request: HttpRequest) -> list[dict]:
        """Get all pending notifications for the request."""
        notifications = []

        for message in django_messages.get_messages(request):
            extra_data = {}
            if message.extra_tags:
                try:
                    extra_data = json.loads(message.extra_tags)
                except (json.JSONDecodeError, TypeError):
                    pass

            notification_data = {
                "id": extra_data.get("id", f"msg_{hash(message)}"),
                "message": str(message),
                "level": message.level_tag or "info",
                "title": extra_data.get("title", ""),
                "icon": extra_data.get("icon", ""),
                "duration": extra_data.get("duration", self.DEFAULT_DURATION),
                "data": extra_data.get("data", {}),
                "source": extra_data.get("source", "django"),
                "timestamp": extra_data.get("timestamp", time.time()),
                "position": extra_data.get("position", self.DEFAULT_POSITION),
            }

            notifications.append(notification_data)

        return notifications

    def handle_validation_error(
        self,
        error_message: str,
        form_data: dict = None,
        redirect_to: str = None,
        target: str = ".fragment--form",
        swap: str = "innerHTML",
        request: HttpRequest = None,
    ) -> HttpResponse:
        """Handle form validation errors."""
        request = request or self._get_request()
        return self.show_notification(
            message=error_message,
            level="error",
            title="Validation Error",
            duration=5000,
            redirect_url=redirect_to,
            replace_form=True,
            target=target,
            swap=swap,
            request=request
        )

    def handle_generic_error(
        self,
        error_message: str,
        exception: Exception = None,
        redirect_to: str = None,
        target: str = ".fragment--form",
        swap: str = "innerHTML",
        request: HttpRequest = None,
    ) -> HttpResponse:
        """Handle generic errors with logging."""
        if exception:
            logger.error(f"{error_message}: {exception}")

        request = request or self._get_request()
        return self.show_notification(
            message=error_message,
            level="error",
            title="Error",
            duration=5000,
            redirect_url=redirect_to,
            replace_form=True,
            target=target,
            swap=swap,
            request=request
        )


class NotificationStore:
    """Server-side notification store for real-time notifications."""

    def __init__(self):
        self._store = {}
        self._expiry_time = 3600  # 1 hour

    def add(self, user_id: int | str, notification: UnifiedNotification):
        """Add notification for specific user."""
        if user_id not in self._store:
            self._store[user_id] = []

        self._clean_expired(user_id)

        self._store[user_id].append({
            "notification": notification,
            "added_at": time.time()
        })

    def get(self, user_id: int | str) -> list[UnifiedNotification]:
        """Get all non-expired notifications for user."""
        if user_id not in self._store:
            return []

        self._clean_expired(user_id)

        return [item["notification"] for item in self._store[user_id]]

    def clear(self, user_id: int | str):
        """Clear all notifications for user."""
        if user_id in self._store:
            del self._store[user_id]

    def pop(self, user_id: int | str) -> list[UnifiedNotification]:
        """Get and clear notifications for user."""
        notifications = self.get(user_id)
        self.clear(user_id)
        return notifications

    def _clean_expired(self, user_id: int | str):
        """Remove expired notifications."""
        if user_id not in self._store:
            return

        current_time = time.time()
        self._store[user_id] = [
            item for item in self._store[user_id]
            if current_time - item["added_at"] < self._expiry_time
        ]

        if not self._store[user_id]:
            del self._store[user_id]


# Global notification store
notification_store = NotificationStore()
