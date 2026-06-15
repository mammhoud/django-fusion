# Interactive Tasks with Prompt Files

You can feed a custom prompt file (e.g., `project_analysis_prompt.txt`) to your local Ollama model and then have an **interactive conversation** where the AI follows that prompt as a persistent instruction. This is useful for:

- Project analysis (e.g., checking alignment with Ollama best practices)
- Code review with specific guidelines
- Generating documentation from a template
- Role‑playing a specific expert (Django security, Docker optimisation, etc.)

---

## Method 1: Using `ai_customizer.py` (Recommended)

Your `ai_customizer.py` script supports a persistent `system_prompt` defined in `ai/config.json`. To load a prompt file:

### Step‑by‑step

1. **Place your prompt file** somewhere in your project, e.g.:
   ```
   docs/ai/prompts/project_analysis_prompt.txt
   ```

2. **Edit `ai/config.json`** in your project root and set the `system_prompt` field to the full content of the prompt file.

   You can do this manually (copy‑paste) or use a small script:

   ```bash
   #!/bin/bash
   # set-prompt.sh
   PROMPT=$(cat docs/ai/prompts/project_analysis_prompt.txt)
   jq --arg sp "$PROMPT" '.system_prompt = $sp' ai/config.json > ai/config.tmp && mv ai/config.tmp ai/config.json
   ```

3. **Run interactive chat**:
   ```bash
   ./ai_customizer.py
   ```

   Now every question you ask will be answered according to the loaded prompt.

4. **To switch between different prompts**, keep multiple prompt files and re‑run the script before starting `ai_customizer.py`.

### Example: Analysing a Project

Assume you have a prompt file `project_analysis_prompt.txt` that instructs the AI to act as an expert in Ollama best practices. After setting it as the `system_prompt`, you can:

```text
You: Here is my project tree:
.
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── myapp/
    ├── models.py
    └── views.py

What improvements would you suggest based on Ollama's documentation?
```

The AI will respond with a structured report as defined in your prompt.

---

## Method 2: Using Continue’s `systemMessage` (VS Code)

If you prefer to work inside VS Code’s Continue chat, you can add the prompt as a `systemMessage` in your `~/.continue/config.json`.

### Steps

1. **Read your prompt file** and escape it for JSON (or copy‑paste directly).

2. **Add a new model entry**:

   ```json
   {
     "models": [
       {
         "title": "Project Analyzer (Gemma)",
         "provider": "ollama",
         "model": "gemma3:4b",
         "apiBase": "http://localhost:11434",
         "systemMessage": "You are an expert AI assistant... (paste the full prompt here)"
       }
     ],
     "tabAutocompleteModel": { ... }
   }
   ```

3. **Restart VS Code**, open Continue, select “Project Analyzer” from the model dropdown, and start chatting. The AI will follow the prompt for the whole conversation.

> 💡 This method keeps your global `ai/config.json` unchanged – useful if you also use `ai_customizer.py` for other tasks.

---

## Method 3: Direct `ollama run` with Pre‑loaded Prompt (One‑off)

For a quick, non‑persistent session, you can pipe the prompt file into `ollama run` and then continue interactively.

### Example (Linux/macOS)

```bash
# Start with the prompt as the first message
cat project_analysis_prompt.txt | ollama run gemma3:4b --interactive
```

The `--interactive` flag keeps the session open so you can ask follow‑up questions. However, the prompt will **not** be re‑sent automatically; you may need to repeat it or rely on the model’s memory (limited by context window).

---

## Best Practices

- **Keep prompts concise but specific** – 500–2000 words is ideal.
- **Store prompts in `docs/ai/prompts/`** for version control.
- **Use the `ai/config.json` method** for daily work – it’s the most reliable.
- **Combine with `@docs` and `@search`** in `ai_customizer.py` to provide real project files as context.

## Related Documentation

- [Configuration Reference](config.md) – for editing `ai/config.json` and Continue settings.
- [AI Customizer Script](customizer.md) – full reference for the interactive CLI.
- [Troubleshooting](troubleshooting.md) – if the model doesn’t behave as expected.

---

Now you can turn any task prompt into a persistent, interactive AI assistant – completely local and private.
