"""Workspace settings entrypoint using full layered configuration when available.
Falls back gracefully if dynaconf stack is unavailable.
"""

import os

_profile = (os.getenv("SERVER_ENV") or os.getenv("DJANGO_SERVER_ENV") or "development").lower()

try:
    from .conf import settings as _settings
    _profile = (os.getenv("SERVER_ENV") or os.getenv("DJANGO_SERVER_ENV") or str(getattr(_settings, "SERVER_ENV", _profile))).lower()
except Exception:
    # keep env-derived profile if dynaconf/pydantic stack isn't importable yet
    pass

if _profile in {"production", "prod"}:
    from .CD.production import *  # noqa: F401,F403
elif _profile in {"demo", "staging"}:
    from .CD.demo import *  # noqa: F401,F403
else:
    from .CD.core import *  # noqa: F401,F403

try:
    from .CD.services import *  # noqa: F401,F403
except Exception:
    pass
