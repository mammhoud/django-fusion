# ====================================
# 🔄 Auto-reload Configuration
# ====================================
from typing import Any

try:
    from core import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

from . import is_debug_mode
from .config import (
    AUTORELOAD_TEMPLATE_LOADERS,
    AUTORELOAD_WATCH_PATHS,
    BASE_DIR,
    TEMPLATE_DEBUG,
)


class AutoreloadSetup:
    """
    Configuration for auto-reloading templates and static files.
    """

    @staticmethod
    def configure_template_loaders(
        templates_config: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Configure template loaders for auto-reload when DEBUG is True.

        Args:
            templates_config: Current TEMPLATES configuration

        Returns:
            Updated TEMPLATES configuration
        """
        if not is_debug_mode():
            logger.debug("DEBUG is False, using cached template loaders.")
            return templates_config

        if not templates_config:
            logger.warning("No TEMPLATES configuration found.")
            return templates_config

        # Enable template debugging
        for template_config in templates_config:
            template_config["OPTIONS"]["debug"] = TEMPLATE_DEBUG

        # Update the first template engine configuration
        templates_config[0]["OPTIONS"]["loaders"] = AUTORELOAD_TEMPLATE_LOADERS

        logger.debug("Configured non-cached template loaders for auto-reload.")
        return templates_config

    @staticmethod
    def configure_autoreload(
        debug: bool,
        templates: list[dict[str, Any]],
        installed_apps: list[str],
        middleware: list[str],
        internal_ips: list[str] = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Configure auto-reload for development environment.

        Args:
            debug: Whether DEBUG mode is enabled
            templates: TEMPLATES configuration
            installed_apps: INSTALLED_APPS list
            middleware: MIDDLEWARE list
            internal_ips: INTERNAL_IPS list

        Returns:
            Dictionary with updated configurations
        """
        result = {
            "installed_apps": installed_apps.copy(),
            "middleware": middleware.copy(),
            "templates": templates.copy(),
            "internal_ips": internal_ips.copy() if internal_ips else [],
        }

        if not debug:
            logger.debug("DEBUG is False, skipping auto-reload configuration.")
            return result

        # Configure template loaders
        result["templates"] = AutoreloadSetup.configure_template_loaders(templates)

        # Configure livereload (if not already configured)
        from .callbacks import enable_livereload

        if enable_livereload():
            logger.debug("Livereload auto-configured for development.")

        return result

    @classmethod
    def setup_django_autoreload(cls):
        """
        Set up Django for auto-reloading.
        This should be called after django.setup().
        """
        if not is_debug_mode():
            return

        try:
            # Additional setup for development
            logger.debug("Django auto-reload setup complete.")

            # Watch for template changes
            class DemoTemplateLoader:
                def __init__(self, engine):
                    self.engine = engine

                def watch_for_changes(self):
                    return []

            # This is where you'd integrate with Django's autoreload
            logger.info("Auto-reload is enabled for templates and static files.")

        except ImportError as e:
            logger.error(f"Error setting up Django auto-reload: {e}")

    @staticmethod
    def get_watch_paths() -> list[str]:
        """
        Get list of paths to watch for changes.

        Returns:
            List of directory paths
        """
        watch_paths = []

        for path in AUTORELOAD_WATCH_PATHS:
            full_path = BASE_DIR / path
            if full_path.exists():
                watch_paths.append(str(full_path))
                logger.debug(f"Added to watch list: {full_path}")
            else:
                logger.warning(f"Watch path does not exist: {full_path}")

        return watch_paths


def configure_autoreload(settings_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Convenience function to configure auto-reload.

    Args:
        settings_dict: Dictionary of current settings

    Returns:
        Updated settings dictionary
    """
    debug = settings_dict.get("DEBUG", False)

    if not debug:
        return settings_dict

    logger.info("Configuring auto-reload for development...")

    # Get configurations
    templates = settings_dict.get("TEMPLATES", [])
    installed_apps = settings_dict.get("INSTALLED_APPS", [])
    middleware = settings_dict.get("MIDDLEWARE", [])
    internal_ips = settings_dict.get("INTERNAL_IPS", [])

    # Configure auto-reload
    result = AutoreloadSetup.configure_autoreload(
        debug=debug,
        templates=templates,
        installed_apps=installed_apps,
        middleware=middleware,
        internal_ips=internal_ips,
    )

    # Update settings dictionary
    settings_dict.update(
        {
            "TEMPLATES": result["templates"],
            "INSTALLED_APPS": result["installed_apps"],
            "MIDDLEWARE": result["middleware"],
            "INTERNAL_IPS": result["internal_ips"],
        }
    )

    # Setup Django auto-reload
    AutoreloadSetup.setup_django_autoreload()

    return settings_dict
