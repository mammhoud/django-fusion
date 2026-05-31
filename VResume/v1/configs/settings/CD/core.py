# ====================================
# 🛠️ Development Environment Settings
# ====================================
import os
from pathlib import Path

from configs.base import *

from ..conf import Environment, settings

# ====================================
# 🔧 Core Settings
# ====================================
MODULE = "CMS"
DEBUG = True

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = settings.get("DJANGO_WSGI_APPLICATION")  # noqa: F405
ASGI_APPLICATION = settings.get("DJANGO_ASGI_APPLICATION")  # noqa: F405

