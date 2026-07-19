# 🦋 Robyn Migration — Solo Sidecar

> Migration plan: Sanic → [Robyn](https://github.com/sparckles/Robyn) for POS Solo extended sidecar.

---

## Why Robyn?

| Aspect | Sanic | Robyn |
|--------|-------|-------|
| Runtime | Pure Python (uvloop) | Rust-powered (actix/maturin) |
| Throughput | ~25k RPS | 60k+ RPS |
| OpenAPI | Manual/plugin | Built-in auto-generation |
| WebSocket | Native (websockets) | Native (built-in) |
| Pydantic | Manual integration | First-class support (`robyn[all]`) |
| Hot reload | `--dev` flag | `--dev` flag |
| AI/MCP | None | Built-in AI agent routing |
| Maturity | Very mature (2016+) | Rapidly growing (2023+) |

---

## Migration Overview

### Current (Sanic)

```python
# server.py — Sanic
from sanic import Sanic, response
from sanic.websocket import WebSocketConnection

app = Sanic("POS-Sidecar")

@app.get("/health")
async def health(request):
    return response.json({"status": "ok"})

@app.websocket("/ws/chat/<room_id>")
async def chat(request, ws: WebSocketConnection, room_id: str):
    while True:
        data = await ws.recv()
        await ws.send(json.dumps({"echo": data}))
```

### Target (Robyn)

```python
# robyn_server.py — Robyn
from robyn import Robyn, jsonify, WebSocket

app = Robyn(__file__)

@app.get("/health")
async def health(request):
    return jsonify({"status": "ok"})

@app.websocket("/ws/chat/:room_id")
async def chat(ws: WebSocket, room_id: str):
    while True:
        data = await ws.receive()
        await ws.send(json.dumps({"echo": data}))
```

---

## Endpoint Migration Map

| Sanic | Robyn | Notes |
|-------|-------|-------|
| `@app.get("/health")` | `@app.get("/health")` | Identical pattern |
| `@app.post("/chat/<room>")` | `@app.post("/chat/:room")` | Path params: `<>` → `:` |
| `@app.websocket("/ws/<id>")` | `@app.websocket("/ws/:id")` | Same pattern |
| `response.json(data)` | `jsonify(data)` | Different helper |
| `response.html(html)` | `Response(status_code=200, body=html, headers={"Content-Type": "text/html"})` | Different API |
| `request.json` | `request.json()` | Method call vs property |
| `request.args.get("q")` | `request.query_params.get("q")` | Different attr name |
| `request.match_info["id"]` | `request.path_params["id"]` | Different attr name |
| `app.add_task(fn)` | `asyncio.create_task(fn)` | Standard asyncio |
| `app.static("/static", "./static")` | `app.serve_static("/static", "./static")` | Different method |

---

## Implementation Phases

### Phase 1: Drop-in Replacement (1 day)

- Create `robyn_server.py` alongside `server.py`
- Port all routes, WebSocket handlers, middleware
- Keep `server.py` as fallback
- Add `robyn` to `requirements.txt`: `robyn[all]>=0.50`

### Phase 2: Pydantic Integration (1 day)

```python
from robyn import Robyn
from pydantic import BaseModel, Field

app = Robyn(__file__)

class ChatMessage(BaseModel):
    room_id: str = Field(min_length=1)
    text: str = Field(max_length=5000)
    sender: str

@app.post("/chat/:room_id")
async def post_chat(request, room_id: str):
    body = request.json()
    msg = ChatMessage(**body)  # Auto-validated
    # ... persist and broadcast
```

### Phase 3: OpenAPI Generation (1 day)

Robyn auto-generates OpenAPI docs at `/docs` (Swagger) and `/redoc` (ReDoc) — no extra config needed. Add custom descriptions:

```python
@app.get("/api/products", openapi_name="List Products",
         openapi_tags=["Products"])
async def list_products(request):
    ...
```

### Phase 4: Performance Tuning (1 day)

```python
# Worker count for optimal CPU usage
app.start(port=8765, workers=4)

# Enable Rust optimizations
# Set in .cargo/config.toml or env:
# RUSTFLAGS="-C target-cpu=native"
```

---

## Compatibility Notes

| Feature | Sanic | Robyn | Migration Effort |
|---------|:-----:|:-----:|:----------------:|
| REST routes | ✅ | ✅ | Low (syntax only) |
| WebSocket | ✅ | ✅ | Low |
| Middleware | ✅ | ✅ | Low (request/response hooks) |
| Static files | ✅ | ✅ | Low |
| Blueprints | ✅ | ❌ | Medium (use sub-routers) |
| Background tasks | ✅ | ✅ | Low (asyncio tasks) |
| Streaming | ✅ | ✅ | Low (SSE support) |
| CORS | ✅ | ✅ | Low |
| Jinja2 templates | ❌ | ✅ | New capability |

---

## Rollback Plan

Both `server.py` (Sanic) and `robyn_server.py` (Robyn) coexist during migration. Switch via env:

```bash
# Use Sanic (default)
POS_SIDECAR_BACKEND=sanic python3 server.py

# Use Robyn (extended)
POS_SIDECAR_BACKEND=robyn python3 robyn_server.py
```

---

## Related

| Resource | Path |
|----------|------|
| Robyn docs | [robyn.tech](https://robyn.tech/) |
| Robyn GitHub | [sparckles/Robyn](https://github.com/sparckles/Robyn) |
| Sidecar overview | [sidecar-readme.md](sidecar-readme.md) |
| POS editions | [../editions.md](../editions.md) |
| Cloud sync plan | [../cloud/sync-plan.md](../cloud/sync-plan.md) |
