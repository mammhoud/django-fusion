from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HandlersRegistrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts.registration"
    label = "handlers_registration"
    verbose_name = _("Registration")

    def ready(self):
        import www.apps.registration.signals  # noqa: F401
        from www.apps.registration.admin import register_user_admin
        register_user_admin()
