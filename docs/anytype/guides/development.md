---
# yaml-language-server: $schema=schemas/page.schema.json
Object type: Guide
Tags: pos-mini, pos-solo, pos-full, frontend, backend
Status: Published
Category: Development
---

# Guide — Development Workflow

> **Type:** Guide 📘
> **Development workflow for all POS editions with project color annotations.**

---

## Project Color Annotations

Colors used throughout development:

| Context | Color | Hex | When You'll See It |
|---------|-------|-----|-------------------|
| **Rust / Tauri** | Rust Red | `#f7524a` | Cargo build output, Rust errors |
| **Python / Sidecar** | Python Blue | `#306998` | Django admin, uv output |
| **TypeScript / React** | TypeScript Blue | `#3178c6` | Vite dev server, tsc output |
| **Database (SQLite)** | Slate | `#64748b` | Database migrations, schema files |
| **Sync / Network** | Teal | `#14b8a6` | Sync status, API endpoints |
| **Frontend UI (Default)** | Indigo/Teal | `#6366f1`/`#14b8a6` | POS app theme (customizable) |

---

## Project Structure

```
projects/pos/
  pos-mini/           # Rust/Tauri edition
    src/pages/        # React pages
    src/components/   # Shared components
    src/contexts/     # React contexts (Theme, Auth)
    src/hooks/        # Custom hooks
    src/i18n/         # Translation files
    src/styles/       # CSS + theme overrides
    src-tauri/        # Rust backend + Tauri config
    sidecar/          # (none — Rust only)

  pos-solo/           # Django + Robyn edition
    (same as pos-mini frontend)
    sidecar/          # Python Robyn server
      server.py       # Entry point
      models/         # Django models
      routes/         # API routes
      services/       # Business logic
      tests/          # Pytest suite

  pos-full/           # Cloud-enabled edition
    (same as pos-solo structure)
```

---

## Common Tasks

### Add a New Page

```typescript
// 1. Create page component
// src/pages/MyNewPage.tsx
export default function MyNewPage() {
  return <PageLayout title="My Page">...</PageLayout>
}

// 2. Add route in src/App.tsx
// 3. Add to navigation in src/navigation.ts
// 4. Add translations in src/i18n/en.json
```

### Add a Tauri Command (pos-mini)

```rust
// src-tauri/src/lib.rs
#[tauri::command]
fn my_new_command() → Result<String, String> {
    Ok("done".to_string())
}
```

### Add a Sidecar API Endpoint (pos-solo/full)

```python
# sidecar/routes/my_route.py
from robyn import Router
router = Router()

@router.get("/api/my-endpoint")
async def my_endpoint(request):
    return {"status": "ok", "data": [...]}
```

---

## Theme Development

```bash
src/styles/theme-overrides.css   # Add variant CSS overrides
src/contexts/ThemeContext.tsx     # Register the new variant
src/pages/Settings.tsx            # Add to Appearance tab
```

The theme system supports 5 built-in color variants (Default, Corporate, Luxury, Pastel, Cyberpunk) — see `theming.md` for the full color palette reference.

---

## i18n Workflow

```bash
# 1. Add keys to English in src/i18n/en.json
# 2. Translate to all locales ({ar,de,es,fr}.json)
# 3. Use in components with useTranslation() hook
```

---

## Testing

```bash
# Frontend (vitest)
npx vitest run

# Sidecar (pytest)
uv run pytest -v

# TypeScript
npx tsc --noEmit
```

---

## Related Docs

- → `setup.md` — Environment setup with color guide
- → `theming.md` — Theme customization & color palettes
- → `../architecture/theme-system.md` — Theme architecture
- → `../references/i18n-keys.md` — Translation keys reference
- → `../README.md` — Master index
