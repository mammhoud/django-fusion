# 📦 POS Release Pipeline

> How the POS Tauri desktop app is built, packaged, and released across Windows, Linux, and macOS.

---

## Edition Release Matrix

| Edition | Platforms | Bundle Formats | Workflow |
|---------|-----------|---------------|----------|
| **Minimal** | Windows, Linux | NSIS, MSI, AppImage | `pos-minimal/.github/workflows/release.yml` |
| **Solo** | Windows, Linux | NSIS, MSI, AppImage | `pos-solo/.github/workflows/release.yml` |
| **Full** | Windows, Linux | NSIS, MSI, AppImage | `pos-full/.github/workflows/release.yml` |

---

## Release Trigger

```yaml
# .github/workflows/release.yml
on:
  push:
    tags: ['v*.*.*']
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release'
      draft:
        description: 'Draft release?'
        type: boolean
        default: true
```

Push a version tag or trigger manually from GitHub Actions UI.

---

## Build Matrix (Full Edition)

| OS | Arch | Bundle |
|----|------|--------|
| `windows-latest` | `x64` | NSIS installer + MSI |
| `windows-latest` | `aarch64` | NSIS installer |
| `windows-latest` | `i686` | NSIS installer |
| `ubuntu-latest` | `x64` | AppImage |

---

## Build Commands (per edition)

```bash
# From projects/pos/
make build-minimal    # pnpm build:desktop (Minimal)
make build-solo       # pnpm build:desktop + pnpm build:sidecar (Solo)
make build-full       # pnpm build:desktop + pnpm build:sidecar (Full)

# Manual Tauri build
cd pos-client/src-tauri
cargo tauri build --target x86_64-pc-windows-msvc --bundles nsis,msi
```

---

## Publish Bundle

```bash
# From projects/pos/
make publish          # Creates publish/ dir with full edition
                      # Excludes: node_modules, .git, src-tauri/target
```

The `make publish` target uses `rsync` to assemble a clean bundle directory:

```makefile
publish:
    mkdir -p publish
    rsync -av --exclude node_modules --exclude .git \
        --exclude src-tauri/target pos-full/ publish/
```

---

## Release Artifacts

Each GitHub release includes:

| Artifact | Format | OS |
|----------|--------|-----|
| `pos-full_<version>_x64-setup.exe` | NSIS | Windows |
| `pos-full_<version>_x64_en-US.msi` | MSI | Windows |
| `pos-full_<version>_amd64.AppImage` | AppImage | Linux |

---

## Development Builds

```bash
# Local dev (with hot reload)
cd projects/pos/pos-client
pnpm install
pnpm tauri dev         # Opens Tauri window with Vite HMR

# Rust-only checks
cd projects/pos/pos-full
cargo build            # Compile Rust backend
cargo test             # Run unit tests
```

---

## Related

| Topic | Path |
|-------|------|
| POS editions | [`../projects/pos/editions.md`](../projects/pos/editions.md) |
| POS infrastructure | [`../projects/pos/infrastructure.md`](../projects/pos/infrastructure.md) |
| CI/CD pipelines | [`ci-cd.md`](ci-cd.md) |
