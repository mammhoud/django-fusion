# Phase 5 — Tag Visibility, Scroll-to-Note & Alpine.js UI Enhancements

**Status:** Planned  
**Scope:** `runtime/server.mjs`, `planing/app/src/`  
**Owner:** Frontend + Backend  
**Depends on:** Phase 2 (SurrealDB file mode)  
**Can run in parallel with:** Phase 3, Phase 4

---

## Objective

Three tightly related UI improvements:

1. **Tag filter sidebar** shows only tags that have at least one note matching
   the current filter context (no empty tags cluttering the sidebar).
2. **Scroll-to-note** — navigate to a specific note by ID via URL param or
   programmatic call, with a highlight pulse animation.
3. **Alpine.js appearance system** — theme variant, accent, radius, density,
   edge strength, shadow depth, button/badge style all apply instantly via CSS
   custom properties driven by Alpine.js, without a React re-render or page
   reload.

---

## Part A — Tag Visibility Filter

### Current State

`GET /api/tags` in `runtime/server.mjs`:
```js
const tags = await q(
  'SELECT id, name, icon, parent, count(<-tagged_with<-notes) AS note_count FROM tag WHERE workspace = $ws ORDER BY name;',
  { ws: wsRecord }
);
```

This returns all tags regardless of whether their notes match the current
filter. The frontend `TagListPanel.tsx` renders the full tree including tags
that have 0 visible notes.

### Backend Change

Update `GET /api/tags` to accept a `?onlyVisible=true` query param (default
`true` for sidebar, `false` for editor tag picker):

```js
app.get('/api/tags', auth, async (req, res) => {
  const onlyVisible = req.query.onlyVisible !== 'false';
  const categoryFilter = req.query.category || null;

  let sql;
  if (onlyVisible) {
    // Only tags with ≥1 note in the current workspace (and optional category)
    sql = `
      SELECT id, name, icon, parent, count() AS note_count
      FROM tag
      WHERE workspace = $ws
        AND <-tagged_with<-notes[WHERE
          workspace = $ws
          AND is_recycle = false
          ${categoryFilter ? 'AND category = $cat' : ''}
        ] IS NOT EMPTY
      ORDER BY name;
    `;
  } else {
    sql = `SELECT id, name, icon, parent, count(<-tagged_with<-notes) AS note_count
           FROM tag WHERE workspace = $ws ORDER BY name;`;
  }

  const tags = await q(sql, { ws: wsRecord, cat: categoryFilter });
  res.json({ tags: buildTagTree(tags) });
});
```

### Frontend Change (`components/Common/TagListPanel.tsx`)

- Pass `onlyVisible: true` when fetching for the sidebar filter panel.
- Add a "Show all tags" toggle at the bottom of the panel (calls with
  `onlyVisible: false`).
- Use Alpine.js `x-show` + `x-transition` to animate the "no tags" empty state.

```tsx
// In TagListPanel, fetch call:
const tags = await fetch(`/api/tags?onlyVisible=${onlyVisible}&category=${currentCategory}`);

// "Show all" toggle:
<button
  x-data="{ showAll: false }"
  @click="showAll = !showAll; $dispatch('tags:reload', { onlyVisible: !showAll })"
  class="tag-panel__show-all"
>
  <span x-text="showAll ? 'Show active only' : 'Show all tags'"></span>
</button>
```

### Acceptance Tests

```bash
# 1. Create tag "alpha", create note with tag "alpha"
# 2. Fetch /api/tags?onlyVisible=true → "alpha" present
# 3. Delete the note
# 4. Fetch /api/tags?onlyVisible=true → "alpha" absent
# 5. Fetch /api/tags?onlyVisible=false → "alpha" still present
```

---

## Part B — Scroll-to-Note

### URL param pattern

```
/?noteId=<id>           → scroll to note in the main list
/?path=all&noteId=<id>  → scroll to note in the all-notes view
```

### Store change (`blinkoStore.tsx`)

```ts
// Add to BlinkoStore:
scrollToNoteId: number | null = null;

scrollToNote(id: number) {
  this.scrollToNoteId = id;
  // If the note isn't on the current page, reset + reload:
  if (!this.noteList.value?.find(n => n.id === id)) {
    this.noteList.resetAndCall({ targetNoteId: id });
  }
}
```

### Component change (`BlinkoCard/index.tsx`)

```tsx
const cardRef = useRef<HTMLDivElement>(null);

useEffect(() => {
  if (blinko.scrollToNoteId === note.id && cardRef.current) {
    cardRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' });
    cardRef.current.classList.add('note-card--highlight');
    const timer = setTimeout(() => {
      cardRef.current?.classList.remove('note-card--highlight');
      blinko.scrollToNoteId = null;
    }, 2000);
    return () => clearTimeout(timer);
  }
}, [blinko.scrollToNoteId, note.id]);
```

### CSS animation

```css
.note-card--highlight {
  animation: highlight-pulse 2s ease-out forwards;
}

@keyframes highlight-pulse {
  0%   { box-shadow: 0 0 0 0 var(--planinc-accent-20); }
  30%  { box-shadow: 0 0 0 8px var(--planinc-accent-40); }
  100% { box-shadow: 0 0 0 0 transparent; }
}
```

### Page change (`pages/index.tsx`)

```tsx
const [searchParams] = useSearchParams();
const noteId = searchParams.get('noteId');

useEffect(() => {
  if (noteId) blinko.scrollToNote(Number(noteId));
}, [noteId]);
```

