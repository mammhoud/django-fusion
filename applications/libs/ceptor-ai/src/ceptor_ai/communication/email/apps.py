from django.apps import AppConfig


class EmailConfig(AppConfig):
    name = "ceptor_ai.email"
    label = "ceptor_ai_email"
    verbose_name = "Email"

    def ready(self):
        pass
