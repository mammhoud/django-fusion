---
title: Design & Frontend — User Guide
description: How to activate themes, switch dark mode, choose components, and author dynamic templates — for editors, operators, and product owners.
object:
  type: "guide"
  id: "docs.design.user-guide"
attributes:
  source_path: "design/user-guide.md"
  canonical_route: "/docs/en/design/user-guide"
  section: "design"
  owner: "workspace"
  status: "maintained"
  source_of_truth: "repository-markdown"
tags:
  - structa-cloud
  - design
  - user-guide
  - theme
  - components
  - templates
links:
  - label: "Design suite home"
    to: "/design"
    icon: "i-lucide-palette"
---

# 🧑‍🎨 User Guide — Design & Frontend Systems

> **Audience:** content editors, operators, and product owners who use the
> design system and template fields without writing code.
> **Scope:** activating themes, dark mode, choosing components, and
> authoring `{{ variable }}` templates in admin screens.

---

## 1. Theme Engine

### Purpose

One product can switch its entire look (colors, fonts, spacing) by changing
a single setting — no redesign, no redeploy of components.

### Architecture (what you see)

The theme is selected per product (e.g. `lms` for Precis, `pos` for
Formint, `crm` for Loop-CRM, `default` for landing pages). A **theme
switcher** may be exposed in the product UI or set by an operator.

### Examples

```text
Precis Main        → data-theme="lms"      (educational indigo-violet)
Formint POS        → data-theme="pos"      (cream paper + verdigris)
Loop CRM           → data-theme="crm"      (data-dense blue-teal)
Landing pages      → data-theme="default"  (canonical indigo/blue)
New variations     → saas · enterprise · corporate · educational ·
                     retail · minimal · dark · contrast
```

### Usage

- **Switching themes:** ask your product owner or an operator to set the
  theme name; every page updates immediately.
- **Dark mode:** toggle the dark-mode control (or `D` where enabled); the
  theme engine remaps colors with no reload.
- **High Contrast:** choose the `contrast` theme for accessibility needs
  (pure black/white, thick borders, AAA contrast).

### Customization

- You cannot (and should not) edit colors directly in production — themes
  are controlled by developers through token files.
- Report visual bugs with the theme name and page URL; engineers fix the
  theme's tokens, which fixes every screen at once.

### Best Practices

- Use **dark mode** for extended sessions (POS registers, admin dashboards).
- Use **High Contrast** when presenting on projectors or for low-vision users.
- Keep one theme per product; avoid mixing themes on the same domain.

---

## 2. SCSS Architecture

### Purpose

Behind the scenes, every theme is a set of small style files. As an editor
you rarely touch them — this section explains why the visual system stays
consistent.

### Architecture

```text
tokens (colors/type/spacing)  →  engine (semantic names)  →  components
```

### Examples

Editing a button's color in one theme's token file changes every button on
every page that uses that theme — this is the payoff of the layered design.

### Usage

- Use the **preview page** (`projects/assets/theme/preview.html`) to compare
  themes side by side before requesting a change.
- If a component looks broken, note whether it happens in **all themes** or
  **one theme** — this tells engineers whether the issue is in the shared
  component or the theme's tokens.

### Customization

- Request new colors/fonts through your engineering team; they change
  tokens, not page templates.
- Brand-specific requests (your logo colors) become a `data-brand` override —
  the rest of the product's palette stays intact.

### Best Practices

- Don't paste custom colors into content (inline styles); ask for a token.
- Test dark mode before shipping any theme change.

---

## 3. Components

### Purpose

A shared catalog of building blocks — buttons, cards, tables, alerts,
forms — that look and behave the same everywhere.

### Architecture

Components are pure HTML + shared styles; the theme changes their look,
never their behavior.

### Examples

| Component | Where you see it |
|---|---|
| `fu-card` / `fu-lms-course-card` | Course listings on Precis |
| `fu-btn` (primary / ghost / danger) | Forms, enrollments, checkouts |
| `fu-table` / `fu-crm-table` | CRM pipelines, POS reports |
| `fu-alert` (success / warning / error) | Payment confirmations, validation |
| `fu-pos-register` / `fu-pos-receipt` | Formint POS checkout screens |
| `fu-pricing` / `fu-testimonial` | Landing and marketing pages |
| `fu-modal` | Confirmations, quick views |

### Examples

A confirmation dialog uses `fu-modal` with a `fu-btn--danger` action; a
success message uses `fu-alert--success` with `role="status"` so screen
readers announce it.

### Usage

- Use the component provided by the product UI — don't hand-roll buttons or
  cards in rich text.
- When in doubt, pick the **primary** button for the main action and
  **ghost** for secondary actions; **danger** only for destructive actions.

### Customization

- Component behavior is fixed and consistent by design (accessibility,
  keyboard support).
- Layout preferences (compact vs spacious tables, card density) are theme
  tokens — request them, don't hack around them.

