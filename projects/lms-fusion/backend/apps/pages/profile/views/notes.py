import json
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST
from django_fusion.routes.http.notifications import NotificationMixin
from django_fusion.routes.pages.handler import PageHandler

from apps.pages.accounts.management.services import CertificateService, MessageService
from apps.pages.lms.management.services import CourseService, NoteService

logger = logging.getLogger(__name__)

User = get_user_model()


class NotesView(PageHandler, NotificationMixin):
    """
    Notes management view.
    """

    page_title = "Notes"
    template_name = "base_profile.html"
    fragment_name = "profile.notes"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get context data for notes page.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        if request.user.is_authenticated:
            try:
                # Get notes statistics
                from apps.pages.accounts.models import Note

                note_stats = Note.objects.get_note_statistics(request.user)

                # Get recent notes
                recent_notes = Note.objects.get_recent_notes(request.user, 10)

                # Get pinned notes
                pinned_notes = Note.objects.get_pinned_notes(request.user, 5)

                context.update(
                    {
                        "note_stats": note_stats,
                        "recent_notes": recent_notes,
                        "pinned_notes": pinned_notes,
                        "tags": self._get_user_tags(request.user),
                        "filters": self._get_note_filters(),
                    }
                )

            except Exception as e:
                logger.error(f"Error getting notes context: {e}")
                self.show_notification(
                    message="Error loading notes",
                    level="error",
                    title="Error",
                    duration=5000,
                    request=request,
                )

        return context

    def _get_user_tags(self, user):
        """Get tags used by user."""
        from apps.pages.accounts.models import Tag

        return Tag.objects.filter(notes__created_by=user).distinct().order_by("name")

    def _get_note_filters(self):
        """Get available note filters."""
        return {
            "visibility": [
                {"value": "private", "label": "Private"},
                {"value": "shared", "label": "Shared"},
                {"value": "public", "label": "Public"},
            ],
            "status": [
                {"value": "pinned", "label": "Pinned"},
                {"value": "archived", "label": "Archived"},
                {"value": "active", "label": "Active"},
            ],
            "date_range": [
                {"value": "today", "label": "Today"},
                {"value": "week", "label": "This Week"},
                {"value": "month", "label": "This Month"},
                {"value": "year", "label": "This Year"},
            ],
        }

    @require_POST
    @login_required
    def create_note(self, request: HttpRequest) -> JsonResponse:
        """
        Create a new note.
        """
        try:
            data = json.loads(request.body) if request.body else {}

            success, message, note = NoteService.create_note(
                user=request.user,
                title=data.get("title", ""),
                content=data.get("content", ""),
                tags=data.get("tags", []),
                visibility=data.get("visibility", "private"),
                is_pinned=data.get("is_pinned", False),
            )

            if success:
                self.show_notification(
                    message=message,
                    level="success",
                    title="Note Created",
                    duration=3000,
                    request=request,
                )

                return JsonResponse(
                    {
                        "status": "success",
                        "message": message,
                        "note": {
                            "id": str(note.id),
                            "title": note.title,
                            "excerpt": note.excerpt,
                            "created_at": note.created_at.isoformat(),
                            "visibility": note.visibility,
                            "is_pinned": note.is_pinned,
                        },
                    }
                )
            else:
                self.show_notification(
                    message=message, level="error", title="Error", duration=5000, request=request
                )

                return JsonResponse({"status": "error", "message": message}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            return JsonResponse(
                {"status": "error", "message": f"Error creating note: {str(e)}"}, status=500
            )

class ContentDashboardView(PageHandler, NotificationMixin):
    """
    Unified content dashboard view.
    """

    page_title = "Content Dashboard"
    template_name = "dashboard/content_dashboard.html"
    fragment_name = "dashboard.content"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get context data for content dashboard.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        if request.user.is_authenticated:
            try:
                # Get all dashboard data
                note_stats = NoteService.get_note_analytics(request.user, 30)
                cert_dashboard = CertificateService.get_certificate_profile(request.user)
                course_dashboard = CourseService.get_user_course_dashboard(request.user)
                message_analytics = MessageService.get_message_analytics(request.user, 30)

                # Recent activity
                recent_activity = self._get_recent_activity(request.user)

                # Quick actions
                quick_actions = self._get_quick_actions(request.user)

                context.update(
                    {
                        "note_stats": note_stats,
                        "cert_dashboard": cert_dashboard,
                        "course_dashboard": course_dashboard,
                        "message_analytics": message_analytics,
                        "recent_activity": recent_activity,
                        "quick_actions": quick_actions,
                        "overall_stats": self._calculate_overall_stats(
                            note_stats, cert_dashboard, course_dashboard, message_analytics
                        ),
                    }
                )

            except Exception as e:
                logger.error(f"Error getting dashboard context: {e}")
                self.show_notification(
                    message="Error loading dashboard",
                    level="error",
                    title="Error",
                    duration=5000,
                    request=request,
                )

        return context

    def _get_recent_activity(self, user):
        """Get recent activity across all content types."""
        activity = []

        # Recent notes
        from apps.pages.accounts.models import Note

        recent_notes = Note.objects.get_recent_notes(user, 3)
        for note in recent_notes:
            activity.append(
                {
                    "type": "note",
                    "title": f"Created note: {note.title}",
                    "description": note.excerpt,
                    "timestamp": note.created_at,
                    "icon": "file-text",
                    "color": "blue",
                    "url": f"/notes/{note.id}/",
                }
            )

        # Recent messages
        from apps.pages.accounts.models import Message

        recent_messages = Message.objects.get_user_messages(user, unread_only=False)[:3]
        for msg in recent_messages:
            activity.append(
                {
                    "type": "message",
                    "title": f"Message: {msg.subject}",
                    "description": f"From: {msg.sender_content_object}",
                    "timestamp": msg.created_at,
                    "icon": "mail",
                    "color": "green",
                    "url": f"/messages/{msg.id}/",
                }
            )

        # Recent course progress
        from apps.pages.lms.models import Enrollment

        recent_enrollments = Enrollment.objects.filter(content_object=user).order_by(
            "-last_accessed_at"
        )[:3]

        for enrollment in recent_enrollments:
            activity.append(
                {
                    "type": "course",
                    "title": f"Course progress: {enrollment.course.title}",
                    "description": f"Progress: {enrollment.progress}%",
                    "timestamp": enrollment.last_accessed_at or enrollment.enrolled_at,
                    "icon": "book",
                    "color": "purple",
                    "url": f"/courses/{enrollment.course.id}/",
                }
            )

        # Sort by timestamp
        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        return activity[:10]  # Return top 10

    def _get_quick_actions(self, user):
        """Get quick actions for the dashboard."""
        actions = []

        # Check for incomplete profile
        from apps.pages.accounts.models import Person

        person = Person.objects.filter(user=user).first()
        if person and person.completion_percentage < 80:
            actions.append(
                {
                    "title": "Complete Profile",
                    "description": "Fill in your profile information",
                    "icon": "user",
                    "url": "/profile/edit/",
                    "color": "primary",
                    "priority": 1,
                }
            )

        # Check for expiring certificates
        from apps.pages.accounts.models import Certificate

        expiring_certs = Certificate.objects.get_expiring_soon(user, 30)
        if expiring_certs.exists():
            actions.append(
                {
                    "title": "Renew Certificates",
                    "description": f"{expiring_certs.count()} certificates expiring soon",
                    "icon": "award",
                    "url": "/certificates/expiring/",
                    "color": "warning",
                    "priority": 2,
                }
            )

        # Check for unread messages
        from apps.pages.accounts.models import Message

        unread_count = Message.objects.get_user_messages(user, unread_only=True).count()
        if unread_count > 0:
            actions.append(
                {
                    "title": "Read Messages",
                    "description": f"You have {unread_count} unread messages",
                    "icon": "mail",
                    "url": "/messages/unread/",
                    "color": "info",
                    "priority": 3,
                }
            )

        # Always show create note action
        actions.append(
            {
                "title": "Create Note",
                "description": "Jot down your thoughts",
                "icon": "edit",
                "url": "/notes/create/",
                "color": "success",
                "priority": 4,
            }
        )

        # Sort by priority
        actions.sort(key=lambda x: x["priority"])
        return actions

    def _calculate_overall_stats(
        self, note_stats, cert_dashboard, course_dashboard, message_analytics
    ):
        """Calculate overall statistics."""
        return {
            "total_content": {
                "notes": note_stats["metrics"]["total_notes"],
                "certificates": cert_dashboard["summary"]["total"],
                "courses": course_dashboard["metrics"]["total_enrollments"],
                "messages": message_analytics["summary"]["total_received"],
            },
            "completion_rates": {
                "profile": self._get_profile_completion(),
                "courses": course_dashboard["metrics"]["average_progress"],
                "tasks": 0,  # Would come from a task system
            },
            "activity_score": self._calculate_activity_score(
                note_stats, course_dashboard, message_analytics
            ),
        }

    def _get_profile_completion(self):
        """Get profile completion percentage."""
        from apps.pages.accounts.models import Person

        person = Person.objects.filter(user=self.request.user).first()
        return person.completion_percentage if person else 0

    def _calculate_activity_score(self, note_stats, course_dashboard, message_analytics):
        """Calculate overall activity score."""
        # Weighted average of different activities
        weights = {
            "notes": 0.3,
            "courses": 0.4,
            "messages": 0.3,
        }

        note_activity = min(note_stats["metrics"]["avg_notes_per_day"] * 10, 100)
        course_activity = course_dashboard["metrics"]["average_progress"]
        message_activity = min(message_analytics["summary"]["total_received"] / 30 * 10, 100)

        score = (
            note_activity * weights["notes"]
            + course_activity * weights["courses"]
            + message_activity * weights["messages"]
        )

        return round(score, 2)