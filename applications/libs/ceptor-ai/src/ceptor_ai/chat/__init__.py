"""Compatibility shim — ``ceptor_ai.chat`` now lives in ``ceptor_ai.communication.chat``.

Import from the canonical path instead::

    from ceptor_ai.communication.chat import CeptorClient, ChatBubble, RasaClient
"""
from __future__ import annotations
from ceptor_ai.communication.chat import ChatBubble, CeptorClient, RasaClient  # noqa: F401

__all__ = ["CeptorClient", "ChatBubble", "RasaClient"]
