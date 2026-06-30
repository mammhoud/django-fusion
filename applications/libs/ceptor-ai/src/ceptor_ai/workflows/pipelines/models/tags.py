"""
ceptor_ai.pipelines.models.tags — shim re-exporting from ceptor_ai.content.models.tags

This module exists for backward compatibility. All tag models live in
ceptor_ai.models.tags.
"""
import warnings

from ceptor_ai.content.models.tags import *  # noqa: F401, F403
from ceptor_ai.content.models.tags import (  # noqa: F401
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
    "ceptor_ai.pipelines.models.tags has been moved to ceptor_ai.models.tags. "
    "Please update your imports.",
    DeprecationWarning,
    stacklevel=2,
)
