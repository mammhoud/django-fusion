"""
ASGI/WSGI server entry point for VResume website.

This module imports the unified server from configs and makes it available
for both development and production use.

Usage:
  gunicorn vresume.server:application
  uvicorn vresume.server:application
"""

import os
import sys
from pathlib import Path

# Set website identifier
os.environ.setdefault("DJANGO_SITE", "vresume")
os.environ.setdefault("DJANGO_WEBSITE", "vresume")
os.environ.setdefault("WEBSITE", "vresume")
os.environ.setdefault("PROJECT_PATH", "vresume")

# Add workspace root to path
workspace_root = Path(__file__).resolve().parent.parent
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

# Import the unified server application
from configs.server import application

__all__ = ["application"]
