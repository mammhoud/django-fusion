"""Website-local settings entrypoint."""
from configs.settings import *  # noqa: E402,F401,F403
from configs.site import configure_site_environment

configure_site_environment("ctc-research.com", module="LMS", default_port=5070)

ROOT_URLCONF = "www.core.urls"
WSGI_APPLICATION = "www.wsgi.application"
ASGI_APPLICATION = "www.asgi.application"
