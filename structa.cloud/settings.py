"""Website-local settings entrypoint for structa.cloud."""

from configs.site import configure_site_environment

from configs.settings import *  # noqa: E402,F401,F403

configure_site_environment("structa.cloud", module="CMS", default_port=5071)

ROOT_URLCONF = "www.core.urls"
WSGI_APPLICATION = "www.wsgi.application"
ASGI_APPLICATION = "www.asgi.application"
