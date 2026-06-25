"""
Chat session and message models.

Stores conversation history and optional DB-linked context objects.
"""
from __future__ import annotations

import json

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class ChatSession(models.Model):
    """Represents a single chat session (keyed by session_id from the browser)."""

    session_id = models.CharField(max_length=128, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: link session to a Django user
    user = models.ForeignKey(
        "auth.User",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="chat_sessions",
    )

    # Optional: link session to any model object (e.g. a Product, Course, etc.)
    content_type = models.ForeignKey(
        ContentType, null=True, blank=True, on_delete=models.SET_NULL
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    context_object = GenericForeignKey("content_type", "object_id")

    # Optional: extra JSON context (e.g. {"product_id": 5, "category": "tech"})
    context_data = models.JSONField(default=dict, blank=True)

    # AI backend used for this session
    backend = models.CharField(
        max_length=32,
        default="openai",
        choices=[
            ("openai", "OpenAI"),
            ("rasa", "Rasa"),
            ("echo", "Echo (dev)"),
        ],
    )

    # Optional system prompt override for this session
    system_prompt = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = _("Chat Session")
        verbose_name_plural = _("Chat Sessions")

    def __str__(self) -> str:
        return f"Session {self.session_id[:8]}… ({self.backend})"

    def get_context_as_json(self) -> str:
        """Return context_data as a JSON string (for prompt injection)."""
        return json.dumps(self.context_data, ensure_ascii=False)

    def get_linked_object_data(self) -> dict:
        """Return serialisable data from the linked context_object, if any."""
        obj = self.context_object
        if obj is None:
            return {}
        # Try common serialisation patterns
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        if hasattr(obj, "__dict__"):
            return {
                k: str(v)
                for k, v in obj.__dict__.items()
                if not k.startswith("_")
            }
        return {"str": str(obj)}


class ChatMessage(models.Model):
    """A single message within a ChatSession."""

    ROLE_USER = "user"
    ROLE_BOT = "bot"
    ROLE_CHOICES = [(ROLE_USER, _("User")), (ROLE_BOT, _("Bot"))]

    session = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=8, choices=ROLE_CHOICES)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Raw response metadata from the AI backend
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Chat Message")
        verbose_name_plural = _("Chat Messages")

    def __str__(self) -> str:
        return f"[{self.role}] {self.text[:60]}"
