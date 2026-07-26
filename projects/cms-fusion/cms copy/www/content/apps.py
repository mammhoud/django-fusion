"""CTC Research — Content app configuration.

Registers the "content" app_label for Wagtail snippet models
(Publication, Course, TeamMember, CourseCategory, ContactSubmission).
"""

from django.apps import AppConfig


class ContentConfig(AppConfig):
    name = "www.content"
    label = "content"
    verbose_name = "CTC Research Content"
    default_auto_field = "django.db.models.BigAutoField"
