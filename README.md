# ☁️ Structa Cloud

**Multi-product monorepo** — Django sites, desktop POS apps, AI services, and shared infrastructure.

```text
                     ┌──────────────────────────────────┐
                     │         Traefik Proxy :443        │
                     │   (Let's Encrypt SSL, auto-cert)  │
                     └────┬──────┬──────┬──────┬────────┘
                          │      │      │      │
              ┌───────────┼──────┼──────┼──────┼───────────┐
              │           │      │      │      │           │
        CTC Research    LMS  Portfolio  Cypercloud  Media Server
          :5070        :5071    :5072     :5073       :80
              │           │      │      │      │           │
              └───────────┴──────┴──────┴──────┴───────────┘
                                 │
                       ┌─────────┴─────────┐
                       │                   │
                 PostgreSQL 16        Redis (broker)
                 (per-site DBs)     (shared-worker queue)
```

## 🎯 What's Inside

| Layer | Technology | Projects |
|-------|-----------|----------|
| **Web Apps** | Django 5.1 + Wagtail + HTMX | LMS, Portfolio, Cypercloud, CTC Research |
| **Desktop POS** | Tauri 2 + Rust + React 19 | POS (Minimal / Solo / Full) |
| **AI Platform** | Ollama + MCP + CeptorAI | Cypercloud Chat, AI Agents |
| **Infrastructure** | Docker + Traefik + Nginx | Proxy, Databases, Workers |

## 📦 Quick Start

```bash
# Clone & init submodules
git clone https://github.com/mammhoud/structa.cloud.git
cd structa.cloud
git submodule update --init --recursive

# Install Python deps
uv sync

# Install local libs
uv pip install -e libs/django-fusion/
uv pip install -e libs/ceptor-ai/

# Start infra
make deploy-databases
make deploy-proxy

# Run a site
cd projects && make dev WEBSITE=lms
```

## 🏗️ Project Structure

```
structa.cloud/
├── projects/              # Django sites + desktop apps
│   ├── configs/           # Shared Django settings
│   ├── assets/            # Shared templates, static, locale
│   ├── www/               # Shared core code + workers
│   ├── lms/               # LMS Demo (structa.cloud)
│   ├── portfolio/         # Portfolio/VResume (vresume.structa.cloud)
│   ├── cypercloud/        # AI Chat Platform
│   ├── ctc-research/      # CTC Research (ctc-research.com)
│   └── pos/               # Desktop POS (Tauri 2 + Rust)
├── libs/                  # Reusable Python packages (submodules)
│   ├── django-fusion/     # Component system + routing framework
│   └── ceptor-ai/         # AI chat + MCP integration toolkit
├── applications/          # Infrastructure + tooling
│   ├── proxy/             # Traefik SSL reverse proxy
│   ├── databases/         # Postgres + Redis containers
│   ├── compose/           # Docker Compose orchestration
│   └── scripts/           # Build + automation scripts
├── docs/                  # Full documentation site
├── tests/                 # Workspace integration tests
└── Makefile               # Root dispatcher
```

## 🧩 Core Libraries

| Library | Description | Status |
|---------|-------------|--------|
| **[django-fusion](libs/django-fusion/)** | Component system, `{% comp %}` tag, declarative routing, forms/tables, auth, Wagtail blocks | ✅ Production |
| **[ceptor-ai](libs/ceptor-ai/)** | AI chat client, MCP server, BEM converter, agent generation | ✅ Beta |

## 🚢 Deployment

```bash
make deploy              # Full stack (DB → media → apps → proxy)
make deploy-databases    # Postgres + Redis
make deploy-app          # Django sites
make deploy-proxy        # Traefik reverse proxy
make status              # Container health
```

## 📚 Documentation

| Section | What You'll Find |
|---------|-----------------|
| [📖 Guides](docs/guides/) | Setup → Dev → Deploy → Customize → Clone |
| [🏢 Projects](docs/projects/) | Per-project docs: features, config, infra, DB |
| [🏗️ Infrastructure](docs/infrastructure/) | Proxy, Docker, deployment, workers |
| [🤖 AI & Agents](docs/ai/) | Agent instructions, prompts, MCP integration |
| [🔄 Changelogs](CHANGELOG.md) | Full version history |

## 🛠️ Key Commands

```bash
make dev          # Run dev server
make check        # Django system checks
make test         # Run tests
make push         # Push repo + submodules
make deploy       # Full deployment
make status       # Container status
```

## 🔗 Links

- **LMS:** [structa.cloud](https://structa.cloud)
- **Portfolio:** [vresume.structa.cloud](https://vresume.structa.cloud)
- **CTC Research:** [ctc-research.com](https://ctc-research.com)
- **Docs:** [docs.structa.cloud](https://docs.structa.cloud)

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ — [Structa Cloud Team](https://structa.cloud)*
