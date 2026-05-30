"""Deployment wrapper settings for structa.cloud."""
from pathlib import Path
import sys

_WORKSPACE_DIR = Path(__file__).resolve().parents[2]
if str(_WORKSPACE_DIR) in sys.path:
    sys.path.remove(str(_WORKSPACE_DIR))
sys.path.insert(0, str(_WORKSPACE_DIR))

from configs.site import configure_site_environment

configure_site_environment("structa.cloud", module="CMS", default_port=5071)

from configs.settings import *  # noqa: F401,F403,E402

ROOT_URLCONF = "www.urls"
WSGI_APPLICATION = "www.wsgi.application"
ASGI_APPLICATION = "www.asgi.application"
