"""
Chat backends — thin adapters over ceptor-ai.

Each backend receives a message + session context and returns a reply string.
"""
from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import ChatSession

logger = logging.getLogger(__name__)


def _build_prompt(session: "ChatSession", message: str) -> str:
    """Inject DB-linked object data and system prompt into the user message."""
    parts = []

    # System prompt (from session or default)
    system = session.system_prompt or os.environ.get("RSEAL_CHAT_SYSTEM_PROMPT", "")
    if system:
        parts.append(f"[System]: {system}")

    # Linked object context
    obj_data = session.get_linked_object_data()
    if obj_data:
        import json
        parts.append(f"[Context]: {json.dumps(obj_data, ensure_ascii=False)}")

    # Extra JSON context
    if session.context_data:
        import json
        parts.append(f"[Extra]: {json.dumps(session.context_data, ensure_ascii=False)}")

    parts.append(message)
    return "\n".join(parts)


def openai_backend(session: "ChatSession", message: str) -> str:
    """Send message to OpenAI via ceptor-ai."""
    try:
        from ceptor_ai.ai.integrations import OpenAIIntegration

        prompt = _build_prompt(session, message)
        ai = OpenAIIntegration(
            model=os.environ.get("RSEAL_CHAT_OPENAI_MODEL", "gpt-3.5-turbo")
        )
        return ai.generate(prompt)
    except ImportError:
        logger.warning("ceptor-ai not installed; falling back to echo backend")
        return echo_backend(session, message)
    except Exception as exc:
        logger.error("openai_backend error: %s", exc)
        return "Sorry, I'm having trouble connecting right now."


def rasa_backend(session: "ChatSession", message: str) -> str:
    """Send message to Rasa via ceptor-ai."""
    try:
        from ceptor_ai.chat.rasa import RasaClient

        rasa_url = os.environ.get("RASA_URL", "http://localhost:5005")
        client = RasaClient(rasa_url=rasa_url)
        response = client.send_message(
            sender=session.session_id,
            message=message,
        )
        return response.text or "…"
    except ImportError:
        logger.warning("ceptor-ai not installed; falling back to echo backend")
        return echo_backend(session, message)
    except Exception as exc:
        logger.error("rasa_backend error: %s", exc)
        return "Sorry, I'm having trouble connecting right now."


def echo_backend(session: "ChatSession", message: str) -> str:
    """Development echo backend — mirrors the user's message."""
    return f"Echo: {message}"


BACKENDS = {
    "openai": openai_backend,
    "rasa": rasa_backend,
    "echo": echo_backend,
}


def get_reply(session: "ChatSession", message: str) -> str:
    """Dispatch to the correct backend for this session."""
    backend_fn = BACKENDS.get(session.backend, echo_backend)
    return backend_fn(session, message)
