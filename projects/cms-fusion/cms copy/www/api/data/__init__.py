"""
CTC Research — django-data API package (replaces DRF).

Modular data handlers organised by domain. Each module exposes a
``register_handlers(bolt)`` function that registers all its endpoints
on the given ``BoltAPI`` instance.

Import pattern (in apis.py)::

    from www.api.data.router import register_all_handlers
    register_all_handlers(bolt)
"""
