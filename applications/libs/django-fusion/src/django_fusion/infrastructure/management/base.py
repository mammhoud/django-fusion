"""
Base management command classes for django-fusion.
Provides enhanced command functionality with logging and error handling.

Migrated from django-grep/management/base.py.
"""
import logging
import sys

from django.core.management.base import BaseCommand as DjangoBaseCommand


class BaseCommand(DjangoBaseCommand):
    """
    Enhanced base command with logging and error handling.

    Usage:
        from django_fusion.management.base import BaseCommand

        class Command(BaseCommand):
            help = "My custom command"

            def handle(self, *args, **options):
                self.log_info("Starting command")
                # Your command logic here
                self.log_success("Command completed")
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    def log_info(self, message, **kwargs):
        """
        Log info message to both logger and stdout.

        Args:
            message: Message to log
            **kwargs: Additional context for logger
        """
        self.logger.info(message, extra=kwargs)
        self.stdout.write(self.style.SUCCESS(f"ℹ {message}"))

    def log_success(self, message, **kwargs):
        """
        Log success message to both logger and stdout.

        Args:
            message: Message to log
            **kwargs: Additional context for logger
        """
        self.logger.info(message, extra=kwargs)
        self.stdout.write(self.style.SUCCESS(f"✓ {message}"))

    def log_warning(self, message, **kwargs):
        """
        Log warning message to both logger and stdout.

        Args:
            message: Message to log
            **kwargs: Additional context for logger
        """
        self.logger.warning(message, extra=kwargs)
        self.stdout.write(self.style.WARNING(f"⚠ {message}"))

    def log_error(self, message, **kwargs):
        """
        Log error message to both logger and stderr.

        Args:
            message: Message to log
            **kwargs: Additional context for logger
        """
        self.logger.error(message, extra=kwargs)
        self.stderr.write(self.style.ERROR(f"✗ {message}"))

    def log_debug(self, message, **kwargs):
        """
        Log debug message to logger only.

        Args:
            message: Message to log
            **kwargs: Additional context for logger
        """
        self.logger.debug(message, extra=kwargs)
        if self.verbosity >= 2:
            self.stdout.write(self.style.NOTICE(f"🔍 {message}"))

    def handle_error(self, error, exit_code=1):
        """
        Handle error with logging and optional exit.

        Args:
            error: Exception or error message
            exit_code: Exit code (0 = don't exit, >0 = exit with code)
        """
        error_msg = str(error)
        self.log_error(error_msg)

        if exit_code > 0:
            sys.exit(exit_code)

    def confirm(self, message, default=False):
        """
        Ask user for confirmation.

        Args:
            message: Confirmation message
            default: Default response if user just presses Enter

        Returns:
            Boolean indicating user's choice
        """
        default_str = "Y/n" if default else "y/N"
        response = input(f"{message} [{default_str}]: ").strip().lower()

        if not response:
            return default

        return response in ["y", "yes"]

    def progress_bar(self, iterable, total=None, prefix="Progress"):
        """
        Display progress bar for iterable.

        Args:
            iterable: Iterable to process
            total: Total items (if not provided, uses len(iterable))
            prefix: Prefix text for progress bar

        Yields:
            Items from iterable
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
    Command with structured logging support.

    Usage:
        from django_fusion.management.base import LoggingCommand

        class Command(LoggingCommand):
            help = "My logging command"

            def handle(self, *args, **options):
                with self.log_context(operation="import_data"):
                    self.log_info("Starting import")
                    # Your command logic here
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.context = {}

    def log_context(self, **kwargs):
        """
        Context manager for adding context to logs.

        Args:
            **kwargs: Context key-value pairs

        Usage:
            with self.log_context(user_id=123, operation="import"):
                self.log_info("Processing")
        """
        return LogContext(self, kwargs)

    def add_context(self, **kwargs):
        """
        Add context to all subsequent logs.

        Args:
            **kwargs: Context key-value pairs
        """
        self.context.update(kwargs)

    def clear_context(self):
        """Clear all context."""
        self.context = {}

    def log_info(self, message, **kwargs):
        """Log info with context."""
        kwargs.update(self.context)
        super().log_info(message, **kwargs)

    def log_success(self, message, **kwargs):
        """Log success with context."""
        kwargs.update(self.context)
        super().log_success(message, **kwargs)

    def log_warning(self, message, **kwargs):
        """Log warning with context."""
        kwargs.update(self.context)
        super().log_warning(message, **kwargs)

    def log_error(self, message, **kwargs):
        """Log error with context."""
        kwargs.update(self.context)
        super().log_error(message, **kwargs)


class LogContext:
    """Context manager for logging context."""

    def __init__(self, command, context):
        self.command = command
        self.context = context
        self.previous_context = {}

    def __enter__(self):
        self.previous_context = self.command.context.copy()
        self.command.add_context(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.command.context = self.previous_context
        return False
