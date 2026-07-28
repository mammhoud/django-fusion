# Configuration Reference – Complete Setup

## 1. Continue `config.json` (VS Code)

**Location**  
- macOS/Linux: `~/.continue/config.json`  
- Windows: `%APPDATA%\Continue\config.json`

### Full Example with Multiple Models & Django System Prompt

```json
{
  "models": [
    {
      "title": "Gemma 3 4B (Chat – Main)",
      "provider": "ollama",
      "model": "gemma3:4b",
      "apiBase": "http://localhost:11434",
      "systemMessage": "You are a senior Django expert. Follow Django best practices, use the ORM correctly, and never suggest raw SQL unless explicitly asked. Keep responses concise and include code examples when relevant.",
      "options": {
        "num_ctx": 4096,
        "temperature": 0.7
      }
    },
    {
      "title": "Qwen3 4B (Fallback – Faster)",
      "provider": "ollama",
      "model": "qwen3:4b",
      "apiBase": "http://localhost:11434",
      "options": {
        "num_ctx": 2048,
        "temperature": 0.5
      }
    }
  ],
  "tabAutocompleteModel": {
    "title": "Llama 3.2 1B (Fast Autocomplete)",
    "provider": "ollama",
    "model": "llama3.2:1b",
    "apiBase": "http://localhost:11434"
  },
  "embeddingsProvider": {
    "provider": "ollama",
    "model": "nomic-embed-text",
    "apiBase": "http://localhost:11434"
  },
  "contextProviders": [
    {
      "name": "codebase",
      "params": {}
    },
    {
      "name": "folder",
      "params": {
        "path": "docs"
      }
    }
  ],
  "allowAnonymousTelemetry": false
}
```

### Explanation of Fields

| Field | Description |
|-------|-------------|
| `models` | Array of chat models you can select from the Continue sidebar. |
| `title` | Display name in VS Code. |
| `provider` | Always `"ollama"` for local models. |
| `model` | Exact name you used in `ollama pull`. |
| `apiBase` | Ollama’s default endpoint. |
| `systemMessage` | Prepended instructions for the assistant (great for Django‑specific behaviour). |
| `options` | Model‑specific parameters: `num_ctx` (context window size in tokens), `temperature` (randomness). |
| `tabAutocompleteModel` | Separate model for inline code completion – use a tiny 1B model for speed. |
| `embeddingsProvider` | Required for `@codebase` context. Use `nomic-embed-text` (pull it: `ollama pull nomic-embed-text`). |
| `contextProviders` | Enable `@codebase` (whole project) and `@folder docs` (documentation folder). |
| `allowAnonymousTelemetry` | Set to `false` for complete privacy. |

### Performance Tuning for 8GB RAM

- **Reduce context window** for the chat model: `"num_ctx": 2048` (or even 1024).
- **Use a 1B autocomplete model** as shown above.
- **Close other heavy applications** (browser tabs, Docker, Slack).

---

## 2. AI Customizer `ai/config.json`

Generated automatically on first run of `ai_customizer.py`. Edit to change behaviour.

### Field Reference

| Field | Description | Default |
|-------|-------------|---------|
| `model` | Ollama model name to use for all tasks. | `gemma3:4b` |
| `temperature` | Sampling temperature (0 = deterministic, 1 = creative). | `0.7` |
| `num_ctx` | Context window size in tokens (higher = more memory). | `4096` |
| `system_prompt` | Base instructions for the assistant (prepended to every prompt). | `"You are a senior Django developer..."` |
| `priority_patterns` | Glob patterns for `--priority` file search. Order = priority. | `["*.py", "*/models.py", ...]` |
| `exclude_patterns` | Glob patterns to ignore when searching files. | `["*/migrations/*", "*/__pycache__/*", ...]` |

After editing, **restart** `ai_customizer.py` for changes to take effect.

---

## 3. Environment Variables (Ollama)

Set these before starting Ollama to tweak its behaviour globally.

| Variable | Purpose | Example |
|----------|---------|---------|
| `OLLAMA_HOST` | Change bind address (default `127.0.0.1:11434`). | `export OLLAMA_HOST=0.0.0.0:11434` |
| `OLLAMA_ORIGINS` | Allow web origins (for local web apps). | `export OLLAMA_ORIGINS="*"` |
| `OLLAMA_KEEP_ALIVE` | How long to keep models loaded after last use (default `5m`). Set to `-1` to stay loaded forever. | `export OLLAMA_KEEP_ALIVE=10m` |
| `OLLAMA_NUM_PARALLEL` | Number of parallel requests (default `1`). | `export OLLAMA_NUM_PARALLEL=2` |

### How to Use Environment Variables

Start Ollama with variables set:

```bash
export OLLAMA_KEEP_ALIVE=10m
ollama serve
```

Or, if running as a systemd service, edit the service file:

```bash
sudo systemctl edit ollama
```

Add:

```ini
[Service]
Environment="OLLAMA_KEEP_ALIVE=10m"
Environment="OLLAMA_NUM_PARALLEL=2"
```

Then restart: `sudo systemctl restart ollama`.

---

## 4. Project Environment (`.env`) for Makefile & Task Runner

Your project root should contain a `.env` file (see example below). This file is used by the `Makefile` and the task runner to locate directories and set defaults.

```bash
# .env – AI Assistant environment
OLLAMA_HOST=http://localhost:11434
OLLAMA_KEEP_ALIVE=5m
DEFAULT_MODEL=gemma3:4b
FAST_MODEL=llama3.2:1b

PROJECT_ROOT=$(pwd)
AI_DIR=ai
DOCS_AI_DIR=docs/ai
TASKS_DIR=$(DOCS_AI_DIR)/tasks
CHANGELOG_DIR=$(AI_DIR)/changelogs

WEBSITES=ctc-research lms-demo vresume
PRIORITY_PATTERNS=*.py */models.py */views.py */serializers.py
EXCLUDE_PATTERNS=*/migrations/* */__pycache__/* .git/* $(AI_DIR)/* $(DOCS_AI_DIR)/*/reports/*
```

**Note**: Do not commit secrets (like API keys) to this file if you use version control.

---

## 5. Task Prompts

Task prompt files are markdown documents (`.md`) placed in `docs/ai/tasks/`. Each file contains a system‑like instruction that the AI follows when you run `make task-run NAME=<task>`. The first line of the file becomes a short description in `make task-list`.

- `analyze_project.md` – full project analysis with N+1 and duplication detection
- `comprehensive_analysis.md` – phased analysis with package check and report generation
- `fix_n_plus_one.md`, `remove_duplications.md`, `refactor_context.md` – follow‑up fixes
- `uniform_docs.md` – standardise all markdown files
- `merge_styles.md`, `replace_pattern.md`, `refactor_design_pattern.md` – code transformations

Create your own by copying an existing task file and modifying the instructions.

---

## 6. Quick Setup Summary

1. **Install Ollama** and pull models:
   ```bash
   ollama pull gemma3:4b
   ollama pull llama3.2:1b
   ollama pull nomic-embed-text
   ```

2. **Configure Continue** – replace `~/.continue/config.json` with the full example above.

3. **Restart VS Code**.

4. **Copy the `.env` example** into your project root and adjust paths.

5. **Run `ai_customizer.py`** once to generate `ai/config.json`, then edit it to your liking.

6. **(Optional) Set environment variables** for persistent model loading.

All done – you now have a production‑ready, fully private AI assistant for Django.
