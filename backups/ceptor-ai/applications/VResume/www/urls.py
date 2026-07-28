"""URL wrapper for the vResume website.

The legacy vResume application keeps its URL declarations in ``core.urls``.
This wrapper lets the workspace use the same ``www.urls`` entry point as the
other websites without changing the legacy route design.
"""
from core.urls import *  # noqa: F401,F403
