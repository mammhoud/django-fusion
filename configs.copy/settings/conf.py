"""
🌐 Enhanced UnifiedSettings with Dynamic Attribute Support
========================================================
Complete configuration management with environment tracking and validation.
Automatically detects Docker runtime environment and supports accessing Dynaconf values directly as attributes.
"""

import ast
import os
from collections.abc import Mapping, Sequence
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dynaconf import Dynaconf
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ==================== ENUMS ====================


class Environment(str, Enum):
    """Server environment."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging level."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Module(str, Enum):
    """Application module."""

    CMS = "cms"


class Runtime(str, Enum):
    """Runtime environment."""

    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"


CONFIG_DIR = Path(__file__).parent / "ENV"
_MISSING = object()


# ==================== MAIN SETTINGS CLASS ====================


class MainSettings(BaseSettings):
    """
    Complete Unified Configuration with Dynamic Attribute Support
    =============================================================
    Combines environment, docker, and security settings.
    Uses Dynaconf for hierarchical configuration with YAML files.
    """

    # ==================== CORE ENVIRONMENT ====================
    SERVER_ENV: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Server environment (development, demo, staging, production)",
    )
    RUNNING_ENV: Runtime = Field(
        default=Runtime.LOCAL, description="Runtime environment (local, docker, kubernetes, cloud)"
    )
    MODULE: Module = Field(default=Module.CMS, description="Application module")
    DEBUG: bool = Field(default=True, description="Debug mode")
    DJANGO_SECRET_KEY: str = Field(
        default="dev-secret-key-change-me", description="Django secret key"
    )
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=5080, description="Server port")
    DOMAIN_NAME: str = Field(default="localhost", description="Primary domain name")
    SSL_ENABLED: bool = Field(default=False, description="Enable SSL/HTTPS")

    # ==================== DYNACONF SETTINGS ====================
    dynaconf_settings: Optional[Dynaconf] = None

    # Pydantic Configuration
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        env_prefix="",
        # validate_assignment=True,
    )

    def __init__(self, **kwargs):
        """Initialize with Docker detection and Dynaconf loading."""
        # Convert string booleans from environment BEFORE Pydantic validation
        self._convert_env_booleans()

        # Detect runtime environment
        self._detect_runtime_environment(kwargs)
        super().__init__(**kwargs)

        # Initialize Dynaconf
        self._init_dynaconf()

    def _convert_env_booleans(self) -> None:
        """Convert string boolean environment variables to actual booleans."""
        bool_fields = ["DEBUG", "SSL_ENABLED"]
        for field in bool_fields:
            if field in os.environ:
                val = os.environ[field].lower()
                if val in ("true", "1", "yes", "on", "t", "y"):
                    os.environ[field] = "true"
                elif val in ("false", "0", "no", "off", "f", "n", "release", "production"):
                    os.environ[field] = "false"

    def _detect_runtime_environment(self, kwargs: Dict[str, Any]) -> None:
        """Detect if running in Docker/Kubernetes container."""
        runtime_from_env = os.environ.get("RUNNING_ENV", "").lower()

        docker_env_indicators = [
            os.path.exists("/.dockerenv"),
            os.path.exists("/run/.containerenv"),
            "DOCKER" in os.environ,
            "COMPOSE" in os.environ,
            "KUBERNETES_SERVICE_HOST" in os.environ,
            "KUBERNETES_PORT" in os.environ,
            "CONTAINER" in os.environ,
            "PATH" in os.environ and "docker" in os.environ.get("PATH", "").lower(),
        ]

        is_containerized = any(docker_env_indicators)

        if runtime_from_env:
            kwargs.setdefault("RUNNING_ENV", runtime_from_env)
        elif is_containerized:
            if "KUBERNETES" in os.environ or "KUBERNETES_SERVICE_HOST" in os.environ:
                kwargs["RUNNING_ENV"] = Runtime.KUBERNETES
            elif "DOCKER" in os.environ or os.path.exists("/.dockerenv"):
                kwargs["RUNNING_ENV"] = Runtime.DOCKER
            else:
                kwargs["RUNNING_ENV"] = Runtime.DOCKER
        else:
            kwargs.setdefault("RUNNING_ENV", Runtime.LOCAL)

    def _init_dynaconf(self) -> None:
        """Initialize Dynaconf configuration."""
        # Define configuration files
        settings_files = [
            CONFIG_DIR / "_core.yml",
            CONFIG_DIR / "database.yml",
            CONFIG_DIR / "security.yml",
            CONFIG_DIR / "storage.yml",
            CONFIG_DIR / "email.yml",
            CONFIG_DIR / "logging.yml",
            CONFIG_DIR / "celery.yml",
            CONFIG_DIR / "rq.yml",
            CONFIG_DIR / f"_{self.SERVER_ENV.value}.yml",
            CONFIG_DIR / ".secrets.yml",
        ]

        existing_files = [str(f) for f in settings_files if f.exists()]

        # Initialize Dynaconf
        self.dynaconf_settings = Dynaconf(
            envvar_prefix="DJANGO",
            settings_files=existing_files,
            environments=True,
            default_env="default",
            env=self.SERVER_ENV.value,
            merge_enabled=True,
            load_dotenv=True,
            # env_switcher=self.SERVER_ENV.value,
            vault_enabled=False,
        )

        # Update instance attributes from Dynaconf
        # self._update_from_dynaconf()

    def _update_from_dynaconf(self) -> None:
        """Update settings from Dynaconf configuration."""
        if not self.dynaconf_settings:
            return

        # Update all fields from Dynaconf
        for field_name in self.model_fields:
            value = self.dynaconf_settings.get(field_name)
            if value is not None:
                setattr(self, field_name, value)

    # ==================== VALIDATORS ====================

    @validator("DEBUG", pre=True)
    def validate_bool(cls, v):
        """Convert string boolean values."""
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower in ("true", "1", "yes", "on", "t", "y"):
                return True
            elif v_lower in ("false", "0", "no", "off", "f", "n"):
                return False
        return v

    @validator("SERVER_ENV", pre=True)
    def validate_server_env(cls, v):
        """Validate server environment."""
        if isinstance(v, str):
            v_lower = v.lower()
            mapping = {
                "dev": Environment.DEVELOPMENT,
                "development": Environment.DEVELOPMENT,
                "prod": Environment.PRODUCTION,
                "production": Environment.PRODUCTION,
            }
            return mapping.get(v_lower, Environment.DEVELOPMENT)
        return v

    @validator("RUNNING_ENV", pre=True)
    def validate_runtime_env(cls, v):
        """Validate runtime environment."""
        if isinstance(v, str):
            v_lower = v.lower()
            mapping = {
                "local": Runtime.LOCAL,
                "docker": Runtime.DOCKER,
                "container": Runtime.DOCKER,
                "k8s": Runtime.KUBERNETES,
                "kubernetes": Runtime.KUBERNETES,
                "cloud": Runtime.CLOUD,
                "aws": Runtime.CLOUD,
                "gcp": Runtime.CLOUD,
                "azure": Runtime.CLOUD,
            }
            return mapping.get(v_lower, Runtime.LOCAL)
        return v

    @validator("MODULE", pre=True)
    def validate_module(cls, v):
        """Validate module."""
        if isinstance(v, str):
            v_upper = v.upper()
            mapping = {
                "CMS": Module.CMS,
                "CONTENT_MANAGEMENT": Module.CMS,
            }
            return mapping.get(v_upper, Module.CMS)
        return v

    @validator("PORT", pre=True)
    def validate_port(cls, v):
        """Validate port numbers."""
        if isinstance(v, str):
            if v.isdigit():
                port = int(v)
                if 1 <= port <= 65535:
                    return port
                else:
                    raise ValueError(f"Port {port} is out of valid range (1-65535)")
        return v

    # ==================== DYNAMIC ATTRIBUTE METHODS ====================

    def __getattr__(self, name: str) -> Any:
        """
        Get dynamic attribute from Dynaconf.
        This allows settings.SOME_SETTING to work even if not defined in class.
        """
        # Check Dynaconf
        if self.dynaconf_settings and hasattr(self.dynaconf_settings, name):
            return getattr(self.dynaconf_settings, name)

        # Check if it's a nested setting with dot notation
        if self.dynaconf_settings and "." in name:
            parts = name.split(".")
            current = self.dynaconf_settings
            for part in parts:
                if hasattr(current, part):
                    current = getattr(current, part)
                else:
                    raise AttributeError(
                        f"'{self.__class__.__name__}' object has no attribute '{name}'"
                    )
            return current

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    # ==================== GET METHODS ====================

    def section(self, name: str, default: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Return a YAML/Dynaconf configuration section as a plain dict."""
        value = self.get(name, default or {})
        if isinstance(value, Mapping):
            return dict(value)
        return default or {}

    def get(
        self,
        key: str,
        default: Any = None,
        cast: Optional[type] = None,
        block: Optional[str] = None,
        env: Optional[str | Sequence[str]] = None,
    ) -> Any:
        """
        Get configuration from env vars, YAML blocks, top-level YAML, or attributes.

        Resolution order:
        1. Explicit env names passed with ``env=``.
        2. The ``DJANGO_<key>`` env var used by Dynaconf.
        3. ``block.key`` from YAML/Dynaconf if ``block`` is provided.
        4. Top-level Dynaconf/YAML key.
        5. MainSettings attribute.
        6. ``default``.
        """
        value = self._get_env_value(env)
        if value is _MISSING:
            value = self._get_env_value(f"DJANGO_{key}")
        if value is _MISSING and block:
            value = self._get_from_mapping(self.section(block), key, _MISSING)
        if value is _MISSING:
            value = self._get_dynaconf_value(key, _MISSING)
        if value is _MISSING and key in self.model_fields:
            value = getattr(self, key, _MISSING)
        if value is _MISSING:
            value = default
        return self._cast_value(value, cast, default)

    def get_bool(
        self,
        key: str,
        default: bool = False,
        *,
        block: Optional[str] = None,
        env: Optional[str | Sequence[str]] = None,
    ) -> bool:
        """Get a setting as a boolean."""
        return self.get(key, default, cast=bool, block=block, env=env)

    def get_int(
        self,
        key: str,
        default: int = 0,
        *,
        block: Optional[str] = None,
        env: Optional[str | Sequence[str]] = None,
    ) -> int:
        """Get a setting as an integer."""
        return self.get(key, default, cast=int, block=block, env=env)

    def get_list(
        self,
        key: str,
        default: Optional[Sequence[Any]] = None,
        *,
        block: Optional[str] = None,
        env: Optional[str | Sequence[str]] = None,
    ) -> list[Any]:
        """Get a setting as a list."""
        return self.get(key, list(default or []), cast=list, block=block, env=env)

    def _cast_value(self, value: Any, cast: Optional[type], default: Any = None) -> Any:
        """Cast a resolved setting to the requested Python type."""
        if cast is None or value is None:
            return value
        try:
            if cast is bool:
                return self._cast_bool(value)
            if cast is int:
                return int(value)
            if cast is list:
                return self._cast_list(value)
            if cast is tuple:
                return tuple(self._cast_list(value))
            if cast is str:
                return str(value)
            return cast(value)
        except (TypeError, ValueError):
            return default

    def _cast_bool(self, value: Any) -> bool:
        """Cast common YAML/env boolean values to bool."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value_lower = value.strip().lower()
            if value_lower in ("true", "1", "yes", "on", "t", "y"):
                return True
            if value_lower in ("false", "0", "no", "off", "f", "n"):
                return False
        return bool(value)

    def _cast_list(self, value: Any) -> List[Any]:
        """Cast YAML lists, tuples, sets, and comma-separated env strings to list."""
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if isinstance(value, (list, tuple, set)):
            return [item for item in value if str(item).strip()]
        return [value]

    def _get_env_value(self, names: Optional[str | Sequence[str]]) -> Any:
        """Return the first non-empty environment variable from ``names``."""
        if names is None:
            return _MISSING
        if isinstance(names, str):
            names = [names]
        for name in names:
            value = os.environ.get(name)
            if value is not None and value.strip() != "":
                return value
        return _MISSING

    def _get_dynaconf_value(self, key: str, default: Any = None) -> Any:
        """Read a top-level or dotted key from the Dynaconf settings object."""
        if not self.dynaconf_settings:
            return default
        if "." in key:
            current = self.dynaconf_settings
            for part in key.split("."):
                current = self._get_from_mapping(current, part, _MISSING)
                if current is _MISSING:
                    return default
            return current
        if hasattr(self.dynaconf_settings, key):
            return getattr(self.dynaconf_settings, key)
        return self.dynaconf_settings.get(key, default)

    @staticmethod
    def _get_from_mapping(source: Any, key: str, default: Any = None) -> Any:
        """Read a key from dict-like objects, Dynaconf boxes, or plain objects."""
        if isinstance(source, Mapping):
            return source.get(key, default)
        if hasattr(source, key):
            return getattr(source, key)
        if hasattr(source, "get"):
            return source.get(key, default)
        return default

    # ==================== PROPERTIES ====================

    # Environment Properties
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.SERVER_ENV == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.SERVER_ENV == Environment.DEVELOPMENT

    @property
    def is_local(self) -> bool:
        """Check if running locally."""
        return self.RUNNING_ENV == Runtime.LOCAL

    @property
    def is_docker(self) -> bool:
        """Check if running in Docker."""
        return self.RUNNING_ENV == Runtime.DOCKER

    @property
    def is_kubernetes(self) -> bool:
        """Check if running in Kubernetes."""
        return self.RUNNING_ENV == Runtime.KUBERNETES

    @property
    def is_cloud(self) -> bool:
        """Check if running in cloud."""
        return self.RUNNING_ENV == Runtime.CLOUD

    @property
    def is_containerized(self) -> bool:
        """Check if running in container."""
        return self.RUNNING_ENV in [Runtime.DOCKER, Runtime.KUBERNETES, Runtime.CLOUD]

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.DEBUG

    @property
    def dynaconf(self) -> Optional[Dynaconf]:
        """Get Dynaconf settings instance."""
        return self.dynaconf_settings

    # ==================== SUMMARY AND REPORTING ====================

    @property
    def summary(self) -> Dict[str, Any]:
        """Get environment summary."""
        runtime_emoji = {
            Runtime.LOCAL: "💻",
            Runtime.DOCKER: "🐳",
            Runtime.KUBERNETES: "☸️",
            Runtime.CLOUD: "☁️",
        }.get(self.RUNNING_ENV, "❓")

        env_emoji = {
            Environment.DEVELOPMENT: "🔧",
            Environment.PRODUCTION: "🚀",
        }.get(self.SERVER_ENV, "❓")

        return {
            "environment": f"{env_emoji} {self.SERVER_ENV.value}",
            "runtime": f"{runtime_emoji} {self.RUNNING_ENV.value}",
            "module": f"📦 {self.MODULE.value}",
            "debug": (
                ("✅ Disabled" if not self.DEBUG else "⚠️ Enabled")
                if self.is_production
                else ("✅ Enabled" if self.DEBUG else "⚠️ Disabled")
            ),
            "host": self.HOST,
            "port": self.PORT,
            "is_production": self.is_production,
            "is_containerized": self.is_containerized,
        }

    def print_summary(self) -> None:
        """Print formatted environment summary."""
        border = "=" * 60

        print(f"\n{border}")
        print("🌍 ENVIRONMENT SUMMARY".center(60))
        print(border)

        # Environment info
        rows = [
            ("Environment", self.summary["environment"]),
            ("Runtime", self.summary["runtime"]),
            ("Module", self.summary["module"]),
            ("Debug Mode", self.summary["debug"]),
            ("Production", "✅ Yes" if self.summary["is_production"] else "❌ No"),
            ("Containerized", "✅ Yes" if self.summary["is_containerized"] else "❌ No"),
        ]

        for label, value in rows:
            print(f"│ {label:<20} : {value:<35} │")

        print(border)
        print("⚙️ CONFIGURATION STATUS".center(60))
        print(border)

        # Configuration status
        config_rows = [
            ("Server Host", self.summary["host"]),
            ("Server Port", str(self.summary["port"])),
        ]

        for label, value in config_rows:
            print(f"│ {label:<20} : {value:<35} │")

        print(f"{border}\n")

    def validate_environment(self) -> List[str]:
        """Validate environment configuration."""
        warnings = []

        # Environment-specific warnings
        if self.is_production and self.DEBUG:
            warnings.append("⚠️ DEBUG mode is enabled in production!")

        if self.is_production and self.DJANGO_SECRET_KEY == "dev-secret-key-change-me":
            warnings.append("🚨 Using default DJANGO_SECRET_KEY in production!")

        # Server warnings
        if self.HOST == "0.0.0.0" and self.PORT == 5080:
            warnings.append("🌐 Using default HOST (0.0.0.0) and PORT (5080)")

        # Check for missing required variables
        required_vars = [
            ("DJANGO_SECRET_KEY", "dev-secret-key-change-me"),
            ("HOST", "0.0.0.0"),
            ("PORT", "5080"),
        ]

        for var, default_value in required_vars:
            value = getattr(self, var, "")
            if str(value) == str(default_value):
                warnings.append(f"⚙️ Using default value for {var}")

        return warnings

    def show_config(self) -> Dict[str, Dict[str, Any]]:
        """Show current configuration."""
        return {
            "core": {
                "server_env": self.SERVER_ENV.value,
                "running_env": self.RUNNING_ENV.value,
                "module": self.MODULE.value,
                "debug": self.DEBUG,
                "host": self.HOST,
                "port": self.PORT,
                "is_containerized": self.is_containerized,
            },
        }

    def print_detailed_report(self) -> None:
        """Print detailed environment report."""
        self.print_summary()

        warnings = self.validate_environment()
        if warnings:
            print("⚠️  WARNINGS & ISSUES:")
            for i, warning in enumerate(warnings, 1):
                print(f"  {i}. {warning}")

        # Show recommendations
        print("\n💡 RECOMMENDATIONS:")
        if self.is_production:
            print("  - Set DEBUG=False in production")
            print("  - Use a strong DJANGO_SECRET_KEY")
            print("  - Ensure all sensitive data is properly secured")

        if self.is_containerized and self.DEBUG:
            print("  - Consider setting DEBUG=False in containerized environments")

        # Print detected environment
        print("\n🔍 DETECTED ENVIRONMENT:")
        print(f"  - Running in: {self.RUNNING_ENV.value}")
        print(f"  - Server environment: {self.SERVER_ENV.value}")
        print(f"  - Containerized: {'Yes' if self.is_containerized else 'No'}")

    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        data = {}

        # Add defined fields
        for field in self.model_fields:
            data[field] = getattr(self, field)

        # Add Dynaconf settings
        if self.dynaconf_settings:
            for key in self.dynaconf_settings.keys():
                if key not in data:
                    data[key] = self.dynaconf_settings.get(key)

        # Mask secrets if not including them
        if not include_secrets:
            secret_fields = ["DJANGO_SECRET_KEY", "SECRET_KEY"]
            for field in secret_fields:
                if field in data and data[field]:
                    data[field] = "***SECRET***"

        return data

    # ==================== HELPER METHODS ====================

    def get_env_file_path(self) -> Path:
        """Get the path to the .env file."""
        return Path(__file__).parent.parent.parent / ".env"

    def reload(self) -> None:
        """Reload settings from environment."""
        self.__init__()


# ==================== GLOBAL INSTANCES =====================

# Singleton instance
settings = MainSettings()

# ==================== UTILITY FUNCTIONS ====================


def init_config(env: Optional[str] = None) -> MainSettings:
    """
    Initialize configuration with optional environment.

    Args:
        env: Environment name (development, staging, production)

    Returns:
        MainSettings instance
    """
    global settings

    if env:
        os.environ["SERVER_ENV"] = env

    # Reinitialize settings
    settings = MainSettings()

    return settings


# ==================== EXPORTS ====================

__all__ = [
    # Main classes
    "MainSettings",
    # Instances
    "settings",
    # Utility functions
    # "get_django_settings",
    "init_config",
    # Enums
    "Environment",
    "LogLevel",
    "Module",
    "Runtime",
]
