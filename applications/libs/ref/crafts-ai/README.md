<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/cover.png">
  <img src="assets/cover.png" alt="nawaai Cover" width="100%">
</picture>

# 🐍 nawaai

<p align="center">
  <em>Pure Python AI/MCP Toolkit — ai, chat, mcp, orchestrator, seeder</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/nawaai/">
    <img src="https://img.shields.io/pypi/v/nawaai?style=flat-square&logo=pypi&logoColor=white&label=PyPI" alt="PyPI version">
  </a>
  <a href="https://python.org">
    <img src="https://img.shields.io/pypi/pyversions/nawaai?style=flat-square&logo=python&logoColor=white" alt="Python versions">
  </a>
  <a href="https://github.com/astral-sh/uv">
    <img src="https://img.shields.io/badge/uv-package%20manager-de3d8b?style=flat-square&logo=uv&logoColor=white" alt="uv">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square" alt="Code style: black">
  </a>
</p>

---

## ✨ Features

- 🤖 **AI Integrations** – OpenAI, Claude, and more
- 💬 **Chat Clients** – REST and Rasa integrations
- 🔌 **MCP Server** – Model Context Protocol support
- 📋 **Spec Orchestrator** – Task execution engine
- 🔒 **Zero Django** – Pure Python, no Django dependencies
- 📦 **`uv`‑ready** – Lightning-fast dependency management

---

## 📦 Installation

```bash
# Install with uv (recommended)
uv add nawaai

# Or with pip
pip install nawaai
```

Optional dependencies:

```bash
uv add "nawaai[openai,anthropic]" --dev
uv add "nawaai[faker]" --dev
uv add "nawaai[mcp]" --dev
uv add "nawaai[all]" --dev
```

---

## 🏁 Quickstart

```python
# AI integrations
from crafts_ai.ai.integrations import OpenAIIntegration

ai = OpenAIIntegration(api_key="...")
response = ai.generate("Summarize this text: ...")

# Chat client
from crafts_ai.chat.client import CraftsClient, ChatBubble

client = CraftsClient(base_url="http://localhost:8765")
bubble = ChatBubble(client=client)
reply = bubble.send("Hello, how are you?", session_id="user123")

# Spec orchestrator CLI
# craftsai scan
# craftsai list
# craftsai execute --task-id 1
```

---

## 📖 Documentation

- [Getting Started](docs/getting-started/)
- [API Reference](docs/api/)
- [CLI Commands](docs/cli/)

---

## 🧪 Development Setup (with `uv`)

```bash
# Install the package
uv add nawaai

# Or with pip
pip install nawaai

# Install with all extras for development
uv add "nawaai[all]" --dev

# Run tests
uv run pytest

# Run linting and formatting
uv run ruff check .
uv run ruff format .
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## 🛠️ Built With

A heartfelt thank you to the tools and AI assistants that made developing this package a joy.

<p align="center">
  <a href="https://kiro.dev" title="Kiro – AI-powered dev environment">
    <img src="https://img.shields.io/badge/Kiro-AI%20Dev%20Environment-6C63FF?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyTDIgN2wxMCA1IDEwLTV6TTIgMTdsOCA0IDgtNE0yIDEybDggNCA4LTQiLz48L3N2Zz4=" alt="Kiro">
  </a>
  &nbsp;
  <a href="https://claude.ai" title="Claude by Anthropic">
    <img src="https://img.shields.io/badge/Claude-Anthropic%20AI-D97757?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude">
  </a>
  &nbsp;
  <a href="https://aws.amazon.com" title="Amazon Web Services">
    <img src="https://img.shields.io/badge/AWS-Amazon%20Web%20Services-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white" alt="AWS">
  </a>
  &nbsp;
  <a href="https://www.hostinger.com" title="Hostinger – Web Hosting">
    <img src="https://img.shields.io/badge/Hostinger-Web%20Hosting-673DE6?style=for-the-badge&logo=hostinger&logoColor=white" alt="Hostinger">
  </a>
</p>

---

## 🙌 Acknowledgements

- Built with ❤️ and [`uv`](https://docs.astral.sh/uv/)
- Badges from [Shields.io](https://shields.io)
- AI powered by [OpenAI](https://openai.com/) and [Anthropic](https://anthropic.com/)

---

## ☕ Support

If you find this project helpful, consider buying me a coffee!

<a href="https://buymeacoffee.com/mammhoud" target="_blank">
  <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" height="50">
</a>
