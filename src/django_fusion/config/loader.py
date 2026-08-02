"""
Dynaconf Configuration Loader for Django-Fusion
===============================================

Enhanced Dynaconf integration for Django projects with:
  - Multi-environment support (development, staging, production)
  - Type validation with Pydantic
  - Environment variable interpolation
  - YAML/ENV precedence management
  - Secure defaults for sensitive settings

Usage
-----
    # In Django settings.py
    from django_fusion.config.loader import load_dynaconf_settings
    
    # Load configuration
    settings = load_dynaconf_settings(
        config_dir="configs/",
        env="development",
        validation_schema=MyPydanticSchema  # optional
    )
    
    # Access settings
    DEBUG = settings.DJANGO.debug
    DB_HOST = settings.DATABASE.host
    MODELS = settings.MODELS.registry

Features
--------
  - YAML Configuration Files
    Load hierarchical YAML configs with environment overrides
    
  - Environment Variable Support
    Use {{ env 'VAR_NAME' or 'default_value' }} syntax
    
  - Pydantic Validation (Optional)
    Validate config structure against a schema
    
  - Secret Management
    Separate secrets from configuration, load from .env
    
  - Precedence Rules
    1. Environment variables (.env)
    2. Environment-specific YAML (settings.{ENV}.yml)
    3. Base YAML (settings.yml)
    4. Hardcoded defaults

Classes
-------
DynaconfSettings
    Wrapper around dynaconf.settings with Django-specific utilities

ModelsRegistry
    Type-safe wrapper for AI model configuration

TemplateRegistry
    Type-safe wrapper for template site configuration
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Type

from dynaconf import Dynaconf

logger = logging.getLogger(__name__)


class DynaconfSettings:
    """
    Enhanced Dynaconf settings with Django-specific utilities.
    
    Handles:
      - Multi-environment configuration loading
      - Type validation with Pydantic
      - Environment variable interpolation
      - Secret management
    """
    
    def __init__(
        self,
        config_dir: str | Path = "configs/",
        env: str | None = None,
        validation_schema: Type | None = None,
        load_dotenv: bool = True,
    ):
        """
        Initialize Dynaconf settings loader.
        
        Parameters
        ----------
        config_dir : str | Path
            Directory containing YAML configuration files
        env : str, optional
            Environment name (development, staging, production).
            Defaults to DJANGO_ENV or TINKER_ENV or development
        validation_schema : Type, optional
            Pydantic schema for validation
        load_dotenv : bool, default True
            Whether to load .env file
        """
        self.config_dir = Path(config_dir)
        self.env = env or self._get_environment()
        self.validation_schema = validation_schema
        self.load_dotenv = load_dotenv
        
        self._settings: Dynaconf | None = None
        self._validated: bool = False
    
    @staticmethod
    def _get_environment() -> str:
        """Detect environment from environment variables."""
        env_choices = [
            os.environ.get("DJANGO_ENV"),
            os.environ.get("TINKER_ENV"),
            os.environ.get("ENV"),
            os.environ.get("ENVIRONMENT"),
        ]
        return next((e for e in env_choices if e), "development")
    
    def load(self) -> Dynaconf:
        """
        Load configuration from YAML files and environment variables.
        
        Returns
        -------
        Dynaconf
            Loaded configuration object
        
        Loading Order
        =============
        1. Base configuration: configs/settings.yml
        2. Environment override: configs/settings.{ENV}.yml
        3. Environment variables: from .env file
        4. Dynaconf overrides: from environment
        
        Examples
        --------
        >>> settings = DynaconfSettings(config_dir="configs/")
        >>> conf = settings.load()
        >>> print(conf.DJANGO.debug)
        True
        >>> print(conf.DATABASE.host)
        'localhost'
        """
        if self._settings is not None:
            return self._settings
        
        # Build config file paths
        base_file = self.config_dir / "settings.yml"
        env_file = self.config_dir / f"settings.{self.env}.yml"
        
        logger.info(
            f"Loading Dynaconf configuration | env={self.env} | "
            f"base={base_file} | env_override={env_file}"
        )
        
        # Verify base config exists
        if not base_file.exists():
            raise FileNotFoundError(
                f"Base configuration not found: {base_file}"
            )
        
        # Load settings with Dynaconf
        self._settings = Dynaconf(
            settings_files=[str(base_file), str(env_file)],
            environments=True,
            env_switcher="TINKER_ENV",
            load_dotenv=self.load_dotenv,
            dotenv_path=".env",
            envvar_prefix="TINKER",
        )
        
        logger.info(f"✅ Dynaconf loaded successfully from {self.env} environment")
        
        # Validate if schema provided
        if self.validation_schema is not None:
            self._validate()
        
        return self._settings
    
    def _validate(self) -> None:
        """
        Validate loaded configuration against Pydantic schema.
        
        Raises
        ------
        ValueError
            If configuration doesn't match schema
        """
        if self._validated or self.validation_schema is None:
            return
        
        logger.info("Validating configuration against schema...")
        
        try:
            # Convert Dynaconf to dict for Pydantic validation
            config_dict = dict(self._settings.as_dict())
            self.validation_schema(**config_dict)
            logger.info("✅ Configuration validation passed")
            self._validated = True
        except Exception as e:
            logger.error(f"❌ Configuration validation failed: {e}")
            raise ValueError(f"Invalid configuration: {e}") from e
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Supports dot notation: "DJANGO.debug", "DATABASE.host"
        
        Parameters
        ----------
        key : str
            Configuration key (supports dot notation)
        default : Any, optional
            Default value if key not found
        
        Returns
        -------
        Any
            Configuration value or default
        
        Examples
        --------
        >>> settings.get("DJANGO.debug")
        True
        >>> settings.get("DATABASE.host", "localhost")
        'localhost'
        """
        if self._settings is None:
            self.load()
        
        keys = key.split(".")
        value = self._settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def __getattr__(self, name: str) -> Any:
        """
        Access settings as attributes.
        
        Examples
        --------
        >>> settings.DJANGO.debug
        True
        >>> settings.DATABASE.host
        'localhost'
        """
        if self._settings is None:
            self.load()
        
        try:
            return getattr(self._settings, name)
        except AttributeError:
            raise AttributeError(f"Settings has no attribute: {name}")


