from django.utils.translation import gettext_lazy as _
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .snippets import (
    ClassesSnippet,
    CourseSnippet,
    EnrollmentViewSet,
    ModuleSnippet,
    PaymentRefundViewSet,
    PaymentTransactionViewSet,
    PaymentWebhookLogViewSet,
    ReviewViewSet,
    ScheduleSnippet,
)

"""
WAGTAIL HOOKS — CTC Research LMS
=================================

Menu groups:
  Classes     (100) — ClassesSnippet, ScheduleSnippet
  Tracks      (140) — ModuleSnippet, CourseSnippet, ReviewViewSet
  Payments    (150) — EnrollmentViewSet + payment sub-views

Icons: wagtail-font-awesome-svg solid set where built-ins are insufficient.
"""


# =============================================================================
# GROUPS
# =============================================================================

class ClassesSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = _("Classes")
    menu_icon = "glasses"
    menu_order = 100
    items = (
        ClassesSnippet,
        ScheduleSnippet,
    )


class TracksSnippetViewSetGroup(SnippetViewSetGroup):
    menu_label = _("Tracks")
    menu_icon = "openquote"
    menu_order = 140
    items = (
        ModuleSnippet,
        CourseSnippet,
        ReviewViewSet,
    )


class EnrollmentSnippetGroup(SnippetViewSetGroup):
    menu_label = _("Enrollments & Payments")
    # FA solid/wallet
    menu_icon = "wagtailfontawesomesvg/solid/wallet.svg"
    menu_order = 150
    items = (
        EnrollmentViewSet,
        PaymentTransactionViewSet,
        PaymentRefundViewSet,
        PaymentWebhookLogViewSet,
    )


# =============================================================================
# REGISTRATION
# =============================================================================

register_snippet(ClassesSnippetViewSetGroup)
register_snippet(TracksSnippetViewSetGroup)
register_snippet(EnrollmentSnippetGroup)
