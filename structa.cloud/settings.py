"""Website-local settings entrypoint for structa.cloud."""

from configs.site import configure_site_environment

configure_site_environment("structa.cloud", module="CMS", default_port=5071)

from configs.settings import *  # noqa: E402,F401,F403
