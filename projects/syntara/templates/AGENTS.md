# Cypercloud — AI Agent Instructions

Path: `projects/cypercloud/` (Makefile alias: `cypercloud`, deployed on port 5073)

## Scope

Cypercloud is an AI-powered platform for building, customizing, and deploying business systems. It features a chat interface with streaming AI responses, a Monaco code editor, prompt library management, and system template deployment.

---

## Key Features

| Feature | Description | Location |
|---------|-------------|----------|
| **AI Chat** | Streaming chat with Ollama/OpenAI/Anthropic backends | `cypercloud/chat/` |
| **Prompt Library** | Reusable prompt templates with variables | `cypercloud/prompts/` |
| **Code Editor** | Monaco-based syntax-aware code editor | `cypercloud/editor/` |
| **Template System** | 1-click deploy: POS, CRM, LMS, Blog | `cypercloud/templates/` |
| **Agent Configs** | Pre-built AI agent configurations | `cypercloud/agents/` |

---

## Template Conventions

This directory (`cypercloud/templates/`) contains Cypercloud-specific templates:

- Build templates as **customization surfaces** for Structa Cloud sites, not as site-specific replacements
- Show available apps first, then template sections/components discovered from each selected site
- Prefer `{% comp %}` tags where a django-fusion component exists; otherwise use narrow `{% include %}` calls with only required context
- Preserve `fragment_name` for fragment identifiers and context keys
- Keep static demo text isolated from CMS or model-provided content

---

## AI Chat Integration

```python
# cypercloud/chat/ceptor.py — stub-backed (ceptor_stubs replaces the removed ceptor-ai lib)
from ceptor_stubs import ChatBubble

bubble = ChatBubble(server_url=settings.AI_SERVER_URL)

async def chat_stream(request):
    """SSE-based streaming chat endpoint."""
    prompt = request.POST.get("prompt")
    model = request.POST.get("model", "gemma3:4b")
    reply = bubble.send(prompt)
    yield f"data: {json.dumps({'content': reply.text})}\n\n"
```

---

## Key Files

| File | Purpose |
|------|---------|
| `cypercloud/chat/views.py` | Chat streaming views |
| `cypercloud/chat/consumers.py` | WebSocket consumers |
| `cypercloud/prompts/models.py` | Prompt template models |
| `cypercloud/editor/views.py` | Monaco editor views |
| `cypercloud/templates/` | Site templates (this directory) |
| `cypercloud/configs/settings.yml` | AI backend configuration |

---

## Development Commands

```bash
cd projects
make dev WEBSITE=cypercloud     # Run dev server
make check WEBSITE=cypercloud   # Django system checks
make test WEBSITE=cypercloud    # Run tests
```

---

## Related Docs

| Resource | Path |
|----------|------|
| Project docs | `docs/projects/cypercloud/` |
| AI overview | `docs/ai/` |
| Ceptor-AI library | `libs/ceptor-ai/` |
| Platform plan | `docs/projects/cypercloud/platform-plan.md` |
