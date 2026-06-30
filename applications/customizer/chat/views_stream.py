"""SSE streaming and markdown rendering views for TemplateTinker."""

from __future__ import annotations

import json

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

        # Build conversation context
        messages_qs = list(conversation.messages.all().order_by("timestamp"))
        api_messages = []
        for msg in messages_qs[-10:]:
            role = "user" if msg.is_user else "assistant"
            api_messages.append({"role": role, "content": msg.content})

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
                    import os
                    api_key = os.environ.get(api_key_env)
                    if api_key:
                        headers["Authorization"] = f"Bearer {api_key}"

                with httpx.Client(timeout=timeout) as client:
                    with client.stream(
                        "POST", endpoint, json=payload, headers=headers
                    ) as response:
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