---

## Part C — Alpine.js Appearance System

### Overview

All appearance settings (theme, accent, radius, density, edge strength, shadow
depth, button style, badge style) are stored in the `workspace` SurrealDB record.
When changed via the settings panel, they should apply **instantly** to the
running page via CSS custom property updates — no React re-render, no page
reload.

### CSS Custom Properties

Define in `app/src/styles/tokens.css`:

```css
:root {
  /* Accent hue — driven by Alpine from workspace.accent */
  --accent-h: 262;           /* violet default */
  --accent-s: 83%;
  --accent-l: 58%;
  --accent: hsl(var(--accent-h) var(--accent-s) var(--accent-l));
  --accent-20: hsl(var(--accent-h) var(--accent-s) var(--accent-l) / 0.2);
  --accent-40: hsl(var(--accent-h) var(--accent-s) var(--accent-l) / 0.4);

  /* Radius scale */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 20px;

  /* Density — gap/padding multiplier */
  --density-gap: 12px;
  --density-padding: 16px;

  /* Edge strength — border opacity */
  --edge-opacity: 0.15;

  /* Shadow depth */
  --shadow-card: 0 1px 3px rgba(0,0,0,0.12);
}
```

### Accent hue map

```ts
// lib/alpineAppearance.ts
const accentHues: Record<string, [number, string, string]> = {
  violet: [262, '83%', '58%'],
  blue:   [217, '91%', '60%'],
  green:  [142, '71%', '45%'],
  orange: [38,  '92%', '50%'],   // amber — PlanInc brand accent
  red:    [0,   '84%', '60%'],
};

const radiusMap: Record<string, string> = {
  none:    '0px',
  subtle:  '3px',
  default: '8px',
  soft:    '14px',
  full:    '9999px',
};

const densityGap: Record<string, string> = {
  compact:     '8px',
  cozy:        '12px',
  comfortable: '20px',
};

const edgeOpacity: Record<string, string> = {
  soft:    '0.08',
  default: '0.15',
  strong:  '0.30',
};

const shadowDepth: Record<string, string> = {
  flat:     'none',
  default:  '0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08)',
  floating: '0 4px 16px rgba(0,0,0,0.18), 0 2px 6px rgba(0,0,0,0.12)',
};
```

### Alpine.js component

```ts
// lib/alpineAppearance.ts
export function registerAppearanceAlpine(Alpine: any) {
  Alpine.data('appearance', () => ({
    apply(settings: WorkspaceSettings) {
      const root = document.documentElement;
      const [h, s, l] = accentHues[settings.accent] || accentHues.violet;
      root.style.setProperty('--accent-h', String(h));
      root.style.setProperty('--accent-s', s);
      root.style.setProperty('--accent-l', l);
      root.style.setProperty('--radius-md', radiusMap[settings.radiusScale] || '8px');
      root.style.setProperty('--density-gap', densityGap[settings.density] || '12px');
      root.style.setProperty('--edge-opacity', edgeOpacity[settings.edgeStrength] || '0.15');
      root.style.setProperty('--shadow-card', shadowDepth[settings.shadowDepth] || shadowDepth.default);
    },
    init() {
      window.addEventListener('appearance:update', (e: CustomEvent) => {
        this.apply(e.detail);
      });
    }
  }));
}
```

### Settings panel wiring

In `components/BlinkoSettings/AppearancePanel.tsx`, after each setting change:

```ts
await fetch('/api/settings', { method: 'PATCH', body: JSON.stringify({ accent }) });
// Dispatch Alpine event immediately (optimistic update):
window.dispatchEvent(new CustomEvent('appearance:update', { detail: { accent } }));
```

### Theme variant system

```ts
const themeVariants: Record<string, Record<string, string>> = {
  default:     { '--bg': '#0d0d0f', '--surface': '#1e1f26', '--text': '#f8fafc' },
  corporate:   { '--bg': '#f4f6f8', '--surface': '#ffffff',  '--text': '#1a1d23' },
  luxury:      { '--bg': '#13100e', '--surface': '#1f1a16',  '--text': '#e8dcc8' },
  pastel:      { '--bg': '#fafafa', '--surface': '#ffffff',  '--text': '#3a3a4a' },
  perplexity:  { '--bg': '#0a0a0f', '--surface': '#16161f',  '--text': '#e2e4ef' },
};
```

Switching variant dispatches `appearance:update` with the full token set.

---

## Package Changes

In `planing/app/package.json`:
```json
{
  "dependencies": {
    "alpinejs": "^3.14.0",
    "@alpinejs/collapse": "^3.14.0",
    "@alpinejs/transition": "^3.14.0"
  }
}
```

Register in `app/src/main.tsx`:
```ts
import Alpine from 'alpinejs';
import { registerAppearanceAlpine } from './lib/alpineAppearance';
registerAppearanceAlpine(Alpine);
Alpine.start();
```

---

## Verification

```bash
# Tag visibility
# 1. Create tag "test", create note with it
# 2. Sidebar shows "test"
# 3. Delete the note
# 4. Sidebar no longer shows "test"

# Scroll-to-note
# 1. Navigate to /?noteId=42
# 2. Note 42 scrolls into view with amber highlight pulse
# 3. After 2s, highlight fades

# Alpine appearance
# 1. Open settings → change accent to orange
# 2. All accent-colored elements update instantly (no reload)
# 3. Change radius to "full"
# 4. All button/card corners update instantly
# 5. PATCH /api/settings confirms settings persisted
```
