# Merge Syntara into Precis LMS

> **Status:** Planned
> **Scope:** Cross-project migration (Syntara → Precis LMS)
> **Date:** 2026-08-17
> **Branch:** `generic`

## Goal

Fold Syntara (the Cypercloud AI chat/customizer) into the Precis LMS main
website (`projects/precis/precis-lms/`) as a first-class **Precis Assistant**
feature, then decommission the standalone Syntara project.

Direction is **one-way**: Syntara's capabilities move into Precis; Syntara stops
being a standalone runtime. This keeps the LMS as the single main website and
gives it an AI assistant backed by the same conversation/streaming machinery.

## Current state

**Syntara** (`projects/syntara/`, port 5073, alias `cypercloud`) is a standalone
Django project. Its core is a single `chat/` app:

| Surface | Files |
|---|---|
| Models | `chat/models.py` — `Conversation`, `Message` |
| Services | `chat/services.py` — `AIService` (Ollama + OpenAI-compatible), `ConversationService` |
| Streaming | `chat/views_stream.py` — SSE views (`StreamChatView`, `CeptorAIStreamChatView`, `CeptorStreamChatView`) |
| Views | `chat/views.py` — chat home/detail, template discovery fragments, Ceptor/MCP API |
| Providers | `chat/ceptor.py` + `ceptor_stubs.py` — stub-backed AI/MCP/chat services |
| Discovery | `chat/site_data.py`, `chat/customizer.py` — template catalog scanning |
| Config | `chat/constants.py`, `configs/models.yml` — model registry |
| UI | `templates/` (Bootstrap), `assets/` (Webpack + Monaco editor) |
| App | `chat/apps.py` (`name = 'chat'`), `chat/urls.py`, `chat/forms.py`, `chat/admin.py`, `chat/migrations/` |

**Precis LMS** (`projects/precis/precis-lms/`) is Django 5.2 + Wagtail 7.4 +
django-fusion + allauth with an Astro frontend. Backend apps live under
`backend/apps/*` using `apps.*` imports; shared settings come from
`configs.default`; there is currently **no** chat/AI app.

## Scope decisions

**In scope**

1. Conversation + message persistence (`Conversation`, `Message`).
2. Provider-agnostic streaming: `AIService` (Ollama + OpenAI-compatible) and the
   SSE streaming view. This is the only transport needed and does **not** require
   `ceptor_stubs`.
3. A re-skinned assistant UI using Precis's design system (django-fusion
   `{% comp %}`, BEM, HTMX) instead of Bootstrap/Monaco.

**Out of scope (deferred / dropped)**

1. **Ceptor/MCP endpoints** (`Ceptor*View`, `ceptor.py`, `ceptor_stubs.py`) —
   Precis already removed the `ceptor-ai` dependency (`precis-ctc` CHANGELOG:
   "ceptor-ai dependency fully removed"). Drop them unless a future requirement
   resurfaces them behind a feature flag.
2. **Template discovery / customizer UI** (`site_data.py`, `customizer.py`,
   Monaco editor). Its configured roots are stale — `settings.CUSTOMIZER_APPS`
   points at `precis-ctc/templates`, `lms/templates`, and `VResume/www/pages/...`,
   none of which exist in the current tree. Defer; if re-introduced, re-point to
   current Precis template roots.
3. **Conversation data migration** — Syntara's `db.sqlite3` is dev-only. Assume
   no data migration unless a real deployment needs it.

## Target architecture

```
projects/precis/precis-lms/backend/apps/chat/
├── apps.py          # AppConfig(name="apps.chat")
├── models.py        # Conversation, Message (ported)
├── services.py      # AIService, ConversationService (ported)
├── views.py         # assistant home + conversation detail (re-skinned)
├── views_stream.py  # SSE streaming view (provider-agnostic only)
├── urls.py          # assistant routes
├── admin.py, forms.py, constants.py, exceptions.py
├── migrations/      # 0001_initial for Conversation/Message
└── templates/chat/  # assistant templates (django-fusion + BEM + HTMX)
```

Routes (namespaced, final prefix TBD — suggested `/assistant/`):

