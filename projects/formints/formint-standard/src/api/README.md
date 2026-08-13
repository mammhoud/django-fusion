# 📁 POS-KO API Client Layer (`src/api/`)

## What's Here

Typed HTTP client and WebSocket connection managers for communicating with the sidecar server.

```
api/
├── index.ts        # Barrel exports — import everything from here
├── sidecar.ts      # 🔴 Base HTTP client + health check
├── chat.ts         # 🔴 Chat REST + WebSocket (createChatWs)
├── tickets.ts      # 🟢 Support ticket CRUD
└── data.ts         # 🟢 Sales, products, settings, invoice
```

## Customization Tags

| Module | Tag | How to customize |
|--------|-----|-----------------|
| `sidecar.ts` | 🔴 `not-customizable` | Base URL, timeouts — change breaks all API calls |
| `chat.ts` | 🔴 `not-customizable` | WebSocket protocol must match sidecar |
| `tickets.ts` | 🟢 `customizable` | Add new ticket fields, query params |
| `data.ts` | 🟢 `customizable` | Add new data endpoints |

## Quick Usage

```typescript
import { sidecar, chat, tickets, data, createChatWs } from '../api';

// Health check
const ok = await sidecar.healthCheck();

// Get sales
const result = await data.listSales();

// Create ticket
await tickets.create({ subject: 'Help!', message: '...' });

// WebSocket chat
const conn = createChatWs({ room: 'support', onMessage: (msg) => ... });
conn.send({ type: 'message', text: 'Hello!', sender: 'user' });
```

## Reference

- [API Layer Docs →](../../docs/typescript/api.md)
- [Sidecar API Reference →](../../docs/server/api-reference.md)
