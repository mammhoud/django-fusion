"""Abstract base for task backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractTaskBackend(ABC):
    """Interface that all task backends must implement."""

    @abstractmethod
    def enqueue(self, registration, args: tuple, kwargs: dict) -> Any:
        """Enqueue a registered task for background execution.

        Args:
            registration: A :class:`TaskRegistration` instance.
            args: Positional arguments for the task.
            kwargs: Keyword arguments for the task.

        Returns:
            A backend-specific message / job identifier.
        """
        ...
