# 📁 POS-KO Components (`src/components/`)

## What's Here

Reusable React 19 UI components for the POS-KO desktop application.

```
components/
├── PageLayout.tsx         # 🔵 Page wrapper — top bar, profile, inactivity toast
├── SideNav.tsx            # 🟢 Slide-out navigation panel
├── ChatSupport.tsx        # 🟢 Floating chat widget (WebSocket)
├── DataTable.tsx          # 🟢 Generic sortable/filterable table
├── Invoice.tsx            # 🟢 Invoice preview component
├── Modal.tsx              # 🟢 Modal dialog wrapper
├── Skeleton.tsx           # 🟢 Loading skeleton placeholders
├── StatusToast.tsx        # 🟢 Toast notification system
├── LanguageToggle.tsx     # 🟢 en/fr/ar language switcher
└── ThemeToggle.tsx        # 🟢 Dark/light mode toggle
```

## Customization Tags

| Component | Tag | How to customize |
|-----------|-----|-----------------|
| `PageLayout.tsx` | 🔵 `template` | Only change styles, not auth logic |
| `SideNav.tsx` | 🟢 `customizable` | Add/remove nav items |
| `ChatSupport.tsx` | 🟢 `customizable` | Change widget style, position |
| `DataTable.tsx` | 🟢 `customizable` | Add new column types, sort modes |
| `Invoice.tsx` | 🟢 `customizable` | Change invoice layout |
| `Modal.tsx` | 🔴 `not-customizable` | Portal + focus trap — don't break |
| `Skeleton.tsx` | 🟢 `customizable` | Add new skeleton variants |
| `StatusToast.tsx` | 🟢 `customizable` | Add toast types, positions |
| `ThemeToggle.tsx` | 🔴 `not-customizable` | Must call `ThemeContext` correctly |
| `LanguageToggle.tsx` | 🔴 `not-customizable` | Must call `LanguageContext` correctly |

## Reference

- [Components Docs →](../../docs/typescript/components.md)
- [Frontend Overview →](../../docs/typescript/README.md)
