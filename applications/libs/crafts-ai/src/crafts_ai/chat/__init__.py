"""
crafts_ai.chat — Chat bubble REST API client for the crafts server.

Provides:
    CraftsClient   — REST API client for the crafts-ai server
    ChatBubble     — High-level chat interface (send message, get reply)
    RasaClient     — Optional Rasa Open Source NLU/dialogue client
"""
from crafts_ai.chat.client import ChatBubble, CraftsClient
from crafts_ai.chat.rasa import RasaClient

__all__ = ["CraftsClient", "ChatBubble", "RasaClient"]
