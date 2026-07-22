"""
Data API Router — registers all domain handlers on a BoltAPI instance.

Usage::

    from www.api.data.router import register_all_handlers

    bolt = BoltAPI(...)
    register_all_handlers(bolt)

This registers every endpoint from all domain modules.  Endpoints that
already exist in ``apis.py`` (e.g. ``/apis/auth/login``, ``/apis/courses``)
are intentionally **not duplicated** — only the missing DRF-converted
endpoints are added by these modules.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def register_all_handlers(bolt):
    """Register all data API endpoints on the given ``BoltAPI`` instance.

    Call this after creating the bolt instance and before running the server.
    Each domain module exports a ``register_handlers(bolt)`` function.
    """
    from www.api.data.auth import register_handlers as register_auth
    from www.api.data.courses import register_handlers as register_courses
    from www.api.data.students import register_handlers as register_students
    from www.api.data.instructors import register_handlers as register_instructors
    from www.api.data.blog import register_handlers as register_blog
    from www.api.data.shop import register_handlers as register_shop
    from www.api.data.events import register_handlers as register_events
    from www.api.data.contact import register_handlers as register_contact

    register_auth(bolt)
    register_courses(bolt)
    register_students(bolt)
    register_instructors(bolt)
    register_blog(bolt)
    register_shop(bolt)
    register_events(bolt)
    register_contact(bolt)

    logger.info("All data API handlers registered from www.api.data package")
