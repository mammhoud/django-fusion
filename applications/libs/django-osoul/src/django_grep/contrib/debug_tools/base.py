# ====================================
# 🔧 Base Classes and Utilities
# ====================================
from typing import Any

try:
    from core import logger
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

from .config import (
    BASE_DIR,
    DEBUG_TOOLBAR_APP,
    DEBUG_TOOLBAR_MIDDLEWARE,
    LIVERELOAD_APP,
    LIVERELOAD_MIDDLEWARE,
    PROMETHEUS_AFTER_MIDDLEWARE,
    PROMETHEUS_BEFORE_MIDDLEWARE,
    SILK_APP,
    SILK_MIDDLEWARE,
    SILKY_PYTHON_PROFILER_RESULT_PATH,
)


def is_debug_mode() -> bool:
    """
    Check if DEBUG mode is enabled.
    """
    try:
        return settings.DEBUG
    except (ImportError, AttributeError):
        # Fallback to environment variable
        return tracker.debug


def is_testing() -> bool:
    """
    Check if running tests.
    """
    try:
        import sys

        return "test" in sys.argv or "pytest" in sys.modules
    except:
        return False


def show_toolbar(*args, **kwargs) -> bool:
    """
    Centralized switch for Django Debug Toolbar.

    Returns True if:
    - DEBUG_TOOLBAR_ENABLED is True
    - 'debug_toolbar' package is installed
    - DEBUG is True
    - Not running tests
    """
    try:

        if not DEBUG_TOOLBAR_ENABLED:
            return False

        if not is_debug_mode():
            return False

        if is_testing():
            return False

    except NameError:
        logger.debug("django-debug-toolbar is not configured.")
        return False
    try:
        import debug_toolbar  # noqa: F401
    except ImportError:
        logger.debug("django-debug-toolbar is not installed.")
        return False

    return True


def enable_silk() -> bool:
    """
    Centralized switch for Django Silk.

    Returns True if:
    - SILK_ENABLED is True
    - 'silk' package is installed
    - DEBUG is True
    - Not running tests
    """
    try:
        if not SILK_ENABLED:
            return False

        if not is_debug_mode():
            return False

        if is_testing():
            return False
    except NameError:
        logger.debug("django-silk is not configured.")
        return False

    try:
        import silk  # noqa: F401
    except ImportError:
        logger.debug("django-silk is not installed.")
        return False

    return True


def enable_livereload() -> bool:
    """
    Centralized switch for Django Livereload.

    Returns True if:
    - LIVERELOAD_ENABLED is True
    - DEBUG is True
    - 'livereload' package is installed
    - Not running tests
    """
    try:
        if not LIVERELOAD_ENABLED:
            return False

        if not is_debug_mode():
            return False

        if is_testing():
            return False

    except NameError:
        logger.debug("django-livereload is not configured.")
        return False
    try:
        import livereload  # noqa: F401
    except ImportError:
        logger.debug("django-livereload is not installed.")
        return False

    return True


class BaseSetup:
    """
    Base class with common utilities.
    """

    @staticmethod
    def _add_middleware(
        middleware: list[str],
        middleware_class: str,
        position: int | None = None,
        skip_if_exists: bool = True,
    ) -> list[str]:
        """
        Helper to add middleware at given position.
        """
        if skip_if_exists and middleware_class in middleware:
            return middleware[:]

        updated = middleware[:]
        if position is None:
            updated.append(middleware_class)
        else:
            updated.insert(position, middleware_class)
        return updated

    @staticmethod
    def _is_package_installed(package_name: str) -> bool:
        """
        Check if a Python package is installed.

        Args:
            package_name: Name of the package

        Returns:
            True if package is installed
        """
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False

    @staticmethod
    def get_middleware_positions(middleware: list[str]) -> dict[str, int]:
        """
        Get current positions of development middleware.

        Args:
            middleware: List of middleware classes

        Returns:
            Dictionary with middleware positions
        """
        positions = {}

        # Define middleware to track
        middleware_to_track = {
            "debug_toolbar": DEBUG_TOOLBAR_MIDDLEWARE,
            "silk": SILK_MIDDLEWARE,
            "livereload": LIVERELOAD_MIDDLEWARE,
            "prometheus_before": PROMETHEUS_BEFORE_MIDDLEWARE,
            "prometheus_after": PROMETHEUS_AFTER_MIDDLEWARE,
        }

        for name, middleware_class in middleware_to_track.items():
            try:
                position = middleware.index(middleware_class)
                positions[name] = position
            except ValueError:
                positions[name] = -1  # Not found

        return positions

    @classmethod
    def create_profiles_directory(cls) -> bool:
        """
        Create the profiles directory if it doesn't exist.

        Returns:
            True if directory exists or was created successfully
        """
        try:
            profiles_dir = SILKY_PYTHON_PROFILER_RESULT_PATH
            profiles_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Profiles directory ready: {profiles_dir}")
            return True
        except Exception as e:
            logger.error(f"Failed to create profiles directory: {e}")
            return False