```text
GET  /assistant/                     assistant home + recent conversations
POST /assistant/                     create conversation
GET  /assistant/<id>/                conversation view
POST /assistant/<id>/                send message (HTMX fragment)
GET  /assistant/<id>/stream/         SSE response stream
POST /assistant/<id>/render-markdown/ markdown → HTML
GET  /assistant/panel/               compact widget panel (HTMX fragment)
```

## Design direction

One assistant, one visual language: **Precis brand-kit** — "clinical ink + warm
paper, clinical teal + evidence amber." The Bootstrap "TemplateTinker" look and
the indigo "ceptor × nawaai" bubble are both removed; nothing Syntara-specific
should be visibly branded after the merge.

### Design system to adopt

Source of truth is `frontend/src/styles/globals.css` (canonical for both the
Astro and Django render roads) plus `_variables.scss` / `_typography.scss` /
`_buttons.scss`.

- **Typography:** Fraunces (serif display) · Inter (UI) · IBM Plex Mono
  (protocol labels/eyebrows).
- **Palette:** paper `#F5F2EB` (`--fu-paper`) · ink `#0C1210` (`--fu-ink`) ·
  clinical teal `#1F8A70` (`--fu-link`) · evidence amber `#C9962E` (`--fu-mark`) ·
  live green `#2FB392` (`--fu-live`); dark mode via the `.dark` class.
- **Signature elements to reuse (no new CSS):**
  - `.card` double-bezel, `.btn-primary` teal pill (spring easing), `.input-field`
  - `.tag-marker` mono `‹assistant›` eyebrow, `.status-line` + pulsing `.dot`
  - `.reveal` scroll reveal, `.prose-fusion` for rendered markdown, film-grain
    overlay, `prefers-reduced-motion` guard
- **Interactivity:** `{% comp %}` components + BEM (no IDs for styling),
  CSRF-protected HTMX fragments, `fragment_name` for swaps, and the
  `frontend/src/fusion/` SSE helper instead of inline `<script>`.

### Syntara → Precis visual mapping

| Syntara today | Precis target |
|---|---|
| `#1e293b` dark sidebar, `#38bdf8` sky accent | ink `--fu-ink` canvas, teal `--fu-link` accent |
| `#8b5a3c` tan user bubble | teal `--fu-link` user bubble; amber `--fu-mark` for actions/conclusions |
| Bootstrap `d-flex` / `message-bubble` | `{% comp %}` + BEM, `.card` double-bezel |
| CDN Monaco editor + Bootstrap Icons | dropped (customizer deferred); inline SVG / mono glyphs |
| "TemplateTinker" + Font Awesome robot | `‹assistant›` eyebrow, "Precis Assistant" |
| inline `<script>` + `@csrf_exempt` SSE | `fusion/` SSE helper + CSRF-protected HTMX |
| `#4f46e5` "ceptor × nawaai" bubble | teal-on-paper assistant surface, unified brand |

### `bubble.html` replacement decision

Precis already ships `assets/templates/components/chat/bubble.html` — a
self-contained floating "ceptor × nawaai" widget (indigo `#4f46e5`, own
`ceptor-chat-*` namespace, inline CSS/JS, header/footer "ceptor × nawaai").
This is a **legacy widget**, not the Syntara app, and is referenced by the CTC
`plugins/TEMPLATE_GUIDE.md` chat-bubble include.

**Decision:** **delete** `bubble.html` and **replace** it with the new
server-rendered Precis Assistant widget. In Phase 3/4:

- [ ] Delete `assets/templates/components/chat/bubble.html` (the indigo
      "ceptor × nawaai" floating widget, its inline CSS/JS, and the
      `ceptor-chat-*` namespace).
- [ ] Add a new `components/assistant/widget.html` that renders the compact
      `/assistant/panel/` HTMX fragment and deep-links to `/assistant/`.
- [ ] Re-brand from "ceptor × nawaai" → "Precis Assistant" and drop the
      "Powered by" footer (or render "Powered by Precis").
- [ ] Update the CTC `plugins/TEMPLATE_GUIDE.md` chat-bubble include to reference
      the new assistant widget so only one chat surface remains in the catalog.

### Identity

Unify on **"Precis Assistant"** across UI, catalog copy, and docs (the legacy
`bubble.html` is removed). Preserve `cypercloud`/`syntara` only as runtime/URL
aliases where an external contract still requires them; do not render either
name in the UI.

