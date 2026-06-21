from django.apps import AppConfig


class EmailConfig(AppConfig):
    name = "django_rseal.email"
    label = "django_rseal_email"
    verbose_name = "Email"

    def ready(self):
        pass
