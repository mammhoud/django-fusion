# Troubleshooting

| Problem | Solution |
|---------|----------|
| **Ollama not found** | Ensure Ollama is running. On Windows, check system tray. On Ubuntu: `sudo systemctl status ollama`. |
| **Continue cannot connect** | `curl http://localhost:11434` – if fails, restart Ollama. Also check firewall. |
| **Slow autocomplete** | Use a 1B model for autocomplete (`llama3.2:1b`). Reduce context window to 2048. |
| **VS Code freezes / memory error** | Reduce `num_ctx` to 1024. Close other applications. Restart VS Code. |
| **Model responses are garbled** | Remove and re‑pull: `ollama rm gemma3:4b ; ollama pull gemma3:4b` |
| **Django server slows down** | Stop the model when not in use (quit Ollama). Restart when needed. |
| **`ai_customizer.py` says “ollama: command not found”** | Ollama must be in PATH. On macOS/Linux, restart terminal. On Windows, add `C:\Program Files\Ollama` to PATH. |
| **`@docs` loads nothing** | Ensure you have a `docs/` folder with `.md` files. The script looks for `docs/` relative to current working directory. |

## Windows Specific

- Use **PowerShell** instead of CMD.
- If `curl` is missing, test Ollama by opening `http://localhost:11434` in a browser.
- To run Python scripts: `python ai_customizer.py` (if `.py` not associated).

## Ubuntu Specific

- Add your user to the `ollama` group: `sudo usermod -aG ollama $USER` then log out/in.
- Restart service: `sudo systemctl restart ollama`
- Check logs: `journalctl -u ollama -f`
