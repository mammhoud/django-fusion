# ====================================
# 🎯 Django Settings Entry Point
# ====================================

from .CD import *

# ====================================
# 🎯 Core Django Settings (from Dynaconf)
# ====================================
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = settings.get("DJANGO_WSGI_APPLICATION")  # noqa: F405
ASGI_APPLICATION = settings.get("DJANGO_ASGI_APPLICATION")  # noqa: F405

