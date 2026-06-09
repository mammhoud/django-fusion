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
WAGTAIL HOOKS CONFIGURATION FOR COURSE MANAGEMENT
==================================================

Menu groups:
- Classes:     ClassesSnippet, ScheduleSnippet
- Tracks:      ModuleSnippet, CourseSnippet, ReviewViewSet
- Enrollments: EnrollmentViewSet
- Payments:    PaymentTransactionViewSet, PaymentRefundViewSet,
               PaymentWebhookLogViewSet

Icons use wagtail-font-awesome-svg (solid set) where Wagtail built-ins
are insufficient.  Group icons follow the same convention:
  "wagtailfontawesomesvg/solid/<name>.svg"
"""


# =============================================================================
# VIEWSET GROUPS
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
    menu_label = _("Enrollments")
    menu_icon = "group"
    menu_order = 200
    items = (EnrollmentViewSet,)


class PaymentSnippetGroup(SnippetViewSetGroup):
    menu_label = _("Payments")
    # FA solid/wallet
    menu_icon = "wagtailfontawesomesvg/solid/wallet.svg"
    menu_order = 250
    items = (
        PaymentTransactionViewSet,
        PaymentRefundViewSet,
        PaymentWebhookLogViewSet,
    )


# =============================================================================
# REGISTRATION
# =============================================================================

register_snippet(TracksSnippetViewSetGroup)
register_snippet(ClassesSnippetViewSetGroup)
register_snippet(EnrollmentSnippetGroup)
register_snippet(PaymentSnippetGroup)
