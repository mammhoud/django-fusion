"""Constants and configuration for the chat application."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

# ── Model Registry ────────────────────────────────────────────
_MODELS_YAML = Path(__file__).resolve().parents[1] / "configs" / "models.yml"
_MODELS_CACHE: dict | None = None


def _load_models() -> dict:
    """Load the model registry from YAML (cached)."""
    global _MODELS_CACHE
    if _MODELS_CACHE is not None:
        return _MODELS_CACHE
    if _MODELS_YAML.exists():
        with open(_MODELS_YAML, encoding="utf-8") as fh:
            _MODELS_CACHE = yaml.safe_load(fh)
    else:
        _MODELS_CACHE = {"models": []}
    return _MODELS_CACHE


def available_models() -> list[dict]:
    """Return every registered model entry."""
    return _load_models().get("models", [])


def get_model(model_id: str) -> dict | None:
    """Look up a single model by its id."""
    for m in available_models():
        if m["id"] == model_id:
            return m
    return None


def default_model_id() -> str:
    """Return the id of the first model marked default=True, falling back to gemma3-4b."""
    for m in available_models():
        if m.get("default"):
            return m["id"]
    return "gemma3-4b"


def model_choices() -> list[tuple[str, str]]:
    """Return (id, display_name) pairs grouped by provider."""
    groups: dict[str, list[tuple[str, str]]] = {"ollama": [], "openai_compatible": []}
    for m in available_models():
        provider = m.get("provider", "ollama")
        if provider in groups:
            groups[provider].append((m["id"], m["name"]))
        else:
            groups.setdefault(provider, []).append((m["id"], m["name"]))
    return groups


# ── Backwards-compatible aliases ──────────────────────────────
_default = get_model(default_model_id()) or {}
OLLAMA_MODEL = _default.get("model", "gemma3:4b")
OLLAMA_BASE_URL = _default.get("base_url", "http://localhost:11434")
OLLAMA_CHAT_ENDPOINT = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TIMEOUT = float(_default.get("timeout", 60))
OLLAMA_STREAM_TIMEOUT = float(_default.get("timeout", 60))

# Message Configuration
MAX_MESSAGE_LENGTH = 10000
CONVERSATION_CONTEXT_LIMIT = 10
TITLE_TRUNCATE_LENGTH = 50

# UI Configuration
RECENT_CONVERSATIONS_LIMIT = 5
MESSAGE_PREVIEW_LENGTH = 100

# Response Messages
ERROR_MESSAGES = {
    "EMPTY_MESSAGE": "Message cannot be empty",
    "MESSAGE_TOO_LONG": f"Message is too long (max {MAX_MESSAGE_LENGTH} characters)",
    "OLLAMA_CONNECTION": "Could not connect to the local model",
    "OLLAMA_ERROR": "Sorry, I'm having trouble connecting to the AI model.",
    "NO_RESPONSE": "No response received from the model",
    "INVALID_JSON": "Invalid JSON in request",
    "UNKNOWN_MODEL": "Unknown model selected",
}

# Model Display Names
_default_name = _default.get("name", "Gemma 3 4B")
AI_DISPLAY_NAME = _default_name
AI_AVATAR_TEXT = "AI"

