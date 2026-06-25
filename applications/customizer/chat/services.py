"""Service layer for business logic"""

import httpx
import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from django.utils import timezone

from .models import Conversation, Message
from .constants import (
    OLLAMA_CHAT_ENDPOINT,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    OLLAMA_STREAM_TIMEOUT,
    CONVERSATION_CONTEXT_LIMIT,
    ERROR_MESSAGES,
)
from .exceptions import OllamaConnectionError, OllamaResponseError


_OLLAMA_PATH = Path(__file__).resolve().parents[2] / "libs" / "crafts-ai" / "src" / "crafts_ai" / "services" / "ollama.py"
_OLLAMA_SPEC = spec_from_file_location("crafts_ai_ollama_service", _OLLAMA_PATH.resolve())
_OLLAMA_MODULE = module_from_spec(_OLLAMA_SPEC)
sys.modules[_OLLAMA_SPEC.name] = _OLLAMA_MODULE
_OLLAMA_SPEC.loader.exec_module(_OLLAMA_MODULE)
CraftsOllamaService = _OLLAMA_MODULE.OllamaService


class OllamaService:
    """Django adapter around the shared crafts_ai Ollama service."""
    
    @staticmethod
    def format_messages(conversation, limit=CONVERSATION_CONTEXT_LIMIT):
        """Format conversation messages for Ollama API"""
        messages = conversation.get_context_messages(limit)
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
    
    @staticmethod
    async def get_completion(messages):
        """Get a completion from Ollama (non-streaming)"""
        service = CraftsOllamaService(default_model=OLLAMA_MODEL, timeout=OLLAMA_TIMEOUT)
        try:
            return service.chat(messages)
        except httpx.ConnectError as e:
            raise OllamaConnectionError(f"{ERROR_MESSAGES['OLLAMA_CONNECTION']}: {str(e)}")
        except httpx.TimeoutException as e:
            raise OllamaConnectionError("Request to Ollama timed out") from e
        except Exception as e:
            raise OllamaResponseError(f"Unexpected error: {str(e)}") from e
    
    @staticmethod
    def stream_completion(messages):
        """Stream a completion from Ollama"""
        
        def generate():
            full_response = ""
            
            try:
                with httpx.Client(timeout=OLLAMA_STREAM_TIMEOUT) as client:
                    with client.stream(
                        "POST",
                        OLLAMA_CHAT_ENDPOINT,
                        json={
                            "model": OLLAMA_MODEL,
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
                                        yield json.dumps({'type': 'token', 'content': token})
                                except json.JSONDecodeError:
                                    continue
                                except Exception as e:
                                    yield json.dumps({'type': 'error', 'content': f'Parse error: {str(e)}'})
            except Exception as e:
                yield json.dumps({'type': 'error', 'content': f'Connection error: {str(e)}'})
                return
            
            # Return the complete response for saving
            if full_response:
                yield json.dumps({
                    'type': 'complete',
                    'content': full_response
                })
            else:
                yield json.dumps({'type': 'error', 'content': ERROR_MESSAGES['NO_RESPONSE']})
        
        return generate


class ConversationService:
    """Service for managing conversations"""
    
    @staticmethod
    def create_conversation(initial_message):
        """Create a new conversation with an initial message"""
        return Conversation.objects.create_with_message(initial_message)
    
    @staticmethod
    def add_user_message(conversation, content):
        """Add a user message to a conversation"""
        return Message.objects.create(
            conversation=conversation,
            content=content,
            is_user=True
        )
    
    @staticmethod
    def add_ai_message(conversation, content):
        """Add an AI message to a conversation"""
        message = Message.objects.create(
            conversation=conversation,
            content=content,
            is_user=False
        )
        # Update conversation's updated_at
        conversation.save()
        return message
    
    @staticmethod
    def get_recent_conversations(limit=5):
        """Get recent conversations"""
        return Conversation.objects.recent(limit)