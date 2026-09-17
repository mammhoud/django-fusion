---
title: Shared language contract
description: How django-fusion resolves, persists, and serves localized content across all Wagtail sites.
navigation:
  title: Language contract
  icon: i-lucide-languages
object:
  type: reference
  id: docs.django-fusion-language
attributes:
  source_path: libs/django-fusion-language.md
  canonical_route: /docs/en/libs/django-fusion-language
  source_of_truth: repository-markdown
  owner: django-fusion
  status: maintained
tags:
  - django-fusion
  - i18n
  - wagtail
  - language
  - localization
links:
  - label: django-fusion package guide
    to: /docs/en/libs/django-fusion
    icon: i-lucide-puzzle
  - label: Architecture
    to: /docs/en/architecture
    icon: i-lucide-landmark
---

# 🌍 Shared Language Contract

> Every Structa Cloud Wagtail site (Precis Main, Precis Landing, CTC Research) shares one
> language resolution, persistence, and API contract from `django-fusion.core.middlewares.language`.

## How it works

### Language resolution priority

```mermaid
flowchart TD
    A[HTTP request] --> B{?lang= query?}
    B -->|yes| C[Query value]
    B -->|no| D{Session _language?}
    D -->|yes| E[Session value]
    D -->|no| F{Cookie django_language?}
    F -->|yes| G[Cookie value]
    F -->|no| H{request.LANGUAGE_CODE?}
    H -->|yes| I[Middleware value]
    H -->|no| J{Accept-Language?}
    J -->|yes| K[Header value]
    J -->|no| L[settings.LANGUAGE_CODE]
    C --> M[Validate against configured codes]
    E --> M
    G --> M
    I --> M
    K --> M
    L --> M
    M --> N[activate + set request.LANGUAGE_CODE]
```

### Language switcher (Astro → Django)

```mermaid
sequenceDiagram
    participant U as User
    participant A as Astro Switcher
    participant D as Django /i18n/setlang/
    participant W as Wagtail Pages

    U->>A: Select language
    A->>A: sessionStorage + localStorage
    A->>D: POST /i18n/setlang/ {language}
    D->>D: session + cookie + activate
    D-->>A: {language, session_key, cookie_name}
    A->>A: document.lang + dir
    A->>W: Next request carries session/cookie
    W->>W: resolve_language → PageTranslation
    W-->>A: Localized content
```

### Settings → Middleware → API → Frontend diagram

```mermaid
graph LR
    subgraph Settings
        FL[FUSION_LANGUAGES]
        LC[LANGUAGE_COOKIE_*]
        SK[LANGUAGE_SESSION_KEY]
    end
    subgraph Middleware
        DLM[DefaultLanguageMiddleware]
    end
    subgraph API
        SLA[POST /i18n/setlang/]
        CLA[GET /apis/content/languages/]
    end
    subgraph Wagtail
        SL[SiteLanguage snippet]
        PT[PageTranslation overlay]
    end
    subgraph Astro
        LS[LanguageSwitcher.astro]
        API[api.ts fetchJSON]
    end
    FL --> DLM
    LC --> DLM
    SK --> DLM
    DLM --> SLA
    DLM --> CLA
    SL --> CLA
    PT --> API
    CLA --> LS
    SLA --> LS
    LS --> API
```

## What changed in this session

1. **django-fusion** (`libs/django-fusion/src/django_fusion/core/middlewares/language.py`) now owns:
   - `resolve_language(request)` — unified resolution chain
   - `persist_language(request, response, language)` — session + cookie write
   - `set_language_api` — POST endpoint shared by all sites
   - `language_context(request)` — template/API metadata
   - `configured_language_codes()` — settings-level validation
   - `normalize_language(value)` — BCP-47 normalization with regional code handling

2. **Precis Main** (`projects/structa.cloud/backend/settings.py`) and **Precis Landing** (`projects/precis/precis-landing/backend/settings.py`) now:
   - Use `DefaultLanguageMiddleware` from django-fusion (no more duplicate `LandingLocaleMiddleware`)
   - Register `/i18n/setlang/` via the shared API
   - Share the same `FUSION_LANGUAGES` catalog

3. **CTC Research** (`projects/precis/precis-ctc/backend/apps/pages/pages/landing_api.py`) now:
   - Delegates to `resolve_language()` instead of its own resolution chain
   - Uses `persist_language()` for the session/cookie write
   - Returns backend-resolved language in all API responses

4. **Astro frontends** (all three sites) now:
   - POST to `/i18n/setlang/` on language selection (server-side persistence)
   - Read language from the backend catalog on init
   - Use `sessionStorage` + `localStorage` for client-side fast path
   - Send `credentials: 'include'` and `Accept-Language` headers

## Affine export

This document uses standard Markdown with Mermaid diagrams. To export to Affine:
- Copy the entire `docs/` tree or this file into an Affine document.
- Mermaid diagrams render natively in Affine's code block editor.
- The `object`, `attributes`, `tags`, and `links` frontmatter are metadata for Docus;
  Affine ignores them gracefully.

## Related docs

- [django-fusion DF-020 Language Contract](../../libs/django-fusion/docs/20-language-contract.md)
- [django-fusion DF-007 Configuration](../../libs/django-fusion/docs/07-configuration.md)
- [Precis CTC documentation](../precis-ctc/)
