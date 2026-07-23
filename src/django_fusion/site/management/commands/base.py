"""
Base management command classes for django-fusion.
Provides enhanced command functionality with structured logging and
colorized console output.

Migrated from django-grep/management/base.py.
"""
from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from typing import Any, Generator

import structlog
from django.conf import settings
from django.core.management.base import BaseCommand as DjangoBaseCommand


def _is_dev() -> bool:
    """Return True when running in a development-ish environment."""
    return getattr(settings, "DEBUG", False) or os.environ.get("DJANGO_ENV") == "development"


def _maybe_strip_emoji(message: str, *, use_emoji: bool = True) -> str:
    """Optionally strip leading emoji markers from a log message."""
    if not use_emoji:
        return message
    return message


class BaseCommand(DjangoBaseCommand):
    """
    Enhanced base command with structured logging and colorized output.

    Usage:
        from django_fusion.site.management.commands.base import BaseCommand

        class Command(BaseCommand):
            help = "My custom command"

            def handle(self, *args, **options):
                self.log_info("Starting command")
                # Your command logic here
                self.log_success("Command completed")
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = structlog.get_logger(self.__class__.__module__ + "." + self.__class__.__name__)

    # ------------------------------------------------------------------
    # Console helpers (kept for backward compatibility and testability)
    # ------------------------------------------------------------------
    def _write_stdout(self, message: str) -> None:
        self.stdout.write(message)

    def _write_stderr(self, message: str) -> None:
        self.stderr.write(message)

    # ------------------------------------------------------------------
    # Structured logging helpers
    # ------------------------------------------------------------------
    def log_info(self, message: str, *, _emoji: bool = True, **kwargs: Any) -> None:
        """
        Log an info message via structlog and echo a colored line to stdout.
        """
        msg = _maybe_strip_emoji(message, use_emoji=_emoji)
        self.logger.info(message, **kwargs)
        self._write_stdout(self.style.SUCCESS(f"ℹ {msg}"))

    def log_success(self, message: str, *, _emoji: bool = True, **kwargs: Any) -> None:
        """
        Log a success message via structlog and echo a colored line to stdout.
        """
        msg = _maybe_strip_emoji(message, use_emoji=_emoji)
        self.logger.info(message, **kwargs)
        self._write_stdout(self.style.SUCCESS(f"✓ {msg}"))

    def log_warning(self, message: str, *, _emoji: bool = True, **kwargs: Any) -> None:
        """
        Log a warning message via structlog and echo a colored line to stdout.
        """
        msg = _maybe_strip_emoji(message, use_emoji=_emoji)
        self.logger.warning(message, **kwargs)
        self._write_stdout(self.style.WARNING(f"⚠ {msg}"))

    def log_error(self, message: str, *, _emoji: bool = True, **kwargs: Any) -> None:
        """
        Log an error message via structlog and echo a colored line to stderr.
        """
        msg = _maybe_strip_emoji(message, use_emoji=_emoji)
        self.logger.error(message, **kwargs)
        self._write_stderr(self.style.ERROR(f"✗ {msg}"))

    def log_debug(self, message: str, *, _emoji: bool = True, **kwargs: Any) -> None:
        """
        Log a debug message via structlog and echo a colored line to stdout
        when verbosity is high.
        """
        msg = _maybe_strip_emoji(message, use_emoji=_emoji)
        self.logger.debug(message, **kwargs)
        if self.verbosity >= 2:
            self._write_stdout(self.style.NOTICE(f"🔍 {msg}"))

    def handle_error(self, error: BaseException | str, exit_code: int = 1) -> None:
        """
        Handle an error with logging and optional exit.

        Args:
            error: Exception or error message.
            exit_code: Exit code (0 = don't exit, >0 = exit with code).
        """
        error_msg = str(error)
        self.log_error(error_msg)

        if exit_code > 0:
            sys.exit(exit_code)

    def confirm(self, message: str, default: bool = False) -> bool:
        """
        Ask user for confirmation.

        Args:
            message: Confirmation message.
            default: Default response if user just presses Enter.

        Returns:
            Boolean indicating user's choice.
        """
        default_str = "Y/n" if default else "y/N"
        response = input(f"{message} [{default_str}]: ").strip().lower()

        if not response:
            return default

        return response in ("y", "yes")

    def progress_bar(self, iterable, total=None, prefix: str = "Progress"):
        """
        Display progress bar for iterable.

        Args:
            iterable: Iterable to process.
            total: Total items (if not provided, uses len(iterable)).
            prefix: Prefix text for progress bar.

        Yields:
            Items from iterable.
        """
        if total is None:
            try:
                total = len(iterable)
            except TypeError:
                # Iterable doesn't support len()
                for item in iterable:
                    yield item
                return

        for i, item in enumerate(iterable, 1):
            percent = (i / total) * 100
            bar_length = 40
            filled = int(bar_length * i / total)
            bar = "█" * filled + "-" * (bar_length - filled)

            self.stdout.write(f"\r{prefix}: |{bar}| {percent:.1f}% ({i}/{total})", ending="")
            self.stdout.flush()

            yield item

        self.stdout.write("")  # New line after completion


class LoggingCommand(BaseCommand):
    """
    Command with structured logging support and context binding.

    Usage:
        from django_fusion.site.management.commands.base import LoggingCommand

        class Command(LoggingCommand):
            help = "My logging command"

            def handle(self, *args, **options):
                with self.log_context(operation="import_data"):
                    self.log_info("Starting import")
                    # Your command logic here
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context: dict[str, Any] = {}

    @contextmanager
    def log_context(self, **kwargs: Any) -> Generator[None, None, None]:
        """
        Context manager for adding context to logs.

        Args:
            **kwargs: Context key-value pairs.

        Usage:
            with self.log_context(user_id=123, operation="import"):
                self.log_info("Processing")
        """
        previous = self.context.copy()
        self.context.update(kwargs)
        try:
            yield
        finally:
            self.context = previous

    def add_context(self, **kwargs: Any) -> None:
        """
        Add context to all subsequent logs.

        Args:
            **kwargs: Context key-value pairs.
        """
        self.context.update(kwargs)

    def clear_context(self) -> None:
        """Clear all context."""
        self.context = {}

    def _merge_context(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        merged = self.context.copy()
        merged.update(kwargs)
        return merged

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log info with context."""
        merged = self._merge_context(kwargs)
        super().log_info(message, **merged)

    def log_success(self, message: str, **kwargs: Any) -> None:
        """Log success with context."""
        merged = self._merge_context(kwargs)
        super().log_success(message, **merged)

    def log_warning(self, message: str, **kwargs: Any) -> None:
        """Log warning with context."""
        merged = self._merge_context(kwargs)
        super().log_warning(message, **merged)

    def log_error(self, message: str, **kwargs: Any) -> None:
        """Log error with context."""
        merged = self._merge_context(kwargs)
        super().log_error(message, **merged)


class LogContext:
    """Context manager for logging context (kept for backward compatibility)."""

    def __init__(self, command: LoggingCommand, context: dict[str, Any]):
        self.command = command
        self.context = context
        self.previous_context: dict[str, Any] = {}

    def __enter__(self) -> "LogContext":
        self.previous_context = self.command.context.copy()
        self.command.add_context(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.command.context = self.previous_context
        return False


# Convenience alias for backward compatibility with older Osoul naming.
OsoulBaseCommand = BaseCommand
