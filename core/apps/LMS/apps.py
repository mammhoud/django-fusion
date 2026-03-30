from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.LMS'
    label = "lms"
    verbose_name = _("LMS Module")
