"""Service layer for business logic — supports Ollama + OpenAI-compatible providers."""

from __future__ import annotations

import json
import os
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import httpx
from django.utils import timezone

from .constants import (
    CONVERSATION_CONTEXT_LIMIT,
    ERROR_MESSAGES,
    OLLAMA_CHAT_ENDPOINT,
    OLLAMA_MODEL,
    OLLAMA_STREAM_TIMEOUT,
    OLLAMA_TIMEOUT,
    available_models,
    get_model,
)
from .exceptions import OllamaConnectionError, OllamaResponseError
from .models import Conversation, Message

# ── Shared ceptor_ai Ollama adapter ────────────────────────
_CEPTOR_PATH = (
    Path(__file__).resolve().parents[2]
    / "libs"
    / "ceptor-ai"
    / "src"
    / "ceptor_ai"
    / "services"
    / "ollama.py"
)
_CEPTOR_SPEC = spec_from_file_location("ceptor_ai_ollama_service", str(_CEPTOR_PATH.resolve()))
_CEPTOR_MODULE = module_from_spec(_CEPTOR_SPEC)
sys.modules[_CEPTOR_SPEC.name] = _CEPTOR_MODULE
_CEPTOR_SPEC.loader.exec_module(_CEPTOR_MODULE)
CeptorOllamaService = _CEPTOR_MODULE.OllamaService


# ═══════════════════════════════════════════════════════════════
#  Multi‑provider AI service
# ═══════════════════════════════════════════════════════════════

class AIService:
    """Unified completion / streaming across Ollama and OpenAI-compatible backends."""

    @staticmethod
    def _resolve_model(model_id: str) -> dict:
        model = get_model(model_id)
        if model is None:
            raise OllamaResponseError(f"{ERROR_MESSAGES['UNKNOWN_MODEL']}: {model_id}")
        return model

    @staticmethod
    def _provider_for(model: dict) -> str:
        return model.get("provider", "ollama")

    @staticmethod
    def _api_key(model: dict) -> str | None:
        env_var = model.get("api_key_env")
        if env_var:
            return os.environ.get(env_var)
        return None

    # ── Non-streaming completion ────────────────────────────────

    @staticmethod
    def chat(model_id: str, messages: list[dict]) -> str:
        model = AIService._resolve_model(model_id)
        provider = AIService._provider_for(model)

        if provider == "ollama":
            return _ollama_chat(model, messages)
        return _openai_compatible_chat(model, messages)

    # ── Streaming completion (returns a generator) ───────────────

    @staticmethod
    def stream(model_id: str, messages: list[dict]):
        model = AIService._resolve_model(model_id)
        provider = AIService._provider_for(model)

        if provider == "ollama":
            return _ollama_stream(model, messages)
        return _openai_compatible_stream(model, messages)


# ═══════════════════════════════════════════════════════════════
#  Ollama helpers
# ═══════════════════════════════════════════════════════════════

def _ollama_chat(model: dict, messages: list[dict]) -> str:
    service = CeptorOllamaService(
        default_model=model["model"],
        timeout=float(model.get("timeout", OLLAMA_TIMEOUT)),
    )
    try:
        return service.chat(messages)
    except httpx.ConnectError as e:
        raise OllamaConnectionError(
            f"{ERROR_MESSAGES['OLLAMA_CONNECTION']}: {str(e)}"
        )
    except httpx.TimeoutException as e:
        raise OllamaConnectionError("Request to Ollama timed out") from e
    except Exception as e:
        raise OllamaResponseError(f"Unexpected error: {str(e)}") from e


