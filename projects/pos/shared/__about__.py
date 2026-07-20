"""
Shared version metadata for POS sidecar servers.

Imported by server.py, manage.py, and routes/info.py to ensure
a single source of truth for version strings.

Usage:
    from shared.__about__ import __version__, __title_solo__

    print(f"{__title_solo__} v{__version__}")
"""

__version__ = "2.0.0"

# Display titles used in CLI output (--version, startup banner)
__title_solo__ = "POS Server"
__title_full__ = "POS Full Server"

# Service names used in /health JSON responses
__service_name_solo__ = "pos_server"
__service_name_full__ = "pos_full_server"

# Service description used in / (index) JSON response
__service_desc_full__ = "POS Full Server (Cloud Master)"

__all__ = [
    "__version__",
    "__title_solo__",
    "__title_full__",
    "__service_name_solo__",
    "__service_name_full__",
    "__service_desc_full__",
]
