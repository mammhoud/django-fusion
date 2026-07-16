# CTC Research — Asset & Media Architecture

> Visual reference for how `ctc-research.com` frontend assets, static files, and media files flow from source code to the browser.

**Date:** 2026-07-12  
**Status:** Current  
**Companion guide:** [`GUIDE.md`](./GUIDE.md)

---

## 1. High-Level Asset Flow

```mermaid
flowchart LR
    subgraph Source
        A1[Django Templates]
        A2[SCSS / JS Sources]
    end

    subgraph Build
        B1[Webpack]
        B2[bundles.json]
        B3[collectstatic]
    end

    subgraph Serve
        C1[Traefik]
        C2[shared-media Nginx]
        C3[Django App]
    end

    subgraph Browser
        D1[HTML / CSS / JS]
    end

    A1 -->|{% render_bundle %}| B2
    A2 -->|import| B1
    B1 -->|hashed chunks| B2
    B2 -->|manifest| A1
    B1 --> B3
    B3 -->|staticfiles/| C2
    C1 -->|/static /media /sites| C2
    C1 -->|dynamic pages| C3
    C2 --> D1
    C3 --> D1
```

**Explanation:**
1. Developers write templates with `{% render_bundle %}` and SCSS/JS sources.
2. Webpack compiles sources into hashed chunks and writes `bundles.json`.
3. Django uses `bundles.json` to render the correct `<script>` / `<link>` tags.
4. `collectstatic` copies all static assets into `staticfiles/`.
5. Traefik routes static/media requests to the `shared-media` Nginx container.
6. Nginx serves files directly from the mounted volumes.

---

## 2. Template to Bundle Mapping

```mermaid
sequenceDiagram
    participant T as Template (base.html)
    participant D as Django + webpack_loader
    participant B as bundles.json
    participant N as shared-media (Nginx)
    participant Br as Browser

    T->>D: {% render_bundle 'static' 'css' %}
    T->>D: {% render_bundle 'main' 'js' %}
    T->>D: {% render_bundle 'app' 'js' %}
    D->>B: read chunks for 'static', 'main', 'app'
    B-->>D: static-a1b2.css, main-e5f6.js, app-i9j0.js
    D-->>T: <link> and <script> tags
    T-->>Br: HTML with asset URLs
    Br->>N: GET /static/bundles/ctc-research/main-e5f6.js
    N-->>Br: 200 OK (immutable cache)
```

---

## 3. Directory & URL Mapping

```mermaid
flowchart TB
    subgraph Host
        H1[core/ctc-research/assets/staticfiles/]
        H2[core/ctc-research/assets/media/]
        H3[core/assets/static/]
    end

    subgraph Container
        C1[/var/www/sites/ctc-research/static/]
        C2[/var/www/media/ctc-research/]
        C3[/var/www/static/]
    end

    subgraph URL
        U1[/static/bundles/ctc-research/...]
        U2[/sites/ctc-research/static/...]
        U3[/media/ctc-research/...]
        U4[/static/...]
    end

    H1 -->|volume mount| C1
    H2 -->|volume mount| C2
    H3 -->|volume mount| C3
    C1 --> U1
    C1 --> U2
    C2 --> U3
    C3 --> U4
```

---

## 4. Traefik Routing

```mermaid
flowchart LR
    Internet --> Traefik

    subgraph Traefik
        direction TB
        R1[ctc-site-https<br/>Host: ctc-research.com]
        R2[ctc-site-media-https<br/>PathPrefix: /static /media /sites]
        R3[ctc-media-https<br/>Host: media.ctc-research.com]
    end

    subgraph Backend
        B1[ctc-research-website:5070]
        B2[shared-media:80]
    end

    R1 --> B1
    R2 --> B2
    R3 --> B2
```

---

## 5. Webpack Entry Points

```mermaid
flowchart LR
    subgraph Inputs
        I1[ctc-research/assets/static/js/static.js]
        I2[core/assets/static/js/core/main.js]
        I3[ctc-research/assets/static/js/app.js]
    end

    subgraph Outputs
        O1[static-[hash].css]
        O2[static-[hash].js]
        O3[main-[hash].js]
        O4[app-[hash].js]
    end

    I1 -->|MiniCssExtractPlugin| O1
    I1 --> O2
    I2 --> O3
    I3 --> O4
```

---

## 6. Request Lifecycle Example

```mermaid
sequenceDiagram
    autonumber
    participant Br as Browser
    participant Tr as Traefik
    participant Ns as shared-media
    participant Dj as ctc-research-website

    Br->>Tr: GET https://ctc-research.com/
    Tr->>Dj: forward dynamic request
    Dj-->>Br: HTML with bundle tags

    Br->>Tr: GET /static/bundles/ctc-research/static-a1b2.css
    Tr->>Ns: PathPrefix /static/
    Ns-->>Br: CSS file

    Br->>Tr: GET /static/bundles/ctc-research/main-e5f6.js
    Tr->>Ns: PathPrefix /static/
    Ns-->>Br: JS file

    Br->>Tr: GET /media/ctc-research/avatars/user1.png
    Tr->>Ns: PathPrefix /media/
    Ns-->>Br: image file
```

---

## 7. Component Diagram

```mermaid
flowchart TB
    subgraph "Django Application"
        D1[Templates]
        D2[webpack_loader]
        D3[Settings: STATIC_ROOT, MEDIA_ROOT]
    end

    subgraph "Build Tools"
        W1[Webpack]
        W2[BundleTracker]
        W3[collectstatic]
    end

    subgraph "Reverse Proxy"
        T1[Traefik]
    end

    subgraph "Static/Media Server"
        N1[Nginx shared-media]
        V1[Volume: ctc-research staticfiles]
        V2[Volume: ctc-research media]
        V3[Volume: shared static]
    end

    D1 --> D2
    D2 --> W2
    W1 --> W2
    W2 --> D2
    W1 --> W3
    W3 --> V1
    V2 --> N1
    V3 --> N1
    V1 --> N1
    T1 --> N1
    T1 --> D1
```

---

## 8. Cache & Security Headers

| Location | Cache-Control | Notes |
|----------|---------------|-------|
| `/static/bundles/ctc-research/` | `public, immutable` | 1 year — hashed filenames never change |
| `/sites/ctc-research/static/` | `public, immutable` | 1 year — versioned by collectstatic |
| `/media/ctc-research/` | `public` | 30 days — user content may change |
| `/static/` (shared) | `public, immutable` | 1 year — shared vendor files |

All static/media responses also include:
- `X-Content-Type-Options: nosniff`
- `gzip` for text assets
- `access_log off` for static/media requests

---

## 9. Related Files

- [`core/assets/templates/base.html`](../../../core/assets/templates/base.html)
- [`core/ctc-research/assets/static/js/app.js`](../../../core/ctc-research/assets/static/js/app.js)
- [`core/ctc-research/assets/static/js/static.js`](../../../core/ctc-research/assets/static/js/static.js)
- [`core/webpack/main.config.js`](../../../core/webpack/main.config.js)
- [`core/configs/base/assets.py`](../../../core/configs/base/assets.py)
- [`applications/proxy/nginx/default.conf`](../../../applications/proxy/nginx/default.conf)
- [`applications/proxy/docker-compose.nginx.yml`](../../../applications/proxy/docker-compose.nginx.yml)
- [`applications/proxy/traefik/dynamic/ctc-research.yml`](../../../applications/proxy/traefik/dynamic/ctc-research.yml)
- [`applications/proxy/traefik/dynamic/media-servers.yml`](../../../applications/proxy/traefik/dynamic/media-servers.yml)
