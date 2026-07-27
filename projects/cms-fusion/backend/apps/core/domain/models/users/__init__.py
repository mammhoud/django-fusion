# Re-export UserGroup from email models
from apps.core.domain.services.email.models import UserGroup  # noqa: F401

from .team import *
from .users import *

__all__ = ["UserGroup"]