class DevelopmentTool:
    """
    Base class for individual development tools.
    """

    def __init__(self, name: str, app_name: str, middleware_class: str):
        self.name = name
        self.app_name = app_name
        self.middleware_class = middleware_class

    def is_installed(self) -> bool:
        """Check if tool is installed."""
        return BaseSetup._is_package_installed(self.app_name)

    def is_enabled(self) -> bool:
        """Check if tool is enabled."""
        raise NotImplementedError("Subclasses must implement is_enabled()")

    def configure(self, **kwargs) -> dict[str, Any]:
        """Configure the tool."""
        raise NotImplementedError("Subclasses must implement configure()")

    def get_status(self) -> dict[str, Any]:
        """Get tool status."""
        return {
            "name": self.name,
            "installed": self.is_installed(),
            "enabled": self.is_enabled(),
            "app_name": self.app_name,
            "middleware_class": self.middleware_class,
        }


class DebugToolbar(DevelopmentTool):
    """Debug Toolbar specific implementation."""

    def __init__(self):
        super().__init__(
            name="debug_toolbar",
            app_name=DEBUG_TOOLBAR_APP,
            middleware_class=DEBUG_TOOLBAR_MIDDLEWARE,
        )
        from .config import DEBUG_TOOLBAR_CONFIG, DEBUG_TOOLBAR_PANELS

        self.default_config = DEBUG_TOOLBAR_CONFIG
        self.panels = DEBUG_TOOLBAR_PANELS

    def is_enabled(self) -> bool:
        return show_toolbar()

    def configure(self, **kwargs) -> dict[str, Any]:
        if not self.is_enabled():
            return {}

        default_config = {
            # Toolbar display
            "DISABLE_PANELS": {
                "debug_toolbar.panels.history.HistoryPanel",
                "debug_toolbar.panels.redirects.RedirectsPanel",
            },
            "INSERT_BEFORE": "</body>",
            "RENDER_PANELS": None,
            "RESULTS_CACHE_SIZE": 25,
            "ROOT_TAG_EXTRA_ATTRS": "",
            "SHOW_COLLAPSED": False,
            "SHOW_TOOLBAR_CALLBACK": show_toolbar,
            # SQL panel
            "SQL_WARNING_THRESHOLD": 500,
            # Profiling
            "PROFILER_MAX_DEPTH": 10,
            "PROFILER_THRESHOLD_RATIO": 0.01,
            # Headers
            "HIDE_IN_STACKTRACES": (
                "socketserver",
                "threading",
                "wsgiref",
                "debug_toolbar",
                "django.db",
                "django.core.handlers",
                "django.core.servers",
                "django.utils.decorators",
                "django.utils.deprecation",
                "django.utils.functional",
            ),
        }

        # Merge with defaults and kwargs
        default_config.update(self.default_config)
        default_config.update(kwargs)

        return default_config


class Silk(DevelopmentTool):
    """Silk specific implementation."""

    def __init__(self):
        super().__init__(
            name="silk", app_name=SILK_APP, middleware_class=SILK_MIDDLEWARE
        )
        from .config import (
            SILKY_ANALYZE_QUERIES,
            SILKY_AUTHENTICATION,
            SILKY_AUTHORISATION,
            SILKY_INTERCEPT_PERCENT,
            SILKY_MAX_RECORDED_REQUESTS,
            SILKY_META,
            SILKY_PYTHON_PROFILER,
            SILKY_PYTHON_PROFILER_BINARY,
            SILKY_PYTHON_PROFILER_RESULT_PATH,
        )

        self.config_values = {
            "SILKY_META": SILKY_META,
            "SILKY_AUTHENTICATION": SILKY_AUTHENTICATION,
            "SILKY_AUTHORISATION": SILKY_AUTHORISATION,
            "SILKY_MAX_RECORDED_REQUESTS": SILKY_MAX_RECORDED_REQUESTS,
            "SILKY_INTERCEPT_PERCENT": SILKY_INTERCEPT_PERCENT,
            "SILKY_ANALYZE_QUERIES": SILKY_ANALYZE_QUERIES,
            "SILKY_PYTHON_PROFILER": SILKY_PYTHON_PROFILER,
            "SILKY_PYTHON_PROFILER_BINARY": SILKY_PYTHON_PROFILER_BINARY,
            "SILKY_PYTHON_PROFILER_RESULT_PATH": SILKY_PYTHON_PROFILER_RESULT_PATH,
        }

    def is_enabled(self) -> bool:
        return enable_silk()

    def configure(self, **kwargs) -> dict[str, Any]:
        if not self.is_enabled():
            return {}

        default_config = {
            # Enable/disable features
            "SILKY_AUTHENTICATION": self.config_values["SILKY_AUTHENTICATION"],
            "SILKY_AUTHORISATION": self.config_values["SILKY_AUTHORISATION"],
            "SILKY_PERMISSIONS": lambda user: user.is_staff,
            # Meta
            "SILKY_META": self.config_values["SILKY_META"],
            # Intercept
            "SILKY_INTERCEPT_PERCENT": self.config_values["SILKY_INTERCEPT_PERCENT"],
            "SILKY_INTERCEPT_FUNC": lambda request: True,
            # Database
            "SILKY_MAX_RECORDED_REQUESTS": self.config_values[
                "SILKY_MAX_RECORDED_REQUESTS"
            ],
            "SILKY_MAX_REQUEST_BODY_SIZE": -1,
            "SILKY_MAX_RESPONSE_BODY_SIZE": -1,
            # Profiling
            "SILKY_PYTHON_PROFILER": self.config_values["SILKY_PYTHON_PROFILER"],
            "SILKY_PYTHON_PROFILER_BINARY": self.config_values[
                "SILKY_PYTHON_PROFILER_BINARY"
            ],
            "SILKY_PYTHON_PROFILER_RESULT_PATH": str(
                self.config_values["SILKY_PYTHON_PROFILER_RESULT_PATH"]
            ),
            # Storage
            "SILKY_STORAGE_CLASS": "silk.storage.ProfilerResultStorage",
            "SILKY_JSON_ENSURE_ASCII": True,
            # UI
            "SILKY_UI_COLLAPSE_REQUESTS": False,
            "SILKY_UI_DARK_MODE": False,
            # Middleware position
            "SILKY_MIDDLEWARE_CLASS": self.middleware_class,
            # Analysis
            "SILKY_ANALYZE_QUERIES": self.config_values["SILKY_ANALYZE_QUERIES"],
            "SILKY_EXPLAIN_FLAGS": {"verbose": True},
            "SILKY_SENSITIVE_KEYS": {"password", "secret", "key", "api", "token"},
        }

        default_config.update(kwargs)
        return default_config


