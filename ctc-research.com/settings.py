"""Website-local settings entrypoint for ctc-research.com."""

from configs.site import configure_site_environment

configure_site_environment("ctc-research.com", module="LMS", default_port=5070)

from configs.settings import *  # noqa: E402,F401,F403
