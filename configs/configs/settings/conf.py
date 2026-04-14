"""
Configuration management for Alliance/Structa.
Reads from .env and YAML files via Dynaconf.
Supports: local, docker runtimes.
Environments: development, staging, production, testing.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from django_rseal.contrib.enums import Environment, LogLevel, Module, Runtime
from dynaconf import Dynaconf
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).parent / "ENV"


class MainSettings(BaseSettings):
    """Unified settings — reads env vars + Dynaconf YAML files."""

    # ---- Core ----
    SERVER_ENV: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Server environment (development, staging, production, testing)",
    )
    RUNNING_ENV: Runtime = Field(
        default=Runtime.LOCAL,
        description="Runtime environment (local, docker)",
    )
    MODULE: Module = Field(default=Module.LMS, description="Application module")
    DEBUG: bool = Field(default=True, description="Debug mode")
    DJANGO_SECRET_KEY: str = Field(
        default="dev-secret-key-change-me", description="Django secret key"
    )
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=5080, description="Server port")

    # ---- Docker ----
    MAIN_CONTAINER: str = Field(default="structa-main", description="Main container name")
    MAIN_BRANCH: str = Field(default="main", description="Main branch name")

    # ---- Dynaconf (internal) ----
    dynaconf_settings: Optional[Dynaconf] = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
        env_prefix="",
    )

    def __init__(self, **kwargs):
        self._detect_runtime(kwargs)
        self._load_secret_key(kwargs)
        super().__init__(**kwargs)
        self._init_dynaconf()

    def _load_secret_key(self, kwargs: Dict[str, Any]) -> None:
        """Read DJANGO_SECRET_KEY from secret.key.txt if it exists."""
        key_file = Path(__file__).parent.parent.parent / "secret.key.txt"
        if key_file.exists():
            try:
                first_line = key_file.read_text(encoding="utf-8").splitlines()[0].strip()
                if first_line and not first_line.startswith("#"):
                    kwargs["DJANGO_SECRET_KEY"] = first_line
                    os.environ.setdefault("DJANGO_SECRET_KEY", first_line)
            except Exception:
                pass

    def _detect_runtime(self, kwargs: Dict[str, Any]) -> None:
        """Detect docker vs local runtime from env vars and filesystem."""
        runtime_from_env = os.environ.get("RUNNING_ENV", "").lower()
        if runtime_from_env:
            kwargs.setdefault("RUNNING_ENV", runtime_from_env)
            return

        is_docker = any([
            os.path.exists("/.dockerenv"),
            os.path.exists("/run/.containerenv"),
            "DOCKER" in os.environ,
            "COMPOSE" in os.environ,
            "CONTAINER" in os.environ,
        ])
        kwargs.setdefault("RUNNING_ENV", Runtime.DOCKER if is_docker else Runtime.LOCAL)

    def _init_dynaconf(self) -> None:
        """Load YAML config files via Dynaconf."""
        settings_files = [
            CONFIG_DIR / "_core.yml",
            CONFIG_DIR / "database.yml",
            CONFIG_DIR / "security.yml",
            CONFIG_DIR / "storage.yml",
            CONFIG_DIR / "email.yml",
            CONFIG_DIR / "logging.yml",
            CONFIG_DIR / ".secrets.yml",
        ]
        existing = [str(f) for f in settings_files if f.exists()]
        self.dynaconf_settings = Dynaconf(
            envvar_prefix="DJANGO",
            settings_files=existing,
            environments=True,
            default_env="default",
            env=self.SERVER_ENV.value,
            merge_enabled=True,
            load_dotenv=True,
            vault_enabled=False,
        )

    # ---- Validators ----

    @validator("DEBUG", pre=True)
    def validate_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on", "t", "y")
        return v

    @validator("SERVER_ENV", pre=True)
    def validate_server_env(cls, v):
        if isinstance(v, str):
            mapping = {
                "dev": Environment.DEVELOPMENT,
                "development": Environment.DEVELOPMENT,
                "demo": Environment.DEVELOPMENT,  # demo → development
                "prod": Environment.PRODUCTION,
                "production": Environment.PRODUCTION,
                "stage": Environment.STAGING,
                "staging": Environment.STAGING,
                "test": Environment.TESTING,
                "testing": Environment.TESTING,
            }
            return mapping.get(v.lower(), Environment.DEVELOPMENT)
        return v

    @validator("RUNNING_ENV", pre=True)
    def validate_runtime_env(cls, v):
        if isinstance(v, str):
            mapping = {
                "local": Runtime.LOCAL,
                "docker": Runtime.DOCKER,
                "container": Runtime.DOCKER,
            }
            return mapping.get(v.lower(), Runtime.LOCAL)
        return v

    @validator("MODULE", pre=True)
    def validate_module(cls, v):
        if isinstance(v, str):
            mapping = {
                "LMS": Module.LMS,
                "LEARNING_MANAGEMENT": Module.LMS,
                "CMS": Module.CMS,
                "CONTENT_MANAGEMENT": Module.CMS,
                "ECOMMERCE": Module.ECOMMERCE,
                "E_COMMERCE": Module.ECOMMERCE,
                "SHOP": Module.ECOMMERCE,
                "CRM": Module.CRM,
                "CUSTOMER_RELATIONSHIP": Module.CRM,
            }
            return mapping.get(v.upper(), Module.LMS)
        return v

    # ---- Dynamic attribute access ----

    def __getattr__(self, name: str) -> Any:
        if self.dynaconf_settings and hasattr(self.dynaconf_settings, name):
            return getattr(self.dynaconf_settings, name)
        raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{name}'")

    # ---- get() with casting ----

    def get(self, key: str, default: Any = None, cast: Optional[type] = None) -> Any:
        if hasattr(self, key) and key in self.model_fields:
            value = getattr(self, key)
            if value is not None and value != "":
                return value

        if self.dynaconf_settings:
            value = self.dynaconf_settings.get(key, default)
        else:
            value = default

        if cast is not None and value is not None:
            try:
                if cast == bool:
                    value = str(value).lower() in ("true", "1", "yes", "on")
                elif cast == int:
                    value = int(value)
                elif cast == list:
                    value = [i.strip() for i in value.split(",")] if isinstance(value, str) else list(value)
                else:
                    value = cast(value)
            except (ValueError, TypeError):
                value = default

        return value

    # ---- Properties ----

    @property
    def is_production(self) -> bool:
        return self.SERVER_ENV == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.SERVER_ENV == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        return self.SERVER_ENV == Environment.STAGING

    @property
    def is_testing(self) -> bool:
        return self.SERVER_ENV == Environment.TESTING

    @property
    def is_local(self) -> bool:
        return self.RUNNING_ENV == Runtime.LOCAL

    @property
    def is_docker(self) -> bool:
        return self.RUNNING_ENV == Runtime.DOCKER

    @property
    def is_containerized(self) -> bool:
        return self.RUNNING_ENV == Runtime.DOCKER

    @property
    def is_debug(self) -> bool:
        return self.DEBUG

    @property
    def docker_configured(self) -> bool:
        return bool(self.MAIN_CONTAINER)

    @property
    def dynaconf(self) -> Optional[Dynaconf]:
        return self.dynaconf_settings

    # ---- Summary / validation ----

    @property
    def summary(self) -> Dict[str, Any]:
        runtime_emoji = {Runtime.LOCAL: "💻", Runtime.DOCKER: "🐳"}.get(self.RUNNING_ENV, "❓")
        env_emoji = {
            Environment.DEVELOPMENT: "🔧",
            Environment.STAGING: "🔄",
            Environment.PRODUCTION: "🚀",
            Environment.TESTING: "🧪",
        }.get(self.SERVER_ENV, "❓")
        return {
            "environment": f"{env_emoji} {self.SERVER_ENV.value}",
            "runtime": f"{runtime_emoji} {self.RUNNING_ENV.value}",
            "module": f"📦 {self.MODULE.value}",
            "debug": "⚠️ Enabled" if self.DEBUG else "✅ Disabled",
            "host": self.HOST,
            "port": self.PORT,
            "is_production": self.is_production,
            "is_containerized": self.is_containerized,
        }

    def print_summary(self) -> None:
        border = "=" * 60
        print(f"\n{border}")
        print("🌍 ENVIRONMENT SUMMARY".center(60))
        print(border)
        for label, value in [
            ("Environment", self.summary["environment"]),
            ("Runtime", self.summary["runtime"]),
            ("Module", self.summary["module"]),
            ("Debug Mode", self.summary["debug"]),
            ("Production", "✅ Yes" if self.summary["is_production"] else "❌ No"),
            ("Containerized", "✅ Yes" if self.summary["is_containerized"] else "❌ No"),
            ("Host", self.summary["host"]),
            ("Port", str(self.summary["port"])),
        ]:
            print(f"│ {label:<20} : {value:<35} │")
        print(f"{border}\n")

    def validate_environment(self) -> List[str]:
        warnings = []
        if self.is_production and self.DEBUG:
            warnings.append("⚠️ DEBUG is enabled in production!")
        if self.is_production and self.DJANGO_SECRET_KEY == "dev-secret-key-change-me":
            warnings.append("🚨 Using default DJANGO_SECRET_KEY in production!")
        return warnings

    def show_config(self) -> Dict[str, Any]:
        return {
            "server_env": self.SERVER_ENV.value,
            "running_env": self.RUNNING_ENV.value,
            "module": self.MODULE.value,
            "debug": self.DEBUG,
            "host": self.HOST,
            "port": self.PORT,
            "main_container": self.MAIN_CONTAINER,
            "main_branch": self.MAIN_BRANCH,
        }

    def to_dict(self, include_secrets: bool = False) -> Dict[str, Any]:
        data = {f: getattr(self, f) for f in self.model_fields}
        if self.dynaconf_settings:
            for key in self.dynaconf_settings.keys():
                if key not in data:
                    data[key] = self.dynaconf_settings.get(key)
        if not include_secrets:
            for field in ("DJANGO_SECRET_KEY", "SECRET_KEY"):
                if field in data:
                    data[field] = "***"
        return data

    def get_env_file_path(self) -> Path:
        return Path(__file__).parent.parent.parent / ".env"

    def reload(self) -> None:
        self.__init__()


# ---- Singleton ----
settings = MainSettings()


def init_config(env: Optional[str] = None) -> MainSettings:
    """Re-initialise settings, optionally forcing a SERVER_ENV."""
    global settings
    if env:
        os.environ["SERVER_ENV"] = env
    settings = MainSettings()
    return settings


__all__ = [
    "MainSettings",
    "settings",
    "init_config",
    "Environment",
    "LogLevel",
    "Module",
    "Runtime",
]
