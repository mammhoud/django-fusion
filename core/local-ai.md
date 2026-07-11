# Local AI Coding Assistant – macOS / Windows / Ubuntu

This guide will help you set up a **private, offline AI coding assistant** optimized for Python and Django development. You will run a small but capable model (default `Qwen3:4B`, or upgrade to `Gemma 3 4B` for better reasoning) using **Ollama** and integrate it into **VS Code** via the **Continue** extension. The model uses ~2.5–3 GB of RAM, leaving plenty for your OS, editor, and Django server.

> ✅ Works on **macOS** (Intel & Apple Silicon), **Windows 10/11**, and **Ubuntu 20.04+**.

---

## 📋 Prerequisites

- **VS Code** – Download from [code.visualstudio.com](https://code.visualstudio.com)
- **Terminal** (Command Prompt / PowerShell on Windows) – you’ll use it to install and run Ollama
- **Stable internet** – to download the model (~2.5–3 GB)

---

## 🐙 Step 1: Install Ollama (by OS)

Ollama is the tool that downloads, runs, and manages local AI models.

### 🍎 macOS (Intel & Apple Silicon)

**Option A – Homebrew (recommended)**
```bash
brew install ollama
```

**Option B – Direct download**  
Go to [ollama.com/download](https://ollama.com/download) → click **macOS** → open the `.dmg` and drag Ollama to Applications.

Then launch Ollama:
```bash
open /Applications/Ollama.app
```

### 🪟 Windows

**Option A – Official installer**  
Download `OllamaSetup.exe` from [ollama.com/download](https://ollama.com/download) and run it.

**Option B – winget** (Windows Package Manager)
```powershell
winget install Ollama.Ollama
```

After installation, launch **Ollama** from the Start menu. You’ll see an icon in the system tray.

### 🐧 Ubuntu (20.04+)

Use the automatic install script:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Alternatively, download the `.deb` package from [ollama.com/download](https://ollama.com/download/linux) and install with:
```bash
sudo dpkg -i ollama*.deb
```

Start the Ollama service:
```bash
sudo systemctl start ollama
```

---

### ✅ Verify Ollama is running (all OS)

Open a **new terminal** and run:
```bash
curl http://localhost:11434
```
Expected output: `Ollama is running`

---

## 🧠 Step 2: Download Your Model (choose one)

We provide two excellent options that fit your 8GB RAM. **Start with Qwen3:4B**, then try Gemma 3 4B for better reasoning and Django logic.

### 🔹 Default model (recommended for first try)
**Qwen3:4B** – balanced, fast, great for general coding.
```bash
ollama pull qwen3:4b
```

### 🔸 Upgrade model (better reasoning & multilingual)
**Gemma 3 4B** – Google's lightweight powerhouse. Excels at understanding complex Django queries and refactoring logic.
```bash
ollama pull gemma3:4b
```

Verify your installed models:
```bash
ollama list
```
You should see the model(s) you pulled.

---

## 💻 Step 3: Install Continue Extension in VS Code

1. Open **VS Code**
2. Go to **Extensions** (`Ctrl+Shift+X` on Windows/Linux, `Cmd+Shift+X` on macOS)
3. Search for **"Continue"** – install the one by *Continue Dev Team*
4. After installation, a new chat icon (two speech bubbles) appears in the left sidebar

---

## ⚙️ Step 4: Configure Continue for Your Model

1. Click the Continue icon in the VS Code sidebar
2. Choose **"Connect your own model"** (or click the gear icon to open `config.json`)
3. Replace the file contents with the configuration for your chosen model.

### 🔧 Config for **Qwen3:4B** (chat + autocomplete)

```json
{
  "models": [
    {
      "title": "Qwen3:4B (Chat)",
      "provider": "ollama",
      "model": "qwen3:4b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Qwen3:4B (Autocomplete)",
    "provider": "ollama",
    "model": "qwen3:4b",
    "apiBase": "http://localhost:11434"
  },
  "allowAnonymousTelemetry": false
}
```

### 🔧 Config for **Gemma 3 4B** (chat + autocomplete)

```json
{
  "models": [
    {
      "title": "Gemma 3 4B (Chat)",
      "provider": "ollama",
      "model": "gemma3:4b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Gemma 3 4B (Autocomplete)",
    "provider": "ollama",
    "model": "gemma3:4b",
    "apiBase": "http://localhost:11434"
  },
  "allowAnonymousTelemetry": false
}
```

> 🚀 **Performance tip** – For a snappier experience on low‑RAM machines, use a tiny 1B model for autocomplete (see the “Faster config” later). This works with either Qwen or Gemma.

4. Save the file and **restart VS Code**.

---

## 🧪 Step 5: Test in a Django Project

Open any Django project (or create a new one).

- **Open Continue chat** – Click the Continue icon or press `Ctrl+Shift+L` (Windows/Linux) / `Cmd+Shift+L` (macOS)
- **Ask a question** – e.g., *"Write a Django model for a blog post with title, content, and created_at"*
- **Try inline autocomplete** – Start typing Python/Django code and press `Tab` to accept gray suggestions.

> 💡 Use `@` in the chat to give context:  
> `@models.py` – attach a file  
> `@terminal` – include terminal output  
> `@codebase` – index your whole project

---

## 📊 Model Comparison: Which is Better for Django & 8GB RAM?

The table below compares the top models that run comfortably on your Mac Mini. **Gemma 3 4B** often outperforms Qwen3:4B in reasoning-heavy tasks (like optimizing Django queries or debugging complex views), while Qwen3:4B is slightly faster for simple code completion.

| Model | RAM Usage (quantized) | Coding Ability | Reasoning (Django logic) | Speed | Best for |
|-------|----------------------|----------------|--------------------------|-------|-----------|
| **Gemma 3 4B** | ~2.8 GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Complex refactoring, query optimization, multilingual docstrings |
| **Qwen3:4B** | ~2.5 GB | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Fast autocomplete, boilerplate generation, everyday coding |
| **Qwen2.5-Coder 7B** | ~4.7 GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Maximum code quality (fits, but less headroom) |
| **Phi-4-mini (3.8B)** | ~2.3 GB | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Math, logic, and structured data tasks |
| **Llama 3.2 1B** (autocomplete only) | ~0.8 GB | ⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | Lightning-fast suggestions, best paired with a larger chat model |

**Recommendation for Django:**  
- **Start with Gemma 3 4B** – its superior reasoning helps with Django’s ORM, class-based views, and debugging.  
- If you notice slowdowns, switch to Qwen3:4B or use the “Faster config” (1B for autocomplete) with Gemma for chat only.

---

## 🎯 Advanced: Direct Django Integration (all OS)

Call the model from your Django code (views, commands, etc.).

1. Install the Python client:
   ```bash
   pip install ollama
   ```

2. Use it in a Django shell or view (change model name as needed):
   ```python
   import ollama

   response = ollama.chat(
       model='gemma3:4b',  # or 'qwen3:4b'
       messages=[{'role': 'user', 'content': 'Explain Django’s MVT pattern in one paragraph.'}]
   )
   print(response['message']['content'])
   ```

3. Analyse your own code:
   ```python
   with open('myapp/models.py', 'r') as f:
       code = f.read()
   response = ollama.chat(
       model='gemma3:4b',
       messages=[{'role': 'user', 'content': f'Suggest improvements for this Django model:\n\n{code}'}]
   )
   ```

---

## 🧠 Memory Management & Performance Tips

| Action | Why |
|--------|------|
| **Close heavy apps** (Chrome, Docker, Slack) | Frees RAM for the model |
| **Limit the context window** in `config.json` | Less memory per request |
| **Use a smaller autocomplete model** | Faster, less resource‑hungry |

### 🔻 Reduce context window (if you run out of memory)

Add an `"options"` block to the model in `config.json`:

```json
"models": [
  {
    "title": "Gemma 3 4B",
    "provider": "ollama",
    "model": "gemma3:4b",
    "apiBase": "http://localhost:11434",
    "options": {
      "num_ctx": 2048
    }
  }
]
```

Default is 8192. Lower values (e.g., 2048 or 1024) use less RAM but shorten the model’s “memory”.

### ⚡ Faster config: Use a 1B model for autocomplete (with any chat model)

First, pull a tiny model:
```bash
ollama pull llama3.2:1b
```

Then replace `config.json` with (example using Gemma for chat, tiny for autocomplete):

```json
{
  "models": [
    {
      "title": "Gemma 3 4B (Chat)",
      "provider": "ollama",
      "model": "gemma3:4b",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Llama 3.2 1B (Fast)",
    "provider": "ollama",
    "model": "llama3.2:1b",
    "apiBase": "http://localhost:11434"
  },
  "allowAnonymousTelemetry": false
}
```

---

## 🧩 Other Alternative Models (all <4 GB after quantization)

| Model | Pull command | Best for |
|-------|--------------|----------|
| **Phi-4-mini (3.8B)** | `ollama pull phi4-mini` | Math, reasoning, logic |
| **DeepSeek-R1-Distill-Qwen-1.5B** | `ollama pull deepseek-r1:1.5b` | Step‑by‑step reasoning |
| **Mistral 7B (q4)** | `ollama pull mistral` | General coding (slightly heavier) |
| **Qwen2.5-Coder 7B** | `ollama pull qwen2.5-coder:7b` | Best pure code generation (needs ~4.7 GB) |

To switch a model in Continue, change the `"model"` value in `config.json`.

---

## 🛠️ Troubleshooting (all OS)

| Problem | Solution |
|---------|----------|
| **Ollama not found** | Make sure Ollama is running. On Windows, check the system tray. On Ubuntu: `sudo systemctl status ollama`. |
| **Continue cannot connect** | Verify Ollama is running (`curl http://localhost:11434`). Restart Ollama. |
| **Slow autocomplete** | Use the “Faster config” with a 1B model for autocomplete. |
| **VS Code freezes / memory error** | Reduce context window (`num_ctx: 1024`). Close other apps. Restart VS Code. |
| **Model responses are garbled** | Remove and re‑pull the model: `ollama rm gemma3:4b ; ollama pull gemma3:4b` |
| **Django server slows down** | Stop the model while not in use (quit Ollama). Restart when needed. |

### 🔧 Windows‑specific notes
- Use **PowerShell** (not CMD) for the best experience.
- If `curl` is not available, test Ollama by opening `http://localhost:11434` in your browser – you should see `Ollama is running`.

### 🐧 Ubuntu‑specific notes
- After installing Ollama, you may need to add your user to the `ollama` group:
  ```bash
  sudo usermod -aG ollama $USER
  ```
  Then log out and back in.
- The Ollama service runs in the background. Use `sudo systemctl restart ollama` if needed.

---

## ✅ Final Checklist

- [ ] Ollama installed and running (check with `curl http://localhost:11434`)
- [ ] Model pulled (`ollama list` shows `gemma3:4b` or `qwen3:4b`)
- [ ] Continue extension installed in VS Code
- [ ] `config.json` updated with your chosen model
- [ ] VS Code restarted
- [ ] Chat works (`Ctrl+Shift+L` / `Cmd+Shift+L`)
- [ ] Autocomplete works (type a few characters in a `.py` file)

You now have a fully private AI assistant for Django that never sends your code to the cloud – on **macOS, Windows, or Ubuntu**. Happy coding!

---

*Guide last updated: June 2026*  
*Tested on: macOS Intel/Apple Silicon, Windows 11, Ubuntu 22.04*
