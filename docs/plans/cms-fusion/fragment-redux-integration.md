# LMS Fragment + Redux Integration Plan
> **Tags:** #cms-fusion #fusion #frontend

> **Goal:** Make the `fusion_response()` fragment-pointer payload from the
> backend actually usable in the Next.js frontend, using the existing
> Redux Toolkit / RTK Query architecture already in place across all
> React projects.

---

## Table of Contents

1. [Cross-Project Integration Status](#1-cross-project-integration-status)
2. [Current State](#2-current-state)
3. [What We Need](#3-what-we-need)
4. [Package Enhancements](#4-package-enhancements)
5. [Frontend Middleware Architecture](#5-frontend-middleware-architecture)
6. [Multi-File Separation](#6-multi-file-separation)
7. [Decision Flow](#7-decision-flow)
8. [Implementation Steps](#8-implementation-steps)
9. [Completed Tasks](#9-completed-tasks)
10. [Not-Completed Tasks](#10-not-completed-tasks)
11. [Cross-Project Integration Roadmap](#11-cross-project-integration-roadmap)
12. [POS Integration](#12-pos-integration)
13. [Test Coverage](#13-test-coverage)
14. [Risks & Mitigations](#14-risks--mitigations)

---

## 1. Cross-Project Integration Status

This section maps django-fusion's fragment-rendering features across every
project in the monorepo that depends on django-fusion.  The goal is a single
source of truth for what has been integrated where, and what remains.

### 1.1 Projects Using django-fusion

| Project | Type | Framework | django-fusion Features Used | Integration Status |
|---------|------|-----------|----------------------------|--------------------|
| **LMS** (lms/cms) | Django CMS + Next.js frontend | Django + Next.js 14 | ``RoutableComponent``, ``FragmentComponent``, ``fusion_render_first``, ``FusionSessionChecker``, ``FusionCodec``, ``fusion_json_response``, `FusionDecoder` (TS), `FusionProxy`, `FusionPage`, ``RobynFusionChecker`` | ✅ Partial |
| **POS Full** (pos/pos-full) | Tauri desktop app + Robyn sidecar | Robyn + Django ORM + Tauri | ``DeviceToken``, ``DataToken`` sync, ``RobynFusionChecker``, `FusionDecoder` (TS vendored) | ✅ Partial |
| **POS Solo** (pos/pos-solo) | Tauri desktop app + Robyn sidecar | Robyn + Django ORM + Tauri | ``DeviceToken``, ``DataToken`` sync, ``RobynFusionChecker``, `FusionDecoder` (TS vendored) | ✅ Partial |
| **ceptor-ai** (libs/ceptor-ai) | Local reusable library | Django | ``Viewset``, ``PageHandler``, ``BaseService``, ``BaseStyledForm``, ``EmailTemplateRegistry`` | ✅ Inherited |
| **Portfolio** (projects/portfolio) | Portfolio site | Django + Wagtail | django-fusion via monorepo dependency | 🔄 Not audited |
| **Fusion CMS** (projects/fusion-cms) | Research site | Django + Wagtail | django-fusion via monorepo dependency | 🔄 Not audited |
| **Test suite** (tests/) | Unit/integration tests | pytest + Django | ``BaseTestCase``, ``AssertEmailMixin``, ``AssertHTMLMixin``, routable components | ✅ Active |

### 1.2 Feature Distribution Matrix

| Feature | django-fusion | LMS | POS Full | POS Solo | ceptor-ai |
|---------|---------------|-----|----------|----------|-----------|
| ``RoutableComponent`` | ✅ Core | ✅ Used | ❌ N/A | ❌ N/A | ✅ Used |
| ``FragmentComponent`` | ✅ Core | ✅ Used | ❌ N/A | ❌ N/A | ❌ N/A |
| ``fusion_render_first`` | ✅ Configurable | ✅ Integrated | ⏳ Planned | ⏳ Planned | ❌ N/A |
| ``FusionSessionChecker`` | ✅ Implemented | ✅ Backend | ✅ Robyn adapter | ✅ Robyn adapter | ❌ N/A |
| ``FusionCodec`` | ✅ Implemented | ✅ Used | ❌ N/A | ❌ N/A | ❌ N/A |
| ``fusion_json_response`` | ✅ Implemented | ✅ Used | ❌ N/A | ❌ N/A | ❌ N/A |
| ``FusionDecoder`` (TS) | ✅ Documented | ✅ src/lib/ | ✅ vendored copy | ✅ vendored copy | ❌ N/A |
| ``RobynFusionChecker`` | ❌ N/A | ❌ N/A | ✅ Implemented | ✅ Implemented | ❌ N/A |
| ``FusionProxy`` (TS) | ❌ N/A | ✅ Created | ⏳ Planned | ⏳ Planned | ❌ N/A |
| ``FusionPage`` (TS) | ❌ N/A | ✅ Created | ⏳ Planned | ⏳ Planned | ❌ N/A |
| ``FusionMiddleware`` (TS) | ❌ N/A | ✅ Created | ⏳ Planned | ⏳ Planned | ❌ N/A |
| ``fusion-types.ts`` (TS) | ❌ N/A | ✅ Created | ⏳ Planned | ⏳ Planned | ❌ N/A |
| ``StaticPageFragment`` | ❌ N/A | ✅ Created | ❌ N/A | ❌ N/A | ❌ N/A |
| ``page_data`` endpoint | ❌ N/A | ✅ Created | ⏳ Planned | ⏳ Planned | ❌ N/A |
| ``/fusion/health`` endpoint | ❌ N/A | ✅ Created | ✅ Created | ✅ Created | ❌ N/A |
| TS codec round-trip tests | ❌ N/A | ✅ 6 tests | ⏳ Planned | ⏳ Planned | ❌ N/A |

**Legend:** ✅ = Done  |  🔄 = Specified/planned  |  ⏳ = Not started  |  ❌ = Not applicable

### 1.3 Dependency Graph

```
django-fusion (libs/django-fusion/)
  ├── Provides: FusionSessionChecker, FusionCodec, fusion_json_response,
  │             RoutableComponent, FragmentComponent, fusion_render_first
  │
  ├── LMS (projects/lms/cms/)          ← consumes all fragment-rendering features
  │    └── LMS Frontend (lms/lms/)     ← FusionDecoder, FusionProxy, FusionPage
  │
  ├── POS Full (pos/pos-full/)         ← RobynFusionChecker, vendored FusionDecoder
  │    └── POS Full Tauri app          ← future: FusionProxy, FusionPage
  │
  ├── POS Solo (pos/pos-solo/)         ← RobynFusionChecker, vendored FusionDecoder
  │    └── POS Solo Tauri app          ← future: FusionProxy, FusionPage
  │
  ├── ceptor-ai (libs/ceptor-ai/)      ← core patterns (Viewset, PageHandler, etc.)
  │
  ├── Portfolio (projects/portfolio/)  ← not audited for fragment features
  │
  └── Fusion CMS (fusion-cms/)     ← not audited for fragment features
```

### 1.4 Detailed Gap Analysis Findings

The following gaps were identified during the code audit of all projects
against the latest django-fusion fragment-rendering features.

#### 1.4.1 Gap: Frontend Middleware (P1)

| Project | Issue | Impact |
|---------|-------|--------|
| LMS Frontend | ``FusionMiddleware.tsx`` was not created — no centralised context provider | Each page duplicated mode-decision logic; ``FusionPage`` had its own state management |
| LMS Frontend | ``fusion-types.ts`` not extracted — types inlined in ``fusion-decoder.ts`` | Unnecessary coupling; ``FusionMiddleware`` couldn't import types without importing the decoder class |
| LMS Frontend | ``FusionPage`` managed its own mode state | Prop-drilling required; no centralised error recovery |
| LMS Frontend | 4 static pages (home, about-us, faq, contact) still using raw data fetching | Not benefiting from fragment-rendering path |

**Status: ✅ P1 delivered — FusionMiddleware, fusion-types.ts, and simplified FusionPage are all created. Page migrations remain.**

#### 1.4.2 Gap: Backend Health Endpoints (P2)

| Project | Issue | Impact |
|---------|-------|--------|
| LMS Backend | No ``/fusion/health`` endpoint existed | Frontend had no way to discover session preference on first load |
| POS Full/ Solo | ``RobynFusionChecker`` not yet created | No ``/fusion/health`` endpoint, no DeviceToken-based preference check |
| POS Full/ Solo | ``FusionSessionChecker`` not adapted for Robyn's ``Request`` interface | ``FusionSessionChecker`` expects Django ``HttpRequest``; Robyn has different attribute names |

**Status: ✅ P2 delivered — ``fusion_health.py`` and ``RobynFusionChecker`` for both POS sidecars created.**

#### 1.4.3 Gap: POS Frontend Integration (P3)

| Project | Issue | Impact |
|---------|-------|--------|
| POS Full/ Solo | FusionDecoder ported but not wired into UI components | Session preference not actually used by Tauri pages |
| POS Full/ Solo | No FusionStore adapter existed | Tauri webview can't use ``sessionStorage``; no Tauri-compatible preference storage |
| POS Full/ Solo | No FusionProxy/FusionPage equivalents for Tauri | No way to fetch and render fragment HTML |
| POS Full/ Solo | ``/fusion/health`` not called on startup | Preference never seeded; always defaults to data mode |

**Status: 🔄 Partial — FusionStore created, /fusion/health endpoint exists, but startup wiring and Tauri UI components remain.**

#### 1.4.4 Gap: Unaudited Sites (P4)

| Project | Issue | Impact |
|---------|-------|--------|
| Portfolio | Not audited; django-fusion version unknown | May be pinned to an older version without fragment features |
| Fusion CMS | Not audited; django-fusion version unknown | Same risk as Portfolio |

**Status: 🔄 Not started — both sites need dependency check and feature audit.**

#### 1.4.5 Gap: Testing (P5)

| Layer | Issue | Impact |
|-------|-------|--------|
| Frontend | No unit tests for FusionMiddleware, FusionProxy, or FusionPage | Regression risk when refactoring |
| POS Backend | No unit tests for ``RobynFusionChecker`` | Cannot verify the 3-level check logic without a running sidecar |
| POS Backend | No integration test for ``/fusion/health`` | Cannot verify response shape in CI |
| Integration | No end-to-end fragment-fetch test | Cannot verify the full flow (backend → sidecar → frontend) |

**Status: 🔄 Not started — 37 backend + 12 LMS + 6 frontend tests exist, but no POS or middleware tests.**

---

## 2. Current State

### Backend (already implemented)

- `projects/lms/cms/www/api/data_adapter.py` exposes `fusion_response()`,
  which returns a canonical payload:

```json
{
  "component": "pages.home",
  "fragment_name": "pages.home",
  "fragment_url": "http://localhost:8000/fragments/pages.home/",
  "fusion_render_first": true,
  "page_slug": "home",
  "title": "Learn Without Limits"
}
```

- `projects/lms/cms/www/api/pages.py` exposes `page_fragment` and `page_data` views.
- `projects/lms/cms/www/api/data_adapter.py` exposes `fusion_response()` helper.
- A unified `GET /apis/pages/<slug>/data/` endpoint exists that serves either HTML
  (``?fusion_render_first=true``) or JSON with codec-encoded data (default).

### Frontend (current)

- Redux Toolkit + RTK Query set up in `src/store/`, `src/store/api/baseApi.ts`,
  and `src/store/api/endpoints/pages.ts`.
- Pages fetch JSON blocks via `useGetPageQuery('home')` from `/apis/pages/<slug>/`.
- **Four RTK Query endpoints** exist: `getPage`, `getPageFragment`, `getPageData`,
  `getPageHtml`.
- `FusionProxy` fetches HTML fragments from a URL and renders via `dangerouslySetInnerHTML`.
- `FusionPage` wrapper supports two modes:
  - **Legacy mode** (default): Two-step fragment-pointer → JSON fallback
  - **Unified mode** (`usePageDataEndpoint=true`): Single `page_data` request
- `FusionDecoder` class provides session health-check, codec decode, and envelope unwrap.
- `LoadingSkeleton`, `ErrorState`, and `EmptyState` components exist.

### Files layout (current)

```
src/
  components/
    FusionPage.tsx      # Page wrapper (two modes)
    FusionProxy.tsx     # HTML fragment fetcher/renderer
    ui/
      LoadingSkeleton.tsx
      ErrorState.tsx
  lib/
    fusion-decoder.ts   # FusionDecoder + types + session
  store/api/endpoints/
    pages.ts            # 4 RTK Query endpoints
```

---

## 3. What We Need

A clean, **middleware-driven** way for any page to:

1. **Decide at runtime** whether to render a server fragment or client React.
2. **Centralise the decision logic** so it's not duplicated across components.
3. **Survive errors gracefully** — if fragment fetch fails, fall back to JSON.
4. **Cache the decision** in `sessionStorage` so subsequent navigations don't
   re-query the backend for the same preference.

---

## 4. Package Enhancements

These changes make the fragment-pointer mechanism configurable, well-documented,
and reusable across any project using django-fusion (including the POS sidecar,
LMS, and future cloud edition sites).

### 4.1 Configurable `fusion_render_first` (default: `false` → get data)

The default rendering strategy is **get data** (`fusion_render_first: false`).
This means by default the API returns JSON blocks and the frontend renders
React components — the fragment-rendering path is only activated when
explicitly enabled.

**How the default flows through the stack:**

| Layer | Mechanism | Default |
|-------|-----------|---------|
| Django settings | ``COMPONENTS.FUSION_RENDER_FIRST_DEFAULT`` | ``False`` |
| ``RoutableComponent`` | ``get_fusion_render_first()`` classmethod → checks setting | ``False`` |
| ``fusion_response()`` helper | 4-level priority: param → ``get_fusion_render_first()`` → attribute → ``False`` | ``False`` |
| ``page_fragment`` endpoint | Calls ``fusion_response()`` without overriding | ``False`` |
| ``FragmentPointer`` payload | ``fusion_render_first`` field in JSON response | ``false`` |
| ``FusionMiddleware`` (frontend) | ``useFusionMode()`` hook → checks session → falls back to ``'data'`` | ``'data'`` |

To **enable** fragment-first rendering:

```python
# Project-wide: in settings.py
COMPONENTS = {
    "FUSION_RENDER_FIRST_DEFAULT": True,
}

# Per-component: override on the subclass
class PrivacyPageFragment(RoutableComponent):
    fusion_render_first = True
```

### 4.2 Standardized JSON Renderer

```python
from django_fusion.routes.rendering.renderers import fusion_json_response
```

The response envelope:

```json
{
  "status": 200,
  "message": "Success",
  "data": { ... }
}
```

### 4.3 Session Health Check (`FusionSessionChecker`)

Caches ``fusion_render_first`` preference in Django session (7-day expiry).
Default heuristic: browser UA = ``True``, programmatic clients = ``False``.
Custom ``check_fn`` callable injectable via constructor.

### 4.4 Encoder / Decoder Codec

Format: ``fusion_v<version>:<base64-json>``

Backend: ``FusionCodec.encode()`` / ``FusionCodec.decode()``
Frontend: ``FusionDecoder.decode()`` / ``FusionDecoder.decodeAs<T>()``

The codec is versioned (``fusion_v1:`` prefix) for backward-compatible upgrades.

---

## 5. Frontend Middleware Architecture

The core enhancement is a **React Context middleware** that centralises the
"API vs Fragment" decision. This replaces the ad-hoc state logic inside
individual components with a single source of truth.

### 5.1 FusionMiddleware (Context Provider)

**File:** `src/components/FusionMiddleware.tsx`

A React context provider that wraps the application (or a subtree) and:

1. **Initialises** the ``fusion_render_first`` preference from ``sessionStorage``
   on mount.
2. **Provides** a ``useFusionMode()`` hook that returns the current mode:
   - ``'fragment'`` — the session says "render server fragments first"
   - ``'data'`` — the session says "fetch JSON data and render React"
   - ``'loading'`` — still initialising
3. **Handles errors** via a callback that flips the mode from ``fragment`` to
   ``data`` when a fragment fetch fails, storing the new preference.
4. **Listens** for ``fusion_render_first`` events dispatched by ``FusionProxy``
   to mode-switch without prop-drilling.

```tsx
// src/components/FusionMiddleware.tsx
'use client';

import {
  createContext,
  useContext,
  useCallback,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import { fusionDecoder } from '@/lib/fusion-decoder';

export type FusionMode = 'fragment' | 'data' | 'loading';

interface FusionContextValue {
  mode: FusionMode;
  fallbackToData: () => void;
  enableFragments: () => void;
}

const FusionContext = createContext<FusionContextValue>({
  mode: 'loading',
  fallbackToData: () => {},
  enableFragments: () => {},
});

export function FusionMiddleware({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<FusionMode>('loading');

  useEffect(() => {
    const pref = fusionDecoder.getSessionPreference();
    if (pref === true) {
      setMode('fragment');
    } else {
      // Default to data mode (false or undefined)
      setMode('data');
    }
  }, []);

  const fallbackToData = useCallback(() => {
    fusionDecoder.clearSession();
    fusionDecoder.initSession(false);
    setMode('data');
  }, []);

  const enableFragments = useCallback(() => {
    fusionDecoder.initSession(true);
    setMode('fragment');
  }, []);

  return (
    <FusionContext.Provider value={{ mode, fallbackToData, enableFragments }}>
      {children}
    </FusionContext.Provider>
  );
}

export function useFusionMode(): FusionContextValue {
  return useContext(FusionContext);
}
```

### 5.2 How Components Use the Middleware

**FusionPage** becomes simpler — it reads the mode from context instead of
managing its own state:

```tsx
// src/components/FusionPage.tsx (simplified)
export function FusionPage({ slug, children, ... }: FusionPageProps) {
  const { mode, fallbackToData } = useFusionMode();

  if (mode === 'loading') return <LoadingSkeleton />;

  if (mode === 'fragment') {
    return (
      <FusionProxy
        fragmentUrl={`/apis/pages/${slug}/data/?fusion_render_first=true`}
        onError={fallbackToData}
        enableScripts={enableScripts}
        errorFallback={errorFallback}
      />
    );
  }

  // Data mode: decode codec-encoded data
  const { data: pageData, isLoading, error } = useGetPageDataQuery(slug);
  // ... decode and render
}
```

**FusionProxy** dispatches an event on error so the middleware hears it:

```tsx
// Inside FusionProxy's catch block
.catch(() => {
  if (!cancelled) {
    setHasError(true);
    setIsLoading(false);
    onError?.();  // Calls fallbackToData from middleware
  }
});
```

### 5.3 Middleware Decision Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                    FusionMiddleware (Context)                      │
│                                                                   │
│  Mount → fusionDecoder.getSessionPreference()                     │
│             │                                                     │
│     ┌───────┴───────┐                                            │
│     ▼               ▼                                             │
│   true           false/undefined                                  │
│     │               │                                             │
│     ▼               ▼                                             │
│  mode='fragment'  mode='data'                                     │
│     │               │                                             │
│     ▼               ▼                                             │
│  FusionPage →      FusionPage →                                  │
│  FusionProxy       useGetPageDataQuery                            │
│     │               │                                             │
│     │ error          │ success                                    │
│     ▼               ▼                                             │
│  fallbackToData()  decode & render children                       │
│  (sets mode='data')                                               │
└──────────────────────────────────────────────────────────────────┘
```

### 5.4 Benefits of Middleware Approach

| Benefit | Description |
|---------|-------------|
| **Single source of truth** | The mode lives in context, not in component state. |
| **No prop drilling** | Any component in the tree can call ``useFusionMode()``. |
| **Centralised error recovery** | ``fallbackToData()`` flips the mode globally. |
| **Testable** | The context can be mocked in unit tests. |
| **Portable** | ``FusionMiddleware`` can be wrapped around any subtree. |
| **Consistent UX** | All pages use the same decision logic. |

---

## 6. Multi-File Separation

### 6.1 Proposed File Layout

To keep the codebase clean and maintainable, the frontend pieces should be
separated into distinct files with single responsibilities:

```
src/
  components/
    FusionMiddleware.tsx    # Context provider + useFusionMode hook
    FusionProxy.tsx         # HTML fragment fetcher/renderer (standalone)
    FusionPage.tsx          # Page wrapper (reads mode from middleware)
  lib/
    fusion-decoder.ts       # FusionDecoder class (codec + session)
    fusion-types.ts         # Shared TypeScript interfaces/enums
  store/api/endpoints/
    pages.ts                # RTK Query endpoints (4 queries)
```

### 6.2 FusionTypes (`src/lib/fusion-types.ts`)

Extract shared types from `fusion-decoder.ts` into a standalone file so both
`FusionMiddleware` and `FusionPage` can import them without importing the
entire decoder class:

```ts
// src/lib/fusion-types.ts

/** Top-level response envelope. */
export interface FusionEnvelope<T = unknown> {
  status: number;
  message: string;
  data: T;
}

/** Fragment pointer as returned by /apis/pages/<slug>/fragment/. */
export interface FragmentPointer {
  component: string;
  fragment_name: string;
  fragment_url: string;
  fusion_render_first: boolean;
  page_slug?: string;
  title?: string;
  [key: string]: unknown;
}

/** Codec payload structure. */
export interface CodedPayload {
  encoded: string;
  version: string;
  b64: string;
}

/** Rendering mode, used by FusionMiddleware. */
export type FusionMode = 'fragment' | 'data' | 'loading';
```

### 6.3 FusionMiddleware (`src/components/FusionMiddleware.tsx`)

New file. Provides the context with:
- ``mode: FusionMode`` — the current rendering mode
- ``fallbackToData()`` — switch from fragment to data mode
- ``enableFragments()`` — switch from data to fragment mode

### 6.4 FusionProxy (`src/components/FusionProxy.tsx`)

Unchanged. Originally separate, already has single responsibility.

### 6.5 FusionPage (`src/components/FusionPage.tsx`)

Simplified. Removes mode-state management (delegates to middleware).
Supports both:
- **Middleware mode** (default): reads from ``useFusionMode()`` context
- **Standalone mode**: manages its own mode (backward compat via prop)

### 6.6 FusionDecoder (`src/lib/fusion-decoder.ts`)

Unchanged. Remove the type exports that moved to ``fusion-types.ts``.

---

## 7. Decision Flow

### 7.1 Full Decision Matrix

The frontend middleware evaluates the following inputs to decide the mode:

```
┌──────────────────────────────┐
│        Decision Inputs        │
├──────────────────────────────┤
│ 1. SessionStorage preference │  (persistent across navigations)
│ 2. Page slug                 │  (some pages may force data mode)
│ 3. User role / device type   │  (admin vs. customer)
│ 4. URL query param override  │  (?fusion_render_first=false)
│ 5. Network condition         │  (offline → force data mode)
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     FusionMiddleware         │
│                              │
│  priority:                   │
│  1. URL override (highest)   │
│  2. Session preference       │
│  3. Page slug overrides      │
│  4. Default (false → data)   │
└──────────────┬───────────────┘
               │
               ▼
     ┌─────────────────┐
     │   mode: FusionMode │
     │ 'fragment' | 'data'│
     └─────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
  [fragment]         [data]
      │                 │
      ▼                 ▼
  FusionProxy      useGetPageDataQuery
      │                 │
      ▼                 ▼
  render HTML       decode codec →
  via innerHTML     render React
```

### 7.2 Priority Order

1. **URL query param** ``?fusion_render_first=true|false`` overrides everything
2. **SessionStorage** preference (set by previous health check or user action)
3. **Page slug overrides** (e.g., ``privacy`` page always uses data mode)
4. **Default**: ``false`` → data mode

### 7.3 Error Recovery

When ``FusionProxy`` fails to fetch/render a fragment:

1. ``onError`` callback fires → calls ``fallbackToData()`` on the middleware
2. Middleware calls ``fusionDecoder.clearSession()`` + ``fusionDecoder.initSession(false)``
3. Sets ``mode='data'`` in context
4. ``FusionPage`` re-renders, fetches JSON data instead
5. On the **next** navigation, the session still says ``false``, so the mode
   stays ``'data'`` — avoids repeated failures

---

## 8. Implementation Steps

### ✅ Step 8.1 — Add RTK Query endpoints (done)

Four endpoints in `src/store/api/endpoints/pages.ts`:

| Endpoint | URL | Returns |
|----------|-----|---------|
| ``getPage`` | ``/apis/pages/<slug>/`` | ``CmsPage`` JSON |
| ``getPageFragment`` | ``/apis/pages/<slug>/fragment/`` | ``FragmentPointer`` (unwrapped) |
| ``getPageData`` | ``/apis/pages/<slug>/data/`` | ``PageDataResponse`` (unwrapped) |
| ``getPageHtml`` | ``/apis/pages/<slug>/data/?fusion_render_first=true`` | Raw HTML string |

### ✅ Step 8.2 — Create FusionProxy (done)

Fetches HTML from a URL, renders via `dangerouslySetInnerHTML`.
Handles loading, error, and optional script re-evaluation.

### ✅ Step 8.3 — Create FusionPage with dual modes (done)

Supports legacy two-step (fragment → JSON) and unified page_data endpoint.
`usePageDataEndpoint` prop switches between modes.

### ✅ Step 8.4 — Create FusionMiddleware (done)

React context provider that centralises the fragment-vs-data decision.
See [Section 4](#4-frontend-middleware-architecture) for full spec.

### ✅ Step 8.5 — Extract fusion-types.ts (done)

Move shared type definitions from `fusion-decoder.ts` into a standalone file.

### ✅ Step 8.6 — Simplify FusionPage to use middleware (done)

Make middleware the default; keep standalone mode as fallback.

### 🔄 Step 8.7 — Migrate remaining static pages (pending)

Wrap `home`, `about-us`, `faq`, `contact` with `FusionPage` using middleware.

### ✅ Step 8.8 — Backend fragment registration (done)

Register ``RoutableComponent`` subclasses for all static pages.

### 🔄 Step 8.9 — Frontend tests (pending)

Unit tests for ``FusionMiddleware``, ``FusionProxy``, ``FusionPage`.

---

## 9. Completed Tasks

### Backend

| Task | Status | Files |
|------|--------|-------|
| ``fusion_response()`` helper | ✅ Done | ``www/api/data_adapter.py`` |
| ``page_fragment`` endpoint | ✅ Done | ``www/api/pages.py`` |
| ``page_data`` unified endpoint | ✅ Done | ``www/api/pages.py``, ``urls.py`` |
| Generic page template | ✅ Done | ``templates/pages/page.html`` |
| ``PrivacyPageFragment`` | ✅ Done | ``plugins/lms/components.py`` |
| ``FusionSessionChecker`` | ✅ Done | ``libs/django-fusion/.../session.py`` |
| ``FusionCodec`` encoder/decoder | ✅ Done | ``libs/django-fusion/.../session.py`` |
| ``fusion_json_response`` renderer | ✅ Done | ``libs/django-fusion/.../renderers.py`` |
| Backend tests (page endpoints) | ✅ Done | ``tests/test_pages.py`` (12 tests) |
| Backend tests (codec + session) | ✅ Done | ``tests/test_routes_renderers.py`` (37 tests) |

### Frontend

| Task | Status | Files |
|------|--------|-------|
| RTK Query endpoints (4 queries) | ✅ Done | ``src/store/api/endpoints/pages.ts`` |
| ``FusionProxy`` component | ✅ Done | ``src/components/FusionProxy.tsx`` |
| ``FusionPage`` wrapper (dual mode) | ✅ Done | ``src/components/FusionPage.tsx`` |
| ``FusionDecoder`` class | ✅ Done | ``src/lib/fusion-decoder.ts`` |
| ``FusionMiddleware`` component | ✅ Done | ``src/components/FusionMiddleware.tsx`` |
| ``fusion-types.ts`` extracted | ✅ Done | ``src/lib/fusion-types.ts`` |
| ``FusionPage`` simplified (middleware default) | ✅ Done | ``src/components/FusionPage.tsx`` |
| Privacy page proof-of-concept | ✅ Done | ``src/app/privacy/page.tsx`` |
| ``FusionDecoder`` port to POS | ✅ Done | ``pos-full/``, ``pos-solo/`` |
| ``FusionStore`` adapter for POS | ✅ Done | ``pos-full/``, ``pos-solo/`` (``fusion-store.ts``) |
| ``/fusion/health`` endpoint (LMS + POS) | ✅ Done | ``fusion_health.py``, ``middleware/fusion.py`` |
| ``RobynFusionChecker`` integration | ✅ Done | ``middleware/fusion.py`` (both POS) |
| TS codec round-trip tests | ✅ Done | ``tests/fusion-decoder-roundtrip.test.mjs`` (6 tests) |

---

## 10. Not-Completed Tasks

### 10.1 Frontend (Pending)

| Task | Section | Priority | Notes |
|------|---------|----------|-------|
| Migrate ``home`` page to ``FusionPage`` | [§8.7](#-step-87--migrate-remaining-static-pages-pending) | High | ``app/page.tsx`` |
| Migrate ``about-us`` page | [§8.7](#-step-87--migrate-remaining-static-pages-pending) | High | ``app/about-us/page.tsx`` |
| Migrate ``faq`` page | [§8.7](#-step-87--migrate-remaining-static-pages-pending) | High | ``app/faq/page.tsx`` |
| Migrate ``contact`` page | [§8.7](#-step-87--migrate-remaining-static-pages-pending) | High | ``app/contact/page.tsx`` |
| Wire ``FusionStore`` + ``/fusion/health`` into POS app startup | [§11.4](#114-phase-3-pos-frontend-integration) | High | ``App.tsx`` or Tauri entry |
| Create ``FusionProxy`` for Tauri (``innerHTML``) | [§11.4](#114-phase-3-pos-frontend-integration) | Medium | Components for POS editions |
| Frontend tests for ``FusionMiddleware`` | [§8.9](#-step-89--frontend-tests-pending) | Medium | Mock context provider |
| Frontend tests for ``FusionProxy`` + ``FusionPage`` | [§8.9](#-step-89--frontend-tests-pending) | Medium | Mock fetch + RTK Query |

### 10.2 Backend (Pending)

| Task | Priority | Notes |
|------|----------|-------|
| Move ``STATIC_PAGES`` to shared module | Medium | ``plugins/pages/content.py`` |
| Create ``FusionMiddleware``-compatible health-check endpoint | Low | Return session pref as JSON |

### 10.3 POS Integration (Pending)

| Task | Priority | Notes |
|------|----------|-------|
| Wire ``FusionDecoder`` into Tauri pages | Low | ``innerHTML`` injection |
| Add ``check_fn`` customisation for device tokens | Low | ``FusionSessionChecker`` |

---

## 11. Cross-Project Integration Roadmap

This section lays out a phased roadmap for completing django-fusion fragment
integration across all projects.  Each phase builds on the previous one,
and dependencies are explicitly noted.

### 11.1 Phases Overview

| Phase | Focus | Projects Affected | Estimated Effort |
|-------|-------|-------------------|------------------|
| **P1** | LMS frontend middleware | LMS | 2-3 days |
| **P2** | Backend fragment registration & POS health checks | LMS, POS Full, POS Solo | 1-2 days |
| **P3** | POS frontend integration | POS Full, POS Solo | 3-4 days |
| **P4** | Portfolio & Fusion CMS audit | Portfolio, Fusion CMS | 1-2 days |
| **P5** | Testing & hardening | All | 2-3 days |

---

### 11.2 Phase 1: LMS Frontend Middleware

**Goal:** Complete the ``FusionMiddleware`` context provider and migrate all
LMS static pages to the middleware-driven pattern.

| Task | Depends On | Priority |
|------|-----------|----------|
| ✅ Create ``FusionMiddleware`` TSX component | None | High |
| ✅ Extract ``fusion-types.ts`` from ``fusion-decoder.ts`` | None | Medium |
| ✅ Simplify ``FusionPage`` to use middleware by default | ``FusionMiddleware`` | High |
| 🔄 Migrate ``home`` page | ``FusionPage`` simplified | High |
| 🔄 Migrate ``about-us`` page | ``FusionPage`` simplified | High |
| 🔄 Migrate ``faq`` page | ``FusionPage`` simplified | High |
| 🔄 Migrate ``contact`` page | ``FusionPage`` simplified | High |
| ✅ Wire ``/fusion/health`` endpoint for session seeding | Backend endpoint | Low |

**Dependencies:**
- ✅ ``FusionMiddleware`` created
- ✅ ``fusion-types.ts`` extracted
- ✅ ``FusionPage`` simplified
- 🔄 Page migrations depend on ``FusionPage`` simplification

---

### 11.3 Phase 2: Backend & Sidecar Integration

**Goal:** Complete backend registration and sidecar health checks.

#### 11.3.1 LMS Backend (already done)

| Fragment | Status |
|----------|--------|
| ``StaticPageFragment("home")`` | ✅ Registered |
| ``StaticPageFragment("about-us")`` | ✅ Registered |
| ``StaticPageFragment("faq")`` | ✅ Registered |
| ``StaticPageFragment("contact")`` | ✅ Registered |
| ``PrivacyPageFragment`` | ✅ Registered |
| Move ``STATIC_PAGES`` to shared module | 🔄 Pending |

#### 11.3.2 POS Sidecar (already done)

| Feature | Status |
|---------|--------|
| ``RobynFusionChecker`` class | ✅ Created |
| ``/fusion/health`` endpoint | ✅ Registered |
| DeviceToken-based ``check_fn`` | ✅ Default (admin/manager → True) |
| Custom ``check_fn`` injection | ✅ Supported via constructor |

#### 11.3.3 POS Backend Fragments (pending)

| Task | Fragment Name | Priority |
|------|---------------|----------|
| Register ``ProductDetailFragment`` | ``products.detail`` | Medium |
| Register ``InventoryFormFragment`` | ``inventory.adjust`` | Low |
| Register ``CustomerProfileFragment`` | ``customers.profile`` | Low |
| Expose fragment pointers in CRUD responses | — | Medium |

---

### 11.4 Phase 3: POS Frontend Integration

**Goal:** Wire the vendored ``FusionDecoder`` into the Tauri UI, create
POS equivalents of ``FusionProxy`` and ``FusionPage`` with a
Tauri-compatible state management for the session preference.

| Task | Files | Priority |
|------|-------|----------|
| Create ``FusionProxy`` for Tauri (``innerHTML`` injection) | ``src/components/FusionProxy.tsx`` (pos-full, pos-solo) | Medium |
| Create ``FusionPage`` for Tauri (read preference from local store) | ``src/components/FusionPage.tsx`` (pos-full, pos-solo) | Medium |
| Add ``@tauri-apps/plugin-store`` dependency | ``package.json`` (pos-full, pos-solo) | Medium |
| Create ``FusionStore`` adapter (local storage instead of ``sessionStorage``) | ``src/lib/fusion-store.ts`` (pos-full, pos-solo) | Medium |
| Wire ``/fusion/health`` endpoint into app startup | ``src-tauri/src/main.rs`` or ``App.tsx`` | High |
| Add fragment-pointer unwrapping to RTK Query endpoints | ``src/store/api/endpoints/*.ts`` | Low |

**Dependencies:**
- ``FusionDecoder`` is vendored ✅
- ``/fusion/health`` endpoint exists ✅
- ``FusionProxy`` and ``FusionPage`` can be adapted from LMS versions

---

### 11.5 Phase 4: Portfolio & Fusion CMS Audit

**Goal:** Audit remaining Django sites for django-fusion usage and identify
where fragment-rendering features can benefit them.

| Task | Project | Effort |
|------|---------|--------|
| Audit ``pyproject.toml`` for django-fusion version | Portfolio | 0.5 day |
| Audit existing views/components for fragment candidates | Portfolio | 0.5 day |
| Audit ``pyproject.toml`` for django-fusion version | Fusion CMS | 0.5 day |
| Audit existing views/components for fragment candidates | Fusion CMS | 0.5 day |
| Add ``robots.txt`` / ``sitemap.xml`` considerations | Both | 0.5 day |

**Note:** These sites may not need fragment rendering at all — the audit
will determine whether integration is warranted.

---

### 11.6 Phase 5: Testing & Hardening

**Goal:** Comprehensive test coverage for fragment-rendering features
across all layers (backend codec, backend session, frontend decoder,
frontend middleware, frontend proxy, integration).

| Layer | Suite | Tests | Status |
|-------|-------|-------|--------|
| **Backend** | ``test_routes_renderers.py`` (django-fusion) | 37 | ✅ |
| **Backend** | ``test_pages.py`` (LMS CMS) | 12 | ✅ |
| **Frontend** | TS codec round-trip | 6 | ✅ |
| **Frontend** | ``FusionMiddleware`` unit tests | — | 🔄 |
| **Frontend** | ``FusionProxy`` unit tests | — | 🔄 |
| **Frontend** | ``FusionPage`` unit tests | — | 🔄 |
| **POS** | ``RobynFusionChecker`` unit tests | — | 🔄 |
| **POS** | ``/fusion/health`` endpoint integration test | — | 🔄 |
| **POS** | ``FusionDecoder`` POS integration test | — | 🔄 |
| **Integration** | End-to-end fragment fetch + render test | — | 🔄 |

**Priority test targets:**
1. ``FusionMiddleware`` — mock context, verify ``fallbackToData()`` flips mode
2. ``FusionProxy`` — mock ``fetch``, verify HTML injection and ``onError``
3. ``RobynFusionChecker`` — mock ``get_token_info()``, verify all 3 check paths
4. ``/fusion/health`` — curl against running sidecar, verify response shape

---

### 11.7 Key Dependencies & Blocker

| Blocker | Affects | Description |
|---------|---------|-------------|
| ✅ ``FusionMiddleware`` created | P1, P3 | Completed — no longer a blocker |
| ``RobynFusionChecker`` lacks unit tests | P3, P5 | Need pytest with mock ``get_token_info()`` |
| POS frontend ``FusionStore`` not wired into app startup | P3 | ``App.tsx`` or ``main.rs`` not updated yet |
| POS sidecar has no component routing | P2 | ``FragmentComponent`` requires django-fusion routing |
| Tauri ``@tauri-apps/plugin-store`` dependency optional | P3 | ``FusionStore`` handles gracefully with fallback |
| Portfolio & Fusion CMS django-fusion version unknown | P4 | May be on older version without fragment features |
| No frontend test framework configured | P5 | Need to decide on Jest vs. Vitest |

---

## 12. POS Integration

### 12.1 Transport Layer Comparison

| Aspect | LMS (Next.js) | POS (Tauri + Sidecar) |
|--------|---------------|----------------------|
| HTTP client | RTK Query (``fetchBaseQuery``) | ``tauri-plugin-http`` or raw ``fetch`` |
| API base URL | ``NEXT_PUBLIC_API_URL`` env var | Sidecar port (e.g. ``localhost:8766``) |
| Auth | Bearer token in ``prepareHeaders`` | ``DeviceToken`` from sidecar models |
| Fragment fetch | ``FusionProxy`` component | ``<webview>`` or ``innerHTML`` injection |
| Session storage | Browser ``sessionStorage`` | ``FusionStore`` adapter → Tauri plugin or in-memory map |
| Middleware | ``FusionMiddleware`` (React context) | ``FusionStore`` (async API, Tauri-compatible) |

### 12.2 Fragment-Pointer in POS

POS endpoints can return fragment pointers alongside JSON data:

```json
{
  "status": 200,
  "message": "Success",
  "data": {
    "product": { "id": 1, "name": "Cappuccino", "price": "5.50" },
    "_fusion": {
      "component": "products.detail",
      "fragment_name": "products.detail_form",
      "fragment_url": "/fragments/products.detail_form/",
      "fusion_render_first": false
    }
  }
}
```

### 12.3 FusionDecoder Ported to POS

The ``FusionDecoder`` class has been ported to both POS projects:

- ``projects/pos/pos-full/src/lib/fusion-decoder.ts``
- ``projects/pos/pos-solo/src/lib/fusion-decoder.ts``

Both pass TypeScript typecheck (``tsc --noEmit`` exit code 0).

### 12.4 FusionStore Adapter (NEW)

A Tauri-compatible session preference storage adapter with:
- ``initSession(value)`` / ``getSessionPreference()`` / ``clearSession()`` API mirroring ``FusionDecoder``
- ``initFromHealthCheck(sidecarUrl)`` — fetches ``/fusion/health`` and caches the preference
- Auto-detection: tries ``@tauri-apps/plugin-store`` first, falls back to in-memory ``Map``

Files:
- ``projects/pos/pos-full/src/lib/fusion-store.ts``
- ``projects/pos/pos-solo/src/lib/fusion-store.ts``

### 12.5 RobynFusionChecker Health Endpoint (NEW)

Both POS sidecars expose ``GET /fusion/health`` via ``RobynFusionChecker``:
- **3-level check:** custom ``check_fn`` → DeviceToken role (admin/manager → True) → User-Agent heuristic
- Returns ``{fusion_render_first: boolean, reason: string}`` response

Files:
- ``projects/pos/pos-full/sidecar/middleware/fusion.py``
- ``projects/pos/pos-solo/sidecar/middleware/fusion.py``

---

## 13. Test Coverage

### 12.1 Backend Tests

| Suite | Tests | Status |
|-------|-------|--------|
| ``test_routes_renderers.py`` (django-fusion) | 37 | ✅ All passing |
| ``test_pages.py`` (LMS CMS) | 12 | ✅ All passing |

### 12.2 Frontend Tests

| Suite | Tests | Status |
|-------|-------|--------|
| TS codec round-trip | 6 | ✅ All passing |
| ``FusionMiddleware`` unit tests (mock context, verify mode flips) | — | 🔄 Not started |
| ``FusionProxy`` unit tests (mock fetch, verify HTML injection & error) | — | 🔄 Not started |
| ``FusionPage`` unit tests (mock RTK Query, verify three paths) | — | 🔄 Not started |

### 12.3 TypeScript Typecheck

| Project | Status |
|---------|--------|
| LMS (``tsc --noEmit``) | ✅ Passes |
| POS Full (``tsc --noEmit``) | ✅ Passes |
| POS Solo (``tsc --noEmit``) | ✅ Passes |

---

## 14. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| ``dangerouslySetInnerHTML`` XSS | Only fetch from the same backend; sanitize in Django templates. |
| Fragment fetch fails / CORS | ``FusionProxy`` calls ``onError`` → middleware flips to data mode. |
| Middleware flash of loading state | Show ``LoadingSkeleton`` immediately; prefer SSR where possible. |
| Context re-render overhead | ``useCallback`` wrappers keep references stable. |
| HTMX/scripts in fragments don't run | Script re-evaluation utility in ``FusionProxy``. |
| Circular dependency if fragment API calls itself | Keep fragment endpoints stateless and read-only. |
| SessionStorage cleared by user | Next navigation re-evaluates, defaults to data mode. |
| Backend fragment not registered | ``FusionPage`` gracefully falls back to data mode. |
