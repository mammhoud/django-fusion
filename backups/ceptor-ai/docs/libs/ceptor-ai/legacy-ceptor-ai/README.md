# ceptor-ai Documentation

Standalone AI/MCP toolkit — ai, chat, mcp, orchestrator, seeder.

## Contents

- AI integrations (OpenAI, Anthropic)
- Chat clients (REST, Rasa)
- MCP server (Model Context Protocol)
- Spec orchestrator (task execution engine)
- Database seeder

## Quick Start

```python
# AI integrations
from ceptor_ai.ai.integrations import OpenAIIntegration

ai = OpenAIIntegration(api_key="...")
response = ai.generate("Summarize this text: ...")

# Chat client (matches `ceptor_ai.chat.client` actual API: CeptorClient + ChatBubble)
from ceptor_ai.chat.client import CeptorClient, ChatBubble

client = CeptorClient(base_url="http://localhost:8765")
bubble = ChatBubble(server_url="http://localhost:8765")
reply = bubble.send("Hello, how are you?", session_id="user123")
```

## CLI Commands

```bash
ceptorai scan
ceptorai list
ceptorai execute --task-id 1
```

## Installation

```bash
uv add ceptor-ai
```

Optional dependencies (matching `pyproject.toml` `[project.optional-dependencies]`: mcp + test):

```bash
uv add "ceptor-ai[mcp]"
uv add "ceptor-ai[test]" --dev
```
