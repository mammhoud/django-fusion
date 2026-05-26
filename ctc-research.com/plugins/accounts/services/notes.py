"""
Notes Service

Service for managing user notes with real-time updates and notifications.
Moved from www/core/handlers/services/notes_service.py
"""

from typing import List

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from plugins.accounts.models.profiles.note import Note, SharedNote

User = get_user_model()


class NotesService:
    """Service for managing user notes."""

    @staticmethod
    def create_note(user, title: str, content: str, visibility: str = "private", content_object=None) -> Note:
        """Create a new note for a user."""
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            return Note.objects.create(
                title=title, content=content, visibility=visibility,
                created_by=user, content_type=content_type, object_id=content_object.id,
            )
        user_content_type = ContentType.objects.get_for_model(User)
        return Note.objects.create(
            title=title, content=content, visibility=visibility,
            created_by=user, content_type=user_content_type, object_id=user.id,
        )

    @staticmethod
    def update_note(note: Note, title: str = None, content: str = None) -> Note:
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        note.updated_at = timezone.now()
        note.save()
        return note

    @staticmethod
    def delete_note(note: Note) -> bool:
        note.delete()
        return True

    @staticmethod
    def get_user_notes(user, visibility: str = None) -> List[Note]:
        user_content_type = ContentType.objects.get_for_model(User)
        qs = Note.objects.filter(created_by=user, content_type=user_content_type, object_id=user.id)
        if visibility:
            qs = qs.filter(visibility=visibility)
        return list(qs.order_by("-created_at"))

    @staticmethod
    def get_shared_notes(user) -> List[Note]:
        return [sn.note for sn in SharedNote.objects.filter(user=user, note__is_archived=False)]

    @staticmethod
    def pin_note(note: Note) -> Note:
        note.is_pinned = True
        note.pinned_at = timezone.now()
        note.save()
        return note

    @staticmethod
    def unpin_note(note: Note) -> Note:
        note.is_pinned = False
        note.pinned_at = None
        note.save()
        return note

    @staticmethod
    def archive_note(note: Note) -> Note:
        note.is_archived = True
        note.archived_at = timezone.now()
        note.save()
        return note

    @staticmethod
    def unarchive_note(note: Note) -> Note:
        note.is_archived = False
        note.archived_at = None
        note.save()
        return note

    @staticmethod
    def share_note(note: Note, users: List, can_edit: bool = False) -> List[SharedNote]:
        shared = []
        for user in users:
            sn, _ = SharedNote.objects.get_or_create(note=note, user=user, defaults={"can_edit": can_edit})
            shared.append(sn)
        if note.visibility == "private":
            note.visibility = "shared"
            note.save()
        return shared

    @staticmethod
    def unshare_note(note: Note, user) -> bool:
        SharedNote.objects.filter(note=note, user=user).delete()
        return True

    @staticmethod
    def get_note_permissions(note: Note, user) -> dict:
        if note.created_by == user:
            return {"can_view": True, "can_edit": True, "can_delete": True, "can_share": True}
        try:
            sn = SharedNote.objects.get(note=note, user=user)
            return {"can_view": True, "can_edit": sn.can_edit, "can_delete": sn.can_delete, "can_share": False}
        except SharedNote.DoesNotExist:
            pass
        if note.visibility == "public":
            return {"can_view": True, "can_edit": False, "can_delete": False, "can_share": False}
        return {"can_view": False, "can_edit": False, "can_delete": False, "can_share": False}

    @staticmethod
    def search_notes(user, query: str) -> List[Note]:
        user_content_type = ContentType.objects.get_for_model(User)
        return list(Note.objects.filter(
            created_by=user, content_type=user_content_type, object_id=user.id,
        ).filter(
            models.Q(title__icontains=query) | models.Q(content__icontains=query)
        ).order_by("-created_at"))

    @staticmethod
    def add_tag_to_note(note: Note, tag_name: str, color: str = None) -> None:
        note.add_tag(tag_name, color)

    @staticmethod
    def get_notes_by_tag(user, tag_name: str) -> List[Note]:
        user_content_type = ContentType.objects.get_for_model(User)
        return list(Note.objects.filter(
            created_by=user, content_type=user_content_type, object_id=user.id, tags__name=tag_name,
        ).order_by("-created_at"))
