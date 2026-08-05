# 🟢 API Layer — `src/api/`

Typed HTTP + WebSocket client for the POS Sanic sidecar. All modules export through `src/api/index.ts`.

> **Customization level**: 🟢 Customizable — add new API methods freely.

## Modules

| Module | File | Purpose |
|--------|------|---------|
| `sidecar` | `sidecar.ts` | Base HTTP client, health check, fetch wrapper |
| `chat` | `chat.ts` | Chat REST + WebSocket helper |
| `tickets` | `tickets.ts` | Support tickets CRUD |
| `data` | `data.ts` | Sales, products, settings, invoice |

## Quick Usage

```typescript
import { sidecar, chat, tickets, data, createChatWs } from '../api';

// Check if sidecar is running
const ok = await sidecar.healthCheck();

// Get chat history
const { data: history } = await chat.getHistory('room-1');

// List tickets
const { data: ticketList } = await tickets.list();

// Create ticket
const { ok, error } = await tickets.create({
  name: 'John',
  email: 'john@test.com',
  subject: 'Bug report',
  message: 'The invoice total is wrong.',
});

// Get sale data
const { data: sale } = await data.getSale(42);

// Get invoice URL
const url = data.getInvoiceUrl(42, 'commercial', 'modern');

// WebSocket chat
const conn = createChatWs({
  room: 'support',
  onMessage: (msg) => console.log(msg.content),
  onStateChange: (state) => console.log(state),
});
conn.send({ type: 'message', text: 'Hello!' });
```

## `sidecar.ts` — Base Client

```typescript
interface SidecarResponse<T> {
  data: T | null;      // Parsed response body
  error: string | null; // Error message if !ok
  ok: boolean;         // HTTP status 2xx
  status: number;      // HTTP status code
}

// Methods
sidecar.get<T>(path)     // GET request
sidecar.post<T>(path, body)  // POST request
sidecar.patch<T>(path, body) // PATCH request
sidecar.healthCheck()    // → boolean
sidecar.getHealth()      // → HealthResponse
```

## Adding a New API Method

```typescript
// 1. Create src/api/my-feature.ts
import sidecar from './sidecar';

export interface MyData { id: number; name: string; }

export const myFeature = {
  list: () => sidecar.get<MyData[]>('/api/my-feature'),
  create: (data: Omit<MyData, 'id'>) => sidecar.post<MyData>('/api/my-feature', data),
};

// 2. Export in src/api/index.ts
export { myFeature } from './my-feature';

// 3. Use anywhere
import { myFeature } from '../api';
const { data } = await myFeature.list();
```

---

→ [Back to TypeScript docs](README.md)
