# Django-Bolt & django-fusion Integration — Historical Case Study

> **Historical notice:** This document records the former integration proposal. The shared `django_fusion.plugins.bolt` package has been removed. Keep Bolt/API integrations in consuming projects; do not import the removed package from django-fusion.

> **Date:** 2026-07-26 | **Branch:** `generic`
> **Scope:** Analysis of django-bolt API patterns across Structa Cloud websites and POS editions, with recommendations for django-fusion integration.

---

## 1. Executive Summary

django-bolt provides a high-performance Rust-backed ASGI server with Flask/FastAPI-style routing. It is used in two distinct patterns across the Structa Cloud ecosystem:

1. **Real BoltAPI** (`@bolt.get/post/patch/delete` decorators) — Used in POS sidecars and the LMS CMS for high-throughput endpoints (auth, courses, CRM, etc.)
2. **bolt_view adapter** (`@bolt_view` decorator) — A local adapter pattern in CTC Research and Fusion projects that converts data-returning views into Django `JsonResponse` objects

This case study records the former proposal. It is retained for migration history only; django-fusion now provides rendered HTML and data-response primitives, while any Bolt-style JSON API remains owned by the consuming project.

---

## 2. django-bolt Architecture Overview

### 2.1 Core Concepts

| Concept | Description |
|---------|-------------|
| `BoltAPI` | Top-level API instance managing routes, auth, middleware |
| `@bolt.get/post/patch/delete` | Route decorators — sync or async handlers |
| `@bolt.websocket` | WebSocket route decorator |
| `runbolt` | Management command — Rust-backed ASGI server (Actix Web / PyO3) |
| `BoltAPI.urls` | Django URL patterns for mounting in `ROOT_URLCONF` |
| `django_bolt.serializers` | Pydantic/msgspec-like type-safe request/response schemas |
| `django_bolt.auth` | JWT + API Key authentication, guards, token revocation |
| `django_bolt.testing.TestClient` | In-process test client (no TCP needed) |

### 2.2 Deployment Modes

```
Mode 1: Standalone (POS)
   python manage.py runbolt --port 8087
   → Rust Actix Web serves all bolt routes directly

Mode 2: Django-mounted (LMS CMS, Fusion)
   urlpatterns = [path("apis/", bolt.urls)]
   → Django WSGI/ASGI serves bolt routes through BoltAPI.urls bridge
```

---

## 3. Usage Analysis by Project

### 3.1 POS Full Edition (`projects/pos/pos-full/sidecar/bolt_api.py`)

**Pattern:** Real `BoltAPI` with msgspec schemas

```python
from django_bolt import BoltAPI, Request
from django_bolt.auth import JWTAuthentication, APIKeyAuthentication, IsAuthenticated

bolt = BoltAPI(prefix="/bolt", namespace="pos-bolt")

@bolt.get("/products", response_model=list[ProductResponse], guards=[IsAuthenticated()])
async def list_products(request: Request) -> list[ProductResponse]:
    return [...]
```

**Key features:**
- Async endpoints backed by Django ORM `aget/acreate`
- `response_model` for OpenAPI schema generation
- Dual auth (JWT + X-API-Key)
- `msgspec.Struct` for request/response schemas (high performance)
- OpenAPI docs at `/bolt/docs`

**Scale:** ~40 endpoints across 7 resource groups (categories, products, customers, sales, inventory, employees, auth)

### 3.2 LMS CMS (`projects/lms/cms/apis.py`)

**Pattern:** Real `BoltAPI` with Pydantic schemas

```python
from django_bolt import BoltAPI

bolt = BoltAPI(prefix="/apis", namespace="precis-ctc-bolt")

@bolt.get("/courses")
def list_courses(request):
    return PaginatedResponse[CourseResponse](...).model_dump()
```

**Key features:**
- Sync handlers using Django ORM (not async)
- Pydantic models for schema contracts (`www/schemas/`)
- TypeScript mirror: `websites/next-lms/src/types/api-schema.d.ts`
- Custom JWT auth backend (`JWTTokenAuthBackend`)
- Modular handler registration via `www/api/data/router.py`

**Scale:** ~55 endpoints across 10+ resource groups (health, publications, team, courses, auth, contact, site settings, blog, events, testimonials, LMS features, products, menu)

### 3.3 CTC Research & Fusion Projects (`www/api/data_adapter.py`)

**Pattern:** `bolt_view` adapter (local pattern)

