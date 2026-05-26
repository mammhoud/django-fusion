"""
🏗️ Django Settings Configuration
================================
Combines Pydantic environment variables with Dynaconf configuration files.
"""

import os

from .conf import settings


# Print environment summary on startup
if os.getenv("DJANGO_PRINT_ENV", "true").lower() == "true":
    settings.print_summary()


__all__ = ["settings"]
