# 🔌 WebSocket Protocol — Sidecar

Real-time chat WebSocket protocol for POS sidecar.

## Tag Legend

| Tag | Meaning |
|-----|---------|
| 🟢 `customizable` | Safe to extend with new message types |
| 🔴 `not-customizable` | Core protocol — changing breaks frontend |
| ⚪ `config-only` | Configure via env vars only |

---

## Connection

### Endpoint 🔴

```
ws://127.0.0.1:8765/ws/chat/<room>
```

| Setting | Env var | Default |
|---------|---------|---------|
| Host | `POS_SIDECAR_HOST` ⚪ | `127.0.0.1` |
| Port | `POS_SIDECAR_PORT` ⚪ | `8765` |

### Connection Lifecycle

```
Client connects
  └── Server: "connected" → stored in room set
       ├── Message received → broadcast to room
       ├── Typing received → broadcast "typing" to room
       └── Connection closed → removed from room set
```

### Auto-Reconnect (Frontend)

The frontend `createChatWs()` handles reconnection:

```typescript
const conn = createChatWs({
  room: 'support',
  reconnectMs: 4000,          // 🟢 Reconnect delay (default: 4s)
  onStateChange: (state) => {
    // 'connecting' → 'open' → 'closed' → 'connecting'...
  },
});
```

---

## Message Format

### Client → Server 🔴

```json
{
  "type": "message",
  "text": "Hello, support!",
  "sender": "user"
}
```

```json
{
  "type": "typing",
  "sender": "user"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | ✅ | `"message"` or `"typing"` 🔴 |
| `text` | string | ✅ for message | Message content |
| `sender` | string | ✅ | `"user"` or `"support"` 🔴 |

### Server → Client 🔴

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "room_id": "support",
  "user": "Admin",
  "content": "Hello! How can I help you?",
  "timestamp": "2026-07-18T12:00:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (UUID) | Unique message identifier |
| `room_id` | string | The chat room |
| `user` | string | Sender display name |
| `content` | string | Message text |
| `timestamp` | string (ISO 8601) | Server timestamp |

### Typing Indicator

```json
// Server broadcasts when it receives a "typing" event
{
  "type": "typing",
  "sender": "user",
  "timestamp": "2026-07-18T12:00:00Z"
}
```

The frontend shows "is typing..." for 2500ms after receiving this, then auto-clears.

---

## Frontend Integration

### TypeScript API (`projects/pos/src/api/chat.ts`)

```typescript
import { createChatWs } from '../api';

// 🔴 Core usage — do not change the message format
const cleanup = createChatWs({
  room: 'support',                              // 🔴 Channel identifier
  onMessage: (msg: ChatMessage) => {            // 🔴 Message handler
    addToChat(msg);
  },
  onStateChange: (state: WsConnState) => {      // 🟢 Connection state UI
    // 'connecting' | 'open' | 'closed'
  },
  onTyping: (isTyping: boolean) => {            // 🟢 Typing indicator
    showTyping(isTyping);
  },
  reconnectMs: 4000,                            // 🟢 Customize retry delay
});

// 🔴 Send a message
conn.send({
  type: 'message',
  text: 'Hello!',
  sender: 'user',
});

// 🟢 Cleanup on unmount
return () => cleanup();
```

### ChatSupport Component (`projects/pos/src/components/ChatSupport.tsx`)

The component manages:
- Connection via `createChatWs` 🔴
- Message history display 🟢
- Typing indicator 🟢
- Ticket fallback (creates support ticket if WebSocket unavailable) 🟢
- Floating button toggle 🟢

---

## Customization Guide

### 🟢 Add a New Message Type

1. **Server** — add handler in `projects/pos/sidecar/server.py`:
```python
# In the WebSocket handler
if data.get("type") == "custom_event":
    await ws.send(json.dumps({
        "type": "custom_response",
        "data": "Your response",
    }))
```

2. **Frontend** — handle in `onMessage`:
```typescript
onMessage: (msg) => {
  if (msg.type === 'custom_response') {
    handleCustom(msg.data);
  }
}
```

### 🟢 Add a Room

The WebSocket protocol is room-agnostic — any string room ID works:

```typescript
const conn = createChatWs({ room: 'orders', onMessage });
```

### 🔴 Do Not Change

| What | Why |
|------|-----|
| Message JSON structure | Frontend `ChatMessage` interface depends on exact field names |
| Field names (`type`, `text`, `sender`, `content`, `user`) | Parsed directly in TypeScript |
| WebSocket path `/ws/chat/<room>` | Hardcoded in `SIDECAR_WS_BASE` |
| `"message"` and `"typing"` type values | Switch/case in ChatSupport |

---

## Troubleshooting

### Connection refused

```bash
# Check sidecar is running
curl http://127.0.0.1:8765/health

# Check port
lsof -i :8765
```

### Messages not broadcasting

```bash
# Verify WebSocket connection in browser DevTools → Network → WS
# Check for "closed" state changes in onStateChange callback
```

### Typing indicator stuck

The frontend auto-clears after 2500ms. If stuck:
- Check `typingTimer` in `createChatWs` implementation
- Ensure `onTyping?.(false)` is called

---

→ [API Reference](sidecar-api.md) | [Server Docs](README.md) | [Back to docs](../README.md)
