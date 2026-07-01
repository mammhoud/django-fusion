"""Chat integration — Django app, REST API client, and Rasa NLU connector.

Sub-modules
-----------
communication.chat.models       Django model for chat messages and sessions.
communication.chat.views        HTMX-compatible chat views.
communication.chat.client       REST client (CeptorClient, ChatBubble) for the crafts server.
communication.chat.rasa         Optional Rasa Open Source NLU/dialogue client.
communication.chat.backends     Custom Django Channels or ASGI chat backends.

Usage::

    from ceptor_ai.communication.chat import ChatBubble, CeptorClient, RasaClient
"""

from .client import ChatBubble, CeptorClient
from .rasa import RasaClient

__all__ = ["CeptorClient", "ChatBubble", "RasaClient"]
