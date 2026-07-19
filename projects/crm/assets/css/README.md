# CRM — Shared POS Design System

The Cloud CRM project uses the same design system as the POS application for visual consistency.

## Shared Styles

Import the POS theme directly:

```html
<link rel="stylesheet" href="../../pos/assets/css/pos-theme.css">
```

## Custom Properties Available

The CRM can use all `--pos-*` CSS custom properties:

| Variable | Value | Usage |
|----------|-------|-------|
| `--pos-primary` | `#2563eb` | Primary actions, links |
| `--pos-secondary` | `#059669` | Success states, confirmations |
| `--pos-accent` | `#f59e0b` | Warnings, highlights |
| `--pos-danger` | `#dc2626` | Errors, deletions |
| `--pos-bg` | `#f8fafc` | Page background |
| `--pos-surface` | `#ffffff` | Card/panel background |
| `--pos-border` | `#e2e8f0` | Borders, dividers |
| `--pos-text` | `#1e293b` | Body text |
| `--pos-radius` | `8px` | Border radius |
| `--pos-font` | `'Inter', sans-serif` | Font family |

## Reusable Components

| Class | Purpose |
|-------|---------|
| `.pos-btn` / `.pos-btn-primary` | Action buttons |
| `.pos-card` | Content panels |
| `.pos-table` | Data tables |
| `.pos-input` | Form inputs |
| `.pos-badge` | Status badges |
| `.pos-layout` / `.pos-sidebar` / `.pos-main` | Page layout |
| `.pos-nav-item` | Sidebar navigation |

## Color Palette

```
Primary:   #2563eb  (Blue-600)
Secondary: #059669  (Emerald-600)
Accent:    #f59e0b  (Amber-500)
Danger:    #dc2626  (Red-600)
Background:#f8fafc  (Slate-50)
Surface:   #ffffff  (White)
Text:      #1e293b  (Slate-800)
```

## Directory

```
projects/crm/
├── assets/
│   └── css/
│       └── README.md       # This file (styles import from ../../pos/assets/css/)
└── ...
```
