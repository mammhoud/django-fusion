---
Object type: Guide
Tags: install, setup
Status: Published
Platform: Windows
---

# Windows Setup Guide

> Description-oriented setup guide for the Windows development environment. Tasks are described by action and outcome; exact commands live in the repository docs.

## Prerequisites

| Tool | Minimum Version | Purpose |
|------|-----------------|---------|
| Python | 3.11+ | Backend and sidecar |
| Node.js | 18+ | Frontend tooling |
| pnpm | 8+ | Package manager |
| Rust | 1.70+ | Tauri desktop builds |
| uv | 0.4+ | Python package management |
| WebView2 | Built-in (Win11 / recent Win10) | Tauri runtime |

## Setup steps

1. **Install the Windows build tools** — install Visual Studio Build Tools with the "Desktop development with C++" workload (via winget or a package manager).
2. **Install Git** — through the Windows package manager or installer.
3. **Install package managers** — set up Node via nvm-windows, then pnpm (npm global) and uv (from the official installer). Verify each with its version check.
4. **Install Rust** — via rustup or winget with the default profile for Tauri builds.
5. **Ensure WebView2** — confirm the runtime is present (built into recent Windows); otherwise install it.
6. **Clone and set up the repository** — clone the monorepo, create a Python virtual environment, install POS dependencies with pnpm, and set up the sidecar with uv.
7. **Verify installation** — confirm each tool version and run the test suites to validate the environment.
8. **Run the development server** — start in browser mode.

## Windows-specific notes

- **WSL2** is recommended for the best development experience; all tooling works identically inside WSL2
- See the Docker guide for WSL2 and container setup
- For native Windows, use PowerShell with an appropriate script-execution policy

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| pnpm cannot be loaded | Adjust the script execution policy for the current user |
| MSBuild tools not found | Ensure Visual Studio Build Tools include the C++ workload |
| SSL build failure | Install OpenSSL via a package manager or use WSL2 |
| Tauri dev fails | Ensure the WebView2 runtime is installed |
| Python not found | Install from python.org and confirm it is on the PATH |
| uv not found | Add the user-local bin directory to the PATH |

## Related

- → `macos.md` — macOS setup guide
- → `linux.md` — Linux setup guide
- → `docker.md` — Docker/WSL setup guide
- → `../configuration.md` — System configuration
- → `../../README.md` — Anytype hub
