---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreifygksb6dfq4qovq7gpaxwcvmj2tl3khj3gqptbel4psixpch7fqa
---
# Theme System   
**Type:** Architecture 🏗️
T**ags: **#`frontend `#`theme-default `#`theme-corporate `#`theme-luxury `#`theme-pastel `#`theme-perplexity
`S**tatus: **Published
E**dition: **Mini, Solo, Full   
 --- 
## Architecture   
```
ThemeContext (React)
    │
    ├─ mode: 'light' | 'dark'
    ├─ variant: 'default' | 'corporate' | 'luxury' | 'pastel' | 'perplexity'
    ├─ followSystem: boolean (OS preference)
    │
    ├──→ <html> class="light|dark" data-theme="variant"
    │
    └──→ CSS Variables (Tailwind v4 token overrides)
              │
              ├─ --color-teal-*  → Primary accent (buttons, active states)
              ├─ --color-slate-* → Surface / text
              ├─ --color-gray-*  → Borders
              ├─ --color-indigo-* → Secondary accent
              └─ --color-amber-*  → Warning / dining accents
                     │
                     ▼
              Tailwind Utility Classes
              (bg-teal-500, text-slate-900, etc.)

```
 --- 
## Theme Variants   
|       Variant   <br> |                    Primary (teal)   <br> |            Surface (slate)   <br> |            Feel   <br> |
|:---------------------|:-----------------------------------------|:----------------------------------|:-----------------------|
|   **Default**   <br> |   Indigo/Teal `#6366f1`→`#14b8a6`   <br> |   Gray `#0f172a`→`#f8fafc`   <br> |   Clean, modern   <br> |
| **Corporate**   <br> |                    Blue `#3b82f6`   <br> |            Slate (neutral)   <br> |    Professional   <br> |
|    **Luxury**   <br> |                    Gold `#eab308`   <br> |                 Warm stone   <br> |         Premium   <br> |
|    **Pastel**   <br> |                    Pink `#ec4899`   <br> |               Light purple   <br> |         Playful   <br> |
| **Perplexity**   <br> |                   Teal   <br> |                     Neutral   <br> |      Minimal & intelligent   <br> |

 --- 
## Light / Dark Inversion   
Each variant supports both light and dark modes:   
```
.dark[data-theme="corporate"] {
  --color-slate-50:  #0f172a;  /* inverted */
  --color-slate-100: #1e293b;
  ...
  --color-slate-900: #f8fafc;
}

```
 --- 
## Key Files   
|                             File   <br> |                            Purpose   <br> |
|:----------------------------------------|:------------------------------------------|
|  `src/contexts/ThemeContext.tsx`   <br> |           React context + provider   <br> |
| `src/styles/theme-overrides.css`   <br> | CSS variable overrides per variant   <br> |
|          `src/styles/themes.css`   <br> |     Additional theme CSS variables   <br> |
|         `src/pages/Settings.tsx`   <br> |                  Appearance tab UI   <br> |

 --- 
## Usage: Adding a New Theme Variant   
```
/* 1. Add CSS variable overrides in theme-overrides.css */
[data-theme="ocean"] {
  --color-teal-50:  #ecfeff;
  --color-teal-500: #06b6d4;
  --color-teal-600: #0891b2;
  /* ... all scale values */
}

/* 2. Define `useTheme` -- in ThemeContext.tsx */
// Already handles any data-theme value

/* 3. Add to THEME_VARIANTS in ThemeContext.tsx */
{ id: 'ocean', label: 'Ocean', icon: '🌊', description: 'Deep blue waters' }

/* 4. Add to Settings.tsx appearance tab */

```
 --- 
## Related Docs   
- → `guides/theming.md` — Theme customization guide   
- → `features/comparison-matrix.md` — Which editions support theming   
- → `references/i18n-keys.md` — Appearance tab i18n keys   
[Theme System](theme-system.md)    
