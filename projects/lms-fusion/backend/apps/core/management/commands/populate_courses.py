"""Compatibility wrapper for django-fusion's populate_courses command."""

from pathlib import Path

from django_fusion.management.commands.populate_courses import Command as FusionCommand


class Command(FusionCommand):
    """Expose the shared Fusion command through this site's models."""

    courses_page_model = "apps.pages.lms.models.courses.index.CoursesPage"
    course_model = "apps.pages.lms.models.courses.info.Course"
    home_page_model = "apps.content.models.pages.home.HomePage"
    event_page_model = "apps.content.models.pages.events.EventPage"
    course_fixtures_dir = Path("plugins/lms/fixtures")
    events_fixture = Path("assets/fixtures/events.json")
