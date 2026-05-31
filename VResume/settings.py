"""Website-local Django settings for vresume.structa.cloud."""
from pathlib import Path
import sys

_SITE_DIR = Path(__file__).resolve().parent
_WORKSPACE_DIR = _SITE_DIR.parent
_SITE_APP_DIR = _SITE_DIR / "www"

for _path in (str(_SITE_APP_DIR), str(_WORKSPACE_DIR), str(_SITE_DIR)):
    if _path in sys.path:
        sys.path.remove(_path)
    sys.path.insert(0, _path)

from configs.site import configure_site_environment

configure_site_environment("vresume", module="CMS", default_port=5072)

from configs.settings import *  # noqa: E402,F401,F403

ROOT_URLCONF = "www.urls"
WSGI_APPLICATION = "www.wsgi.application"
ASGI_APPLICATION = "www.asgi.application"
