---
Object type: Guide
Tags: install, setup
Status: Published
Platform: macOS
---

# macOS Setup Guide

> Description-oriented setup guide for the macOS development environment. Tasks are described by action and outcome; exact commands live in the repository docs.

## Prerequisites

| Tool | Minimum Version | Purpose |
|------|-----------------|---------|
| macOS | 13+ (Ventura) | Operating system |
| Python | 3.12 | Backend and sidecar |
| Node.js | 18+ | Frontend tooling |
| pnpm | 8+ | Package manager |
| Rust | 1.70+ | Tauri desktop builds |
| uv | 0.4+ | Python package management |

## Setup steps

1. **Install package managers** — set up Node via nvm (recommended for version control), then install pnpm and uv. Verify each with its version check.
2. **Install Rust** — via rustup with the default profile. Add the Apple Silicon and Intel macOS targets as needed for Tauri builds.
3. **Install system dependencies** — macOS uses the native WebView, so most desktop dependencies are bundled with Xcode Command Line Tools. Install those tools when prompted.
4. **Clone and set up the repository** — clone the monorepo, create a Python virtual environment, install the POS dependencies with pnpm, and set up the sidecar with uv.
5. **Verify installation** — confirm each tool version meets the minimums and run the test suites to validate the environment.
6. **Run the development server** — choose browser mode or desktop mode (full Tauri app).

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Command line tools already installed | Reset the tools, then retry the Xcode installation |
| nvm not found | Source the nvm startup script in the shell profile and restart the terminal |
| cargo not found | Source the Rust environment file to load the cargo path |
| uv not found | Add the user-local bin directory to the shell PATH |

## Related

- → `linux.md` — Linux setup guide
- → `windows.md` — Windows setup guide
- → `docker.md` — Docker setup guide
- → `../configuration.md` — System configuration
- → `../../README.md` — Anytype hub
