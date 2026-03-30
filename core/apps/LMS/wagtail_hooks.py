from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .snippets import *

"""
WAGTAIL HOOKS CONFIGURATION FOR COURSE MANAGEMENT
==================================================

This file configures the Wagtail admin interface for all course-related models.
It provides comprehensive admin views for managing courses, modules, images, and specializations.

Menu Company:
- Courses & Content: Main course management
- Learning Structure: Modules and curriculum
- Media & Assets: Course images and media
- Specializations: Course categories and topics

Icons Reference:
- book: Courses
- folder: Modules
- image: Course images
- tag: Specializations
- star: Featured content
"""




# =============================================================================
# VIEWSET GROUPS - Organizing course models in admin menu
# =============================================================================


class ClassesSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = _("Classes")
    menu_icon = "glasses"
    menu_order = 100
    items = (
        ClassesSnippet,
        ScheduleSnippet,
        # CourseImageViewSet,
        # SpecializationViewSet,
    )


class TracksSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = _("Tracks")
    menu_icon = "openquote"
    menu_order = 140
    items = (
        # TrackSnippet,
        ModuleSnippet,
        CourseSnippet,
        ReviewViewSet,
    )


# =============================================================================
# REGISTRATION
# =============================================================================

register_snippet(TracksSnippetViewSetGroup)
register_snippet(ClassesSnippetViewSetGroup)

class EnrollmentSnippetGroup(SnippetViewSetGroup):
    menu_label = _("Enrollments")
    menu_icon = "group"
    menu_order = 200
    items = (
        EnrollmentViewSet,
    )

# register_snippet(EnrollmentSnippetGroup)

