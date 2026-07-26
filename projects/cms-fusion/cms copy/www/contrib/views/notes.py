"""
Notes Profile Section Views

Handles displaying and managing user notes in profile.
"""

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from www.contrib.models.profiles.note import Note
from www.contrib.services.notes_service import NotesService


@login_required
@require_http_methods(["GET"])
def notes_section(request):
    """Display notes section in user profile."""
    notes = NotesService.get_user_notes(request.user)
    pinned_notes = [n for n in notes if n.is_pinned]
    regular_notes = [n for n in notes if not n.is_pinned and not n.is_archived]

    context = {
        "pinned_notes": pinned_notes,
        "regular_notes": regular_notes,
        "total_notes": len(notes),
    }

    return render(request, "profile/notes_section.html", context)


@login_required
@require_http_methods(["GET"])
def notes_list(request):
    """Get list of user's notes via HTMX."""
    notes = NotesService.get_user_notes(request.user)
    pinned_notes = [n for n in notes if n.is_pinned]
    regular_notes = [n for n in notes if not n.is_pinned and not n.is_archived]

    context = {
        "pinned_notes": pinned_notes,
        "regular_notes": regular_notes,
    }

    return render(request, "profile/notes_list.html", context)


@login_required
@require_http_methods(["GET"])
def note_detail(request, note_id):
    """Display note detail modal."""
    try:
        note = Note.objects.get(id=note_id, created_by=request.user)
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)

    context = {"note": note}
    return render(request, "profile/note_detail_modal.html", context)


@login_required
@require_http_methods(["GET"])
def note_edit_modal(request, note_id):
    """Display note edit modal."""
    try:
        note = Note.objects.get(id=note_id, created_by=request.user)
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)

    context = {"note": note}
    return render(request, "profile/note_edit_modal.html", context)


@login_required
@require_http_methods(["POST"])
def create_note(request):
    """Create a new note."""
    try:
        data = json.loads(request.body)
        title = data.get("title", "Untitled")
        content = data.get("content", "")

        note = NotesService.create_note(request.user, title, content)

        return JsonResponse(
            {
                "success": True,
                "note": {
                    "id": str(note.id),
                    "title": note.title,
                    "content": note.content,
                    "created_at": note.created_at.isoformat(),
                },
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def update_note(request, note_id):
    """Update an existing note."""
    try:
        note = Note.objects.get(id=note_id, created_by=request.user)
        data = json.loads(request.body)

        title = data.get("title")
        content = data.get("content")

        note = NotesService.update_note(note, title, content)

        return JsonResponse(
            {
                "success": True,
                "note": {
                    "id": str(note.id),
                    "title": note.title,
                    "content": note.content,
                    "updated_at": note.updated_at.isoformat(),
                },
            }
        )
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_note(request, note_id):
    """Delete a note."""
    try:
        note = Note.objects.get(id=note_id, created_by=request.user)
        NotesService.delete_note(note)

        return JsonResponse({"success": True, "message": "Note deleted"})
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def pin_note(request, note_id):
    """Pin a note."""
    try:
        note = Note.objects.get(id=note_id, created_by=request.user)
        note = NotesService.pin_note(note)

        return JsonResponse(
            {
                "success": True,
                "message": "Note pinned",
                "is_pinned": note.is_pinned,
            }
        )
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def unpin_note(request, note_id):
    """Unpin a note."""
    try:
        note = Note.objects.get(id=note_id, created_by=request.user)
        note = NotesService.unpin_note(note)

        return JsonResponse(
            {
                "success": True,
                "message": "Note unpinned",
                "is_pinned": note.is_pinned,
            }
        )
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def archive_note(request, note_id):
    """Archive a note."""
    try:
        note = Note.objects.get(id=note_id, created_by=request.user)
        note = NotesService.archive_note(note)

        return JsonResponse(
            {
                "success": True,
                "message": "Note archived",
                "is_archived": note.is_archived,
            }
        )
    except Note.DoesNotExist:
        return JsonResponse({"error": "Note not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def search_notes(request):
    """Search user's notes."""
    query = request.GET.get("q", "")

    if not query:
        return JsonResponse({"notes": []})

    notes = NotesService.search_notes(request.user, query)

    return JsonResponse(
        {
            "notes": [
                {
                    "id": str(note.id),
                    "title": note.title,
                    "excerpt": note.excerpt,
                    "created_at": note.created_at.isoformat(),
                }
                for note in notes
            ]
        }
    )
