"""Landing-fusion auth app configuration."""

from django.apps import AppConfig


class AuthConfig(AppConfig):
    name = "apps.auth"
    label = "landing_auth"
    verbose_name = "Landing Auth"
