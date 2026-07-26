---
Object type: Workspace
Tags: install, setup---

# Install — Platform Setup Guides

> Platform-specific installation guides for every operating system and deployment method.

---

## Contents

| Guide | Platform | Package Manager | Best For |
|-------|----------|----------------|----------|
| `macos.md` | macOS | Homebrew | Development, Testing |
| `linux.md` | Linux | apt/dnf/pacman | Production, Development |
| `windows.md` | Windows | winget/choco | Development, Testing |
| `docker.md` | Docker | Docker Compose | Production, Deployment |

---

## Prerequisites

Before starting, ensure your system meets these minimum requirements:

| Requirement | Version |
|-------------|---------|
| Python | ≥ 3.11 |
| Node.js | ≥ 18 |
| pnpm | ≥ 8 |
| Rust (for Tauri) | ≥ 1.70 |
| uv (for sidecar) | ≥ 0.4 |

---

## Quick Start

Once your platform is set up:

```bash
cd projects/pos/pos-solo
pnpm install
pnpm dev            # Browser dev mode
pnpm dev:desktop    # Full desktop app
```

---

## Related

- → `../setup.md` — Quick start guide
- → `../configuration.md` — System configuration
- → `../../objects/configuration.md` — Configuration object type
- → `../../README.md` — Master index