```python
def bolt_view(view_func):
    """Decorator that converts data-returning views into Django JsonResponse."""
    def wrapper(request, *args, **kwargs):
        result = view_func(request, *args, **kwargs)
        if isinstance(result, tuple):
            data, status = result
            return JsonResponse(data, status=status)
        return JsonResponse(result, status=200)
    return wrapper

@bolt_view
def page_detail(request, slug):
    return STATIC_PAGES.get(normalized)
```

**Key features:**
- Pure Django views — no dependency on django-bolt
- Simple data-to-JSON wrapping
- Used alongside `FusionCodec`, `FusionSessionChecker`, and `fusion_response`
- Coexists with django-fusion fragment rendering

**Scale:** ~3 endpoints per project (health, page detail, page fragment, page data)

### 3.4 POS Cloud CRM (`projects/pos-cloud/core/api.py`)

**Pattern:** Minimal BoltAPI for cloud CRM

```python
from django_bolt import BoltAPI
bolt = BoltAPI()
```

**Scale:** Lightweight, proof-of-concept integration.

---

## 4. django-fusion Current Integration Points

### 4.1 Component System

| Feature | Status | Bolt Integration |
|---------|:------:|------------------|
| `{% comp "name" /%}` | ✅ | N/A — template-side only |
| `RoutableComponent` | ✅ | Could expose bolt endpoints |
| `FragmentComponent` | ✅ | Already serves fragments via `/fragments/` |
| `FusionCodec` | ✅ | Encodes page data for frontend decoding |
| `FusionSessionChecker` | ✅ | Health check for render-first preference |

### 4.2 Fragment Rendering Pipeline

```
Browser → /api/pages/<slug>/fragment/  → FragmentPointer (JSON)
       → /fragments/pages.<slug>/       → Rendered HTML
       → FusionDecoder.decode()         → Page data blocks
       → FusionProxy renders component
```

### 4.3 What's Missing for Full Bolt Integration

1. **No `BoltAPI` instance** in django-fusion itself — components can't auto-expose bolt endpoints
2. **No serialization layer** connecting django-fusion components to bolt response models
3. **No auth bridge** — bolt's JWT/APIKey auth isn't wired into fusion component guards
4. **No OpenAPI generation** for fusion component APIs

---

## 5. Former Proposed Integration Architecture (Retired)

### 5.1 Former goal (retired)

The former goal was to expose every django-fusion `RoutableComponent` as a
django-bolt endpoint. This was not adopted. Consuming projects now own their
API routes, serializers, authentication, and framework adapters.

### 5.2 Removed module: `django_fusion.bolt`

```
django_fusion/
├── bolt/
│   ├── __init__.py          # Public API exports
│   ├── api.py               # FusionBoltAPI — BoltAPI subclass with fusion awareness
│   ├── serializers.py        # Auto-serializer from component metadata
│   ├── decorators.py        # @fusion_endpoint — bolt + fragment dual-purpose
│   ├── auth.py              # FusionBoltAuthBackend — bridge fusion session → bolt auth
│   └── design.md
```

### 5.3 Key Types

```python
# RETIRED EXAMPLE — do not copy; the shared django-fusion Bolt package was removed.
# django_fusion/bolt/api.py
class FusionBoltAPI(BoltAPI):
    """BoltAPI subclass that integrates with django-fusion components."""

    def register_component(self, component_class: type[RoutableComponent]):
        """Auto-generate bolt endpoints for a RoutableComponent."""
        ...

    def register_fragment(self, fragment_name: str):
        """Expose a fragment as a bolt endpoint."""
        ...

# django_fusion/bolt/decorators.py
def fusion_endpoint(path: str, **kwargs):
    """Decorator that registers both a bolt route AND a fragment renderer."""
    ...

# django_fusion/bolt/serializers.py
def component_serializer(component_class) -> type[Serializer]:
    """Generate a django-bolt Serializer from a component's metadata."""
    ...
```

### 5.4 Usage Pattern

```python
# RETIRED EXAMPLE — do not import this removed package.
# In a consuming project, import its own API adapter instead.
from django_fusion.bolt import FusionBoltAPI
from plugins.pages.components import HomePage

fusion_bolt = FusionBoltAPI(prefix="/api/v2")

# Auto-expose all public pages as bolt endpoints
fusion_bolt.register_component(HomePage)

# Or manually with decorators
@fusion_endpoint("/pages/home")
class HomePage(RoutableComponent):
    """Renders HTML (fusion_render_first) AND serves JSON (bolt)."""
    ...
```

### 5.5 Changeable Settings per Fusion Project

Each Fusion project (precis-lms, cms-fusion) should have its own bolt configuration:

