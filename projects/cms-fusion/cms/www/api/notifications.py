"""
Notifications API — list, unread count, mark as read, preferences (bolt-pattern).

All endpoints require authentication via token or session.
"""

from __future__ import annotations

import logging
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone

from www.api.data_adapter import bolt_view, login_required, parse_body
from www.api.data.helpers import paginate_queryset, paginated_response

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# Notification CRUD
# ═══════════════════════════════════════════════════════════════════════


@bolt_view
@login_required
def notification_list(request):
    """GET /apis/notifications/ — List notifications for current user.

    Query params:
        unread_only (bool): If true, only return unread notifications
        limit (int): Max results (default 20)
        offset (int): Pagination offset
    """
    from plugins.lms.models import Notification

    qs = Notification.objects.filter(user=request.user, is_dismissed=False).order_by("-created_at")

    if request.GET.get("unread_only") == "true":
        qs = qs.filter(is_read=False)

    items, pagination = paginate_queryset(qs, request, default_per_page=20)
    serialized = [_serialize_notification(n) for n in items]
    return paginated_response(items, pagination, request, serialized)


@bolt_view
@login_required
def notification_unread_count(request):
    """GET /apis/notifications/unread-count/ — Get unread count for current user."""
    from plugins.lms.models import Notification

    count = Notification.objects.filter(user=request.user, is_read=False, is_dismissed=False).count()
    return {"status": "success", "data": {"unread_count": count}}


@bolt_view
@login_required
def notification_mark_read(request, pk):
    """PATCH /apis/notifications/<pk>/read/ — Mark a single notification as read."""
    from plugins.lms.models import Notification

    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
    except Notification.DoesNotExist:
        return {"status": "error", "message": "Notification not found"}, 404

    notification.mark_as_read()
    return {"status": "success", "data": _serialize_notification(notification)}


@bolt_view
@login_required
def notification_mark_all_read(request):
    """POST /apis/notifications/mark-all-read/ — Mark all notifications as read."""
    from plugins.lms.models import Notification

    now = timezone.now()
    updated = Notification.objects.filter(
        user=request.user, is_read=False, is_dismissed=False
    ).update(is_read=True, read_at=now)

    return {"status": "success", "data": {"marked_read": updated}}


@bolt_view
@login_required
def notification_dismiss(request, pk):
    """DELETE /apis/notifications/<pk>/ — Dismiss a notification."""
    from plugins.lms.models import Notification

    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
    except Notification.DoesNotExist:
        return {"status": "error", "message": "Notification not found"}, 404

    notification.mark_as_dismissed()
    return {"status": "success", "message": "Notification dismissed"}


# ═══════════════════════════════════════════════════════════════════════
# Notification Triggers — called by other parts of the system
# ═══════════════════════════════════════════════════════════════════════


def create_notification(
    user: User,
    notification_type: str,
    title: str,
    message: str = "",
    link: str = "",
) -> dict:
    """Create a notification for a user.

    Respects the user's notification preferences — if the notification type
    is disabled in their preferences, the notification is not created.

    Returns the serialized notification or None if skipped.
    """
    from plugins.lms.models import Notification, NotificationPreference

    # Check if user has disabled this notification type
    try:
        pref = NotificationPreference.objects.get(user=user)
        type_field = f"{notification_type}_notifications"
        if hasattr(pref, type_field) and not getattr(pref, type_field):
            return None
        if not pref.in_app_notifications:
            return None
    except NotificationPreference.DoesNotExist:
        pass  # Default: allow all notifications

    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
    )
    return _serialize_notification(notification)


def notify_enrollment(student: User, course_title: str, course_id: int) -> dict | None:
    """Notify student about course enrollment."""
    return create_notification(
        user=student,
        notification_type="enrollment",
        title=f"Enrolled in {course_title}",
        message=f"You have successfully enrolled in {course_title}.",
        link=f"/course-details/{course_id}/",
    )


def notify_course_update(instructor: User, course_title: str, course_id: int) -> dict | None:
    """Notify instructor about a course update."""
    return create_notification(
        user=instructor,
        notification_type="course_update",
        title=f"Course Updated: {course_title}",
        message=f"Your course {course_title} has been updated.",
        link=f"/dashboard/courses/{course_id}/",
    )


