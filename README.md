# ☁️ Structa Cloud

**Multi-product monorepo** — Django sites, desktop POS apps, AI services, and shared infrastructure on one Django + Wagtail + django-fusion foundation.

```text
                     ┌──────────────────────────────────┐
                     │         Traefik Proxy :443        │
                     │   (Let's Encrypt SSL, auto-cert)  │
                     └────┬──────┬──────┬──────┬────────┘
                          │      │      │      │
              ┌───────────┼──────┼──────┼──────┼───────────┐
              │           │      │      │      │           │
        CTC Research   Precis  Syntara  Loop-CRM  Media Server
          :5070        :5074    :5073    :80xx      :80
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
| **Web Apps** | Django + Wagtail + HTMX + django-fusion | Precis (LMS + landing), CTC Research, Loop-CRM |
| **AI Platform** | Ollama + MCP + CeptorAI | Syntara (AI chat/customizer) |
| **Desktop POS** | Tauri 2 + Rust + React 19 | Formint POS (Community / Standard / Pro / Cloud / Client) |
| **Infrastructure** | Docker + Traefik + Nginx | Proxy, Databases, Workers, Tools |
| **Documentation** | Docus (Nuxt Content) | `docs/` — EN + AR, `docs.structa.cloud` |

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

# Start infrastructure
make deploy-databases
make deploy-proxy

# Run a site
cd projects && make run-dev WEBSITE=precis-main
```

## 🏗️ Project Structure

```
structa.cloud/
├── projects/                  # Product code + shared Django config
│   ├── precis/                # Precis product group
│   │   ├── precis-main/       # Unified Precis (LMS + landing, canonical)
│   │   ├── precis-landing/    # Legacy Precis Landing copy (kept)
│   │   └── precis-ctc/        # CTC Research (ctc-research.com)
│   ├── syntara/               # Cypercloud AI chat/customizer runtime
│   ├── formints/              # POS editions (community/pro/cloud/standard/client)
│   ├── loop-crm/              # Sales + marketing CRM
│   ├── configs/               # Shared Django settings
│   └── Makefile               # Site dispatcher (WEBSITE=...)
├── libs/
│   └── django-fusion/         # Shared Django/Wagtail framework (submodule)
├── application/               # Infrastructure + tooling
│   ├── proxy/                 # Traefik SSL reverse proxy + Nginx shared-proxy
│   ├── databases/             # Postgres + Redis containers
│   ├── tools/                 # Self-hosted tools (affine, ollama, adminer, mailpit, monitoring)
│   └── scripts/               # Build + automation scripts
├── docs/                      # Full documentation site (Docus, EN + AR)
├── tests/                     # Workspace integration tests
└── Makefile                   # Root dispatcher + deploy cascade
```

## 🧩 Core Libraries

| Library | Description | Status |
|---------|-------------|--------|
| **[django-fusion](libs/django-fusion/)** | Component system, `{% comp %}` tag, declarative routing, forms/tables, auth, Wagtail blocks | ✅ Production |

## 🚢 Deployment

```bash
make deploy              # Full stack (DB → coder → media → apps → tasks → docs → proxy)
make deploy-databases    # Postgres + Redis
make deploy-app          # Django sites
make deploy-docs         # Docus documentation site
make deploy-proxy        # Traefik reverse proxy
make deploy-tools        # Self-hosted tools
make status              # Container health
```

The cascade is ordered `postgres-first` by default — see
[`docs/COMMANDS.md`](docs/COMMANDS.md) for the full delegation chain and the
unified `up`/`deploy`/`down` verb convention.

## 📚 Documentation

| Section | What You'll Find |
|---------|-----------------|
| [🏠 Docs home](docs/README.md) | Product table, quick links, Docus source note |
| [🗺️ Reference map](docs/REFERENCE.md) | Every docs dir/subdir → owning project → file contents |
| [🛠️ Commands](docs/COMMANDS.md) | Unified verbs, delegation chain, deploy cascade |
| [📖 Guides](docs/guides/) | Setup → Dev → Deploy → Customize → Clone |
| [🤖 AI & Agents](docs/ai/) | Agent instructions, prompts, MCP integration |
| [🚀 Startup strategy 🔒](docs/startup/README.md) | MVP canvas, TAM/SAM/SOM, ideal clients (private) |
| [🔄 Changelogs](CHANGELOG.md) | Full version history |

## 🔗 Links

- **Precis:** [structa.cloud](https://structa.cloud)
- **CTC Research:** [ctc-research.com](https://ctc-research.com)
- **Docs:** [docs.structa.cloud](https://docs.structa.cloud)
- **Tools:** [tools.structa.cloud](https://tools.structa.cloud)
- **Workspace:** [space.structa.cloud](https://space.structa.cloud)

## 📄 License

MIT — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ — [Structa Cloud Team](https://structa.cloud)*
