# Syntara / Cypercloud Templates — AI Agent Instructions

**Scope:** `projects/syntara/templates/`
**Product path:** `projects/syntara/` (historical runtime name: Cypercloud)

Read `projects/syntara/AGENTS.md` and the root `AGENTS.md` first.

## Template tree

```text
templates/
├── base.html                 # Site shell and asset loading
├── homepage.html             # Chat/customizer landing page
├── chat.html                 # Conversation UI
├── pages.html                # Discovered page/template view
├── websites.html             # Configured site list
├── sections.html             # Discovered section view
├── apps.html                 # App/catalog view
├── components/               # Message bubbles, editor, cards, nav, alerts
└── fragments/                # HTMX swaps and send-result fragments
```

Templates here present AI conversations and discovered project structure. They
are not the source of truth for the sites being inspected.

## Rules

- Preserve model-provided conversation, provider, page, section, and template
  data. Do not replace it with static demo text.
- Escape generated code and markdown according to the existing rendering
  boundary; never mark arbitrary AI output safe.
- Preserve SSE/HTMX targets, triggers, out-of-band swaps, loading indicators,
  and error fragments.
- Use `{% comp %}` when a registered django-fusion component exists; otherwise
  use a narrow `{% include %}` with explicit context.
- Use `fragment_name` for fragment identifiers and context keys.
- Use BEM-style classes and do not use IDs for styling.
- Keep provider/model controls accessible and retain form labels and error
  feedback.

Before changing a template, inspect its view in `chat/views.py` or
`chat/views_stream.py`, the URL in `chat/urls.py`, and neighboring fragments.
Test both a normal page request and the HTMX/SSE path when applicable.
