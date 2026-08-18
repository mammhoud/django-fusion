# Syntara — Use Cases

## 1. AI-Powered Code Assistant (`code-assistant`)

- **Purpose:** Chat interface for code generation, debugging, and refactoring
- **Key features:** Streaming responses (SSE), multi-model support (Ollama/OpenAI/Claude/Gemini), Monaco code editor
- **Customization:** Add new AI backends via Ceptor-AI agent config

## 2. Template Discovery & Customization (`template-discovery`)

- **Purpose:** Browse and modify Django/Wagtail templates across multiple sites
- **Key features:** Multi-site scanning (CTC Research, LMS, VResume), template hierarchy display, section/block preview
- **Customization:** Add new sites to `CUSTOMIZER_APPS` in settings.py

## 3. MCP Tool Execution (`mcp-tools`)

- **Purpose:** Execute Model Context Protocol tools via AI agents
- **Key features:** Tool-calling prompts, structured JSON responses, multi-backend agent config
- **Customization:** Add new MCP tools in `ceptor-ai` library

## 4. Local AI Development (`local-ai`)

- **Purpose:** Self-hosted AI with Ollama — no API keys required
- **Key features:** Ollama integration, local model serving, privacy-preserving
- **Customization:** Switch models via `OLLAMA_MODEL` env var

## Related

| Resource | Path |
|----------|------|
| Syntara README | [`README.md`](README.md) |
| Configuration | [`configuration.md`](configuration.md) |
| AI & Agents | [`../../ai/`](../../ai/) |
