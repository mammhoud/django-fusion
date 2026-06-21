"""
crafts_ai.site.mixins
========================

Application-layer view and model mixins for the rseal app.

These mixins depend on ``crafts_ai.models`` (``Person``,
``PersonService``, etc.) and ``apps.handlers``.

Classes
-------
ProfileContextMixin
    Injects the authenticated user's ``Person`` profile into template context.
ProfileOperationsMixin
    Handles profile update AJAX endpoints (info, image, notifications, security).
ProfileDashboardMixin
    Extends ``ProfileContextMixin`` with dashboard metrics and quick actions.
NoteMixin
    Adds note-taking capabilities to any model via GenericRelation.
CertificateMixin
    Adds certificate management to any model via GenericRelation.
CourseMixin
    Adds course-enrollment tracking to any model via GenericRelation.
MessageMixin
    Adds message send/receive to any model via GenericRelation.
BaseCartMixin
    Abstract base for site-specific cart implementations.
BaseDashboardMixin
    Abstract base for site-specific dashboard implementations.
"""

from abc import abstractmethod
from typing import Any, Dict

# Project-specific imports removed
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.http import HttpRequest, JsonResponse
from django.utils import timezone
from django.views.generic.base import ContextMixin

from crafts_ai.content.models import Person


class ProfileContextMixin(ContextMixin):
    """
    Mixin to add profile context data to views.
    Provides person and profile information.
    """

    def get_profile_context(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Get comprehensive profile context.
        """
        context = {}

        if request.user.is_authenticated:
            try:
                # Get person record
                person = Person.objects.filter(user=request.user).first()

                if person:
                    # Get profile information via service
                    profile_info = PersonService.get_user_profile_information(request.user)

                    context.update(
                        {
                            "person": person,
                            "profile_info": profile_info,
                            "completion_percentage": person.completion_percentage,
                            "is_complete": person.is_complete,
                            "social_links": person.social_links,
                            "certifications": person.certifications,
                            "projects": person.projects,
                            "profile_stats": self._get_profile_stats(person),
                        }
                    )
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error getting profile context: {e}")

        return context

    def _get_profile_stats(self, person: Person) -> Dict[str, Any]:
        """
        Get profile statistics.
        """
        return {
            "completion_percentage": person.completion_percentage,
            "is_complete": person.is_complete,
            "has_profile_image": bool(person.profile_image),
            "has_resume": bool(person.resume) if hasattr(person, "resume") else False,
            "social_links_count": len(person.social_links),
            "certifications_count": len(person.certifications),
            "projects_count": len(person.projects),
            "days_since_joined": (timezone.now().date() - person.created_at.date()).days,
            "last_active": person.last_active,
        }

    def get_context_data(self, **kwargs):
        """
        Add profile context to view context.
        """
        context = super().get_context_data(**kwargs)
        if hasattr(self, "request"):
            context.update(self.get_profile_context(self.request))
        return context


class ProfileOperationsMixin():
    """
    Mixin for handling profile operations with notification support.
    """

    def update_profile_information(self, request: HttpRequest) -> JsonResponse:
        """
        Handle profile information updates with notification.
        """
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required."}, status=401
            )

        try:
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return JsonResponse(
                    {"status": "error", "message": "Profile not found."}, status=404
                )

            # Get update data
            update_data = self._extract_profile_data(request)

            # Apply updates
            updated_fields = []
            for field, value in update_data.items():
                if hasattr(person, field) and value is not None:
                    setattr(person, field, value)
                    updated_fields.append(field)

            if updated_fields:
                person.save(update_fields=updated_fields)

                # Invalidate cache
                # Project-specific imports removed

                PersonManager().invalidate_object_cache(person)

                # Sync email with user if changed
                if "email" in updated_fields and person.user:
                    person.user.email = person.email
                    person.user.save(update_fields=["email"])

                # Show success notification
                if hasattr(self, "show_notification"):
                    self.show_notification(
                        message="Profile updated successfully",
                        level="success",
                        title="Profile Update",
                        duration=3000,
                        request=request,
                    )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Profile updated successfully.",
                    "updated_fields": updated_fields,
                    "completion_percentage": person.completion_percentage,
                    "is_complete": person.is_complete,
                }
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error updating profile: {e}")

            # Show error notification
            if hasattr(self, "show_notification"):
                self.show_notification(
                    message=f"Error updating profile: {str(e)}",
                    level="error",
                    title="Update Failed",
                    duration=5000,
                    request=request,
                )

            return JsonResponse(
                {"status": "error", "message": f"Error updating profile: {str(e)}"}, status=500
            )

    def update_profile_image(self, request: HttpRequest) -> JsonResponse:
        """
        Handle profile image updates with notification.
        """
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required."}, status=401
            )

        uploaded_file = request.FILES.get("image")
        if not uploaded_file:
            return JsonResponse({"status": "error", "message": "No file provided."}, status=400)

        try:
            # Validate file
            validation_error = self._validate_image_file(uploaded_file)
            if validation_error:
                return validation_error

            # Get person record
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return JsonResponse(
                    {"status": "error", "message": "Profile not found."}, status=404
                )

            # Update profile image
            person.profile_image = uploaded_file
            person.save(update_fields=["profile_image"])

            # Invalidate cache
            # Project-specific imports removed

            PersonManager().invalidate_object_cache(person)

            # Show success notification
            if hasattr(self, "show_notification"):
                self.show_notification(
                    message="Profile image updated successfully",
                    level="success",
                    title="Image Updated",
                    duration=3000,
                    request=request,
                )

            # Return success with image URL
            image_url = person.profile_image.url if person.profile_image else None

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Profile image updated successfully.",
                    "image_url": image_url,
                    "person_id": str(person.id),
                }
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error updating profile image: {e}")

            # Show error notification
            if hasattr(self, "show_notification"):
                self.show_notification(
                    message=f"Error updating image: {str(e)}",
                    level="error",
                    title="Upload Failed",
                    duration=5000,
                    request=request,
                )

            return JsonResponse(
                {"status": "error", "message": f"Error updating image: {str(e)}"}, status=500
            )

    def update_notification_settings(self, request: HttpRequest) -> JsonResponse:
        """
        Handle notification settings updates with notification.
        """
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required."}, status=401
            )

        try:
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return JsonResponse(
                    {"status": "error", "message": "Profile not found."}, status=404
                )

            # Get notification preferences
            preferences = {}
            for field in ["email_notifications", "newsletter_notifications"]:
                if value := request.POST.get(field):
                    preferences[field] = value.lower() == "true"

            # Update via service
            success, message = PersonService.update_notification_preferences(
                str(person.id), preferences
            )

            if success:
                # Show success notification
                if hasattr(self, "show_notification"):
                    self.show_notification(
                        message=message,
                        level="success",
                        title="Settings Updated",
                        duration=3000,
                        request=request,
                    )

                return JsonResponse(
                    {
                        "status": "success",
                        "message": message,
                        "preferences": preferences,
                    }
                )
            else:
                # Show error notification
                if hasattr(self, "show_notification"):
                    self.show_notification(
                        message=message,
                        level="error",
                        title="Update Failed",
                        duration=5000,
                        request=request,
                    )

                return JsonResponse(
                    {
                        "status": "error",
                        "message": message,
                    },
                    status=400,
                )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error updating notifications: {e}")

            # Show error notification
            if hasattr(self, "show_notification"):
                self.show_notification(
                    message=f"Error updating notifications: {str(e)}",
                    level="error",
                    title="Update Failed",
                    duration=5000,
                    request=request,
                )

            return JsonResponse(
                {"status": "error", "message": f"Error updating notifications: {str(e)}"},
                status=500,
            )

    def update_security_settings(self, request: HttpRequest) -> JsonResponse:
        """
        Handle security settings updates with notification.
        """
        if not request.user.is_authenticated:
            return JsonResponse(
                {"status": "error", "message": "Authentication required."}, status=401
            )

        try:
            # Get security settings from request
            settings = {}
            for field in ["email_verified", "phone_verified"]:
                if value := request.POST.get(field):
                    settings[field] = value.lower() == "true"

            # Update person record
            person = Person.objects.filter(user=request.user).first()
            if not person:
                return JsonResponse(
                    {"status": "error", "message": "Profile not found."}, status=404
                )

            updated_fields = []
            for field, value in settings.items():
                if hasattr(person, field):
                    setattr(person, field, value)
                    updated_fields.append(field)

            if updated_fields:
                person.save(update_fields=updated_fields)

                # Invalidate cache
                # Project-specific imports removed

                PersonManager().invalidate_object_cache(person)

                # Show success notification
                if hasattr(self, "show_notification"):
                    self.show_notification(
                        message="Security settings updated successfully",
                        level="success",
                        title="Security Updated",
                        duration=3000,
                        request=request,
                    )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Security settings updated.",
                    "updated_fields": updated_fields,
                }
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error updating security settings: {e}")

            # Show error notification
            if hasattr(self, "show_notification"):
                self.show_notification(
                    message=f"Error updating security settings: {str(e)}",
                    level="error",
                    title="Update Failed",
                    duration=5000,
                    request=request,
                )

            return JsonResponse(
                {"status": "error", "message": f"Error updating security settings: {str(e)}"},
                status=500,
            )

    def _extract_profile_data(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Extract profile data from request.
        """
        data = {}

        # Basic information
        for field in ["first_name", "last_name", "email", "phone"]:
            if value := request.POST.get(field):
                data[field] = value

        # Personal information
        for field in ["birth_date", "gender", "address", "city", "country"]:
            if value := request.POST.get(field):
                data[field] = value

        # Professional information
        for field in ["job_title", "company", "industry", "bio"]:
            if value := request.POST.get(field):
                data[field] = value

        # Social information
        for field in ["website", "linkedin_url", "github_url"]:
            if value := request.POST.get(field):
                data[field] = value

        return data

    def _validate_image_file(self, uploaded_file) -> JsonResponse or None:
        """
        Validate uploaded image file.
        """
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if uploaded_file.content_type not in allowed_types:
            return JsonResponse(
                {"status": "error", "message": "Invalid file type. Allowed: JPEG, PNG, GIF, WebP."},
                status=400,
            )

        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if uploaded_file.size > max_size:
            return JsonResponse(
                {"status": "error", "message": "File too large. Maximum size is 5MB."}, status=400
            )

        return None


class ProfileDashboardMixin(ProfileContextMixin):
    """
    Mixin for dashboard views with profile operations.
    """

    def get_dashboard_context(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Get dashboard context including profile metrics.
        """
        context = self.get_profile_context(request)

        if request.user.is_authenticated:
            try:
                person = Person.objects.filter(user=request.user).first()
                if person:
                    # Add dashboard-specific metrics
                    context.update(self._get_dashboard_metrics(person))

                    # Add quick actions
                    context["quick_actions"] = self._get_quick_actions(person)
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(f"Error getting dashboard context: {e}")

        return context

    def _get_dashboard_metrics(self, person: Person) -> dict:
        """
        Get dashboard metrics and statistics.
        """
        metrics = {
            "metrics": {},
            "stats": {},
        }

        try:
            # Get profile stats
            profile_stats = Person.objects.get_profile_statistics(str(person.id))

            metrics["metrics"] = {
                "completion": {
                    "value": person.completion_percentage,
                    "label": "Profile Complete",
                    "icon": "check-circle",
                    "color": "success" if person.completion_percentage >= 80 else "warning",
                    "action": "/profile/",
                },
                "verification": {
                    "value": sum([person.email_verified, person.phone_verified]),
                    "label": "Verifications",
                    "icon": "shield",
                    "color": "success"
                    if person.email_verified and person.phone_verified
                    else "warning",
                    "action": "/settings/security/",
                },
                "notifications": {
                    "value": len(person.notification_channels),
                    "label": "Active Channels",
                    "icon": "bell",
                    "color": "info",
                    "action": "/settings/notifications/",
                },
                "activity": {
                    "value": self._get_activity_days(person),
                    "label": "Active Days",
                    "icon": "activity",
                    "color": "primary",
                    "action": "/profile/activity/",
                },
            }

            metrics["stats"] = {
                "profile_views": profile_stats.get("profile_views", 0),
                "last_active": person.last_active,
                "days_active": (timezone.now().date() - person.created_at.date()).days,
                "completion_score": person.completion_percentage,
            }

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error getting dashboard metrics: {e}")

        return metrics

    def _get_activity_days(self, person: Person) -> int:
        """
        Calculate active days for dashboard.
        """
        # Placeholder - implement based on your activity tracking
        return (timezone.now().date() - person.created_at.date()).days

    def _get_quick_actions(self, person: Person) -> list:
        """
        Get quick action buttons for dashboard.
        """
        actions = []

        # Profile completion actions
        if person.completion_percentage < 80:
            actions.append(
                {
                    "title": "Complete Profile",
                    "description": "Fill in missing profile information",
                    "icon": "user-plus",
                    "url": "/profile/edit/",
                    "color": "primary",
                    "priority": 1,
                }
            )

        # Profile image action
        if not person.profile_image:
            actions.append(
                {
                    "title": "Add Profile Photo",
                    "description": "Upload a profile picture",
                    "icon": "camera",
                    "url": "/profile/image/upload/",
                    "color": "success",
                    "priority": 2,
                }
            )

        # Social links action
        if not person.website and not person.linkedin_url and not person.github_url:
            actions.append(
                {
                    "title": "Add Social Links",
                    "description": "Connect your social media profiles",
                    "icon": "link",
                    "url": "/profile/edit/#social",
                    "color": "info",
                    "priority": 3,
                }
            )

        # Share profile action
        actions.append(
            {
                "title": "Share Profile",
                "description": "Create shareable profile link",
                "icon": "share-2",
                "url": "/profile/share/",
                "color": "warning",
                "priority": 4,
            }
        )

        # Sort by priority
        actions.sort(key=lambda x: x["priority"])

        return actions


class NoteMixin(models.Model):
    """
    Mixin for adding note-taking capabilities to any model.
    """

    class Meta:
        abstract = True

    notes = GenericRelation(
        "Note",
        content_type_field="content_type",
        object_id_field="object_id",
        related_query_name="%(class)s_notes",
    )

    @property
    def recent_notes(self):
        """Get recent notes for this object."""
        return self.notes.all().order_by("-created_at")[:5]

    @property
    def note_count(self):
        """Get total note count."""
        return self.notes.count()

    def add_note(self, title, content, created_by=None, tags=None, visibility="private"):
        """
        Add a note to this object.

        Args:
            title: Note title
            content: Note content
            created_by: User creating the note
            tags: List of tags
            visibility: 'private', 'shared', or 'public'

        Returns:
            Created Note object
        """
        # Project-specific imports removed - use dependency injection

        note = Note.objects.create(
            title=title,
            content=content,
            content_object=self,
            created_by=created_by,
            visibility=visibility,
        )

        if tags:
            note.tags.set(tags)

        return note

    def get_notes_by_tag(self, tag_name):
        """Get notes filtered by tag."""
        return self.notes.filter(tags__name=tag_name).order_by("-created_at")

    def get_notes_by_visibility(self, visibility):
        """Get notes filtered by visibility."""
        return self.notes.filter(visibility=visibility).order_by("-created_at")


class CertificateMixin(models.Model):
    """
    Mixin for certificate management.
    """

    class Meta:
        abstract = True

    certificates = GenericRelation(
        "Certificate",
        content_type_field="content_type",
        object_id_field="object_id",
        related_query_name="%(class)s_certificates",
    )

    @property
    def valid_certificates(self):
        """Get currently valid certificates."""
        today = timezone.now().date()
        return self.certificates.filter(
            issue_date__lte=today, expiry_date__gte=today, status="valid"
        ).order_by("-issue_date")

    @property
    def certificate_count(self):
        """Get total certificate count."""
        return self.certificates.count()

    def add_certificate(self, **kwargs):
        """
        Add a certificate.

        Args:
            **kwargs: Certificate fields

        Returns:
            Created Certificate object
        """
        # Project-specific imports removed - use dependency injection

        return Certificate.objects.create(content_object=self, **kwargs)

    def get_expiring_certificates(self, days=30):
        """
        Get certificates expiring within specified days.

        Args:
            days: Days threshold for expiration

        Returns:
            QuerySet of expiring certificates
        """

        expiry_threshold = timezone.now().date() + timezone.timedelta(days=days)
        return self.certificates.filter(
            expiry_date__lte=expiry_threshold,
            expiry_date__gte=timezone.now().date(),
            status="valid",
        ).order_by("expiry_date")


class CourseMixin(models.Model):
    """
    Mixin for course enrollment and management.
    """

    class Meta:
        abstract = True

    enrollments = GenericRelation(
        "Enrollment",
        content_type_field="content_type",
        object_id_field="object_id",
        related_query_name="%(class)s_enrollments",
    )

    @property
    def active_enrollments(self):
        """Get active course enrollments."""
        return self.enrollments.filter(status="active").order_by("-enrolled_at")

    @property
    def completed_courses(self):
        """Get completed courses."""
        return self.enrollments.filter(status="completed", completion_date__isnull=False).order_by(
            "-completion_date"
        )

    @property
    def course_progress(self):
        """Calculate overall course progress."""
        active_enrollments = self.enrollments.filter(status="active")
        if not active_enrollments:
            return 0

        total_progress = sum(enrollment.progress for enrollment in active_enrollments)
        return round(total_progress / active_enrollments.count(), 2)

    def enroll_in_course(self, course, **kwargs):
        """
        Enroll in a course.

        Args:
            course: Course object
            **kwargs: Additional enrollment fields

        Returns:
            Enrollment object
        """
        # Project-specific imports removed - use dependency injection

        return Enrollment.objects.create(content_object=self, course=course, **kwargs)

    def get_enrollment(self, course):
        """
        Get enrollment for specific course.

        Args:
            course: Course object

        Returns:
            Enrollment object or None
        """
        return self.enrollments.filter(course=course).first()


class MessageMixin(models.Model):
    """
    Mixin for message sending and receiving.
    """

    class Meta:
        abstract = True

    sent_messages = GenericRelation(
        "Message",
        content_type_field="sender_content_type",
        object_id_field="sender_object_id",
        related_query_name="sent_messages",
    )

    received_messages = GenericRelation(
        "Message",
        content_type_field="recipient_content_type",
        object_id_field="recipient_object_id",
        related_query_name="received_messages",
    )

    @property
    def unread_message_count(self):
        """Count unread messages."""
        return self.received_messages.filter(is_read=False).count()

    @property
    def recent_messages(self):
        """Get recent messages."""
        return self.received_messages.all().order_by("-sent_at")[:10]

    def send_message(self, recipient, subject, content, message_type="general", **kwargs):
        """
        Send a message to another entity.

        Args:
            recipient: Recipient object
            subject: Message subject
            content: Message content
            message_type: Type of message
            **kwargs: Additional message fields

        Returns:
            Message object
        """
        # Project-specific imports removed - use dependency injection

        return Message.objects.create(
            sender_content_object=self,
            recipient_content_object=recipient,
            subject=subject,
            content=content,
            message_type=message_type,
            **kwargs,
        )

    def get_conversation(self, other_party, limit=50):
        """
        Get conversation between this entity and another party.

        Args:
            other_party: The other party in conversation
            limit: Maximum messages to return

        Returns:
            QuerySet of messages
        """
        # Project-specific imports removed - use dependency injection

        # Get messages where this entity is sender and other party is recipient
        sent_messages = Message.objects.filter(
            sender_content_object=self, recipient_content_object=other_party
        )

        # Get messages where other party is sender and this entity is recipient
        received_messages = Message.objects.filter(
            sender_content_object=other_party, recipient_content_object=self
        )

        # Combine and order by sent_at
        conversation = (sent_messages | received_messages).order_by("-sent_at")[:limit]
        return conversation.order_by("sent_at")  # Reorder chronologically

    def mark_messages_as_read(self, sender=None):
        """
        Mark messages as read.

        Args:
            sender: Optional sender to filter by

        Returns:
            Number of messages marked as read
        """
        queryset = self.received_messages.filter(is_read=False)
        if sender:
            queryset = queryset.filter(sender_content_object=sender)

        count = queryset.count()
        queryset.update(is_read=True, read_at=timezone.now())
        return count


class BaseCartMixin:
    """
    Abstract base for site-specific cart implementations.

    ctc-research.com: LMS course cart (CourseCartItem model)
    structa.cloud: Generic e-commerce cart (Product model)

    Subclass and implement all abstract methods for your site.
    """
    @abstractmethod
    def get_cart_items(self, request): ...

    @abstractmethod
    def calculate_total(self, items): ...

    @abstractmethod
    def add_item(self, request, item_id): ...

    @abstractmethod
    def remove_item(self, request, item_id): ...


class BaseDashboardMixin:
    """
    Abstract base for site-specific dashboard implementations.

    ctc-research.com: LMS analytics (enrollment stats, learning streaks)
    structa.cloud: Generic workspace dashboard

    Subclass and implement get_dashboard_context() for your site.
    """
    @abstractmethod
    def get_dashboard_context(self, request): ...

    @abstractmethod
    def get_recent_activity(self, user): ...
