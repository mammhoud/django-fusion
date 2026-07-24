# Guide — Development Workflow

**Type:** Guide 📘
**Tags:** `#pos-mini` `#pos-solo` `#pos-full` `#frontend` `#backend`
**Status:** Published
**Category:** Development

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

### Add a new page
```typescript
// 1. Create page component
// src/pages/MyNewPage.tsx
export default function MyNewPage() {
  return <PageLayout title="My Page">...</PageLayout>
}

// 2. Add route
// src/App.tsx
<Route path="/my-new-page" element={<MyNewPage />} />

// 3. Add to navigation
// src/navigation.ts
{ path: '/my-new-page', label: 'My Page', icon: FaStar }

// 4. Add translations
// src/i18n/en.json — Add "myNewPage": { ... }
```

### Add a Tauri command (pos-mini)
```rust
// src-tauri/src/lib.rs
#[tauri::command]
fn my_new_command() -> Result<String, String> {
    // Business logic
    Ok("done".to_string())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![my_new_command])
        .run(tauri::generate_context!())
}
```

### Add a sidecar API endpoint (pos-solo/full)
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

```
src/styles/theme-overrides.css ←─ Add variant overrides
src/contexts/ThemeContext.tsx   ←─ Register variant
src/pages/Settings.tsx          ←─ Add to Appearance tab
```

See → `guides/theming.md` for details.

---

## i18n Workflow

```bash
# 1. Add keys to English
# src/i18n/en.json
"MySection": { "myKey": "My Translation" }

# 2. Translate to all locales
# src/i18n/{ar,de,es,fr}.json

# 3. Use in components
import { useTranslation } from 'react-i18next';
const { t } = useTranslation();
t('MySection.myKey')
```

---

## Testing

```bash
# Frontend (vitest)
cd projects/pos/pos-mini
npx vitest run

# Sidecar (pytest)
cd projects/pos/pos-solo/sidecar
uv run pytest -v

# TypeScript
npx tsc --noEmit
```

---

## Related Docs
- → `guides/setup.md` — Environment setup
- → `guides/theming.md` — Theme customization
- → `references/i18n-keys.md` — Translation keys reference