def _ollama_stream(model: dict, messages: list[dict]):
    base = model.get("base_url", "http://localhost:11434")
    endpoint = f"{base.rstrip('/')}/api/chat"
    timeout = float(model.get("timeout", OLLAMA_STREAM_TIMEOUT))

    def generate():
        full_response = ""
        try:
            with httpx.Client(timeout=timeout) as client:
                with client.stream(
                    "POST",
                    endpoint,
                    json={
                        "model": model["model"],
                        "messages": messages,
                        "stream": True,
                    },
                ) as response:
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    token = data["message"]["content"]
                                    full_response += token
                                    yield json.dumps(
                                        {"type": "token", "content": token}
                                    )
                            except json.JSONDecodeError:
                                continue
                            except Exception as e:
                                yield json.dumps(
                                    {"type": "error", "content": f"Parse error: {str(e)}"}
                                )
        except Exception as e:
            yield json.dumps(
                {"type": "error", "content": f"Connection error: {str(e)}"}
            )
            return

        if full_response:
            yield json.dumps({"type": "complete", "content": full_response})
        else:
            yield json.dumps(
                {"type": "error", "content": ERROR_MESSAGES["NO_RESPONSE"]}
            )

    return generate


# ═══════════════════════════════════════════════════════════════
#  OpenAI-compatible helpers (Claude via Anthropic, GPT-4o, etc.)
# ═══════════════════════════════════════════════════════════════

def _openai_compatible_chat(model: dict, messages: list[dict]) -> str:
    base = model["base_url"].rstrip("/")
    endpoint = f"{base}/chat/completions"
    api_key = AIService._api_key(model)
    timeout = float(model.get("timeout", 90))

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                endpoint,
                json={"model": model["model"], "messages": messages},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
    except httpx.ConnectError as e:
        raise OllamaConnectionError(
            f"{ERROR_MESSAGES['OLLAMA_CONNECTION']}: {str(e)}"
        )
    except httpx.TimeoutException as e:
        raise OllamaConnectionError(
            f"Request to {model['name']} timed out"
        ) from e
    except Exception as e:
        raise OllamaResponseError(f"Unexpected error: {str(e)}") from e


def _openai_compatible_stream(model: dict, messages: list[dict]):
    base = model["base_url"].rstrip("/")
    endpoint = f"{base}/chat/completions"
    api_key = AIService._api_key(model)
    timeout = float(model.get("timeout", 90))

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    def generate():
        full_response = ""
        try:
            with httpx.Client(timeout=timeout) as client:
                with client.stream(
                    "POST",
                    endpoint,
                    json={
                        "model": model["model"],
                        "messages": messages,
                        "stream": True,
                    },
                    headers=headers,
                ) as response:
                    for line in response.iter_lines():
                        if line and line.startswith("data:"):
                            chunk = line.removeprefix("data:").strip()
                            if chunk == "[DONE]":
                                break
                            try:
                                data = json.loads(chunk)
                                delta = (
                                    data.get("choices", [{}])[0]
                                    .get("delta", {})
                                    .get("content", "")
                                )
                                if delta:
                                    full_response += delta
                                    yield json.dumps(
                                        {"type": "token", "content": delta}
                                    )
                            except (json.JSONDecodeError, KeyError, IndexError):
                                continue
                            except Exception as e:
                                yield json.dumps(
                                    {"type": "error", "content": f"Parse error: {str(e)}"}
                                )
        except Exception as e:
            yield json.dumps(
                {"type": "error", "content": f"Connection error: {str(e)}"}
            )
            return

        if full_response:
            yield json.dumps({"type": "complete", "content": full_response})
        else:
            yield json.dumps(
                {"type": "error", "content": ERROR_MESSAGES["NO_RESPONSE"]}
            )

    return generate


# ═══════════════════════════════════════════════════════════════
#  Conversation management
# ═══════════════════════════════════════════════════════════════

class ConversationService:
    """Service for managing conversations."""

    @staticmethod
    def create_conversation(initial_message: str) -> Conversation:
        return Conversation.objects.create_with_message(initial_message)

    @staticmethod
    def add_user_message(conversation: Conversation, content: str) -> Message:
        return Message.objects.create(
            conversation=conversation, content=content, is_user=True
        )

    @staticmethod
    def add_ai_message(conversation: Conversation, content: str) -> Message:
        message = Message.objects.create(
            conversation=conversation, content=content, is_user=False
        )
        conversation.save()
        return message

    @staticmethod
    def get_recent_conversations(limit: int = 5):
        return Conversation.objects.recent(limit)
