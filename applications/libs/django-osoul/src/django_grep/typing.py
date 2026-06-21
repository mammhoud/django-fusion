# ruff: noqa: E402
import warnings

warnings.warn(
    "django_grep.typing is deprecated. Use django_osoul.typing instead.",
    DeprecationWarning,
    stacklevel=2,
)
from django_osoul.typing import *  # noqa: F401, F403
