---
# yaml-language-server: $schema=schemas/page.schema.json
Object type:
    - Page
Creation date: "2026-07-24T19:54:39Z"
Created by:
    - mammhoud
id: bafyreib5v6onx43stu45wynn5szaf7ekytd7pswmkr3bbde2bdlhlzxcly
---
# Guide — Theme Customization   
**Type:** Guide 📘
T**ags: **#`frontend `#`pos-mini `#`pos-solo `#`pos-full
`S**tatus: **Published
C**ategory: **Theming   
 --- 
## How Themes Work   
```
[data-theme="variant"] {
  --color-teal-500: #3b82f6;  /* Overrides bg-teal-500, text-teal-500, etc. */
  --color-slate-900: #f8fafc; /* Overrides dark mode text */
}

```
Tailwind v4 utility classes (e.g. `bg-teal-500`) use CSS custom properties. Theme variants redefine these properties at the `[data-theme]` level.   
 --- 
## Existing Variants   
|     Variant   <br> | Teal becomes   <br> | Slate becomes   <br> |        Best for   <br> |
|:-------------------|:--------------------|:---------------------|:-----------------------|
|   `default`   <br> |  Indigo/teal   <br> |     Cool gray   <br> |     General use   <br> |
| `corporate`   <br> |         Blue   <br> | Neutral slate   <br> |         Offices   <br> |
|    `luxury`   <br> |   Gold/amber   <br> |    Warm stone   <br> |     Fine dining   <br> |
|    `pastel`   <br> |  Pink/purple   <br> | Soft lavender   <br> | Cafes, bakeries   <br> |
| `cyberpunk`   <br> | Magenta/neon   <br> |     Dark gray   <br> |  Gaming centers   <br> |

 --- 
## Adding a New Variant   
### 1. CSS Overrides → theme-overrides.css   
```
/* Define ALL color tokens the app uses */
[data-theme="ocean"] {
  /* Primary (teal replacement) */
  --color-teal-50:  #ecfeff;
  --color-teal-100: #cffafe;
  --color-teal-200: #a5f3fc;
  --color-teal-300: #67e8f9;
  --color-teal-400: #22d3ee;
  --color-teal-500: #06b6d4;
  --color-teal-600: #0891b2;
  --color-teal-700: #0e7490;
  --color-teal-800: #155e75;
  --color-teal-900: #164e63;

  /* Surface (slate replacement) */
  --color-slate-50:  #f0f9ff;
  /* ... full spectrum ... */
  --color-slate-900: #0c4a6e;

  /* Also override: gray, indigo, amber, red, green, etc. */
}

/* Dark mode inversion */
.dark[data-theme="ocean"] {
  --color-teal-50:  #164e63;
  --color-teal-500: #06b6d4;
  /* Invert slate for dark bg */
  --color-slate-50:  #0c4a6e;
  --color-slate-900: #f0f9ff;
}

```
### 2. Register Variant → ThemeContext.tsx   
```
{ id: 'ocean', label: 'Ocean', icon: '🌊', description: 'Deep blue waters' }

```
### 3. Add Translations → i18n/en.json   
```
"appearanceTab": {
  "themeOcean": "Ocean",
  "oceanDesc": "Deep blue waters — calm and professional"
}

```
### 4. Settings UI → Settings.tsx   
```
<THEME_VARIANTS.map(v => (
  <button onClick={() => setVariant(v.id)}>
    {v.icon} {t(`appearanceTab.theme${v.id.charAt(0).toUpperCase() + v.id.slice(1)}`)}
  </button>
))}

```
 --- 
## Light / Dark Mode   
```
ThemeContext followSystem=true → @media (prefers-color-scheme)
ThemeContext setMode('light')  → html.classList.add('light')
ThemeContext setMode('dark')   → html.classList.add('dark')

```
The `html` element's `class` drives `.light` / `.dark` CSS selectors that invert slate values.   
 --- 
## Required Override Colors   
To make a variant fully work, override these token groups:   
|                Group   <br> |         Used For   <br> |                  Example Classes   <br> |
|:----------------------------|:------------------------|:----------------------------------------|
|    `--color-teal-\*`   <br> |   Primary accent   <br> |   `bg-teal-500`, `text-teal-400`   <br> |
|   `--color-slate-\*`   <br> |  Background/text   <br> | `bg-slate-100`, `text-slate-900`   <br> |
|    `--color-gray-\*`   <br> |     Dark borders   <br> |           `dark:border-gray-600`   <br> |
|  `--color-indigo-\*`   <br> | Secondary accent   <br> |                  `bg-indigo-500`   <br> |
|   `--color-amber-\*`   <br> |   Warning/dining   <br> |                   `bg-amber-400`   <br> |
| `--color-emerald-\*`   <br> |          Success   <br> |               `text-emerald-500`   <br> |
|     `--color-red-\*`   <br> |           Danger   <br> |                     `bg-red-500`   <br> |
|  `--color-purple-\*`   <br> |        Analytics   <br> |                `text-purple-600`   <br> |
|    `--color-cyan-\*`   <br> |     Light accent   <br> |                    `bg-cyan-500`   <br> |
|     `--color-sky-\*`   <br> |    Info/delivery   <br> |                   `text-sky-500`   <br> |
|  `--color-orange-\*`   <br> | Accent alternate   <br> |                  `bg-orange-400`   <br> |

 --- 
## Related Docs   
- → `architecture/theme-system.md` — Theme architecture   
- → `references/i18n-keys.md` — Appearance tab translations   
- → `guides/development.md` — Development workflow   
[Guide — Theme Customization](guide-theme-customization.md)    
