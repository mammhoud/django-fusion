---
# yaml-language-server: $schema=../../schemas/page.schema.json
Object type: Guide
Tags: install, pos-mini, pos-solo, pos-full
Status: Published
Platform: Linux
---

# Linux Installation Guide

> Comprehensive setup guide for Linux development environment (Ubuntu/Debian, Fedora, Arch).

---

## Prerequisites

Select your distribution below.

### Ubuntu / Debian

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
    build-essential \
    curl \
    wget \
    git \
    pkg-config \
    libssl-dev \
    libwebkit2gtk-4.1-dev \
    libgtk-3-dev \
    libayatana-appindicator3-dev \
    librsvg2-dev \
    python3 \
    python3-pip \
    python3-venv
```

### Fedora

```bash
sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y \
    curl \
    wget \
    git \
    pkg-config \
    openssl-devel \
    webkit2gtk4.1-devel \
    gtk3-devel \
    libappindicator-gtk3-devel \
    librsvg2-devel \
    python3 \
    python3-pip \
    python3-venv
```

### Arch Linux

```bash
sudo pacman -Syu
sudo pacman -S --needed \
    base-devel \
    curl \
    wget \
    git \
    pkg-config \
    openssl \
    webkit2gtk-4.1 \
    gtk3 \
    libappindicator-gtk3 \
    librsvg \
    python \
    python-pip
```

---

## Step 1: Install Package Managers

```bash
# Node.js via nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm use --lts

# Verify
node --version   # ≥ 18
npm --version

# pnpm
npm install -g pnpm
pnpm --version   # ≥ 8

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv --version     # ≥ 0.4
```

---

## Step 2: Install Rust (for Tauri builds)

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
rustc --version   # ≥ 1.70
```

---

## Step 3: Clone & Setup Repository

```bash
git clone https://github.com/mammhoud/structa.cloud.git
cd structa.cloud

# Python virtual env
python3 -m venv .venv
source .venv/bin/activate
pip install uv

# Install POS deps
cd projects/pos/pos-solo
pnpm install
cd sidecar && uv sync
```

---

## Step 4: Verify

```bash
cd sidecar && uv run pytest
cd .. && pnpm vitest run
pnpm dev            # Browser mode
pnpm dev:desktop    # Desktop mode
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `webkit2gtk-4.1 not found` | Ensure you installed the correct package for your distro |
| `openssl-sys build failed` | Install `libssl-dev` (Ubuntu) or `openssl-devel` (Fedora) |
| `nvm: command not found` | Add `source ~/.nvm/nvm.sh` to `~/.bashrc` |
| `Permission denied` | Use `sudo` for system package installs only |

---

## Related

- → `macos.md` — macOS setup guide
- → `windows.md` — Windows setup guide
- → `docker.md` — Docker setup guide
- → `../configuration.md` — System configuration
- → `../../objects/configuration.md` — Configuration object type
- → `../../README.md` — Master index
