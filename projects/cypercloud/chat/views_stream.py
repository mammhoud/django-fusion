"""SSE streaming and markdown rendering views for TemplateTinker."""

from __future__ import annotations

import json
import os

import httpx
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin

from .constants import ERROR_MESSAGES, get_model
from .models import Conversation, Message
from .services import AIService, ConversationService
from .views import render_markdown

# Default ceptor chat server URL (lazy-read from env at request time)
_DEFAULT_CEPTOR_SERVER_URL = "http://localhost:8765"


@method_decorator(csrf_exempt, name="dispatch")
class StreamChatView(SingleObjectMixin, View):
    """SSE endpoint for streaming AI responses — provider-agnostic."""

    model = Conversation
    pk_url_kwarg = "conversation_id"

    def get(self, request, *args, **kwargs):
        message_id = request.GET.get("message_id")
        model_id = request.GET.get("model_id", "gemma3-4b")

        if not message_id:
            return HttpResponse("Missing message_id", status=400)

        model_cfg = get_model(model_id)
        if model_cfg is None:
            return HttpResponse(f"Unknown model: {model_id}", status=400)

        self.object = self.get_object()
        conversation = self.object
        user_message = get_object_or_404(
            Message, id=message_id, conversation=conversation, is_user=True
        )

        # Build the bounded context window in chronological order.
        api_messages = []
        for msg in conversation.get_context_messages(
            10, exclude_id=user_message.id
        ):
            role = "user" if msg.is_user else "assistant"
            api_messages.append({"role": role, "content": msg.content})
        # The active message is excluded from history above, then appended
        # exactly once as the provider's latest user prompt.
        api_messages.append({"role": "user", "content": user_message.content})

        def generate():
            full_response = ""
            try:
                provider = model_cfg.get("provider", "ollama")
                base = model_cfg["base_url"].rstrip("/")
                timeout = float(model_cfg.get("timeout", 60))

                if provider == "ollama":
                    endpoint = f"{base}/api/chat"
                    payload = {
                        "model": model_cfg["model"],
                        "messages": api_messages,
                        "stream": True,
                    }
                else:
                    endpoint = f"{base}/chat/completions"
                    payload = {
                        "model": model_cfg["model"],
                        "messages": api_messages,
                        "stream": True,
                    }

                headers = {"Content-Type": "application/json"}
                api_key_env = model_cfg.get("api_key_env")
                if api_key_env:
                    api_key = os.environ.get(api_key_env)
                    if api_key:
                        headers["Authorization"] = f"Bearer {api_key}"

                with httpx.Client(timeout=timeout) as client:
                    with client.stream(
                        "POST", endpoint, json=payload, headers=headers
                    ) as response:
                        response.raise_for_status()
                        for line in response.iter_lines():
                            if not line:
                                continue

                            if provider == "ollama":
                                # Ollama: each line is a complete JSON object
                                try:
                                    data = json.loads(line)
                                    if (
                                        "message" in data
                                        and "content" in data["message"]
                                    ):
                                        token = data["message"]["content"]
                                        full_response += token
                                        yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                                except (json.JSONDecodeError, KeyError):
                                    continue
                            else:
                                # OpenAI-compatible: SSE-style data: prefix
                                if line.startswith("data:"):
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
                                            yield f"data: {json.dumps({'type': 'token', 'content': delta})}\n\n"
                                    except (json.JSONDecodeError, KeyError, IndexError):
                                        continue
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': f'Connection error: {str(e)}'})}\n\n"
                return

            if full_response:
                ai_message = ConversationService.add_ai_message(
                    conversation, full_response
                )
                local_time = ai_message.timestamp.astimezone()
                timestamp_str = (
                    local_time.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
                )
                yield f"data: {json.dumps({'type': 'done', 'timestamp': timestamp_str})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'content': ERROR_MESSAGES['NO_RESPONSE']})}\n\n"

        response = StreamingHttpResponse(generate(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


# ═══════════════════════════════════════════════════════════════
#  Ceptor AI Stream — uses CeptorAIService (ceptor_stubs-backed)
# ═══════════════════════════════════════════════════════════════

@method_decorator(csrf_exempt, name="dispatch")
class CeptorAIStreamChatView(SingleObjectMixin, View):
    """SSE endpoint that streams completions via CeptorAIService.

    Uses the local ``ceptor_stubs`` AIIntegrationRegistry to call OpenAI,
    Claude, Gemini, etc. directly — no external chat server required.
    Model is selected via the ``model_id`` query parameter:

    - ``ceptor-openai`` → OpenAI (requires ``OPENAI_API_KEY`` env var)
    - ``ceptor-claude`` → Claude (requires ``ANTHROPIC_API_KEY`` env var)
    - ``ceptor-gemini`` → Gemini (requires ``GEMINI_API_KEY`` env var)
    """

    model = Conversation
    pk_url_kwarg = "conversation_id"

    def get(self, request, *args, **kwargs):
        message_id = request.GET.get("message_id")
        model_id = request.GET.get("model_id", "ceptor-openai")

        if not message_id:
            return HttpResponse("Missing message_id", status=400)

        # Map model_id to AI backend
        backend_map = {
            "ceptor-openai": "openai",
            "ceptor-claude": "claude",
            "ceptor-gemini": "gemini",
        }
        backend = backend_map.get(model_id)
        if backend is None:
            return HttpResponse(
                f"Unknown ceptor AI model: {model_id}. "
                f"Use {', '.join(backend_map.keys()) or 'ceptor-openai'}.",
                status=400,
            )

        self.object = self.get_object()
        conversation = self.object
        user_message = get_object_or_404(
            Message, id=message_id, conversation=conversation, is_user=True
        )

        def generate():
            full_response = ""
            try:
                from .ceptor import get_ai_service

                ai = get_ai_service()

                # Build the bounded context window in chronological order.
                context_parts: list[str] = []
                for msg in conversation.get_context_messages(
                    10, exclude_id=user_message.id
                ):
                    role = "User" if msg.is_user else "Assistant"
                    context_parts.append(f"{role}: {msg.content}")
                context_str = "\n".join(context_parts) if context_parts else ""

                prompt = user_message.content
                if context_str:
                    prompt = (
                        f"Previous conversation:\n{context_str}\n\n"
                        f"User: {user_message.content}\nAssistant:"
                    )

                # Stream tokens from the stub-backed AI service
                for chunk in ai.stream(backend, prompt):
                    if chunk:
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"

            except ImportError:
                yield f"data: {json.dumps({'type': 'error', 'content': 'ceptor-ai is not installed. Install with: pip install ceptor-ai'})}\n\n"
                return
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': f'Ceptor AI error: {str(e)}'})}\n\n"
                return

            if full_response:
                ai_message = ConversationService.add_ai_message(
                    conversation, full_response
                )
                local_time = ai_message.timestamp.astimezone()
                timestamp_str = (
                    local_time.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
                )
                yield f"data: {json.dumps({'type': 'done', 'timestamp': timestamp_str})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'content': ERROR_MESSAGES['NO_RESPONSE']})}\n\n"

        response = StreamingHttpResponse(generate(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


@method_decorator(csrf_exempt, name="dispatch")
class RenderMarkdownView(View):
    """API endpoint to render markdown to HTML."""

    def post(self, request, conversation_id):
        try:
            data = json.loads(request.body)
            content = data.get("content", "")
            rendered = render_markdown(content)
            return HttpResponse(rendered)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": ERROR_MESSAGES["INVALID_JSON"]}, status=400
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# ═══════════════════════════════════════════════════════════════
#  Ceptor-AI Chat Stream — routes messages through CeptorChatService
# ═══════════════════════════════════════════════════════════════

@method_decorator(csrf_exempt, name="dispatch")
class CeptorStreamChatView(SingleObjectMixin, View):
    """SSE endpoint that proxies messages through CeptorChatService.

    Sends the conversation to the chat server (configurable via
    ``CEPTOR_CHAT_SERVER_URL`` env var, default ``http://localhost:8765``),
    streams the reply back as SSE tokens.
    """

    model = Conversation
    pk_url_kwarg = "conversation_id"

    def get(self, request, *args, **kwargs):
        message_id = request.GET.get("message_id")
        server_url = request.GET.get(
            "server_url",
            os.environ.get("CEPTOR_CHAT_SERVER_URL", _DEFAULT_CEPTOR_SERVER_URL),
        )
        timeout = int(request.GET.get("timeout", 30))

        if not message_id:
            return HttpResponse("Missing message_id", status=400)

        self.object = self.get_object()
        conversation = self.object
        user_message = get_object_or_404(
            Message, id=message_id, conversation=conversation, is_user=True
        )

        def generate():
            full_response = ""
            try:
                from .ceptor import CeptorChatService

                chat = CeptorChatService(
                    server_url=server_url, timeout=timeout
                )

                # Check server availability first
                if not chat.is_available():
                    yield f"data: {json.dumps({'type': 'error', 'content': f'Ceptor chat server unreachable at {server_url}.'})}\n\n"
                    return

                # Build the bounded context window in chronological order.
                context_parts: list[str] = []
                for msg in conversation.get_context_messages(
                    10, exclude_id=user_message.id
                ):
                    role = "User" if msg.is_user else "Assistant"
                    context_parts.append(f"{role}: {msg.content}")
                context_str = "\n".join(context_parts) if context_parts else ""

                # Send message with conversation history as context
                session_id = str(conversation.id)
                enriched_message = user_message.content
                if context_str:
                    enriched_message = (
                        f"Conversation so far:\n{context_str}\n\n"
                        f"User's latest message: {user_message.content}"
                    )

                reply = chat.send_message(
                    enriched_message,
                    session_id=session_id,
                )
                full_response = reply["text"]

                # Simulate token-by-token streaming since ChatBubble returns
                # complete reply — split into word-level tokens for smooth UI
                words = full_response.split(" ")
                for i, word in enumerate(words):
                    token = word + (" " if i < len(words) - 1 else "")
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            except ImportError:
                yield f"data: {json.dumps({'type': 'error', 'content': 'ceptor-stubs are not available.'})}\n\n"
                return
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': f'Ceptor chat error: {str(e)}'})}\n\n"
                return

            if full_response:
                ai_message = ConversationService.add_ai_message(
                    conversation, full_response
                )
                local_time = ai_message.timestamp.astimezone()
                timestamp_str = (
                    local_time.strftime("%I:%M %p").lstrip("0").replace(" 0", " ")
                )
                yield f"data: {json.dumps({'type': 'done', 'timestamp': timestamp_str})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'error', 'content': ERROR_MESSAGES['NO_RESPONSE']})}\n\n"

        response = StreamingHttpResponse(generate(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
