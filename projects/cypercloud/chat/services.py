"""Service layer for business logic — supports Ollama + OpenAI-compatible providers."""

from __future__ import annotations

import json
import os

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

# ── Minimal Ollama service — inline replacement for the former
#    external Ollama adapter (removed with ceptor-ai) ──

class OllamaService:
    """Minimal Ollama chat client talking directly to the Ollama HTTP API.

    Replaces the former external Ollama adapter that was removed along
    with the ceptor-ai package.
    """

    def __init__(
        self,
        default_model: str = "llama3",
        timeout: float = 300.0,
        base_url: str = "http://localhost:11434",
    ):
        self.default_model = default_model
        self.timeout = timeout
        self.base_url = base_url

    def chat(self, messages: list[dict]) -> str:
        """Send a non-streaming chat request and return the reply text."""
        endpoint = f"{self.base_url.rstrip('/')}/api/chat"
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                endpoint,
                json={
                    "model": self.default_model,
                    "messages": messages,
                    "stream": False,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")


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
    service = OllamaService(
        default_model=model["model"],
        timeout=float(model.get("timeout", OLLAMA_TIMEOUT)),
        base_url=model.get("base_url", "http://localhost:11434"),
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
                    response.raise_for_status()
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

    return generate()


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
                    response.raise_for_status()
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

    return generate()


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
        message = Message.objects.create(
            conversation=conversation, content=content, is_user=True
        )
        # Keep recent-conversation ordering correct immediately after a send,
        # before the asynchronous/provider response is available.
        conversation.save(update_fields=["updated_at"])
        return message

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
