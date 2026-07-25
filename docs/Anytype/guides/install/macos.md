---
# yaml-language-server: $schema=../../schemas/page.schema.json
Object type: Guide
Tags: install, pos-mini, pos-solo, pos-full
Status: Published
Platform: macOS
---

# macOS Installation Guide

> Comprehensive setup guide for macOS development environment.

---

## Prerequisites

```bash
# Check macOS version (requires macOS 13+ Ventura or newer)
sw_vers

# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install python@3.12
brew install node
brew install rustup-init
```

---

## Step 1: Install Package Managers

```bash
# Node.js via nvm (recommended for version management)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.zshrc
nvm install --lts
nvm use --lts

# Verify
node --version   # ≥ 18
npm --version

# pnpm (fast, disk-efficient package manager)
npm install -g pnpm
pnpm --version   # ≥ 8

# uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc
uv --version     # ≥ 0.4
```

---

## Step 2: Install Rust (for Tauri builds)

```bash
# Install Rust via rustup
rustup-init
# Select option 1 (default installation)

# Verify
rustc --version   # ≥ 1.70
cargo --version

# Add macOS target for Tauri
rustup target add aarch64-apple-darwin  # Apple Silicon
rustup target add x86_64-apple-darwin   # Intel
```

---

## Step 3: Install System Dependencies

```bash
# Tauri system dependencies (macOS)
# Most are bundled with Xcode Command Line Tools
xcode-select --install

# WebKit2GTK (not needed on macOS — uses native WebView)
# GLib and Cairo (bundled with macOS)
```

---

## Step 4: Clone & Setup Repository

```bash
# Clone the monorepo
git clone https://github.com/mammhoud/structa.cloud.git
cd structa.cloud

# Set up Python virtual environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install uv

# Install POS dependencies
cd projects/pos/pos-solo
pnpm install

# Set up sidecar
cd sidecar
uv sync
```

---

## Step 5: Verify Installation

```bash
# Run all verification checks
python3 --version   # ≥ 3.11
uv --version        # ≥ 0.4
node --version      # ≥ 18
pnpm --version      # ≥ 8
cargo --version     # ≥ 1.70

# Run tests
cd sidecar && uv run pytest
cd .. && pnpm vitest run
```

---

## Step 6: Run Development Server

```bash
# Browser mode (no Tauri APIs)
pnpm dev

# Desktop mode (full Tauri app)
pnpm dev:desktop
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `xcode-select: error: command line tools are already installed` | Run `sudo rm -rf /Library/Developer/CommandLineTools` then retry |
| `nvm: command not found` | Add `source ~/.nvm/nvm.sh` to `~/.zshrc` and restart terminal |
| `cargo: command not found` | Run `source ~/.cargo/env` |
| `uv: command not found` | Add `export PATH="$HOME/.local/bin:$PATH"` to `~/.zshrc` |

---

## Related

- → `linux.md` — Linux setup guide
- → `windows.md` — Windows setup guide
- → `docker.md` — Docker setup guide
- → `../configuration.md` — System configuration
- → `../../objects/configuration.md` — Configuration object type
- → `../../README.md` — Master index
