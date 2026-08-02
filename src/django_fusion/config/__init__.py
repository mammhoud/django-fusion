"""Package-level configuration — constants, conf helpers, and logging setup.

Modules
-------
config.conf                  App settings with defaults (OsoulConf dataclass).
config.conf_utils            Utility functions for reading conf values safely.
config.constants             Package-wide constants (cache key prefixes, timeouts).
config.logging               Structured logging configuration helpers.
config.loader       Enhanced Dynaconf integration for Django.
config.assets       Unified component/webpack/static asset pipeline options.
config.manifest     Component and merged webpack asset manifests.

Dynaconf Features
-----------------
Enhanced multi-environment configuration with:
  - YAML-based settings with environment overrides
  - Environment variable interpolation
  - Type validation with Pydantic
  - Secure secret management via .env
  - Model and template registries

Usage::

    from django_fusion.config import OsoulConf
    from django_fusion.config.constants import CACHE_KEY_PREFIX
    from django_fusion.config.loader import load_dynaconf_settings
    
    # Load Dynaconf configuration
    settings = load_dynaconf_settings(config_dir="configs/")
    settings.load()
    
    # Access settings
    DEBUG = settings.DJANGO.debug
    MODELS = settings.MODELS.registry
"""
