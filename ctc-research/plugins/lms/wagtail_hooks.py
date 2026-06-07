from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .snippets import *

"""
WAGTAIL HOOKS CONFIGURATION FOR COURSE MANAGEMENT
==================================================

This file configures the Wagtail admin interface for all course-related models.
It provides comprehensive admin views for managing courses, modules, images, 
specializations, enrollments, and payments.

Menu Organization:
- Courses & Content: Main course management
- Learning Structure: Modules and curriculum
- Enrollments: Student enrollment management
- Payments: Payment transactions, refunds, webhooks
- Media & Assets: Course images and media

Icons Reference:
- book: Courses
- folder: Modules
- image: Course images
- tag: Specializations
- star: Featured content
- user: Enrollments
- credit: Payments
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

class EnrollmentSnippetGroup(SnippetViewSetGroup):
    menu_label = _("Enrollments & Payments")
    menu_icon = "wallet"
    menu_order = 150
    items = (
        EnrollmentViewSet,
        PaymentTransactionViewSet,
        PaymentRefundViewSet,
        PaymentWebhookLogViewSet,
    )

register_snippet(EnrollmentSnippetGroup)
register_snippet(TracksSnippetViewSetGroup)
register_snippet(ClassesSnippetViewSetGroup)

