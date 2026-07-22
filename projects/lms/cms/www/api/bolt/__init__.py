"""
CTC Research — django-bolt API package (replaces DRF).

Modular bolt handlers organised by domain. Each module exposes a
``register_handlers(bolt)`` function that registers all its endpoints
on the given ``BoltAPI`` instance.

Import pattern (in apis.py)::

    from www.api.bolt.router import register_all_handlers
    register_all_handlers(bolt)
"""
