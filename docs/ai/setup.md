# Setup: Ollama + Continue

Follow these steps to install Ollama, pull a model, and configure Continue in VS Code.

## 1. Install Ollama

### macOS
```bash
brew install ollama
open /Applications/Ollama.app
```

### Windows
Download `OllamaSetup.exe` from [ollama.com/download](https://ollama.com/download).

### Ubuntu
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl start ollama
```

## 2. Pull Models

```bash
ollama pull gemma3:4b      # main model
ollama pull llama3.2:1b    # fast autocomplete
```

## 3. Install Continue in VS Code

- Extensions → search "Continue" → Install.

## 4. Configure Continue

Edit `~/.continue/config.json`:

```json
{
  "models": [{
    "title": "Gemma 3 4B",
    "provider": "ollama",
    "model": "gemma3:4b",
    "apiBase": "http://localhost:11434"
  }],
  "tabAutocompleteModel": {
    "title": "Llama 3.2 1B",
    "provider": "ollama",
    "model": "llama3.2:1b",
    "apiBase": "http://localhost:11434"
  },
  "allowAnonymousTelemetry": false
}
```

## 5. Install the AI Customizer

Place `ai_customizer.py` (provided separately) in your project root and make it executable:

```bash
chmod +x ai_customizer.py
```

Then run `./ai_customizer.py chat` to start.

For task automation, see [make_commands.md](make_commands.md).
