from django.conf import settings
from django.db import models
from django_fusion.models.base import BaseModel as DefaultBase

from apps.pages.lms.managers.enrollments import EnrollmentManager


class Enrollment(
    DefaultBase,
):
    """Track student enrollment in courses.
    this class for lms every profile with signal to add the enrollment for each profile.
    at student module"""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    is_active = models.BooleanField(default=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    payment_reference = models.CharField(max_length=255, null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    payment_id = models.CharField(max_length=200, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_date = models.DateTimeField(null=True, blank=True)
    course = models.ForeignKey("lms.Course", on_delete=models.CASCADE, related_name='enrollments')

    # Progress tracking (Aligned with Manager)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('dropped', 'Dropped'),
            ('expired', 'Expired'),
        ],
        default='active'
    )
    progress = models.FloatField(default=0.0)  # 0-100%
    last_accessed_at = models.DateTimeField(auto_now=True)

    objects = EnrollmentManager()
    # packages = GenericRelation(
    #     PackageAssignment,
    #     content_type_field="content_type",
    #     object_id_field="object_id",
    # )
    class Meta:
        app_label = "lms"
        unique_together = ["student" ,'course']
        ordering = ["-created_at"]
        db_table = "Enrollments"

    def __str__(self):
        return f"Enrollment for {self.student} - {self.course.title} - Active: {self.is_active}"

    def get_packages(self):
        return self.packages.all() if hasattr(self, 'packages') else []

    def get_active_packages(self):
        return self.packages.filter(is_active=True) if hasattr(self, 'packages') else []

    def get_completed_packages(self):
        return self.packages.filter(is_completed=True) if hasattr(self, 'packages') else []

    def get_incomplete_packages(self):
        return self.packages.filter(is_completed=False) if hasattr(self, 'packages') else []

    def get_active_courses(self):
        return self.packages.filter(is_active=True).values_list("course", flat=True) if hasattr(self, 'packages') else []