### Best Practices

- One main action per screen (primary button), never two.
- Alerts must be actionable: say what happened and what to do next.
- Keep form labels visible and adjacent to their fields.

---

## 4. Design System

### Purpose

The design system defines the palette, typography, spacing, and grid that
make all Structa Cloud products feel like one family.

### Architecture

```text
Design system spec → per-theme palettes → your screen
```

### Examples

- **Colors:** primary (brand actions), secondary, accent, success, warning,
  error, neutral. Each theme has its own palette derived from the same roles.
- **Typography:** display / heading / body / caption sizes with consistent
  line heights.
- **Spacing:** a 4px-based scale; spacing between sections is always a token
  multiple, which keeps pages balanced.

### Usage

- Follow the product's existing visual rhythm when writing content:
  headings at the start of sections, one idea per card, generous whitespace.
- Use the **accent** color sparingly (CTAs, highlights), never for body text.

### Customization

- Content guidelines (tone, heading order) live with the product teams.
- Palette changes are token-level and roll out everywhere at once.

### Best Practices

- Body text: dark ink on light surface (or inverted in dark mode); never
  low-contrast gray on gray.
- Keep at least 4.5:1 contrast for body text (the system enforces this
  unless overridden).
- Use semantic success/warning/error colors — never invent a new color for
  a state.

---

## 5. Django Fusion

### Purpose

The shared Django framework that renders pages, fragments, and emails using
the components and themes above.

### Architecture (editor's view)

You edit content (Wagtail pages, email templates, product settings); the
framework renders it consistently across web, HTMX fragments, and email.

### Examples

- **Wagtail pages:** edit a page in admin; the layout uses registered
  components (`{% comp %}`) so new content never breaks styling.
- **Emails:** choose a pre-built email template (e.g. invoice receipt,
  enrollment confirmation) that auto-fills from records.
- **Fragments:** list/detail sections update in place via HTMX without a
  full page reload.

### Usage

- Prefer structured content blocks (StreamFields, forms) over free HTML.
- Use the email templates provided by your product; they render against
  live data automatically.

### Customization

- Adding a new page type or email layout is an engineering task; request it
  through your team with a clear description of the content fields needed.

### Best Practices

- Keep content structured: title, body, image, meta — not raw HTML.
- Test emails with **preview mode** before sending to customers.
- Never paste scripts or raw HTML into rich-text fields.

---

## 6. Dynamic Templates

### Purpose

Write messages, documents, and emails with placeholders that fill in
automatically from your data: `{{ customer.name }}`, `{{ order.total }}`,
`{{ invoice.number }}`.

### Architecture (what you see)

You write `{{ field }}` placeholders; the system resolves them against
known data sources, validates them, and previews the result before sending.

### Examples

```text
Email subject:   Your invoice {{ invoice.number }} is ready
Email body:      Hi {{ customer.name }},

                 Your order total is {{ order.total }}.
                 Due date: {{ invoice.due_date|date:"%Y-%m-%d" }}
```

Fallbacks keep things clean when data is missing:

```text
{{ customer.phone|default:"—" }}   →  shows "—" when no phone is on file
```

### Usage

1. Open the template editor (email template, document template, notification).
2. Type `{{` to see the **available fields** for the data source.
3. Add optional filters: `|upper`, `|date:"%Y-%m-%d"`, `|default:"…"`.
4. Click **Preview** — the system renders with sample data, shows a
   watermark, and lists any validation issues.
5. Save and send.

### Customization

- Available fields depend on the record type (customer, order, invoice,
  course enrollment…). Missing a field? Ask engineering to extend the schema.
- Fallback values and date formats are per-template — set them in the editor.

### Best Practices

- Always add a `|default:"…"` for optional fields — never ship a blank
  "Dear ,".
- Preview before every send; check the validation issues panel.
- Use `|date`, `|currency`, and `|upper` filters instead of hand-formatting.
- Security is handled for you: values are escaped automatically and only
  allowed data sources are reachable — you cannot access arbitrary data.

---

## Troubleshooting Quick Table

| Symptom | Likely cause | Action |
|---|---|---|
| Page looks unstyled | Theme not activated | Ask operator to set `data-theme` |
| Dark mode doesn't apply | Theme lacks `.dark` block | Report theme name to engineering |
| `{{ customer.name }}` shows fallback | Field missing on record | Check data, or extend schema |
| Preview shows warnings | Required field unresolved | Fill data or add fallback |
| Colors look wrong in one theme | Token misconfiguration | Report theme + page URL |

## Remarks & Notes

- Theme names in this guide follow the library: `default`, `lms`, `crm`,
  `pos`, plus eight variations (`saas`, `enterprise`, `corporate`,
  `educational`, `retail`, `minimal`, `dark`, `contrast`).
- Preview mode output is watermarked — it must never be sent as-is.
- <!-- AI-generated: review needed -->
