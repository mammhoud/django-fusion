
import json
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from apps.handlers.services import CertificateService, MessageService
from apps.LMS.services import CourseService, NoteService
from alliance import logger
from django_grep.comp.site import NotificationMixin, PageHandler

User = get_user_model()



class MessagesView(PageHandler, NotificationMixin):
    """
    Messages management view.
    """

    page_title = "Messages"
    template_name = "base_profile.html"
    fragment_name = "profile.messages"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get context data for messages page.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        if request.user.is_authenticated:
            try:
                # Get message statistics
                from apps.handlers.models import Message

                message_stats = Message.objects.get_message_statistics(request.user)

                # Get recent messages
                recent_messages = Message.objects.get_user_messages(
                    request.user, unread_only=False
                )[:10]

                # Get unread messages
                unread_messages = Message.objects.get_user_messages(request.user, unread_only=True)[
                    :5
                ]

                context.update(
                    {
                        "message_stats": message_stats,
                        "recent_messages": recent_messages,
                        "unread_messages": unread_messages,
                        "message_types": Message.MessageTypeChoices.choices,
                    }
                )

            except Exception as e:
                logger.error(f"Error getting messages context: {e}")
                self.show_notification(
                    message="Error loading messages",
                    level="error",
                    title="Error",
                    duration=5000,
                    request=request,
                )

        return context

    @require_POST
    @csrf_exempt
    @login_required
    def send_message(self, request: HttpRequest) -> JsonResponse:
        """
        Send a message.
        """
        try:
            data = json.loads(request.body) if request.body else {}

            # Get recipient
            from django.contrib.auth.models import User

            try:
                recipient = User.objects.get(id=data.get("recipient_id"))
            except User.DoesNotExist:
                return JsonResponse(
                    {"status": "error", "message": "Recipient not found"}, status=404
                )

            success, message, message_obj = MessageService.send_message(
                sender=request.user,
                recipient=recipient,
                subject=data.get("subject", ""),
                content=data.get("content", ""),
                message_type=data.get("message_type", "general"),
                priority=data.get("priority", 1),
            )

            if success:
                self.show_notification(
                    message=message,
                    level="success",
                    title="Message Sent",
                    duration=3000,
                    request=request,
                )

                return JsonResponse(
                    {
                        "status": "success",
                        "message": message,
                        "message_id": str(message_obj.id),
                        "sent_at": message_obj.sent_at.isoformat() if message_obj.sent_at else None,
                    }
                )
            else:
                self.show_notification(
                    message=message,
                    level="error",
                    title="Send Failed",
                    duration=5000,
                    request=request,
                )

                return JsonResponse({"status": "error", "message": message}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse(
                {"status": "error", "message": f"Error sending message: {str(e)}"}, status=500
            )

