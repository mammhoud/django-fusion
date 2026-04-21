from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models, transaction
from django.db.models import Prefetch, Q, QuerySet
from django.utils import timezone

from apps import logger

User = get_user_model()


class MessageService:
    """
    Service for message operations.
    Delegates to django_rseal.pipelines.services.MessageServiceBase
    """

    @staticmethod
    def send_message(
        sender,
        recipient,
        subject: str,
        content: str,
        message_type: str = 'general',
        **kwargs
    ) -> Tuple[bool, str, Any]:
        """
        Send a message.

        Args:
            sender: Sending entity
            recipient: Receiving entity
            subject: Message subject
            content: Message content
            message_type: Type of message
            **kwargs: Additional message fields

        Returns:
            Tuple of (success, message, message_object)
        """
        from www.apps.accounts.models import Message

        try:
            # Create message
            message = Message.objects.create(
                sender_content_object=sender,
                recipient_content_object=recipient,
                subject=subject,
                content=content,
                message_type=message_type,
                **kwargs
            )

            # Send message
            message.send()

            # Invalidate cache
            cache_key = f"message_stats_{recipient.id}"
            cache.delete(cache_key)

            return True, "Message sent successfully", message

        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False, f"Error sending message: {str(e)}", None

    @staticmethod
    def get_message_analytics(
        user,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get message analytics for a user.

        Args:
            user: The user
            days: Days to analyze

        Returns:
            Dictionary with analytics
        """
        from django.db.models import Count, Q
        from django.db.models.functions import TruncDate

        from www.apps.accounts.models import Message

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        # Get user's messages in period
        user_type = ContentType.objects.get_for_model(user)

        received_messages = Message.objects.filter(
            recipient_content_type=user_type,
            recipient_object_id=user.id,
            created_at__range=[start_date, end_date]
        )

        sent_messages = Message.objects.filter(
            sender_content_type=user_type,
            sender_object_id=user.id,
            created_at__range=[start_date, end_date]
        )

        # Calculate metrics
        total_received = received_messages.count()
        total_sent = sent_messages.count()

        # Response rate
        replied_messages = received_messages.filter(replies__isnull=False).count()
        response_rate = (
            (replied_messages / total_received * 100)
            if total_received > 0 else 0
        )

        # Read rate
        read_messages = received_messages.filter(is_read=True).count()
        read_rate = (
            (read_messages / total_received * 100)
            if total_received > 0 else 0
        )

        # Messages by type
        received_by_type = dict(
            received_messages.values('message_type')
            .annotate(count=Count('id'))
        )

        # Daily activity
        daily_activity = list(
            received_messages.annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(
                received=Count('id'),
                read=Count('id', filter=Q(is_read=True))
            )
            .order_by('date')
        )

        # Top correspondents
        top_correspondents = list(
            received_messages.values(
                'sender_content_type__model',
                'sender_object_id'
            ).annotate(
                count=Count('id'),
                unread=Count('id', filter=Q(is_read=False))
            ).order_by('-count')[:5]
        )

        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': days,
            },
            'summary': {
                'total_received': total_received,
                'total_sent': total_sent,
                'response_rate': round(response_rate, 2),
                'read_rate': round(read_rate, 2),
                'unread_count': received_messages.filter(is_read=False).count(),
            },
            'breakdown': {
                'received_by_type': received_by_type,
                'sent_by_type': dict(
                    sent_messages.values('message_type')
                    .annotate(count=Count('id'))
                ),
            },
            'activity': {
                'daily_activity': daily_activity,
                'busiest_day': max(
                    daily_activity,
                    key=lambda x: x['received']
                ) if daily_activity else None,
            },
            'correspondents': {
                'top_correspondents': top_correspondents,
                'most_active': max(
                    top_correspondents,
                    key=lambda x: x['count']
                ) if top_correspondents else None,
            },
            'trends': MessageService._calculate_message_trends(daily_activity),
        }

    @staticmethod
    def _calculate_message_trends(daily_activity):
        """Calculate message trend analytics."""
        if not daily_activity:
            return {}

        # Calculate daily averages
        total_received = sum(day['received'] for day in daily_activity)
        avg_per_day = total_received / len(daily_activity)

        # Get recent trend (last 7 days vs previous 7 days)
        recent_days = daily_activity[-7:] if len(daily_activity) >= 7 else daily_activity
        previous_days = daily_activity[-14:-7] if len(daily_activity) >= 14 else []

        recent_avg = sum(day['received'] for day in recent_days) / len(recent_days) if recent_days else 0
        previous_avg = sum(day['received'] for day in previous_days) / len(previous_days) if previous_days else 0

        if previous_avg > 0:
            trend_percentage = ((recent_avg - previous_avg) / previous_avg) * 100
        else:
            trend_percentage = 100 if recent_avg > 0 else 0

        # Read rate trend
        recent_read = sum(day['read'] for day in recent_days)
        recent_total = sum(day['received'] for day in recent_days)
        recent_read_rate = (recent_read / recent_total * 100) if recent_total > 0 else 0

        return {
            'daily_average': round(avg_per_day, 2),
            'recent_trend': round(trend_percentage, 2),
            'trend_direction': 'up' if trend_percentage > 0 else 'down',
            'recent_read_rate': round(recent_read_rate, 2),
            'is_increasing': trend_percentage > 0,
        }
