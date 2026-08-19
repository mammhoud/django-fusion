# 🦋 Robyn Migration — Complete ✅

> **Status:** Migration complete — both Solo and Full editions now use Robyn with Django ORM.
> The old Sanic-based sidecar has been fully replaced.

---

## Why Robyn?

| Aspect | Sanic (old) | Robyn (current) |
|--------|:-----------:|:----------------:|
| Runtime | Pure Python (uvloop) | Rust-powered (actix/maturin) |
| Throughput | ~25k RPS | 60k+ RPS |
| OpenAPI | Manual/plugin | Built-in auto-generation |
| WebSocket | Native (websockets) | Native (built-in) |
| Pydantic | Manual integration | First-class support (`robyn[all]`) |
| Hot reload | `--dev` flag | `--dev` flag |
| AI/MCP | None | Built-in AI agent routing |
| Maturity | Very mature (2016+) | Rapidly growing (2023+) |

---

## Current Architecture

Both server.py files are now Robyn-based with Django ORM:

```
projects/formints/
├── pos-solo/sidecar/server.py    # Robyn — 60+ endpoints, port 8765
├── pos-full/sidecar/server.py    # Robyn — 70+ endpoints, port 8766
└── shared/                       # Shared module (package structure)
    ├── signals/                  # Signal definitions
    ├── models/                   # Shared models (audit, approval, token)
    ├── handlers/                 # Signal receivers
    ├── services/                 # ProductSyncEngine
    ├── middleware/               # Auth middleware
    └── api/                      # CRUD helpers
```

### Key Migration Details

| Component | Sanic (old) | Robyn (current) |
|-----------|:-----------:|:----------------:|
| Path params | `<param>` | `:param` |
| JSON helpers | `response.json(data)` | `jsonify(data)` |
| Request body | `request.json` (property) | `request.json()` (method) |
| Query params | `request.args.get("q")` | `request.query_params.get("q")` |
| Path params | `request.match_info["id"]` | `request.path_params["id"]` or function arg |
| WebSocket | `websockets` async recv | `ws.receive_text()` / `ws.send_text()` |
| Background tasks | `app.add_task(fn)` | `asyncio.create_task(fn)` |
| CORS | Manual middleware | Manual middleware (compatible) |
| Models | Flat files (`models.py`, `unified_models.py`) | Organized packages (`models/`) |
| Shared | Flat files (`signals.py`, `auth.py`, etc.) | Organized packages (`signals/`, `middleware/`, etc.) |

### Package Restructure

Alongside the Robyn migration, the model and shared module files were restructured:

```
# Before (flat files)
models.py
unified_models.py
shared/signals.py
shared/auth.py
shared/server_base.py
shared/signal_models.py
shared/approval_models.py
shared/signal_handlers.py
shared/product_sync.py
shared/cloud/token_models.py

# After (organized packages)
models/node.py, config.py, sync.py           # Full edition
models/pos.py, menu.py, node.py, config.py, sync.py  # Solo edition
shared/signals/__init__.py
shared/models/audit.py, approval.py, token.py
shared/handlers/signal.py
shared/services/sync.py
shared/middleware/auth.py
shared/api/crud.py
```

Old files preserved as backward-compatible re-export shims.

---

## Related

| Resource | Path |
|----------|------|
| Sidecar overview | [sidecar-readme.md](sidecar-readme.md) |
| POS editions | [../editions.md](../editions.md) |
| Cloud sync plan | [../cloud/sync-plan.md](../cloud/sync-plan.md) |
| Sidecar v2 Reference | [SIDECAR_V2.md](../../../projects/formints/docs/SIDECAR_V2.md) |
