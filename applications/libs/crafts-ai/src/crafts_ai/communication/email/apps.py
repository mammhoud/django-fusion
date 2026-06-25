from django.apps import AppConfig


class EmailConfig(AppConfig):
    name = "crafts_ai.email"
    label = "crafts_ai_email"
    verbose_name = "Email"

    def ready(self):
        pass
