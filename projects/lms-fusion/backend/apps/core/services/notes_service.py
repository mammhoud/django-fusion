"""
Notes Service

Service for managing user notes with real-time updates and notifications.
"""

from typing import List

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from apps.core.models.profiles.note import Note, SharedNote

User = get_user_model()


class NotesService:
    """Service for managing user notes."""

    @staticmethod
    def create_note(
        user: User,
        title: str,
        content: str,
        visibility: str = "private",
        content_object=None,
    ) -> Note:
        """Create a new note for a user."""
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            note = Note.objects.create(
                title=title,
                content=content,
                visibility=visibility,
                created_by=user,
                content_type=content_type,
                object_id=content_object.id,
            )
        else:
            # Create a note for the user's profile
            user_content_type = ContentType.objects.get_for_model(User)
            note = Note.objects.create(
                title=title,
                content=content,
                visibility=visibility,
                created_by=user,
                content_type=user_content_type,
                object_id=user.id,
            )

        return note

    @staticmethod
    def update_note(note: Note, title: str = None, content: str = None) -> Note:
        """Update an existing note."""
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content

        note.updated_at = timezone.now()
        note.save()

        return note

    @staticmethod
    def delete_note(note: Note) -> bool:
        """Delete a note."""
        note.delete()
        return True

    @staticmethod
    def get_user_notes(user: User, visibility: str = None) -> List[Note]:
        """Get all notes for a user."""
        user_content_type = ContentType.objects.get_for_model(User)
        notes = Note.objects.filter(
            created_by=user,
            content_type=user_content_type,
            object_id=user.id,
        )

        if visibility:
            notes = notes.filter(visibility=visibility)

        return list(notes.order_by("-created_at"))

    @staticmethod
    def get_shared_notes(user: User) -> List[Note]:
        """Get all notes shared with a user."""
        shared_notes = SharedNote.objects.filter(user=user, note__is_archived=False)
        return [sn.note for sn in shared_notes]

    @staticmethod
    def pin_note(note: Note) -> Note:
        """Pin a note."""
        note.is_pinned = True
        note.pinned_at = timezone.now()
        note.save()
        return note

    @staticmethod
    def unpin_note(note: Note) -> Note:
        """Unpin a note."""
        note.is_pinned = False
        note.pinned_at = None
        note.save()
        return note

    @staticmethod
    def archive_note(note: Note) -> Note:
        """Archive a note."""
        note.is_archived = True
        note.archived_at = timezone.now()
        note.save()
        return note

    @staticmethod
    def unarchive_note(note: Note) -> Note:
        """Unarchive a note."""
        note.is_archived = False
        note.archived_at = None
        note.save()
        return note

    @staticmethod
    def share_note(note: Note, users: List[User], can_edit: bool = False) -> List[SharedNote]:
        """Share a note with specific users."""
        shared_notes = []

        for user in users:
            shared_note, created = SharedNote.objects.get_or_create(
                note=note,
                user=user,
                defaults={"can_edit": can_edit},
            )
            shared_notes.append(shared_note)

        # Update visibility if sharing
        if note.visibility == "private":
            note.visibility = "shared"
            note.save()

        return shared_notes

    @staticmethod
    def unshare_note(note: Note, user: User) -> bool:
        """Stop sharing a note with a user."""
        SharedNote.objects.filter(note=note, user=user).delete()
        return True

    @staticmethod
    def get_note_permissions(note: Note, user: User) -> dict:
        """Get user's permissions for a note."""
        # Check if user is the creator
        if note.created_by == user:
            return {
                "can_view": True,
                "can_edit": True,
                "can_delete": True,
                "can_share": True,
            }

        # Check if note is shared with user
        try:
            shared_note = SharedNote.objects.get(note=note, user=user)
            return {
                "can_view": True,
                "can_edit": shared_note.can_edit,
                "can_delete": shared_note.can_delete,
                "can_share": False,
            }
        except SharedNote.DoesNotExist:
            pass

        # Check visibility
        if note.visibility == "public":
            return {
                "can_view": True,
                "can_edit": False,
                "can_delete": False,
                "can_share": False,
            }

        return {
            "can_view": False,
            "can_edit": False,
            "can_delete": False,
            "can_share": False,
        }

    @staticmethod
    def search_notes(user: User, query: str) -> List[Note]:
        """Search user's notes."""
        user_content_type = ContentType.objects.get_for_model(User)
        notes = Note.objects.filter(
            created_by=user,
            content_type=user_content_type,
            object_id=user.id,
        ).filter(
            models.Q(title__icontains=query) | models.Q(content__icontains=query)
        )

        return list(notes.order_by("-created_at"))

    @staticmethod
    def add_tag_to_note(note: Note, tag_name: str, color: str = None) -> None:
        """Add a tag to a note."""
        note.add_tag(tag_name, color)

    @staticmethod
    def get_notes_by_tag(user: User, tag_name: str) -> List[Note]:
        """Get all notes with a specific tag."""
        user_content_type = ContentType.objects.get_for_model(User)
        notes = Note.objects.filter(
            created_by=user,
            content_type=user_content_type,
            object_id=user.id,
            tags__name=tag_name,
        )

        return list(notes.order_by("-created_at"))


# Import models for search query
from django.db import models
