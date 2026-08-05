# ⚛️ TypeScript — POS Frontend

React 19 + TypeScript + Vite frontend for the POS desktop application.

## Use Cases

### 1. POS Desktop UI (`pages/*.tsx` + `components/*.tsx`)
- **Purpose:** Render 22 route-level pages (POS, Inventory, Sales, Analytics, Customers, Employees, Reports, etc.) with 15 reusable UI components — providing the complete restaurant management interface
- **Key traits:** Most pages/components are 🟢 customizable; page routing guarded by auth context; Framer Motion page transitions

### 2. Sidecar API Client (`api/*.ts`)
- **Purpose:** Provide a typed HTTP + WebSocket client layer for communicating with the Python/Sanic sidecar — health checks, data queries, chat, tickets, invoice rendering
- **Key traits:** Base client handles fetch/error normalization; typed endpoints match sidecar REST schema; WebSocket client in `chat.ts` with auto-reconnect

### 3. Real-Time Chat Widget (`components/ChatSupport.tsx` + `api/chat.ts`)
- **Purpose:** Floating chat widget for customer-staff messaging — connects via WebSocket for real-time communication with typing indicators
- **Key traits:** Room-based support chat; auto-scrolls to latest message; status toast on connection state change; 💡 protocol is 🔴 not-customizable (frontend depends on exact JSON format)

### 4. Internationalization (`i18n/*.json`)
- **Purpose:** Support English, French, and Arabic locales with i18next — translating all UI labels, messages, invoices, and reports
- **Key traits:** JSON files are 🔵 template (add/edit keys); auto-detects system language; RTL layout support for Arabic; `i18n-audit` script detects missing keys

---

## Project Structure

```
src/
├── main.tsx                  # 🔴 App entry, providers, language init
├── App.tsx                   # 🔴 Router, auth gate, page transitions
├── types.ts                  # 🟢 Shared TypeScript interfaces
├── api/                      # 🟢 Sidecar API client layer
│   ├── index.ts              # Barrel exports
│   ├── sidecar.ts            # Base HTTP client, health check
│   ├── chat.ts               # Chat REST + WebSocket
│   ├── tickets.ts            # Support tickets API
│   └── data.ts               # Sales, products, settings, invoice
├── components/               # 🟢 Reusable UI components
│   ├── ChatSupport.tsx       # Floating chat widget (WebSocket)
│   ├── DataTable.tsx         # Generic sortable/filterable table
│   ├── Invoice.tsx           # Invoice preview component
│   ├── Modal.tsx             # Modal dialog
│   ├── PageLayout.tsx        # 🔵 Page wrapper with top bar + profile
│   ├── SideNav.tsx           # Slide-out navigation panel
│   ├── Skeleton.tsx          # Loading skeleton placeholders
│   ├── StatusToast.tsx       # Toast notifications
│   ├── LanguageToggle.tsx    # Language switcher (en/fr/ar)
│   └── ThemeToggle.tsx       # Dark/light mode toggle
├── contexts/                 # 🔴 React context providers
│   ├── AuthContext.tsx       # Auth state, login/logout, inactivity
│   ├── ThemeContext.tsx      # Dark/light theme
│   └── LanguageContext.tsx   # i18n language
├── hooks/                    # 🟢 Custom hooks
│   ├── useStatusToast.ts     # Toast state management
│   └── useDebouncedSearch.ts # Debounced search input
├── i18n/                     # 🔵 Translation files
│   ├── index.ts              # i18next configuration
│   ├── en.json               # English (reference)
│   ├── fr.json               # French
│   └── ar.json               # Arabic
├── pages/                    # 🟢 Route-level page components
│   ├── Home.tsx              # Dashboard grid
│   ├── Auth.tsx              # Login/register/setup flow
│   ├── Sale.tsx              # Point of sale
│   ├── Analytics.tsx         # Charts & analytics
│   ├── Inventory.tsx         # Stock management
│   ├── ...                   # (all other pages)
├── styles/                   # 🔵 SCSS styles
│   ├── base/                 # Variables, reset
│   ├── components/            # Card, receipt styles
│   └── utilities/            # Animations, RTL, scrollbar
├── utils/                    # 🟢 Utility functions
│   ├── invoicePdf.ts         # jsPDF generation
│   └── export.ts             # Excel export
└── test/                     # 🟢 Vitest unit tests
```

## Customization Guide

### 🟢 Customizable (safe to modify)
| Module | What you can change |
|--------|-------------------|
| `pages/*.tsx` | Page layouts, UI, business logic |
| `components/DataTable.tsx` | Column configs, sort/filter behavior |
| `components/Invoice.tsx` | Invoice design, layout |
| `utils/invoicePdf.ts` | PDF generation settings |
| `utils/export.ts` | Export formats |
| `hooks/*.ts` | Hook logic |

### 🔴 Not Customizable (framework core)
| Module | Why not |
|--------|---------|
| `App.tsx` | Routing structure, auth gate — change carefully |
| `main.tsx` | Provider order, initialization |
| `contexts/AuthContext.tsx` | Auth flow, session management |
| `contexts/ThemeContext.tsx` | Theme toggling logic |

### 🔵 Template (i18n + styles)
| Module | Customize via |
|--------|-------------|
| `i18n/*.json` | Add/edit translation keys |
| `styles/` | SCSS variables in `_variables.scss` |

### 🟡 Delegate Pattern
| Pattern | How to use |
|---------|-----------|
| Add a page | Create `pages/NewPage.tsx` → add route in `App.tsx` |
| Add API method | Create in `src/api/` → add to barrel export |
| Add component | Create in `components/` → import where needed |
| Add translation | Add key to `en.json` → add translations to `fr.json`, `ar.json` |

## Key APIs

### Sidecar Client (`api/sidecar.ts`)
```typescript
import { sidecar } from '../api';

// Health check
const running = await sidecar.healthCheck();

// Typed HTTP calls
const { data, ok, error } = await sidecar.get<MyType>('/api/sales');
const result = await sidecar.post<Ticket>('/api/support/ticket', payload);
```

### Auth Context
```typescript
import { useAuth } from '../contexts/AuthContext';

const { user, isAuthRequired, login, logout } = useAuth();
// user: { id, email, name } | null
```

### Chat WebSocket (`api/chat.ts`)
```typescript
import { createChatWs } from '../api';

const conn = createChatWs({
  room: 'support',
  onMessage: (msg) => console.log(msg),
  onStateChange: (state) => console.log(state),
});
conn.send({ type: 'message', text: 'Hello!' });
conn.close();
```

## Tests

```bash
cd POS
pnpm vitest run                # Run all frontend tests
pnpm vitest -- --reporter=verbose  # Verbose output
```

---

→ [Back to docs](../README.md)
