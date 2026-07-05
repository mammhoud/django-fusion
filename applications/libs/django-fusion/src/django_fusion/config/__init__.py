"""Package-level configuration — constants, conf helpers, and logging setup.

Modules
-------
config.conf             App settings with defaults (OsoulConf dataclass).
config.conf_utils       Utility functions for reading conf values safely.
config.constants        Package-wide constants (cache key prefixes, timeouts).
config.logging          Structured logging configuration helpers.

Usage::

    from django_fusion.config import OsoulConf
    from django_fusion.config.constants import CACHE_KEY_PREFIX
"""
