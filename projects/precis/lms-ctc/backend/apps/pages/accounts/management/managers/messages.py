import logging

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.aggregates import Count
from django.utils import timezone
from django_fusion.management.managers.base import BaseManager, cached_method

logger = logging.getLogger(__name__)

class MessageManager(BaseManager):
    """
    Enhanced manager for Message model.
    """

    def get_user_messages(self, user, message_type=None, unread_only=False):
        """
        Get messages for a user.

        Args:
            user: The user
            message_type: Filter by message type
            unread_only: Only unread messages

        Returns:
            QuerySet of messages
        """
        # Get user's content type
        user_type = ContentType.objects.get_for_model(user)

        queryset = self.filter(
            recipient_content_type=user_type,
            recipient_object_id=user.id
        )

        if message_type:
            queryset = queryset.filter(message_type=message_type)

        if unread_only:
            queryset = queryset.filter(is_read=False)

        return queryset.order_by('-created_at')

    def get_conversation(self, sender, recipient, limit=50):
        """
        Get conversation between two parties.

        Args:
            sender: Sender object
            recipient: Recipient object
            limit: Maximum messages to return

        Returns:
            QuerySet of messages
        """
        sender_type = ContentType.objects.get_for_model(sender)
        recipient_type = ContentType.objects.get_for_model(recipient)

        # Messages from sender to recipient
        sent = self.filter(
            sender_content_type=sender_type,
            sender_object_id=sender.id,
            recipient_content_type=recipient_type,
            recipient_object_id=recipient.id
        )

        # Messages from recipient to sender
        received = self.filter(
            sender_content_type=recipient_type,
            sender_object_id=recipient.id,
            recipient_content_type=sender_type,
            recipient_object_id=sender.id
        )

        # Combine and order
        conversation = (sent | received).order_by('-created_at')[:limit]
        return conversation.order_by('created_at')

    def send_system_message(self, recipient, subject, content, **kwargs):
        """
        Send a system message.

        Args:
            recipient: Recipient object
            subject: Message subject
            content: Message content
            **kwargs: Additional message fields

        Returns:
            Sent message
        """
        from django.contrib.auth.models import User

        # Create system sender
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={'is_active': False}
        )

        message = self.create(
            sender_content_object=system_user,
            recipient_content_object=recipient,
            subject=subject,
            content=content,
            message_type='system',
            **kwargs
        )

        message.send()
        return message

    def send_bulk_messages(self, sender, recipients, subject, content_template, **kwargs):
        """
        Send messages to multiple recipients.

        Args:
            sender: Sender object
            recipients: List of recipient objects
            subject: Message subject
            content_template: Content template (can contain {recipient})
            **kwargs: Additional message fields

        Returns:
            List of sent messages
        """
        messages = []

        for recipient in recipients:
            # Format content with recipient info
            content = content_template.format(recipient=recipient)

            message = self.create(
                sender_content_object=sender,
                recipient_content_object=recipient,
                subject=subject,
                content=content,
                **kwargs
            )

            message.send()
            messages.append(message)

        return messages

    @cached_method(timeout=300)
    def get_message_statistics(self, user):
        """
        Get message statistics for a user.

        Args:
            user: The user

        Returns:
            Dictionary of statistics
        """
        messages = self.get_user_messages(user)

        return {
            'total_messages': messages.count(),
            'unread_messages': messages.filter(is_read=False).count(),
            'sent_messages': self.filter(
                sender_content_type=ContentType.objects.get_for_model(user),
                sender_object_id=user.id
            ).count(),
            'messages_by_type': dict(
                messages.values_list('message_type')
                .annotate(count=models.Count('id'))
            ),
            'messages_by_sender': self._get_top_senders(user),
            'recent_activity': self._get_recent_message_activity(user),
        }

    def _get_top_senders(self, user, limit=5):
        """Get top senders for a user."""
        user_type = ContentType.objects.get_for_model(user)

        # Get messages grouped by sender
        from django.db.models import Count

        return list(
            self.filter(
                recipient_content_type=user_type,
                recipient_object_id=user.id
            ).values(
                'sender_content_type__model',
                'sender_object_id'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:limit]
        )

    def _get_recent_message_activity(self, user):
        """Get recent message activity."""
        from django.db.models.functions import TruncDate

        user_type = ContentType.objects.get_for_model(user)

        return list(
            self.filter(
                recipient_content_type=user_type,
                recipient_object_id=user.id,
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('-date')[:7]
        )

    def cleanup_old_messages(self, days=365):
        """
        Clean up old messages.

        Args:
            days: Days threshold

        Returns:
            Number of deleted messages
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        # Get old messages (excluding important ones)
        old_messages = self.filter(
            created_at__lt=cutoff_date,
            priority__lt=3,  # Not high priority
            message_type__in=['general', 'notification']  # Not system or alerts
        )

        count = old_messages.count()
        old_messages.delete()

        return count

    def mark_conversation_as_read(self, user, other_party):
        """
        Mark all messages in a conversation as read.

        Args:
            user: The user
            other_party: Other party in conversation

        Returns:
            Number of messages marked as read
        """
        conversation = self.get_conversation(other_party, user)
        unread_messages = conversation.filter(is_read=False)

        count = unread_messages.count()
        unread_messages.update(is_read=True, read_at=timezone.now())

        return count
