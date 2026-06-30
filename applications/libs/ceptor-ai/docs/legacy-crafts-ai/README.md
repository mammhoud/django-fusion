# nawaai Documentation

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

# Chat client
from ceptor_ai.chat.client import CraftsClient, ChatBubble

client = CraftsClient(base_url="http://localhost:8765")
bubble = ChatBubble(client=client)
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
uv add nawaai
```

Optional dependencies:

```bash
uv add "nawaai[openai,anthropic]" --dev
uv add "nawaai[faker]" --dev
uv add "nawaai[mcp]" --dev
```
