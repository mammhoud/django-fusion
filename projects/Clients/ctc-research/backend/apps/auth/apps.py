"""AppConfig for the Precis auth adapter package.

The plain module path ``apps.auth`` would collide with the label of
``django.contrib.auth``, so an explicit AppConfig with a unique label is
required. The package carries no models — only allauth adapters.
"""

from django.apps import AppConfig


class PrecisAuthConfig(AppConfig):
    name = "apps.auth"
    label = "precis_auth"
    verbose_name = "Precis Auth (allauth adapters)"
