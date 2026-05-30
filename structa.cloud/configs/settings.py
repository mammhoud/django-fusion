"""Local configs shim that exposes `settings` used by the project.

This file imports the settings defined in the workspace-level configs
and adds website-specific Django application settings.
"""

from configs.settings import *  # noqa: E402,F401

# Website-specific Django application settings
ROOT_URLCONF = "www.core.urls"
WSGI_APPLICATION = "www.wsgi.application"
ASGI_APPLICATION = "www.asgi.application"
