"""
ASGI/WSGI server entry point for ctc-research website.

This module imports the unified server from configs and makes it available
for both development and production use.

Usage:
  gunicorn ctc-research.server:application
  uvicorn ctc-research.server:application
"""

import os
import sys
from pathlib import Path

# Set website identifier
os.environ.setdefault("DJANGO_SITE", "ctc-research")
os.environ.setdefault("DJANGO_WEBSITE", "ctc-research")
os.environ.setdefault("WEBSITE", "ctc-research")
os.environ.setdefault("PROJECT_PATH", "ctc-research")

# Add workspace root to path
workspace_root = Path(__file__).resolve().parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

# Import the unified server application
from configs.server import application

__all__ = ["application"]
