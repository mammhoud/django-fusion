# Guides — Setup & Quick Start

**Type:** Guide 📘
**Tags:** `#pos-mini` `#pos-solo` `#pos-full`
**Status:** Published
**Category:** Setup

---

## pos-mini Setup

```bash
cd projects/pos/pos-mini

# Install frontend deps
pnpm install

# Seed database
pnpm db:seed

# Dev (browser only — no Tauri APIs)
pnpm dev

# Dev (full desktop app)
pnpm dev:desktop

# TypeScript check
npx tsc --noEmit
```

## pos-solo Setup

```bash
cd projects/pos/pos-solo

# Frontend
pnpm install

# Sidecar (Python + uv)
cd sidecar
uv sync          # Install Python deps
uv run pytest    # Run tests

# Dev
cd ..
pnpm dev          # Frontend only
pnpm dev:desktop  # Full app + sidecar
```

## pos-full Setup

```bash
cd projects/pos/pos-full

# Same as pos-solo:
pnpm install
cd sidecar && uv sync
cd .. && pnpm dev:desktop
```

---

## Sidecar Quick Start (uv)

```bash
# Sidecar uses uv for Python dependency management
cd projects/pos/pos-{solo,full}/sidecar

uv sync                          # Install from pyproject.toml
uv run python3 server.py          # Start sidecar
uv run pytest                     # Run tests
uv add django                     # Add dependency
uv add --dev pytest               # Add dev dependency
```

### pyproject.toml Structure
```toml
[project]
name = "pos-sidecar"
dependencies = [
    "django>=5.1,<6",
    "robyn>=0.60,<1",
]
requires-python = ">=3.11"

[dependency-groups]
dev = ["pytest", "pytest-asyncio"]

[tool.uv]
dev-dependencies = ["pytest", "pytest-asyncio"]
```

---

## Environment Check

```bash
# Verify setup
python3 --version    # ≥ 3.11
uv --version         # uv package manager
node --version       # ≥ 18
pnpm --version       # ≥ 8
cargo --version      # Rust (Tauri builds)
```

---

## Related Docs
- → `guides/development.md` — Development workflow
- → `guides/deployment.md` — Deployment guides
- → `architecture/editions-overview.md` — Choose your edition
