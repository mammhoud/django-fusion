# 🔌 MCP Integration

> Model Context Protocol integration across the Structa Cloud monorepo — Kilo server, ceptor-ai client, and AI tool definitions.

---

## Architecture

```
┌─────────────────────────────────────┐
│         AI Editor / Agent            │
│    (Continue, Cursor, etc.)          │
└────────────┬────────────────────────┘
             │ MCP Protocol (stdio/HTTP)
┌────────────▼────────────────────────┐
│       Kilo MCP Server                │
│   applications/agents/                 │
│   • search_codebase                  │
│   • read_files                       │
│   • run_tests                        │
│   • get_docs                         │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│       Prompt Catalog (read-only)     │
│   applications/agents/prompts/       │
│   • skill prompts                    │
│   • project descriptions              │
│   • agent workflows                  │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│       ceptor-ai (MCP Client)         │
│   libs/ceptor-ai/                    │
│   • ceptor_ai.mcp_server:app         │
│   • endpoint discovery               │
│   • tool invocation                  │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│         Structa Cloud Monorepo       │
│   projects/ + libs/ + applications/  │
└─────────────────────────────────────┘
```

---

## Kilo MCP Server

### Location

```
applications/agents/
├── config.json          # Tool definitions
├── mcp_server.py        # Server implementation
├── tools/
│   ├── search.py        # Code search tool
│   ├── files.py         # File read tool
│   ├── test_runner.py   # Test execution tool
│   └── docs.py          # Documentation tool
└── AGENTS.md            # Agent instructions
```

### Tool Definitions

```json
// applications/agents/config.json
{
  "tools": [
    {
      "name": "search_codebase",
      "description": "Search for code patterns across the Structa Cloud monorepo",
      "parameters": {
        "pattern": { "type": "string", "required": true },
        "file_types": { "type": "array", "items": "string" },
        "directory": { "type": "string" }
      }
    },
    {
      "name": "read_files",
      "description": "Read specific source files with line numbers",
      "parameters": {
        "paths": { "type": "array", "items": "string", "required": true },
        "max_lines": { "type": "integer", "default": 500 }
      }
    },
    {
      "name": "run_tests",
      "description": "Execute test suites for specific projects",
      "parameters": {
        "project": { "type": "string", "required": true },
        "test_path": { "type": "string" },
        "verbose": { "type": "boolean", "default": false }
      }
    },
    {
      "name": "get_docs",
      "description": "Retrieve documentation for a project or component",
      "parameters": {
        "path": { "type": "string", "required": true },
        "section": { "type": "string" }
      }
    }
  ]
}
```

---

## Ceptor-AI MCP Server

### Location

```
libs/ceptor-ai/src/ceptor_ai/
├── mcp_server.py        # FastAPI/Starlette server
├── mcp_client.py        # Client-side protocol
├── chat/
│   ├── client.py        # Chat client (CeptorClient)
│   └── bubble.py        # ChatBubble UI component
└── tools/
    └── registry.py      # Tool registration
```

### Starting the Server

```bash
# Install with MCP extras
cd libs/ceptor-ai
uv pip install -e '.[mcp]'

# Start server (local only — bound to 127.0.0.1)
PYTHONPATH=libs/ceptor-ai/src \
uvicorn ceptor_ai.mcp_server:app \
  --host 127.0.0.1 \
  --port 8002
```

### Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server health status |
| `/features` | GET | List registered MCP tools |
| `/tools` | GET | Tool schema definitions |
| `/file-structure` | GET | Repository file tree |
| `/django-fusion` | GET | django-fusion component registry |
| `/web-configs` | GET | Active web configurations |
| `/ssl-proxy` | GET | SSL/Proxy certificate status |

### Client Usage

```python
from ceptor_ai.chat.client import CeptorClient

client = CeptorClient(server_url="http://127.0.0.1:8002")

# Check server health
health = client.get_health()
print(f"Server: {health['status']}")

# List available tools
tools = client.get_features()
for tool in tools:
    print(f"  {tool['name']}: {tool['description']}")

# Search the codebase
results = client.search_codebase(
    pattern="class RegistrationAdapter",
    directory="projects/precis/"
)

# Read specific files
contents = client.read_files([
    "projects/precis/plugins/accounts/adapters.py",
    "libs/django-fusion/src/django_fusion/comp/registry.py",
])
```

---

## AI Editor Configuration

### Continue (VS Code / JetBrains)

```json
// ~/.continue/config.json
{
  "models": [
    {
      "title": "Gemma 3 (Ollama)",
      "provider": "ollama",
      "model": "gemma3:4b",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Qwen 3 (Ollama - Fallback)",
      "provider": "ollama",
      "model": "qwen3:4b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Llama 3.2 (Fast)",
    "provider": "ollama",
    "model": "llama3.2:1b",
    "apiBase": "http://localhost:11434"
  },
  "embeddingsProvider": {
    "provider": "ollama",
    "model": "nomic-embed-text",
    "apiBase": "http://localhost:11434"
  },
  "systemMessage": "You are a senior Django expert working on the Structa Cloud monorepo.",
  "contextProviders": [
    { "name": "codebase" },
    { "name": "docs" }
  ],
  "allowAnonymousTelemetry": false,
  "mcpServers": [
    {
      "name": "kilo",
      "command": "python",
      "args": ["applications/agents/mcp_server.py"],
      "env": {
        "PROJECT_ROOT": "/home/structa.cloud"
      }
    }
  ]
}
```

### Recommended Ollama Models

| Model | RAM | Use Case |
|-------|-----|----------|
| `gemma3:4b` | ~3 GB | Main chat — strong code understanding |
| `qwen3:4b` | ~3 GB | Fallback chat — alternative model |
| `llama3.2:1b` | ~1 GB | Fast autocomplete — minimal latency |
| `nomic-embed-text` | ~0.5 GB | Embeddings for codebase indexing |
| `llama3.2:latest` | ~2 GB | Alternative main model |

---

## Cypercloud AI Integration

The Cypercloud platform uses ceptor-ai for its AI chat features:

```python
# projects/syntara/chat/views.py
from ceptor_ai.chat.client import CeptorClient

client = CeptorClient(server_url=settings.AI_SERVER_URL)

async def chat_stream(request):
    """SSE-based streaming chat endpoint."""
    prompt = request.POST.get("prompt")
    model = request.POST.get("model", "gemma3:4b")

    async for chunk in client.stream_chat(prompt, model=model):
        yield f"data: {json.dumps(chunk)}\n\n"
```

---

## Task-Based AI Prompts

Pre-built prompt templates for common development tasks were previously stored
under `docs/dev/pre-restructure/ai/tasks/` (deprecated — directory removed).
See `docs/ai/prompts.md` and `docs/ai/PROMPT_CATALOG.md` for current AI prompt guidance. The catalog endpoints are repository-specific read-only REST metadata endpoints, not standard MCP `prompts/list` and `prompts/get` methods.

---

## Related

| Topic | Path |
|------|------|
| AI overview | [`README.md`](README.md) |
| Agent instructions | [`agents.md`](agents.md) |
| Prompt engineering | [`prompts.md`](prompts.md) |
| Ceptor-AI library | [`../libs/README.md`](../libs/README.md) |
| Cypercloud AI | [`../projects/syntara/`](../projects/syntara/) |
