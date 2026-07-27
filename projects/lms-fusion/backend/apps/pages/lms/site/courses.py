
import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_POST
from django_fusion.site.interface.notifications import NotificationMixin
from django_fusion.site.interface.page_handler import PageHandler

logger = logging.getLogger(__name__)
from apps.pages.lms.management.services.courses import CourseService


class CoursesView(PageHandler, NotificationMixin):
    """
    Courses management view.
    """

    page_title = "Courses"
    template_name = "base_profile.html"
    fragment_name = "profile.courses"
    layout_path = "profile/skeleton.html"

    def get_context_data(self, request: HttpRequest, **kwargs):
        """
        Get context data for courses page.
        """
        self.request = request
        context = super().get_context_data(**kwargs)

        if request.user.is_authenticated:
            try:
                # Get course dashboard
                dashboard = CourseService.get_user_course_dashboard(request.user)

                # Get active courses
                from apps.pages.lms.models import Course

                active_courses = Course.objects.get_active_courses(request.user)

                # Get recommended courses
                recommended_courses = Course.objects.get_recommended_courses(request.user, 3)

                context.update(
                    {
                        "dashboard": dashboard,
                        "active_courses": active_courses,
                        "recommended_courses": recommended_courses,
                        "difficulties": Course.DifficultyChoices.choices,
                        "categories": self._get_course_categories(),
                    }
                )

            except Exception as e:
                logger.error(f"Error getting courses context: {e}")
                self.show_notification(
                    message="Error loading courses",
                    level="error",
                    title="Error",
                    duration=5000,
                    request=request,
                )

        return context

    def _get_course_categories(self):
        """Get course categories."""
        # This would typically come from a Category model
        return [
            {"id": "web", "name": "Web Development"},
            {"id": "mobile", "name": "Mobile Development"},
            {"id": "data", "name": "Data Science"},
            {"id": "ai", "name": "Artificial Intelligence"},
            {"id": "business", "name": "Business"},
            {"id": "design", "name": "Design"},
        ]

    @require_POST
    @login_required
    def enroll_course(self, request: HttpRequest) -> JsonResponse:
        """
        Enroll in a course.
        """
        try:
            data = json.loads(request.body) if request.body else {}
            course_id = data.get("course_id")

            if not course_id:
                return JsonResponse(
                    {"status": "error", "message": "Course ID is required"}, status=400
                )

            success, message, enrollment = CourseService.enroll_user_in_course(
                user=request.user,
                course_id=course_id,
            )

            if success:
                self.show_notification(
                    message=message,
                    level="success",
                    title="Enrollment Successful",
                    duration=3000,
                    request=request,
                )

                return JsonResponse(
                    {
                        "status": "success",
                        "message": message,
                        "enrollment": {
                            "id": str(enrollment.id),
                            "course_title": enrollment.course.title,
                            "status": enrollment.status,
                            "progress": enrollment.progress,
                        },
                    }
                )
            else:
                self.show_notification(
                    message=message,
                    level="error",
                    title="Enrollment Failed",
                    duration=5000,
                    request=request,
                )

                return JsonResponse({"status": "error", "message": message}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
        except Exception as e:
            logger.error(f"Error enrolling in course: {e}")
            return JsonResponse(
                {"status": "error", "message": f"Error enrolling in course: {str(e)}"}, status=500
            )
