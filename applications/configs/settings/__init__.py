"""Workspace settings entrypoint.

Selects one compact settings layer from ``SERVER_ENV``/``DJANGO_SERVER_ENV`` and
then appends shared service configuration.
"""

import os

from .conf import settings as _settings

_profile = (
    os.getenv("SERVER_ENV")
    or os.getenv("DJANGO_SERVER_ENV")
    or str(getattr(_settings, "SERVER_ENV", "development"))
).lower()

if _profile in {"production", "prod"}:
    from .CD.production import *  # noqa: F401,F403
elif _profile in {"demo", "staging"}:
    from .CD.demo import *  # noqa: F401,F403
else:
    from .CD.core import *  # noqa: F401,F403

from .CD.services import *  # noqa: F401,F403