## Assistant surface

**Decision: both, with distinct roles — one backend, two entry points.**

| Surface | Role | Deliverable |
|---|---|---|
| **Full-page route** (`/assistant/`) | Primary: owns conversation history, model selection, and deep context | Phase 3 |
| **Floating widget** (replaces `bubble.html`) | Discoverability: always-available entry point, deep-links into the full page | Phase 4 |

Rationale:

- The ported Syntara conversation views map **directly** onto a full-page route,
  so it ships first with no Astro dependency.
- Precis already has a floating-bubble precedent (`bubble.html`), so a widget is
  the natural way to make the assistant discoverable site-wide without changing
  every page.
- Both surfaces stay on the **Django + HTMX render road** and share one `apps.chat`
  backend, one SSE endpoint, and one CSRF handling path — avoiding a second
  client-side implementation. The Astro shell only embeds the server-rendered
  widget if a public surface is required.

Widget contract:

- `/assistant/panel/` renders the compact HTMX fragment (no sidebar/history).
- The widget's "Open full assistant" action links to `/assistant/` to hand off to
  the primary surface, carrying the active `conversation_id`.
- The widget is a new server-rendered `components/assistant/widget.html` that
  **replaces** (does not re-token) `bubble.html` per the
  [replacement decision](#bubblehtml-replacement-decision).

## Phases

### Phase 0 — Baseline & freeze

- [ ] Confirm `git status` is clean except the `libs/django-fusion` submodule bump
      (do not touch the submodule).
- [ ] Snapshot Syntara inventory (tables above) and note any live `db.sqlite3`.
- [ ] Decide conversation data migration: **no** (dev-only), confirm with owner.
- [ ] Decide final URL prefix (`/assistant/` vs `/chat/`) and app label
      (`apps.chat` vs `apps.assistant`).

### Phase 1 — Port the app into Precis backend

- [ ] Create `backend/apps/chat/` skeleton (`__init__.py`, `apps.py`, `migrations/__init__.py`).
- [ ] Port models to `backend/apps/chat/models.py`; re-run `makemigrations chat`
      for a fresh `0001_initial` (do not copy Syntara's migration files blindly).
- [ ] Port `services.py`, `constants.py`, `exceptions.py`, `forms.py`, `admin.py`.
- [ ] **Re-namespace:** `AppConfig.name` → `apps.chat`; keep `from .models` imports
      relative; add the app's URL `namespace` in the include.
- [ ] **Remove Ceptor/MCP code paths:** drop `ceptor.py` dependency, `Ceptor*View`s,
      `ceptor_stubs` imports, and the `ceptor-*` virtual model entries from
      `constants.py`. Keep only `AIService` (Ollama + OpenAI-compatible).
- [ ] **Replace `import yaml`** in `constants.py`/`ceptor.py`. Precis does not
      guarantee PyYAML (`configs/site.py` reads YAML without it; validate_config
      uses dynaconf's vendored `ruamel.yaml`). Load the model registry via
      dynaconf vendored YAML or move model entries into `cfg()`/Dynaconf settings.
- [ ] Add `apps.chat` to `INSTALLED_APPS` in `backend/settings.py`.
- [ ] Add a `FUSION_CHAT_*` settings block (model registry location, provider
      base URLs, timeouts, context limit) resolved through `cfg()`.

### Phase 2 — Wire URLs

- [ ] Add `chat/urls.py` with the assistant routes above.
- [ ] Register in `backend/apps/urls.py` (the root URL config) with a namespace,
      placed before the Wagtail catch-all; keep it outside `i18n_patterns` unless
      translation is required.
- [ ] Confirm no collision with existing `/chat/`/`/api/` routes; update the
      root-URL comment block.

### Phase 3 — UI re-skin (templates + assets)

- [ ] Port `chat.html` / `homepage.html` into `backend/apps/chat/templates/chat/`.
- [ ] Replace Bootstrap markup (`d-flex`, `message-bubble`, inline SSE `<script>`)
      with django-fusion `{% comp %}` + BEM classes + the project's HTMX/SSE
      helpers (`frontend/src/fusion/`, `fusion-bridge`).
- [ ] Apply the Precis brand-kit tokens and components from the
      [Design direction](#design-direction) section (teal-on-paper, Fraunces/Inter/
      IBM Plex Mono, `.card`/`.btn-primary`/`.status-line`).
- [ ] **Remove the legacy `bubble.html`:** delete the "ceptor × nawaai" widget
      per the [replacement decision](#bubblehtml-replacement-decision) and update
      the CTC `plugins/TEMPLATE_GUIDE.md` reference.
- [ ] Keep `fragment_name` stable and preserve CSRF on POSTs; **remove the broad
      `@csrf_exempt` decorators** in favor of CSRF-protected HTMX requests.
- [ ] Move any needed SCSS/JS into `precis/precis-lms/assets/`; do **not** bring
      the Monaco/Bootstrap Webpack pipeline unless the customizer is revived.

### Phase 4 — Floating widget entry point (second pass)

- [ ] Add the new `components/assistant/widget.html` (replacing the deleted
      `bubble.html`) that opens the compact `/assistant/panel/` fragment, with an
      "Open full assistant" deep link to `/assistant/` carrying the active
      `conversation_id`.
- [ ] Keep the widget on the Django/HTMX render road (same SSE + CSRF handling as
      the full-page route); if the Astro shell embeds it, mount the server-rendered
      widget rather than reimplementing the client.
- [ ] Preserve the render-first / data-API contracts; do not hard-code demo
      responses when the API is unavailable.

### Phase 5 — Tests & validation

- [ ] Port/adjust chat tests into `backend/tests/`: model invariants, JSON/SSE
      response shapes, streaming via a deterministic provider stub, error/fallback
      when the provider is unreachable, markdown rendering.
- [ ] Run `cd backend && make check`, `ruff check`, and the focused test module.
- [ ] Manual smoke: create conversation → send → stream tokens → render markdown.

### Phase 6 — Decommission Syntara

- [ ] `rg` for `syntara`, `cypercloud`, `ceptor_stubs`, `projects/syntara`
      references across the repo; update or remove each.
- [ ] Update `projects/Makefile` to drop/redirect the `cypercloud`/`syntara`
      aliases and the `projects`/`lint`/`format`/`typecheck` aggregate lists.
- [ ] Update catalog/marketing copy that lists Syntara as a standalone product
      (`precis-ctc`/`precis-landing` frontend product cards, `content-translations.ts`,
      `brand.ts`, pricing, docs/sites) → point at "Precis Assistant" or remove.
- [ ] Remove `projects/syntara/` after confirming zero references.
- [ ] Update `AGENTS.md` (root + `projects/AGENTS.md`) and docs paths.

## Dependency check (already verified)

- `httpx` — **available**: declared in `projects/pyproject.toml` (`httpx>=0.25.0`).
- `pyyaml` — **not guaranteed** in Precis; use dynaconf's vendored `ruamel.yaml`
  or `cfg()` instead of `import yaml`.
- `rest_framework`, `webpack_loader`, `ceptor_stubs` — **not needed** for the
  in-scope assistant; drop with the Ceptor/MCP surface.

## Risks & open questions

- **Naming:** `apps.chat` vs `apps.assistant`; `/assistant/` vs `/chat/` — confirm.
- **Security:** streaming is a long-lived request; ensure CSRF on the initiating
  POST and keep provider keys env-only (never hard-coded).
- **UI ownership:** resolved — Django templates + HTMX own both the full-page
  route and the floating widget (one SSE/CSRF source of truth); the Astro shell
  only embeds the server-rendered widget when a public surface is needed.
- **Template discovery revival:** if the customizer comes back, its roots must be
  re-pointed to current Precis paths and gated by path-permission checks.

## Definition of done

- [ ] `apps.chat` lives in Precis with migrations applied; no `chat`/`ceptor_stubs`
      imports outside it.
- [ ] Assistant conversation + SSE streaming works end-to-end on the Precis site.
- [ ] Chat tests pass (`make check` + focused pytest) with a deterministic stub.
- [ ] `projects/syntara/` removed and all dispatcher/docs/marketing references updated.
- [ ] Legacy `bubble.html` removed and replaced by the Precis Assistant widget.
