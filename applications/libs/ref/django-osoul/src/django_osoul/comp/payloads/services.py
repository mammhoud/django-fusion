"""Base service payload classes."""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseService:
    """Base class for service layer objects."""

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.to_dict()})"


class TokenService(BaseService):
    """Service payload for token-based operations."""

    token: str = ""
    expires_at: Any = None
    user_id: Any = None

    def is_valid(self) -> bool:
        return bool(self.token)


__all__ = ["BaseService", "TokenService"]
