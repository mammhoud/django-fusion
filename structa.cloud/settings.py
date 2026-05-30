"""Website-local settings entrypoint."""
from configs.settings import *  # noqa

# Website-specific Django application settings
ROOT_URLCONF = "www.core.urls"
WSGI_APPLICATION = "www.wsgi.application"
ASGI_APPLICATION = "www.asgi.application"
