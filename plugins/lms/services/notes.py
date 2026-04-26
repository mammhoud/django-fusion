
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from django.core.cache import cache
from django.utils import timezone

import logging
logger = logging.getLogger(__name__)


class NoteService:
    """
    Service for note operations.
    """
    
    @staticmethod
    def create_note(
        user,
        title: str,
        content: str,
        content_object=None,
        tags: List[str] = None,
        visibility: str = 'private',
        **kwargs
    ) -> Tuple[bool, str, Any]:
        """
        Create a new note.
        
        Args:
            user: Creating user
            title: Note title
            content: Note content
            content_object: Associated object
            tags: List of tag names
            visibility: Note visibility
            **kwargs: Additional note fields
        
        Returns:
            Tuple of (success, message, note)
        """
        from plugins.accounts.models import Note, Tag
        
        try:
            # Create note
            note = Note.objects.create(
                title=title,
                content=content,
                created_by=user,
                visibility=visibility,
                **kwargs
            )
            
            # Associate with content object if provided
            if content_object:
                note.content_object = content_object
                note.save()
            
            # Add tags
            if tags:
                tag_objects = []
                for tag_name in tags:
                    tag, _ = Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={'color': '#3B82F6'}
                    )
                    tag_objects.append(tag)
                
                note.tags.set(tag_objects)
            
            # Generate summary
            note.generate_summary()
            
            # Invalidate cache
            cache_key = f"note_stats_{user.id}"
            cache.delete(cache_key)
            
            return True, "Note created successfully", note
            
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            return False, f"Error creating note: {str(e)}", None
    
    @staticmethod
    def update_note(
        note_id: str,
        user,
        **updates
    ) -> Tuple[bool, str, Any]:
        """
        Update an existing note.
        
        Args:
            note_id: Note ID
            user: Updating user
            **updates: Fields to update
        
        Returns:
            Tuple of (success, message, note)
        """
        from plugins.accounts.models import Note
        
        try:
            note = Note.objects.get(id=note_id)
            
            # Check permissions
            if note.created_by != user and note.visibility != 'public':
                return False, "You don't have permission to update this note", None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(note, field):
                    setattr(note, field, value)
            
            note.save()
            
            # Invalidate cache
            cache_key = f"note_stats_{user.id}"
            cache.delete(cache_key)
            
            return True, "Note updated successfully", note
            
        except Note.DoesNotExist:
            return False, "Note not found", None
        except Exception as e:
            logger.error(f"Error updating note: {e}")
            return False, f"Error updating note: {str(e)}", None
    
    @staticmethod
    def share_note(
        note_id: str,
        user,
        share_with: List,
        can_edit: bool = False,
        can_delete: bool = False,
        expires_at: datetime = None
    ) -> Tuple[bool, str]:
        """
        Share a note with other users.
        
        Args:
            note_id: Note ID
            user: Sharing user
            share_with: List of users to share with
            can_edit: Allow editing
            can_delete: Allow deletion
            expires_at: Expiration datetime
        
        Returns:
            Tuple of (success, message)
        """
        from plugins.accounts.models import Note, SharedNote
        
        try:
            note = Note.objects.get(id=note_id)
            
            # Check ownership
            if note.created_by != user:
                return False, "You can only share notes you created"
            
            # Update visibility if private
            if note.visibility == 'private':
                note.visibility = 'shared'
                note.save()
            
            # Create shared instances
            shared_count = 0
            for target_user in share_with:
                if target_user != user:  # Don't share with self
                    SharedNote.objects.update_or_create(
                        note=note,
                        user=target_user,
                        defaults={
                            'can_edit': can_edit,
                            'can_delete': can_delete,
                            'expires_at': expires_at
                        }
                    )
                    shared_count += 1
            
            # Invalidate cache for all involved users
            for target_user in share_with:
                cache_key = f"note_stats_{target_user.id}"
                cache.delete(cache_key)
            
            return True, f"Note shared with {shared_count} user(s)"
            
        except Note.DoesNotExist:
            return False, "Note not found"
        except Exception as e:
            logger.error(f"Error sharing note: {e}")
            return False, f"Error sharing note: {str(e)}"
    
    @staticmethod
    def search_notes(
        user,
        query: str = "",
        filters: Dict[str, Any] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Search notes with pagination.
        
        Args:
            user: Searching user
            query: Search query
            filters: Search filters
            page: Page number
            page_size: Items per page
        
        Returns:
            Dictionary with results and metadata
        """
        from plugins.accounts.models import Note
        
        # Get base queryset
        notes = Note.objects.search_notes(user, query, **(filters or {}))
        
        # Calculate pagination
        total = notes.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size
        
        # Get paginated results
        paginated_notes = notes[offset:offset + page_size]
        
        return {
            'results': list(paginated_notes.values()),
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1,
            },
            'query': query,
            'filters': filters,
        }
    
    @staticmethod
    def get_note_analytics(user, days: int = 30) -> Dict[str, Any]:
        """
        Get note analytics for a user.
        
        Args:
            user: The user
            days: Days to analyze
        
        Returns:
            Dictionary of analytics
        """
        from django.db.models import Count
        from django.db.models.functions import TruncDate

        from plugins.accounts.models import Note
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        # Get user's notes in period
        notes = Note.objects.filter(
            created_by=user,
            created_at__range=[start_date, end_date]
        )
        
        # Calculate metrics
        total_notes = notes.count()
        avg_notes_per_day = total_notes / days if days > 0 else 0
        
        # Notes by day
        notes_by_day = list(
            notes.annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        # Notes by visibility
        notes_by_visibility = dict(
            notes.values('visibility')
            .annotate(count=Count('id'))
        )
        
        # Notes by tag
        from django.db.models import Count
        notes_by_tag = list(
            notes.values('tags__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        
        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': days,
            },
            'metrics': {
                'total_notes': total_notes,
                'avg_notes_per_day': round(avg_notes_per_day, 2),
                'pinned_notes': notes.filter(is_pinned=True).count(),
                'archived_notes': notes.filter(is_archived=True).count(),
            },
            'breakdown': {
                'by_day': notes_by_day,
                'by_visibility': notes_by_visibility,
                'by_tag': notes_by_tag,
            },
            'trends': NoteService._calculate_note_trends(notes_by_day),
        }
    
    @staticmethod
    def _calculate_note_trends(notes_by_day):
        """Calculate note creation trends."""
        if not notes_by_day:
            return {}
        
        # Calculate daily average
        total_notes = sum(day['count'] for day in notes_by_day)
        avg_per_day = total_notes / len(notes_by_day)
        
        # Get recent trend (last 7 days vs previous 7 days)
        recent_days = notes_by_day[-7:] if len(notes_by_day) >= 7 else notes_by_day
        previous_days = notes_by_day[-14:-7] if len(notes_by_day) >= 14 else []
        
        recent_avg = sum(day['count'] for day in recent_days) / len(recent_days) if recent_days else 0
        previous_avg = sum(day['count'] for day in previous_days) / len(previous_days) if previous_days else 0
        
        if previous_avg > 0:
            trend_percentage = ((recent_avg - previous_avg) / previous_avg) * 100
        else:
            trend_percentage = 100 if recent_avg > 0 else 0
        
        return {
            'daily_average': round(avg_per_day, 2),
            'recent_trend': round(trend_percentage, 2),
            'trend_direction': 'up' if trend_percentage > 0 else 'down',
            'is_increasing': trend_percentage > 0,
        }

