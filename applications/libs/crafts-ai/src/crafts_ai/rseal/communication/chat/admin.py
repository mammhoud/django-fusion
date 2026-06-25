"""Admin registration for chat models."""
from django.contrib import admin

from .models import ChatMessage, ChatSession


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ("role", "text", "created_at", "metadata")
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("session_id", "backend", "user", "created_at", "updated_at")
    list_filter = ("backend",)
    search_fields = ("session_id", "user__username")
    readonly_fields = ("session_id", "created_at", "updated_at")
    inlines = [ChatMessageInline]


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("session", "role", "text_preview", "created_at")
    list_filter = ("role",)
    search_fields = ("text", "session__session_id")

    def text_preview(self, obj):
        return obj.text[:80]
    text_preview.short_description = "Text"
