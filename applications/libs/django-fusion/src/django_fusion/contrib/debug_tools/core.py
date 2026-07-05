"""
Core classes for django_fusion debug tools.

This module provides the main classes for managing development tools
configuration including DebugToolbarSetup for centralized tool management.

Classes:
    DebugToolbarSetup: Main class for managing development tools configuration.

Functions:
    get_internal_ips: Dynamically determine INTERNAL_IPS based on environment.
    get_environment_info: Get information about the current environment.

Usage::

    from django_fusion.contrib.debug_tools.core import DebugToolbarSetup

    setup = DebugToolbarSetup()
    setup.print_status()
"""

from typing import Any

try:
    from core import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from .base import BaseSetup, DebugToolbar, Livereload, Silk, is_debug_mode, is_testing
from .config import DEFAULT_MIDDLEWARE_POSITIONS


class DebugToolbarSetup(BaseSetup):
    """
    Main class for managing development tools configuration.
    """

    def __init__(self):
        self.tools = {
            'debug_toolbar': DebugToolbar(),
            'silk': Silk(),
            'livereload': Livereload(),
        }

    def update_middleware(
        self,
        middleware: list[str],
        positions: dict[str, int | None] = None,
    ) -> list[str]:
        """
        Conditionally adds development middleware.

        Args:
            middleware: Current middleware list
            positions: Dictionary with positions for each middleware
        """
        if positions is None:
            positions = DEFAULT_MIDDLEWARE_POSITIONS

        updated_middleware = middleware[:]

        # Add each tool's middleware if enabled
        for tool_name, tool in self.tools.items():
            if tool.is_enabled():
                updated_middleware = self._add_middleware(
                    updated_middleware,
                    tool.middleware_class,
                    positions.get(tool_name),
                    skip_if_exists=True
                )

        return updated_middleware

    def configure_apps(
        self,
        installed_apps: list[str],
        add_to_beginning: bool = True,
        include_all: bool = True
    ) -> list[str]:
        """
        Conditionally adds development tools to INSTALLED_APPS.
        """
        updated_apps = installed_apps[:]
        apps_to_add = []

        # Determine which apps to add
        for tool_name, tool in self.tools.items():
            if (include_all or tool.is_enabled()) and tool.app_name not in updated_apps:
                apps_to_add.append(tool.app_name)

        # Add apps in the correct order
        for app in reversed(apps_to_add):
            if add_to_beginning:
                updated_apps.insert(0, app)
                logger.debug(f"Added {app} to beginning of INSTALLED_APPS.")
            else:
                updated_apps.append(app)
                logger.debug(f"Added {app} to end of INSTALLED_APPS.")

        return updated_apps

    def configure_middleware(
        self,
        middleware: list[str],
        positions: dict[str, int | None] = None,
    ) -> list[str]:
        """
        Configure middleware with proper ordering.
        """
        return self.update_middleware(middleware, positions)

    def do_settings(
        self,
        installed_apps: list[str],
        middleware: list[str],
        positions: dict[str, int | None] = None,
        add_to_beginning: bool = True,
        include_all: bool = True
    ) -> tuple[list[str], list[str]]:
        """
        Convenience method to configure both apps and middleware.
        """
        updated_apps = self.configure_apps(
            installed_apps=installed_apps,
            add_to_beginning=add_to_beginning,
            include_all=include_all
        )

        updated_middleware = self.configure_middleware(
            middleware=middleware,
            positions=positions
        )

        return updated_apps, updated_middleware

    def get_status(self) -> dict[str, Any]:
        """
        Get status of all development tools.
        """
        import sys

        from .config import (
            AUTORELOAD_WATCH_PATHS,
            BASE_DIR,
            SILKY_PYTHON_PROFILER_RESULT_PATH,
        )

        tools_status = {}
        for tool_name, tool in self.tools.items():
            tools_status[tool_name] = tool.get_status()

        # Add Prometheus status
        tools_status['prometheus'] = {
            'installed': self._is_package_installed('django_prometheus'),
        }

        return {
            'debug_mode': is_debug_mode(),
            'testing_mode': is_testing(),
            'tools': tools_status,
            'paths': {
                'base_dir': str(BASE_DIR),
                'profiles_dir': str(SILKY_PYTHON_PROFILER_RESULT_PATH),
                'watch_paths': AUTORELOAD_WATCH_PATHS,
            },
            'python': {
                'version': sys.version,
                'executable': sys.executable,
            }
        }

    def print_status(self):
        """
        Print status of development tools to console.
        """
        status = self.get_status()

        print("📊 Environment:")
        print(f"  • Debug Mode: {'✅ Enabled' if status['debug_mode'] else '❌ Disabled'}")
        print(f"  • Testing Mode: {'✅ Yes' if status['testing_mode'] else '❌ No'}")
        print(f"  • Python: {status['python']['version'].split()[0]}")
        print("="*65)
        print("🛠️ Tools:")

        for tool_name, tool_info in status['tools'].items():
            if 'enabled' in tool_info:
                enabled = tool_info['enabled']
                installed = tool_info['installed']

                if enabled:
                    status_icon = '✅' if installed else '⚠️'
                    status_text = 'Installed' if installed else 'Not Installed'
                    print(f"  • {tool_name.title()}: {status_icon} {status_text}")
                else:
                    print(f"  • {tool_name.title()}: ❌ Disabled")
            else:
                installed = tool_info.get('installed', False)
                status_icon = '✅' if installed else '⚠️'
                print(f"  • {tool_name.title()}: {status_icon} {'Installed' if installed else 'Not Installed'}")
        print("="*65)
        print("📁 Paths:")
        print(f"  • Base Directory: {status['paths']['base_dir']}")
        print(f"  • Profiles Directory: {status['paths']['profiles_dir']}")

    def configure_all_tools(self, **kwargs) -> dict[str, Any]:
        """
        Configure all development tools.

        Returns:
            Dictionary with tool configurations
        """
        configs = {}
        for tool_name, tool in self.tools.items():
            configs[f"{tool_name}_config"] = tool.configure(**kwargs.get(tool_name, {}))

        return configs

    def run_livereload_server(self, **kwargs):
        """
        Run livereload server.
        """
        self.tools['livereload'].run_server(**kwargs)
