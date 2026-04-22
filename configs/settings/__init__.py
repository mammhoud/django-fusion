# ====================================
# 🎯 Django Settings Entry Point
# ====================================

from .CD import *

# ====================================
# 🎯 Core Django Settings (from Dynaconf)
# ====================================
ROOT_URLCONF = "www.urls"
WSGI_APPLICATION = settings.get("DJANGO_WSGI_APPLICATION", "www.wsgi.application")  # noqa: F405
ASGI_APPLICATION = settings.get("DJANGO_ASGI_APPLICATION", "www.asgi.application")  # noqa: F405

