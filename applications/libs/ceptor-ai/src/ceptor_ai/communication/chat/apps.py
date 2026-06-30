from django.apps import AppConfig


class RsealChatConfig(AppConfig):
    name = "ceptor_ai.chat"
    label = "rseal_chat"
    verbose_name = "Rseal Chat"

    def ready(self):
        pass  # signal hooks can be registered here