```python
# settings.py — per-project overrides
FUSION_BOLT = {
    "enabled": True,                           # Enable/disable bolt API
    "prefix": "/api/v2",                       # Bolt API prefix
    "openapi_title": "Fusion LMS API",         # OpenAPI title
    "openapi_version": "1.0.0",
    "auth_backends": ["jwt", "api_key"],       # Supported auth backends
    "serializer_format": "pydantic",           # pydantic | msgspec | dict
    "rate_limit": "100/minute",                # Optional rate limiting
    "cors_origins": ["http://localhost:3000"],  # CORS for Next.js frontend
    "component_auto_register": True,           # Auto-register registered components
}
```

---

## 6. Frontend Integration Strategy

### 6.1 Next.js + django-bolt Client

```typescript
// lib/api-client.ts — shared across all fusion frontends
import { FusionDecoder } from '@/lib/fusion-decoder';
import type { FusionEnvelope, FragmentPointer } from '@/lib/fusion-types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5070/api';

class FusionApiClient {
  private decoder = new FusionDecoder();

  async fetchFragment(slug: string): Promise<FragmentPointer> {
    const res = await fetch(`${API_BASE}/pages/${slug}/fragment/`);
    const envelope: FusionEnvelope = await res.json();
    return this.decoder.decodeFragmentPointer(envelope);
  }

  async fetchPageData<T>(slug: string, renderFirst = false): Promise<T> {
    const params = renderFirst ? '?fusion_render_first=true' : '';
    const res = await fetch(`${API_BASE}/pages/${slug}/data/${params}`);
    const envelope: FusionEnvelope = await res.json();
    return this.decoder.unwrap(envelope);
  }

  async checkHealth(): Promise<{ fusion_render_first: boolean }> {
    const res = await fetch(`${API_BASE}/fusion/health`);
    const envelope: FusionEnvelope = await res.json();
    return this.decoder.unwrap(envelope);
  }
}

export const fusionApi = new FusionApiClient();
```

### 6.2 Frontend File Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with fusion middleware
│   │   ├── page.tsx            # Homepage with FusionProxy
│   │   ├── globals.css         # Tailwind + fusion theme
│   │   └── [slug]/
│   │       └── page.tsx        # Dynamic page route
│   ├── components/
│   │   ├── FusionProxy.tsx     # Renders HTML fragment or JSON data
│   │   ├── FusionPage.tsx      # Page-level fusion component
│   │   ├── Providers.tsx       # Redux/context providers
│   │   ├── Header.tsx          # Site header with navigation
│   │   ├── Footer.tsx          # Site footer
│   │   └── ErrorBoundary.tsx   # Error boundary
│   ├── lib/
│   │   ├── fusion-types.ts     # TypeScript types for fusion protocol
│   │   ├── fusion-decoder.ts   # FusionCodec TypeScript counterpart
│   │   ├── fusion-store.ts     # State management for fusion mode
│   │   └── api-client.ts       # Bolt API client
│   └── store/
│       └── index.ts            # Redux store setup
├── package.json
├── next.config.js
├── tsconfig.json
├── tailwind.config.js
└── postcss.config.js
```

---

## 7. CMS-Fusion Specific: Data APIs with Fallbacks

CMS-Fusion needs data APIs that work with both django-bolt and fallback to django-fusion renderer. The strategy:

### 7.1 Dual-Mode Endpoints

```python
# cms-fusion backend — www/api/pages.py
def page_data(request, slug):
    """Returns HTML or JSON depending on client preference."""
    render_first = _get_fusion_render_first_from_request(request)
    page = STATIC_PAGES.get(normalize_slug(slug))

    if render_first:
        # django-fusion path: render HTML
        return render_template("pages/page.html", page=page)
    else:
        # django-bolt path: return JSON via FusionCodec
        encoded = FusionCodec.encode(page)
        return fusion_json_response(data={"slug": slug, "encoded": encoded})
```

### 7.2 Fallback Chain

```
Frontend request
  ↓
Try bolt API (fast, JSON)
  ↓ failure
Try fusion health check
  ↓
Try fusion_render_first (HTML)
  ↓ failure
