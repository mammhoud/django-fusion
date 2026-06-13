# nawaai Documentation

## Overview
nawaai is a pure Python AI/MCP toolkit for the ecosystem. It provides AI integrations, chat functionality, and MCP server support.

## Key Principles
- **Zero Django imports** - Pure Python only
- **Standalone** - No dependencies on other ecosystem packages
- **AI-focused** - Built for AI/NLP workloads

## Sub-modules

### ai/
AI integration utilities

### chat/
Chat functionality and handlers

### mcp/
MCP (Model Context Protocol) server support

### orchestrator/
Task orchestration utilities

### seeder/
Data seeding for AI workloads

## Installation

```bash
cd venv/libs/nawaai
uv sync
```

## Usage

```python
from nawaai.ai import AIEngine
from nawaai.chat import ChatHandler

# Use AI capabilities
engine = AIEngine()
response = engine.process("Hello, world!")

# Use chat functionality
chat = ChatHandler()
chat.send_message("Hello!")
```

## Documentation Links
- [nawaai README](../../../venv/libs/nawaai/README.md)

## Related Packages
- [django-osoul](../django-osoul/) - Pure Django foundation
- [django-rseal](../django-rseal/) - Wagtail automation
- [django-grep](../django-grep/) - Testing infrastructure