class Livereload(DevelopmentTool):
    """Livereload specific implementation."""

    def __init__(self):
        super().__init__(
            name="livereload",
            app_name=LIVERELOAD_APP,
            middleware_class=LIVERELOAD_MIDDLEWARE,
        )
        from .config import AUTORELOAD_WATCH_PATHS, LIVERELOAD_ENABLED

        self.enabled_default = LIVERELOAD_ENABLED
        self.watch_paths = AUTORELOAD_WATCH_PATHS

    def is_enabled(self) -> bool:
        return enable_livereload()

    def configure(self, **kwargs) -> dict[str, Any]:
        if not self.is_enabled():
            return {}

        from .detection import INTERNAL_IPS

        default_config = {
            # Server configuration
            "LIVERELOAD_HOST": "localhost",
            "LIVERELOAD_PORT": 35729,
            "LIVERELOAD_SCRIPT": "livereload.js",
            # Watch settings
            "LIVERELOAD_WATCH_PATTERNS": [
                "*.html",
                "*.css",
                "*.js",
                "*.png",
                "*.jpg",
                "*.jpeg",
                "*.gif",
                "*.svg",
            ],
            "LIVERELOAD_IGNORE_PATTERNS": [
                "*.swp",
                "*.swo",
                "*~",
                ".git/*",
                ".hg/*",
                ".svn/*",
            ],
            # LiveReload options
            "LIVERELOAD_ENABLED": self.enabled_default,
            "LIVERELOAD_NO_RELOAD": False,
            "LIVERELOAD_USE_POLLING": False,
            "LIVERELOAD_POLLING_INTERVAL": 500,
            # Watch directories
            "LIVERELOAD_WATCH_DIRS": self.watch_paths,
            # Middleware position
            "LIVERELOAD_MIDDLEWARE_CLASS": self.middleware_class,
            # Debug options
            "LIVERELOAD_DEBUG": False,
            "LIVERELOAD_VERBOSE": False,
            # Security
            "LIVERELOAD_ALLOWED_HOSTS": INTERNAL_IPS,
            "LIVERELOAD_DISABLE_IN_PRODUCTION": True,
        }

        default_config.update(kwargs)
        return default_config

    def run_server(
        self,
        host: str = "localhost",
        port: int = 35729,
        watch_paths: list[str] | None = None,
        extra_extensions: list[str] | None = None,
    ) -> None:
        """
        Start the livereload server.
        """
        if not self.is_enabled():
            logger.warning("Livereload is not enabled. Server not started.")
            return

        try:
            from livereload import Server
        except ImportError:
            logger.error("livereload package not installed.")
            return

        # Default watch paths
        if watch_paths is None:
            watch_paths = self.watch_paths

        # Default extensions to watch
        if extra_extensions is None:
            extra_extensions = ["html", "css", "js", "py"]

        server = Server()

        # Add watch paths
        for path in watch_paths:
            full_path = BASE_DIR / path
            if full_path.exists():
                server.watch(str(full_path))
                logger.info(f"Livereload watching: {full_path}")
            else:
                logger.warning(f"Watch path does not exist: {full_path}")

        # Watch specific file extensions
        for ext in extra_extensions:
            server.watch(f"**/*.{ext}")

        logger.info(f"Starting livereload server on {host}:{port}")
        try:
            server.serve(host=host, port=port, debug=True)
        except KeyboardInterrupt:
            logger.info("Livereload server stopped by user")
        except Exception as e:
            logger.error(f"Failed to start livereload server: {e}")
