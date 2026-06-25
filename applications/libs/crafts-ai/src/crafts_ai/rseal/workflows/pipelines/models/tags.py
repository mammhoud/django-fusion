"""
crafts_ai.pipelines.models.tags — shim re-exporting from crafts_ai.content.models.tags

This module exists for backward compatibility. All tag models live in
crafts_ai.models.tags.
"""
import warnings

from crafts_ai.content.models.tags import *  # noqa: F401, F403
from crafts_ai.content.models.tags import (  # noqa: F401
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
    "crafts_ai.pipelines.models.tags has been moved to crafts_ai.models.tags. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
