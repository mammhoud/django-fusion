---
Object type: Guide
Tags: install, setup
Status: Published
Platform: Linux
---

# Linux Setup Guide

> Description-oriented setup guide for the Linux development environment (Ubuntu/Debian, Fedora, Arch). Tasks are described by action and outcome; exact commands live in the repository docs.

## Prerequisites

| Tool | Minimum Version | Purpose |
|------|-----------------|---------|
| Python | 3.11+ | Backend and sidecar |
| Node.js | 18+ | Frontend tooling |
| pnpm | 8+ | Package manager |
| Rust | 1.70+ | Tauri desktop builds |
| uv | 0.4+ | Python package management |

## Setup steps by distribution

| Distribution | System Packages | Notes |
|--------------|-----------------|-------|
| Ubuntu / Debian | Build essentials, curl, wget, git, SSL headers, webkit2gtk, GTK3, python tooling | Standard development toolchain |
| Fedora | Development Tools group, curl, git, SSL, webkit, GTK3, python | Equivalent tools via dnf |
| Arch Linux | base-devel, curl, git, SSL, webkit2gtk, GTK3, python | Equivalent tools via pacman |

## Setup steps

1. **Install system packages** — install the required build, SSL, webkit, GTK, and Python packages for your distribution.
2. **Install package managers** — set up Node via nvm, then install pnpm and uv. Verify each with its version check.
3. **Install Rust** — via rustup with the default profile for Tauri builds.
4. **Clone and set up the repository** — clone the monorepo, create a Python virtual environment, install POS dependencies with pnpm, and set up the sidecar with uv.
5. **Verify installation** — confirm each tool version and run the test suites to validate the environment.
6. **Run the development server** — choose browser mode or desktop mode.

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| webkit2gtk not found | Install the correct webkit package for your distribution |
| SSL build failure | Ensure the SSL development headers are installed for your distro |
| nvm not found | Source the nvm startup script in the shell profile |

## Related

- → `macos.md` — macOS setup guide
- → `windows.md` — Windows setup guide
- → `docker.md` — Docker setup guide
- → `../configuration.md` — System configuration
- → `../../README.md` — Anytype hub
