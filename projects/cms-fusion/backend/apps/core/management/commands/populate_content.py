"""Compatibility wrapper for django-fusion's populate_content command."""

from django_fusion.management.commands.populate_content import Command as FusionCommand


class Command(FusionCommand):
    """Expose the shared Fusion command through this site's models."""

    model_paths = {
        "HomePage": "apps.content.models.pages.home.HomePage",
        "AboutPage": "apps.content.models.pages.about.AboutPage",
        "ContactPage": "apps.content.models.pages.contact.ContactPage",
        "TeamPage": "apps.content.models.pages.team.TeamPage",
        "CoursesPage": "apps.pages.lms.models.courses.index.CoursesPage",
        "EventPage": "apps.content.models.pages.events.EventPage",
        "ServicesPage": "apps.content.models.pages.services.ServicesPage",
    }
    organization_model_paths = ("apps.handlers.models.manage.company.Organization",)
