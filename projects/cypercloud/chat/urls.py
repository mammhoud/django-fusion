from django.urls import path
from . import views
from .views_stream import (
    StreamChatView,
    RenderMarkdownView,
    CeptorStreamChatView,
    CeptorAIStreamChatView,
)

urlpatterns = [
    path("", views.HomepageView.as_view(), name="homepage"),
    path("chat/<int:conversation_id>/", views.ChatView.as_view(), name="chat"),
    path(
        "chat/<int:conversation_id>/stream/",
        StreamChatView.as_view(),
        name="stream_chat",
    ),
    path(
        "chat/<int:conversation_id>/ceptor-stream/",
        CeptorStreamChatView.as_view(),
        name="ceptor_stream_chat",
    ),
    path(
        "chat/<int:conversation_id>/ceptor-ai-stream/",
        CeptorAIStreamChatView.as_view(),
        name="ceptor_ai_stream_chat",
    ),
    path(
        "chat/<int:conversation_id>/render-markdown/",
        RenderMarkdownView.as_view(),
        name="render_markdown",
    ),
    path(
        "fragment/template-sidebar/<str:website_slug>/",
        views.TemplateSidebarFragmentView.as_view(),
        name="fragment_template_sidebar",
    ),
    # ── Ceptor-AI API endpoints ──
    path(
        "api/ceptor/health/",
        views.CeptorHealthView.as_view(),
        name="ceptor_health",
    ),
    path(
        "api/ceptor/config/",
        views.CeptorConfigPreloadView.as_view(),
        name="ceptor_config",
    ),
    path(
        "api/ceptor/mcp/<str:tool_name>/",
        views.CeptorMCPToolView.as_view(),
        name="ceptor_mcp_tool",
    ),
    path(
        "api/ceptor/ai/complete/",
        views.CeptorAICompleteView.as_view(),
        name="ceptor_ai_complete",
    ),
]
