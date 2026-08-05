# POS Editions

## Comparison

| Feature | forge-pos (Mini) | formint-pos (Merged) | pos-client |
|---------|------------------|----------------------|------------|
| **Tauri shell** | ✅ | ✅ | ✅ (Vue 3) |
| **Astro frontend** | ❌ | ✅ | ❌ |
| **Rust backend** | ✅ | ✅ (minimal shell) | ✅ |
| **Django Ninja backend** | ❌ | ✅ | ❌ |
| **Robyn sidecar** | ❌ | ✅ | ❌ |
| **Unfold admin** | ❌ | ✅ | ❌ |
| **WebSocket streams** | ❌ | ✅ | ❌ |
| **Cloud sync** | ❌ | ✅ | ❌ |
| **Port** | 1420 | 8767 (backend) / 4321 (frontend) | 1420 |

> **Note**: The former `pos-full` (Cloud Master) and `pos-solo` (Standalone)
> editions were merged into `formint-pos/` — the merged package now owns the
> single Robyn sidecar (`formint-pos/sidecar/`) and both legacy React UIs are
> archived under `formint-pos/legacy-react/`.

## Architecture Per Edition

### formint-pos (Merged — recommended)
```
Astro → HTMX/JSON → Django Ninja backend → Django ORM → SQLite
  └── /api/v1 (45 paginated resources, django-fusion encoder/decoder)
  └── /htmx   (django-fusion tables + forms fragments)
  └── /fusion (render-mode / navigation / assets)
  └── /admin  (Unfold dashboard + KPI cards + charts)
  └── Robyn Sidecar (:8765) → WebSocket streams + data sync + webhooks
```

### forge-pos (Mini)
```
React → Tauri Commands → Rust/Diesel → SQLite
```

### pos-client (Vue 3 desktop)
```
Vue 3 → Tauri Commands → Rust → SQLite
```

## Preset Configurations (formint-pos)

| Preset | Brand | Products |
|--------|-------|----------|
| `all` | Level Up Gaming Center | base + gaming + coffee |
| `base` | POS KO | Core POS products |
| `gaming` | Level Up Gaming Center | Gaming station products |
| `coffee` | The Daily Grind | Coffee shop products |
