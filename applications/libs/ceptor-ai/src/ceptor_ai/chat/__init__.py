"""
ceptor_ai.chat — Chat bubble REST API client for the crafts server.

Provides:
    CeptorClient   — REST API client for the ceptor-ai server
    ChatBubble     — High-level chat interface (send message, get reply)
    RasaClient     — Optional Rasa Open Source NLU/dialogue client
"""
from ceptor_ai.chat.client import ChatBubble, CeptorClient
from ceptor_ai.chat.rasa import RasaClient

__all__ = ["CeptorClient", "ChatBubble", "RasaClient"]
