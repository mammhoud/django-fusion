from django.db import models
from django.db.models import F, Q


class EnrollmentQuerySet(models.QuerySet):
    """QuerySet helpers for learner entitlements."""

    def verified(self):
        """Only entitlements that are valid for the course's price.

        A free course is always valid; a paid course requires a provider
        reference whose amount covers the price (a provider name alone is
        not a payment integration).
        """
        return self.filter(
            Q(course__price__lte=0)
            | Q(provider_reference__gt="", amount_paid__gte=F("course__price"))
        )

    def active_or_completed(self):
        return self.filter(status__in=["active", "completed"])

    def for_course(self, course):
        return self.filter(course=course)