class ModelsRegistry:
    """
    Type-safe wrapper for AI model configuration.
    
    Provides access to model definitions loaded from Dynaconf.
    """
    
    def __init__(self, settings: DynaconfSettings | Dynaconf):
        """
        Initialize models registry.
        
        Parameters
        ----------
        settings : DynaconfSettings | Dynaconf
            Settings object containing model configuration
        """
        self.settings = settings
        self._models: list[dict[str, Any]] | None = None
    
    def list_models(self) -> list[dict[str, Any]]:
        """
        Get all configured models.
        
        Returns
        -------
        list[dict]
            List of model configurations
        """
        if self._models is None:
            if hasattr(self.settings, "get"):
                # DynaconfSettings wrapper
                self._models = self.settings.get("models", {}).get("registry", [])
            else:
                # Raw Dynaconf
                self._models = self.settings.models.registry
        
        return self._models or []
    
    def get_model(self, model_id: str) -> dict[str, Any] | None:
        """
        Get a specific model by ID.
        
        Parameters
        ----------
        model_id : str
            Model identifier
        
        Returns
        -------
        dict | None
            Model configuration or None if not found
        """
        for model in self.list_models():
            if model.get("id") == model_id:
                return model
        return None
    
    def get_default_model(self, provider: str | None = None) -> dict[str, Any] | None:
        """
        Get default model, optionally filtered by provider.
        
        Parameters
        ----------
        provider : str, optional
            Filter by provider (ollama, openai_compatible, etc.)
        
        Returns
        -------
        dict | None
            Default model or None
        """
        for model in self.list_models():
            if model.get("default"):
                if provider is None or model.get("provider") == provider:
                    return model
        return None
    
    def get_by_provider(self, provider: str) -> list[dict[str, Any]]:
        """
        Get all models for a specific provider.
        
        Parameters
        ----------
        provider : str
            Provider name (ollama, openai_compatible, etc.)
        
        Returns
        -------
        list[dict]
            Models from the specified provider
        """
        return [m for m in self.list_models() if m.get("provider") == provider]


class TemplateRegistry:
    """
    Type-safe wrapper for template site configuration.
    
    Provides access to template sites and their directories.
    """
    
    def __init__(self, settings: DynaconfSettings | Dynaconf):
        """
        Initialize template registry.
        
        Parameters
        ----------
        settings : DynaconfSettings | Dynaconf
            Settings object containing template configuration
        """
        self.settings = settings
        self._apps: list[dict[str, Any]] | None = None
    
    def list_apps(self) -> list[dict[str, Any]]:
        """
        Get all configured template sites.
        
        Returns
        -------
        list[dict]
            List of template site configurations
        """
        if self._apps is None:
            if hasattr(self.settings, "get"):
                # DynaconfSettings wrapper
                self._apps = self.settings.get("CUSTOMIZER", {}).get("apps", [])
            else:
                # Raw Dynaconf
                self._apps = self.settings.CUSTOMIZER.apps
        
        return self._apps or []
    
    def get_app(self, slug: str) -> dict[str, Any] | None:
        """
        Get a specific app by slug.
        
        Parameters
        ----------
        slug : str
            App slug identifier
        
        Returns
        -------
        dict | None
            App configuration or None if not found
        """
        for app in self.list_apps():
            if app.get("slug") == slug:
                return app
        return None
    
    def get_template_root(self, slug: str) -> Path | None:
        """
        Get template root directory for an app.
        
        Parameters
        ----------
        slug : str
            App slug identifier
        
        Returns
        -------
        Path | None
            Path to template directory or None
        """
        app = self.get_app(slug)
        if app:
            return Path(app.get("template_root", ""))
        return None


def load_dynaconf_settings(
    config_dir: str | Path = "configs/",
    env: str | None = None,
    validation_schema: Type | None = None,
    load_dotenv: bool = True,
) -> DynaconfSettings:
    """
    Load Dynaconf configuration for Django.
    
    Parameters
    ----------
    config_dir : str | Path
        Directory containing YAML configuration files
    env : str, optional
        Environment name. Auto-detected if not provided.
    validation_schema : Type, optional
        Pydantic schema for validation
    load_dotenv : bool, default True
        Whether to load .env file
    
    Returns
    -------
    DynaconfSettings
        Loaded settings object
    
    Examples
    --------
    >>> from django_fusion.config.loader import load_dynaconf_settings
    >>> settings = load_dynaconf_settings(config_dir="configs/")
    >>> settings.load()
    >>> print(settings.DJANGO.debug)
    True
    
    Environment Variables
    ----------
    TINKER_ENV, DJANGO_ENV, ENV, ENVIRONMENT
        Used to determine environment (development, production, etc.)
    
    Configuration Files
    -------------------
    configs/settings.yml              Base configuration
    configs/settings.development.yml  Development overrides
    configs/settings.production.yml   Production overrides
    .env                              Environment variables
    """
    return DynaconfSettings(
        config_dir=config_dir,
        env=env,
        validation_schema=validation_schema,
        load_dotenv=load_dotenv,
    )
