# ====================================
# 🎯 Django Settings Entry Point
# ====================================

from .CD import *

# ====================================
# 🎯 Core Django Settings (from Dynaconf)
# ====================================
ROOT_URLCONF = "alliance.urls"
WSGI_APPLICATION = settings.get("DJANGO_WSGI_APPLICATION", "alliance.wsgi.application")  # noqa: F405
ASGI_APPLICATION = settings.get("DJANGO_ASGI_APPLICATION", "alliance.asgi.application")  # noqa: F405

