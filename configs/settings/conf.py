"""
🌐 Enhanced UnifiedSettings with Dynamic Attribute Support
========================================================
Complete configuration management with environment tracking and validation.
Automatically detects Docker runtime environment and supports accessing Dynaconf values directly as attributes.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from django_rseal.contrib.enums import Direction, Environment, LogLevel, Module, Runtime, Workflow
from dynaconf import Dynaconf
from pydantic import Field, validator
from pydantic.dataclasses import dataclass
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).parent / "ENV"

# ==================== DATA CLASSES ====================


@dataclass
class SyncConfigData:
    """Sync configuration data class."""

    environment: Environment = Environment.DEVELOPMENT
    direction: Direction = Direction.SYNC
    workflow: Workflow = Workflow.STANDARD
    container: str = ""
    branch: str = ""
    restart_container: bool = False
    run_tests: bool = False
    auto_commit: bool = True


# ==================== MAIN SETTINGS CLASS ====================


class MainSettings(BaseSettings):
    """
    Complete Unified Configuration with Dynamic Attribute Support
    =============================================================
    Combines environment, git, docker, sync, security, and dynamic settings.
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
    MODULE: Module = Field(default=Module.LMS, description="Application module")
    DEBUG: bool = Field(default=True, description="Debug mode")
    DJANGO_SECRET_KEY: str = Field(
        default="dev-secret-key-change-me", description="Django secret key"
    )
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=5070, description="Server port")

    # ==================== GIT CONFIGURATION ====================
    GIT_REPO: str = Field(default="", description="Git repository name")
    GIT_USERNAME: str = Field(default="", description="Git username")
    GIT_EMAIL: str = Field(default="", description="Git email")
    GIT_TOKEN: Optional[str] = Field(default=None, description="GitHub token")

    # ==================== VARIANT REPOSITORIES ====================
    CORE_REPO: str = Field(default="", description="Repository for Core variant")
    BLOG_REPO: str = Field(default="", description="Repository for Blog variant")
    LMS_REPO: str = Field(default="", description="Repository for LMS variant")
    ALL_REPO: str = Field(default="", description="Repository for Full variant")

    # ==================== DOCKER CONFIGURATION ====================
    DEMO_CONTAINER: str = Field(default="django-demo", description="Demo container name")
    MAIN_CONTAINER: str = Field(default="django-main", description="Main container name")
    DEMO_BRANCH: str = Field(default="dev", description="Demo branch name")
    MAIN_BRANCH: str = Field(default="main", description="Main branch name")

    # ==================== SYNC CONFIGURATION ====================
    SYNC_ENVIRONMENT: Environment = Field(
        default=Environment.DEVELOPMENT, description="Sync environment"
    )
    SYNC_DIRECTION: Direction = Field(default=Direction.SYNC, description="Sync direction")
    SYNC_WORKFLOW: Workflow = Field(default=Workflow.STANDARD, description="Sync workflow")
    SYNC_CONTAINER: str = Field(default="", description="Sync container name")
    SYNC_BRANCH: str = Field(default="", description="Sync branch")
    SYNC_RESTART_CONTAINER: bool = Field(default=False, description="Restart container after sync")
    SYNC_RUN_TESTS: bool = Field(default=False, description="Run tests after sync")
    SYNC_AUTO_COMMIT: bool = Field(default=True, description="Auto commit after sync")

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
        # Detect runtime environment
        self._detect_runtime_environment(kwargs)
        # Load secret key from file if available
        self._load_secret_key(kwargs)
        super().__init__(**kwargs)

        # Initialize Dynaconf
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

    @validator("DEBUG", "SYNC_RESTART_CONTAINER", "SYNC_RUN_TESTS", "SYNC_AUTO_COMMIT", pre=True)
    def validate_bool(cls, v):
        """Convert string boolean values."""
        if isinstance(v, str):
            v_lower = v.lower()
            if v_lower in ("true", "1", "yes", "on", "t", "y"):
                return True
            elif v_lower in ("false", "0", "no", "off", "f", "n"):
                return False
        return v

    @validator("SERVER_ENV", "SYNC_ENVIRONMENT", pre=True)
    def validate_server_env(cls, v):
        """Validate server environment."""
        if isinstance(v, str):
            v_lower = v.lower()
            mapping = {
                "dev": Environment.DEVELOPMENT,
                "development": Environment.DEVELOPMENT,
                "demo": Environment.DEMO,
                "prod": Environment.PRODUCTION,
                "production": Environment.PRODUCTION,
                "stage": Environment.STAGING,
                "staging": Environment.STAGING,
                "test": Environment.TESTING,
                "testing": Environment.TESTING,
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
            return mapping.get(v_upper, Module.LMS)
        return v

    @validator("GIT_TOKEN", pre=True)
    def validate_git_token(cls, v):
        """Validate git token."""
        if v and v.startswith("ghp_"):
            if len(v) < 40:
                raise ValueError("GitHub token appears to be invalid (too short)")
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

    @validator("SYNC_DIRECTION", pre=True)
    def validate_sync_direction(cls, v):
        """Validate sync direction."""
        if isinstance(v, str):
            v_lower = v.lower()
            try:
                return Direction(v_lower)
            except ValueError:
                return Direction.SYNC
        return v

    @validator("SYNC_WORKFLOW", pre=True)
    def validate_sync_workflow(cls, v):
        """Validate sync workflow."""
        if isinstance(v, str):
            v_lower = v.lower()
            try:
                return Workflow(v_lower)
            except ValueError:
                return Workflow.STANDARD
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

    def get(self, key: str, default: Any = None, cast: Optional[type] = None) -> Any:
        """
        Get configuration value.
        """
        # Check defined attributes first (if they have a non-default value)
        if hasattr(self, key) and key in self.model_fields:
            value = getattr(self, key)
            if value:
                # If the attribute has a non-empty/truthy value, return it
                # This prioritizes explicitly set attributes
                if not (isinstance(value, (str, list, dict)) and not value): # Check for non-empty strings, lists, dicts
                    return value
                elif value is not None: # For other types, check if not None
                    return value

        # Check Dynaconf if attribute is empty or not defined, or if the attribute was empty
        if self.dynaconf_settings and hasattr(self.dynaconf_settings, key):
            dyna_value = getattr(self.dynaconf_settings, key)
            if dyna_value is not None:
                # If Dynaconf has a non-None value, return it
                return dyna_value

        # If still no value, try to get from Dynaconf using its .get() method with default
        if self.dynaconf_settings:
            value = self.dynaconf_settings.get(key, default)
        else:
            value = default

        # Apply casting
        if cast is not None and value is not None:
            try:
                if cast is bool:
                    value = self._cast_bool(value)
                elif cast is int:
                    value = self._cast_int(value)
                elif cast is list:
                    value = self._cast_list(value)
                elif cast is str:
                    value = str(value)
                else:
                    value = cast(value)
            except (ValueError, TypeError):
                value = default

        return value

    def _cast_bool(self, value: Any) -> bool:
        """Cast value to boolean."""
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on", "t", "y")
        return bool(value)

    def _cast_int(self, value: Any) -> int:
        """Cast value to integer."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def _cast_list(self, value: Any) -> List:
        """Cast value to list."""
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        elif isinstance(value, list):
            return value
        return []

    # ==================== PROPERTIES ====================

    @property
    def git_is_configured(self) -> bool:
        """Check if git is minimally configured."""
        return bool(self.GIT_REPO and self.GIT_USERNAME and self.GIT_EMAIL)

    @property
    def git_has_token(self) -> bool:
        """Check if git token is set."""
        return bool(self.GIT_TOKEN and self.GIT_TOKEN.strip())

    def _get_container(self, env: Environment) -> str:
        """Get container name for environment."""
        return {
            Environment.DEVELOPMENT: self.DEMO_CONTAINER,
            Environment.DEMO: self.DEMO_CONTAINER,
            Environment.PRODUCTION: self.MAIN_CONTAINER,
            Environment.STAGING: "django-staging",
            Environment.TESTING: self.DEMO_CONTAINER,
        }.get(env, self.DEMO_CONTAINER)

    def _get_branch(self, env: Environment) -> str:
        """Get branch name for environment."""
        return {
            Environment.DEVELOPMENT: self.DEMO_BRANCH,
            Environment.DEMO: self.DEMO_BRANCH,
            Environment.PRODUCTION: self.MAIN_BRANCH,
            Environment.STAGING: "staging",
            Environment.TESTING: "test",
        }.get(env, self.DEMO_BRANCH)

    @property
    def docker_configured(self) -> bool:
        """Check if docker is configured."""
        return bool(self.DEMO_CONTAINER and self.MAIN_CONTAINER)

    @property
    def sync_container(self) -> str:
        """Get sync container for current environment."""
        if self.SYNC_CONTAINER:
            return self.SYNC_CONTAINER
        return self._get_container(self.SYNC_ENVIRONMENT or self.SERVER_ENV)

    @property
    def sync_branch(self) -> str:
        """Get sync branch for current environment."""
        if self.SYNC_BRANCH:
            return self.SYNC_BRANCH
        return self._get_branch(self.SYNC_ENVIRONMENT or self.SERVER_ENV)

    @property
    def sync_config(self) -> Dict[str, Any]:
        """Get complete sync configuration."""
        return {
            "environment": self.SYNC_ENVIRONMENT,
            "direction": self.SYNC_DIRECTION,
            "workflow": self.SYNC_WORKFLOW,
            "container": self.sync_container,
            "branch": self.sync_branch,
            "restart_container": self.SYNC_RESTART_CONTAINER,
            "run_tests": self.SYNC_RUN_TESTS,
            "auto_commit": self.SYNC_AUTO_COMMIT,
        }

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
    def is_demo(self) -> bool:
        """Check if running in demo."""
        return self.SERVER_ENV == Environment.DEMO

    @property
    def is_staging(self) -> bool:
        """Check if running in staging."""
        return self.SERVER_ENV == Environment.STAGING

    @property
    def is_testing(self) -> bool:
        """Check if running in testing."""
        return self.SERVER_ENV == Environment.TESTING

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

    # ==================== SYNC CONFIGURATION METHODS ====================

    def get_sync_config(
        self,
        env: Optional[Union[str, Environment]] = None,
        direction: Optional[Union[str, Direction]] = None,
        workflow: Optional[Union[str, Workflow]] = None,
    ) -> SyncConfigData:
        """Get sync configuration."""
        # Parse environment
        if env:
            if isinstance(env, str):
                try:
                    environment = Environment(env.lower())
                except ValueError:
                    environment = self.SERVER_ENV
            else:
                environment = env
        else:
            environment = self.SERVER_ENV

        # Parse direction
        if direction:
            if isinstance(direction, str):
                try:
                    direction_enum = Direction(direction.lower())
                except ValueError:
                    direction_enum = Direction.SYNC
            else:
                direction_enum = direction
        else:
            direction_enum = Direction.SYNC

        # Parse workflow
        if workflow:
            if isinstance(workflow, str):
                try:
                    workflow_enum = Workflow(workflow.lower())
                except ValueError:
                    workflow_enum = Workflow.STANDARD
            else:
                workflow_enum = workflow
        else:
            workflow_enum = Workflow.STANDARD

        # Get container and branch for environment
        container = self._get_container(environment)
        branch = self._get_branch(environment)

        return SyncConfigData(
            environment=environment,
            direction=direction_enum,
            workflow=workflow_enum,
            container=container,
            branch=branch,
            restart_container=self.SYNC_RESTART_CONTAINER,
            run_tests=self.SYNC_RUN_TESTS,
            auto_commit=self.SYNC_AUTO_COMMIT,
        )

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
            Environment.DEMO: "🎬",
            Environment.STAGING: "🔄",
            Environment.PRODUCTION: "🚀",
            Environment.TESTING: "🧪",
        }.get(self.SERVER_ENV, "❓")

        return {
            "environment": f"{env_emoji} {self.SERVER_ENV.value}",
            "runtime": f"{runtime_emoji} {self.RUNNING_ENV.value}",
            "module": f"📦 {self.MODULE.value}",
            "debug": ("✅ Disabled" if not self.DEBUG else "⚠️ Enabled") if self.is_production else ("✅ Enabled" if self.DEBUG else "⚠️ Disabled"),
            "host": self.HOST,
            "port": self.PORT,
            "is_production": self.is_production,
            "is_containerized": self.is_containerized,
            "git_configured": self.git_is_configured,
            "git_has_token": self.git_has_token,
            "docker_configured": self.docker_configured,
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
            ("Git Configuration", "✅ Complete" if self.summary["git_configured"] else "⚠️ Partial"),
            ("Git Token", "✅ Present" if self.summary["git_has_token"] else "⚠️ Missing"),
            ("Docker Config", "✅ Complete" if self.summary["docker_configured"] else "⚠️ Partial"),
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

        # Git warnings
        if not self.GIT_REPO:
            warnings.append("📝 GIT_REPO is not set")

        if not self.GIT_USERNAME:
            warnings.append("👤 GIT_USERNAME is not set")

        if not self.GIT_EMAIL:
            warnings.append("📧 GIT_EMAIL is not set")

        if not self.GIT_TOKEN:
            warnings.append("🔑 GIT_TOKEN is not set (sync operations may fail)")

        # Docker warnings
        if self.is_containerized and not self.DEMO_CONTAINER:
            warnings.append("🐳 DEMO_CONTAINER is not set for Docker environment")

        # Server warnings
        if self.HOST == "0.0.0.0" and self.PORT == 5070:
            warnings.append("🌐 Using default HOST (0.0.0.0) and PORT (5070)")

        # Enhanced warnings for missing configurations
        if not self.git_is_configured:
            warnings.append("📚 Git is not fully configured (repo, username, or email missing)")

        if not self.git_has_token:
            warnings.append("🔐 Git token is missing (required for sync operations)")

        if not self.docker_configured:
            warnings.append("📦 Docker containers are not configured")

        # Check for missing required variables
        required_vars = [
            ("DJANGO_SECRET_KEY", "dev-secret-key-change-me"),
            ("HOST", "0.0.0.0"),
            ("PORT", "5070"),
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
            "git": {
                "repo": self.GIT_REPO or "Not set",
                "username": self.GIT_USERNAME or "Not set",
                "email": self.GIT_EMAIL or "Not set",
                "token": "***SET***" if self.GIT_TOKEN else "Not set",
                "configured": self.git_is_configured,
            },
            "docker": {
                "demo_container": self.DEMO_CONTAINER,
                "main_container": self.MAIN_CONTAINER,
                "demo_branch": self.DEMO_BRANCH,
                "main_branch": self.MAIN_BRANCH,
                "configured": self.docker_configured,
            },
            "sync": {
                "environment": self.SYNC_ENVIRONMENT.value,
                "direction": self.SYNC_DIRECTION.value,
                "workflow": self.SYNC_WORKFLOW.value,
                "container": self.sync_container,
                "branch": self.sync_branch,
                "restart_container": self.SYNC_RESTART_CONTAINER,
                "run_tests": self.SYNC_RUN_TESTS,
                "auto_commit": self.SYNC_AUTO_COMMIT,
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

        if not self.git_has_token:
            print("  - Set GIT_TOKEN for sync operations")
            print("  - Generate a personal access token with repo scope")

        if not self.docker_configured:
            print("  - Configure DEMO_CONTAINER and MAIN_CONTAINER")
            print("  - Set appropriate Docker image names")

        if self.is_containerized and self.DEBUG:
            print("  - Consider setting DEBUG=False in containerized environments")

        # Print detected environment
        print("\n🔍 DETECTED ENVIRONMENT:")
        print(f"  - Running in: {self.RUNNING_ENV.value}")
        print(f"  - Server environment: {self.SERVER_ENV.value}")
        print(f"  - Containerized: {'Yes' if self.is_containerized else 'No'}")

    # ==================== SETTINGS EXPORT ====================

    # def get_django_settings(self) -> Dict[str, Any]:
    #     """Get Django settings from configuration."""
    #     django_settings = {
    #         # Core Django
    #         "DEBUG": self.DEBUG,
    #         "SECRET_KEY": self.DJANGO_SECRET_KEY,
    #         "ALLOWED_HOSTS": self.ALLOWED_HOSTS,
    #         "CORS_ALLOWED_ORIGINS": self.CORS_ALLOWED_ORIGINS,
    #         "CSRF_TRUSTED_ORIGINS": self.CSRF_TRUSTED_ORIGINS,
    #         # Common Django settings (use get() for dynamic ones)
    #         "ADMIN_URL": self.get("ADMIN_URL", "admin/"),
    #         "STATIC_URL": self.get("STATIC_URL", "/static/"),
    #         "MEDIA_URL": self.get("MEDIA_URL", "/media/"),
    #         "LANGUAGE_CODE": self.get("LANGUAGE_CODE", "en-us"),
    #         "TIME_ZONE": self.get("TIME_ZONE", "UTC"),
    #     }

    #     # Add any other Django settings from Dynaconf
    #     django_specific_keys = [
    #         "INSTALLED_APPS",
    #         "MIDDLEWARE",
    #         "DATABASES",
    #         "AUTH_PASSWORD_VALIDATORS",
    #         "REST_FRAMEWORK",
    #         "LOGGING",
    #         "SESSION_COOKIE_SECURE",
    #         "CSRF_COOKIE_SECURE",
    #         "SECURE_SSL_REDIRECT",
    #         "SECURE_HSTS_SECONDS",
    #     ]

    #     for key in django_specific_keys:
    #         value = self.get(key)
    #         if value is not None:
    #             django_settings[key] = value

    #     return django_settings

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
            secret_fields = ["GIT_TOKEN", "DJANGO_SECRET_KEY", "SECRET_KEY"]
            for field in secret_fields:
                if field in data and data[field]:
                    data[field] = "***SECRET***"

        return data

    # ==================== HELPER METHODS ====================

    def get_environment_config(
        self, env: Optional[Union[str, Environment]] = None
    ) -> Dict[str, str]:
        """Get configuration for a specific environment."""
        if env is None:
            env = self.SERVER_ENV

        if isinstance(env, str):
            try:
                env = Environment(env.lower())
            except ValueError:
                env = self.SERVER_ENV

        return {
            "container": self._get_container(env),
            "branch": self._get_branch(env),
            "environment": env.value,
        }

    def get_env_file_path(self) -> Path:
        """Get the path to the .env file."""
        return Path(__file__).parent.parent.parent / ".env"

    def reload(self) -> None:
        """Reload settings from environment."""
        self.__init__()


# ==================== GLOBAL INSTANCES ====================

# Singleton instance
settings = MainSettings()

# ==================== UTILITY FUNCTIONS ====================


# def get_django_settings() -> Dict[str, Any]:
# """Get Django settings from main configuration."""
# return settings.get_django_settings()


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
    "SyncConfigData",
    # Instances
    "settings",
    # Utility functions
    # "get_django_settings",
    "init_config",
    # Enums
    "Direction",
    "Environment",
    "LogLevel",
    "Module",
    "Runtime",
    "Workflow",
]