Show error boundary
```

### 7.3 Frontend Fallback Component

```tsx
// components/FusionProxy.tsx
export function FusionProxy({ slug }: { slug: string }) {
  const [mode, setMode] = useState<'bolt' | 'fusion' | 'error'>('bolt');
  const [content, setContent] = useState<FragmentPointer | null>(null);

  useEffect(() => {
    fusionApi.fetchFragment(slug)
      .then(setContent)
      .catch(async () => {
        // Fallback to fusion render-first
        setMode('fusion');
        try {
          const html = await fusionApi.fetchPageData(slug, true);
          setContent(html);
        } catch {
          setMode('error');
        }
      });
  }, [slug]);

  if (mode === 'error') return <ErrorFallback />;
  if (!content) return <Loading />;

  return mode === 'bolt'
    ? <PageRenderer data={content} />
    : <div dangerouslySetInnerHTML={{ __html: content }} />;
}
```

---

## 8. POS Bolt API Analysis

### 8.1 bolt_api.py Statistics

| Resource | Endpoints | Models | Auth |
|----------|:---------:|:------:|:----:|
| Health | 1 | — | None |
| Auth | 1 | TokenCreate | AllowAny |
| Categories | 5 | CategoryCreate/Update/Response | JWT+APIKey |
| Products | 5 | ProductCreate/Update/Response | JWT+APIKey |
| Customers | 5 | CustomerCreate/Update/Response | JWT+APIKey |
| Sales | 5 | SaleCreate/Update/Response | JWT+APIKey |
| Inventory | 5 | InventoryCreate/Update/Response | JWT+APIKey |
| Employees | 5 | EmployeeCreate/Update/Response | JWT+APIKey |

**Total:** 32 endpoints, ~30 struct types, dual auth

### 8.2 Performance Characteristics

- Rust-backed via `runbolt` — 60k+ RPS on Actix Web
- `msgspec.Struct` serialization — zero-copy JSON parsing
- In-process `TestClient` — no TCP overhead in tests

### 8.3 Frontend Consumption (POS Tauri)

```typescript
// POS Full uses fusion-store.ts + fusion-decoder.ts
import { fusionStore } from '@/lib/fusion-store';
import { FusionDecoder } from '@/lib/fusion-decoder';

// API calls go through the bolt sidecar
const response = await fetch('http://localhost:8765/bolt/products');
const data = await response.json();
```

---

## 9. Recommendations

### 9.1 Historical immediate recommendations

1. ✅ **Build out precis-lms and cms-fusion frontends** with full Next.js + Fusion types + bolt API client
2. ✅ **Add real BoltAPI endpoints** to both fusion backends via `apis.py`
3. ✅ **Create shared frontend lib** (`fusion-types.ts`, `fusion-decoder.ts`, `api-client.ts`)
4. ✅ **Add per-project bolt settings** (`FUSION_BOLT` dict in settings.py)
5. ⬜ **Mark migration plans as complete** once all items are verified

### 9.2 Retired short-term recommendations

These recommendations are closed and must not be implemented in django-fusion:

1. ~~Create `django_fusion.bolt` module with `FusionBoltAPI`~~ — removed
2. ~~Add `@fusion_endpoint` decorator~~ — removed
3. ~~Auto-generate OpenAPI schemas from fusion components~~ — project-owned
4. ~~Add `FusionBoltAuthBackend` for session→bolt auth bridge~~ — project-owned

### 9.3 Long-Term

1. Replace `runbolt` with direct Actix Web integration for fusion projects
2. Add WebSocket support for live fragment updates
3. Build a component registry that auto-discovers fusion+bolt endpoints
4. Server-sent events for fragment invalidation

---

## 10. Migration Checklist

| # | Item | precis-lms | cms-fusion |
|---|------|:----------:|:----------:|
| 1 | `django_fusion` in `INSTALLED_APPS` | ✅ | ✅ |
| 2 | Fusion branding context processor | ✅ | ✅ |
| 3 | Fusion health endpoint (`/api/fusion/health`) | ✅ | ✅ |
| 4 | Fragment pointer endpoint (`/api/pages/<slug>/fragment/`) | ✅ | ✅ |
| 5 | Page data endpoint (`/api/pages/<slug>/data/`) | ✅ | ✅ |
| 6 | `FusionCodec` encode/decode | ✅ | ✅ |
| 7 | `bolt_view` adapter pattern | ✅ | ✅ |
| 8 | Full Next.js frontend with fusion libs | 🟡 | 🟡 |
| 9 | Real `BoltAPI` with `@bolt.get/post` | 🟡 | 🟡 |
| 10 | `fu-` CSS rename in templates/styles | ✅ | ✅ |
| 11 | Per-project bolt settings (`FUSION_BOLT`) | 🟡 | 🟡 |
| 12 | Frontend bolt API client | 🟡 | 🟡 |
| 13 | Fallback rendering chain | 🟡 | 🟡 |
| 14 | Tests passing | ⬜ | ⬜ |

---

## 11. Legend

| Symbol | Meaning |
|:------:|---------|
| ✅ | Complete |
| 🟡 | In Progress |
| ⬜ | Not Started |
| ❌ | Blocked |
