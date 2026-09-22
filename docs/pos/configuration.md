# ⚙️ POS — Configuration

> Configuration reference for the POS Tauri desktop application — Tauri, Rust
> backend. **⛔ The sidecar Django portal is historical** — Community/Standard are
> offline-first (Rust/Diesel only); Pro/Cloud serve Django themselves.

---

## Tauri Configuration

```json
// projects/formints/formint-community/src-tauri/tauri.conf.json
{
  "productName": "POS",
  "identifier": "com.mammhoud.pos",
  "version": "0.1.0",
  "build": {
    "devUrl": "http://localhost:1420",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [{
      "title": "POS",
      "width": 1200,
      "height": 800,
      "center": true,
      "decorations": true
    }]
  },
  "bundle": {
    "publisher": "Structa Cloud",
    "category": "Business",
    "shortDescription": "Point of Sale with Tauri, React, Rust"
  }
}
```

### Tauri CLI

```bash
pnpm tauri dev          # Dev with hot reload (Vite :1420)
pnpm tauri build        # Production bundle
pnpm tauri build --target x86_64-pc-windows-msvc --bundles nsis
```

---

## Rust Backend Dependencies

```toml
# projects/formints/formint-community/src-tauri/Cargo.toml
[dependencies]
tauri = { version = "2", features = [] }
tauri-plugin-opener = "2"
tauri-plugin-dialog = "2"
tauri-plugin-fs = "2"
tauri-plugin-shell = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
base64 = "0.22"
lettre = { version = "0.11", features = ["smtp-transport", "builder"] }
tokio = { version = "1", features = ["full"] }
dotenvy = "0.15"

[build-dependencies]
tauri-build = { version = "2", features = [] }
```

### Key Crates

| Crate | Purpose |
|-------|---------|
| `tauri` 2.x | Desktop app framework |
| `serde` + `serde_json` | JSON serialization for Tauri commands |
| `lettre` | Email (SMTP receipts, invoices) |
| `tokio` | Async runtime for sidecar HTTP calls |
| `dotenvy` | `.env` file loading |
| `tauri-plugin-shell` | Sidecar binary spawning |
| `tauri-plugin-dialog` | Native file/open dialogs |
| `tauri-plugin-fs` | Filesystem access |

---

## Sidecar Django Portal — ⛔ removed

> The embedded sidecar Django portal no longer exists. Pro (`formint-pro/`) and
> Cloud (`formint-cloud/`) run Django directly (see their READMEs).

```python
# historical: pos-solo/sidecar/settings.py — removed

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_fusion.comp",      # Component system
    "django_fusion.core",      # Core handlers
    "shared",                  # Shared POS models
    "portal",                  # Django admin portal
    "node",                    # Node API for sync
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "solo_portal.db",
    }
}
```

### Solo-Specific Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `CLOUD_CRM_URL` | `http://localhost:8082` | Cloud CRM sync endpoint |
| `CLOUD_CRM_API_KEY` | `""` | API key for cloud sync |
| `SYNC_INTERVAL` | `60` | Seconds between sync cycles |

---

## Edition-Specific Configs

| Setting | Minimal | Solo | Full |
|---------|:-------:|:----:|:----:|
| Tauri plugins | shell, fs | + dialog, opener | + dialog, opener |
| Sidecar binary | ❌ | ✅ (embedded) | ✅ (external server) |
| Django portal | ❌ | ✅ (sidecar) | ✅ (full Django ORM) |
| WebSocket | ❌ | ❌ | ✅ (real-time sync) |
| Cloud CRM sync | ❌ | ✅ (push only) | ✅ (master + broadcast) |
| Multi-terminal | ❌ | ❌ | ✅ |

---

## Makefile Build Targets

```bash
# From projects/formints/
make dev              # Start dev (all editions)
make build-minimal    # pnpm build:desktop
make build-solo       # pnpm build:desktop + pnpm build:sidecar
make build-full       # pnpm build:desktop + pnpm build:sidecar
make publish          # Create publish bundle (rsync)
```

---

## Environment Variables

```bash
# .env (for dotenvy crate)
DATABASE_URL=pos.db
SIDECAR_PORT=3000

# Solo portal
SOLO_PORTAL_SECRET_KEY=dev-key
SOLO_PORTAL_DEBUG=1
CLOUD_CRM_URL=http://localhost:8082
CLOUD_CRM_API_KEY=
SYNC_INTERVAL=60
```

---

## Related

| Topic | Path |
|-------|------|
| POS editions | [`editions.md`](editions.md) |
| POS features | [`features.md`](features.md) |
| POS infrastructure | [`infrastructure.md`](infrastructure.md) |
| POS release pipeline | [`../../publish/pos-release.md`](../../publish/pos-release.md) |
| Rust backend | [`rust-backend.md`](backend/rust-backend.md) |
