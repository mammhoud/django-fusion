"""
django_rseal.pipelines.models.tags — shim re-exporting from django_rseal.content.models.tags

This module exists for backward compatibility. All tag models live in
django_rseal.models.tags.
"""
import warnings

from django_rseal.content.models.tags import *  # noqa: F401, F403
from django_rseal.content.models.tags import (  # noqa: F401
    BaseTag,
    BaseTagCategory,
    PersonTagCategory,
    Tag,
    TagHistory,
    TagImportanceChoices,
    TagRelationship,
    TagVisibilityChoices,
)

warnings.warn(
    "django_rseal.pipelines.models.tags has been moved to django_rseal.models.tags. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
