"""Local configs shim that exposes `settings` used by the project.

This file imports the settings defined in /app/settings.py so that
`from configs.settings import *` works in containers that expect the
`configs` package.
"""

from settings import *  # noqa: E402,F401
