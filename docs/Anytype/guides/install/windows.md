---
# yaml-language-server: $schema=../../schemas/page.schema.json
Object type: Guide
Tags: install, pos-mini, pos-solo, pos-full
Status: Published
Platform: Windows
---

# Windows Installation Guide

> Comprehensive setup guide for Windows development environment.

---

## Prerequisites

### Install Windows Build Tools

```powershell
# Windows Package Manager (winget) — built into Windows 11 / Windows 10 2022+
winget install Microsoft.VisualStudio.2022.BuildTools
# During install, select "Desktop development with C++"

# Or install via Chocolatey (if you prefer)
# choco install visualstudio2022buildtools
```

### Install Git

```powershell
winget install Git.Git
```

---

## Step 1: Install Package Managers

### Node.js via nvm-windows

```powershell
# Download and install nvm-windows
# https://github.com/coreybutler/nvm-windows/releases
# Run nvm-setup.exe

# Or via winget:
winget install CoreyButler.NVMforWindows

# Restart terminal, then:
nvm install lts
nvm use lts

# Verify
node --version   # ≥ 18
npm --version

# pnpm
npm install -g pnpm
pnpm --version   # ≥ 8
```

### uv (Python Package Manager)

```powershell
# Using PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Step 2: Install Rust (for Tauri builds)

```powershell
# Download and run rustup-init.exe
# https://rustup.rs/
# Select option 1 (default installation)

# Or via winget:
winget install Rustlang.Rustup

# Verify
rustc --version   # ≥ 1.70
cargo --version
```

---

## Step 3: Install WebView2 (for Tauri)

> WebView2 is built into Windows 11 and recent Windows 10 builds.
> If missing, download from: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

```powershell
# Check if WebView2 is available
# It should be pre-installed on Windows 10 (2020+) and Windows 11
```

---

## Step 4: Clone & Setup Repository

```powershell
# Clone
git clone https://github.com/mammhoud/structa.cloud.git
cd structa.cloud

# Python virtual env (use Python 3.11+ from python.org)
python -m venv .venv
.venv\Scripts\activate
pip install uv

# Install POS deps
cd projects\pos\pos-solo
pnpm install
cd sidecar
uv sync
```

---

## Step 5: Verify

```powershell
# Check installed versions
python --version    # ≥ 3.11
uv --version        # ≥ 0.4
node --version      # ≥ 18
pnpm --version      # ≥ 8
cargo --version     # ≥ 1.70

# Run tests
cd sidecar && uv run pytest
cd .. && pnpm vitest run

# Start dev server (browser mode)
pnpm dev
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `pnpm : File cannot be loaded` | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `MSBuild tools not found` | Ensure Visual Studio Build Tools are installed with C++ workload |
| `openssl-sys build failed` | Install OpenSSL via `vcpkg install openssl` or use WSL |
| `Tauri dev fails` | Ensure WebView2 runtime is installed |
| `Python not found` | Install from python.org and check PATH |
| `uv: command not found` | Add `%USERPROFILE%\.local\bin` to PATH |

---

## Windows-Specific Notes

- **WSL2** is recommended for the best development experience on Windows
- See `docker.md` for WSL2/Docker setup
- All pnpm, cargo, and uv commands work identically in WSL2
- For native Windows: use PowerShell with ExecutionPolicy bypass

---

## Related

- → `macos.md` — macOS setup guide
- → `linux.md` — Linux setup guide
- → `docker.md` — Docker/WSL setup guide
- → `../configuration.md` — System configuration
- → `../../objects/configuration.md` — Configuration object type
- → `../../README.md` — Master index