def notify_grade(student: User, course_title: str, grade: str) -> dict | None:
    """Notify student about a grade/submission result."""
    return create_notification(
        user=student,
        notification_type="grading",
        title=f"Grade Posted: {course_title}",
        message=f"Your grade for {course_title} has been posted: {grade}.",
        link="/dashboard/",
    )


def notify_announcement(
    target_users: list[User], course_title: str, announcement_title: str
) -> list[dict]:
    """Notify all enrolled students about a course announcement."""
    results = []
    for user in target_users:
        result = create_notification(
            user=user,
            notification_type="announcement",
            title=f"New Announcement: {course_title}",
            message=announcement_title,
            link="/dashboard/",
        )
        if result:
            results.append(result)
    return results


def notify_quiz_result(student: User, quiz_title: str, score: int, total: int) -> dict | None:
    """Notify student about quiz results."""
    return create_notification(
        user=student,
        notification_type="quiz",
        title=f"Quiz Result: {quiz_title}",
        message=f"You scored {score}/{total} on {quiz_title}.",
        link="/dashboard/",
    )


# ═══════════════════════════════════════════════════════════════════════
# Notification Preferences
# ═══════════════════════════════════════════════════════════════════════


@bolt_view
@login_required
def notification_preferences_get(request):
    """GET /apis/notifications/preferences/ — Get current user's notification preferences."""
    from plugins.lms.models import NotificationPreference

    pref, _ = NotificationPreference.objects.get_or_create(user=request.user)
    return {"status": "success", "data": _serialize_preferences(pref)}


@bolt_view
@login_required
def notification_preferences_update(request):
    """PATCH /apis/notifications/preferences/ — Update notification preferences."""
    from plugins.lms.models import NotificationPreference

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    pref, _ = NotificationPreference.objects.get_or_create(user=request.user)

    # Allowed boolean fields on the preference model
    bool_fields = [
        "in_app_notifications",
        "email_notifications",
        "enrollment_notifications",
        "course_update_notifications",
        "assignment_notifications",
        "grading_notifications",
        "quiz_notifications",
        "review_notifications",
        "announcement_notifications",
        "system_notifications",
    ]

    for field in bool_fields:
        if field in body:
            setattr(pref, field, bool(body[field]))

    if "digest_frequency" in body:
        allowed_freqs = ["immediate", "daily", "weekly", "never"]
        if body["digest_frequency"] in allowed_freqs:
            pref.digest_frequency = body["digest_frequency"]

    pref.save()
    return {"status": "success", "data": _serialize_preferences(pref)}


# ═══════════════════════════════════════════════════════════════════════
# Serializers
# ═══════════════════════════════════════════════════════════════════════


def _serialize_notification(notification) -> dict:
    """Serialize a single notification to the frontend contract."""
    return {
        "id": notification.id,
        "type": notification.notification_type,
        "type_label": notification.get_notification_type_display(),
        "title": notification.title,
        "message": notification.message,
        "link": notification.link,
        "is_read": notification.is_read,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
        "time_ago": _time_ago(notification.created_at) if notification.created_at else "",
    }


def _serialize_preferences(pref) -> dict:
    """Serialize notification preferences."""
    return {
        "in_app_notifications": pref.in_app_notifications,
        "email_notifications": pref.email_notifications,
        "enrollment_notifications": pref.enrollment_notifications,
        "course_update_notifications": pref.course_update_notifications,
        "assignment_notifications": pref.assignment_notifications,
        "grading_notifications": pref.grading_notifications,
        "quiz_notifications": pref.quiz_notifications,
        "review_notifications": pref.review_notifications,
        "announcement_notifications": pref.announcement_notifications,
        "system_notifications": pref.system_notifications,
        "digest_frequency": pref.digest_frequency,
    }


def _time_ago(dt) -> str:
    """Human-readable 'time ago' string."""
    now = timezone.now()
    diff = now - dt

    if diff < timedelta(minutes=1):
        return "Just now"
    if diff < timedelta(hours=1):
        mins = int(diff.total_seconds() / 60)
        return f"{mins}m ago"
    if diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return f"{hours}h ago"
    if diff < timedelta(days=7):
        days = diff.days
        return f"{days}d ago"
    if diff < timedelta(days=30):
        weeks = int(diff.days / 7)
        return f"{weeks}w ago"
    return dt.strftime("%b %d")
