# AI Customizer Script

The `ai_customizer.py` script gives you **full control** over your local AI assistant from the terminal. It allows:

- Priority‑based file search (`@search keyword`)
- Inject documentation as context (`@docs`)
- Log every conversation and task as snake_case markdown changelogs
- Custom model parameters (temperature, context size, system prompt)

## 1. Save the Script

Create a file named `ai_customizer.py` in your **project root** with the content below (copy the full script from the end of this document).

## 2. Make it Executable (macOS/Linux)

```bash
chmod +x ai_customizer.py
```

## 3. Run Interactive Chat

```bash
./ai_customizer.py
```

### Commands inside the chat

| Command | Action |
|---------|--------|
| `@docs` | Loads your entire `docs/` folder as context for the next question. |
| `@search keyword` | Finds files containing `keyword`, lets you select one, and loads its content into context. |
| `save` | Saves the current conversation to `ai/changelogs/chat_YYYYMMDD_HHMMSS_slug.md`. |
| `exit` | Quits. |

### Example

```text
You: @docs What are Django signal best practices?
AI: (answers using your documentation)

You: @search get_absolute_url
🔍 Found 2 files...
Enter number: 1
Loaded blog/models.py into context.

You: Explain the get_absolute_url method.
AI: (explains your actual code)

You: save
Conversation saved to ai/changelogs/chat_20260613_152030_get_absolute_url.md
```

## 4. Single Task Mode

```bash
./scripts/ai_customizer.py --task "write a Django model for a shopping cart" --priority --with-docs
```

- `--priority` – interactively select files based on priority patterns.
- `--with-docs` – include documentation as context.

The response is printed and also saved to `ai/changelogs/task_...md`.

Now you have a powerful terminal‑based AI assistant that respects your project structure and logs everything.
