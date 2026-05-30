"""Website-local Django settings for ctc-research.com."""
from pathlib import Path
import sys

_WORKSPACE_DIR = Path(__file__).resolve().parents[1]
if str(_WORKSPACE_DIR) in sys.path:
    sys.path.remove(str(_WORKSPACE_DIR))
sys.path.insert(0, str(_WORKSPACE_DIR))


from configs.site import configure_site_environment

configure_site_environment("ctc-research.com", module="LMS", default_port=5070)

from configs.settings import *  # noqa: E402,F401,F403

ROOT_URLCONF = "www.urls"
WSGI_APPLICATION = "www.wsgi.application"
ASGI_APPLICATION = "www.asgi.application"
