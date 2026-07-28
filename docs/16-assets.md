# Assets Pipeline — DF-016

> Source of truth: `src/django_fusion/core/assets/views.py`,
> `src/django_fusion/core/assets/urls.py`,
> `src/django_fusion/comp/templatetags/fusion_assets.py`.

## Overview

The assets module provides API endpoints that describe which CSS, font,
and JS assets should be loaded by the frontend. Designed for
**Next.js + django-fusion** architectures where Wagtail/Django controls
the asset manifest and the Next.js frontend fetches it at runtime.

Top assets (CSS, fonts) are handled at **build time** via static imports
in `layout.tsx`. Bottom assets (deferred JS) are **fetched at runtime**
via the `/fusion/assets/manifest/` endpoint.

## Views

| Class | URL | Returns | Status codes |
|-------|-----|---------|--------------|
| `AssetsTopView` | `/fusion/assets/top/` | `{"status":"ok","data":{"css":[...],"fonts":[...],...}}` | `200` |
| `AssetsBottomView` | `/fusion/assets/bottom/` | `{"status":"ok","data":{"js":[...],"inline_js":[...]}}` | `200` |
| `AssetsManifestView` | `/fusion/assets/manifest/` | combined top + bottom manifest | `200` |

## Wiring

```python
# urls.py
from django_fusion.core.assets import urls as assets_urls

urlpatterns = [
    # ... other routes ...
    path("fusion/assets/", include(assets_urls)),
]
```

This exposes three endpoints:

| Endpoint | Purpose |
|----------|---------|
| `GET /fusion/assets/top/` | CSS links, font preloads, preconnect hints for `<head>` |
| `GET /fusion/assets/bottom/` | JS scripts for before `</body>` |
| `GET /fusion/assets/manifest/` | Full manifest (top + bottom) |

## Configuration

Configure via `FUSION_ASSETS` in Django settings:

```python
FUSION_ASSETS = {
    "top": {
        "css": [
            "/static/css/fusion.css",
        ],
        "fonts": [
            "/static/fonts/remixicon/remixicon.css",
            "/static/fonts/fontawesome-free/css/all.min.css",
        ],
        "preconnect": [
            "https://fonts.googleapis.com",
        ],
        "inline_css": [],
    },
    "bottom": {
        "js": [
            "/static/js/fusion-bridge.js",
        ],
        "inline_js": [],
    },
}
```

### Default values

If `FUSION_ASSETS` is not configured, all asset arrays default to empty
lists — the endpoints return empty manifests and the frontend degrades
gracefully.

## Response shape (JSON)

### Top assets

```json
{
  "status": "ok",
  "data": {
    "css": ["/static/css/fusion.css"],
    "fonts": ["/static/fonts/remixicon/remixicon.css"],
    "preconnect": ["https://fonts.googleapis.com"],
    "inline_css": []
  }
}
```

### Bottom assets

```json
{
  "status": "ok",
  "data": {
    "js": ["/static/js/fusion-bridge.js"],
    "inline_js": []
  }
}
```

### Full manifest

```json
{
  "status": "ok",
  "data": {
    "top": {
      "css": ["/static/css/fusion.css"],
      "fonts": ["/static/fonts/remixicon/remixicon.css"],
      "preconnect": ["https://fonts.googleapis.com"],
      "inline_css": []
    },
    "bottom": {
      "js": ["/static/js/fusion-bridge.js"],
      "inline_js": []
    }
  }
}
```

## Template Tags

The `fusion_assets` template tag library provides server-side asset
injection for Django/Wagtail templates:

```django
{% load fusion_assets %}

<head>
    {% fusion_top_assets %}       <!-- CSS links + font preloads -->
    {% fusion_assets_manifest %}  <!-- JSON manifest <script> block -->
</head>
<body>
    ...
    {% fusion_bottom_assets %}    <!-- JS scripts before </body> -->
</body>
```

| Tag | Output |
|-----|--------|
| `{% fusion_top_assets %}` | `<link rel="preconnect">`, `<link rel="stylesheet">`, `<style>` blocks |
| `{% fusion_bottom_assets %}` | `<script src="..." defer>`, inline `<script>` blocks |
| `{% fusion_assets_manifest %}` | `<script>window.__FUSION_ASSETS__ = {...};</script>` |

The manifest tag injects `window.__FUSION_ASSETS__` so the Next.js
`FusionAssets` component can hydrate without a second API call when
server-rendered with `fusion_render_first=True`.

## Next.js Integration

The `FusionAssets` component fetches the manifest from the backend and
dynamically injects scripts:

```tsx
// layout.tsx
import FusionAssets from '@/components/FusionAssets';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <ErrorBoundary>
            <Header />
            <main>{children}</main>
            <Footer />
          </ErrorBoundary>
          <FusionAssets />
        </Providers>
      </body>
    </html>
  );
}
```

Key behaviors:
- **Top assets** (CSS, fonts) → handled at build time via `import '../styles/theme/fusion-theme.scss'` — not fetched from API
- **Bottom assets** (JS) → fetched from `/fusion/assets/manifest/` and injected before `</body>`
- **Graceful degradation** → if the API is unreachable, the component renders nothing and the app still works with locally bundled assets
- **Server-side hydration** → if `window.__FUSION_ASSETS__` exists (injected by `{% fusion_assets_manifest %}`), the API call is skipped

## Design rationale

| Asset type | Loading strategy | Why |
|-----------|-----------------|-----|
| CSS (fusion-theme.scss) | Build-time static import | Needed before first paint — client-side injection is too late |
| Fonts (Inter, remixicon) | Build-time static import | Performance — font loading should not wait for API response |
| JS (fusion-bridge.js) | Runtime API fetch | Deferred scripts don't block rendering; backend can change manifest without rebuild |

## Cross-references

- [DF-009 Health Checks](./09-health.md) — the health module beside which assets lives
- [DF-003 Component System](./03-component-system.md) — template tags and component loading
- [DF-007 Configuration](./07-configuration.md) — `FUSION_ASSETS` setting
