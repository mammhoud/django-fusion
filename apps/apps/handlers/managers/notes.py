import logging
from typing import Any, Dict, List, Optional, Tuple

from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models
from django.utils import timezone

from django_grep.pipelines.managers import BaseManager, CachedManager, cached_method

logger = logging.getLogger(__name__)


class NoteManager(BaseManager):
    """
    Enhanced manager for Note model with advanced query methods.
    """
    
    def get_user_notes(self, user, include_shared=True, include_public=True):
        """
        Get all notes accessible by a user.
        
        Args:
            user: The user
            include_shared: Include notes shared with user
            include_public: Include public notes
        
        Returns:
            QuerySet of notes
        """
        from apps.handlers.models import Note
        
        # Notes created by user
        queryset = self.filter(created_by=user)
        
        if include_shared:
            # Notes shared with user
            shared_notes = self.filter(
                shared_with__user=user,
                visibility='shared'
            )
            queryset = queryset | shared_notes
        
        if include_public:
            # Public notes
            public_notes = self.filter(visibility='public')
            queryset = queryset | public_notes
        
        return queryset.distinct()
    
    @cached_method(timeout=300)
    def search_notes(self, user, query, **filters):
        """
        Search notes with full-text search capabilities.
        
        Args:
            user: The user
            query: Search query
            **filters: Additional filters
        
        Returns:
            QuerySet of matching notes
        """
        from django.db.models import Q
        
        # Base queryset
        queryset = self.get_user_notes(user)
        
        # Search query
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(summary__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        # Apply filters
        if tags := filters.get('tags'):
            queryset = queryset.filter(tags__name__in=tags)
        
        if visibility := filters.get('visibility'):
            queryset = queryset.filter(visibility=visibility)
        
        if is_pinned := filters.get('is_pinned'):
            queryset = queryset.filter(is_pinned=is_pinned)
        
        if is_archived := filters.get('is_archived'):
            queryset = queryset.filter(is_archived=is_archived)
        
        if date_from := filters.get('date_from'):
            queryset = queryset.filter(created_at__gte=date_from)
        
        if date_to := filters.get('date_to'):
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    def get_pinned_notes(self, user, limit=10):
        """
        Get pinned notes for a user.
        
        Args:
            user: The user
            limit: Maximum notes to return
        
        Returns:
            QuerySet of pinned notes
        """
        return self.get_user_notes(user).filter(
            is_pinned=True,
            is_archived=False
        ).order_by('-pinned_at')[:limit]
    
    def get_recent_notes(self, user, limit=10):
        """
        Get recent notes for a user.
        
        Args:
            user: The user
            limit: Maximum notes to return
        
        Returns:
            QuerySet of recent notes
        """
        return self.get_user_notes(user).filter(
            is_archived=False
        ).order_by('-created_at')[:limit]
    
    @cached_method(timeout=300)
    def get_note_statistics(self, user):
        """
        Get note statistics for a user.
        
        Args:
            user: The user
        
        Returns:
            Dictionary of statistics
        """
        notes = self.get_user_notes(user)
        
        stats = {
            'total_notes': notes.count(),
            'pinned_notes': notes.filter(is_pinned=True).count(),
            'archived_notes': notes.filter(is_archived=True).count(),
            'shared_notes': notes.filter(visibility='shared').count(),
            'public_notes': notes.filter(visibility='public').count(),
            'recent_notes_7d': notes.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count(),
            'notes_by_visibility': dict(
                notes.filter(visibility__in=['private', 'shared', 'public'])
                .values_list('visibility')
                .annotate(count=models.Count('id'))
            ),
            'notes_by_month': self._get_notes_by_month(notes),
        }
        
        return stats
    
    def _get_notes_by_month(self, notes):
        """Get note count by month."""
        from django.db.models.functions import TruncMonth
        
        return list(
            notes.annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=models.Count('id'))
            .order_by('-month')[:12]
        )
    
    def bulk_update_notes(self, note_ids, **updates):
        """
        Bulk update notes.
        
        Args:
            note_ids: List of note IDs
            **updates: Fields to update
        
        Returns:
            Number of updated notes
        """
        result = self.filter(id__in=note_ids).update(**updates)
        
        # Invalidate cache for affected users
        if result > 0:
            user_ids = self.filter(id__in=note_ids).values_list('created_by', flat=True).distinct()
            for user_id in user_ids:
                cache.delete(f"note_stats_{user_id}")
        
        return result
    
    def get_notes_by_tag(self, user, tag_name):
        """
        Get user's notes by tag.
        
        Args:
            user: The user
            tag_name: Tag name
        
        Returns:
            QuerySet of notes
        """
        return self.get_user_notes(user).filter(
            tags__name=tag_name
        ).order_by('-created_at')
    
    def get_notes_by_date_range(self, user, start_date, end_date):
        """
        Get user's notes within date range.
        
        Args:
            user: The user
            start_date: Start date
            end_date: End date
        
        Returns:
            QuerySet of notes
        """
        return self.get_user_notes(user).filter(
            created_at__range=[start_date, end_date]
        ).order_by('-created_at')

