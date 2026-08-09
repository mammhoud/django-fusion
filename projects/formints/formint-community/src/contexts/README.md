# 📁 POS-KO Contexts (`src/contexts/`)

> **Related Names:** `contexts`, `providers`, `auth`, `theme`, `language`, `state management`
> **Tags:** #react #contexts #auth #theme #language

3 React Context providers for cross-component state.

```
contexts/
├── AuthContext.tsx       # 🟢 Authentication — user, login, logout, profile
├── ThemeContext.tsx      # 🔴 Dark/light mode — must sync with CSS variables
└── LanguageContext.tsx   # 🔴 Language — must sync with i18next
```

## Customization Tags

| Context | Tag | How to customize |
|---------|-----|-----------------|
| `AuthContext.tsx` | 🟢 `customizable` | Add user fields, permissions, roles |
| `ThemeContext.tsx` | 🔴 `not-customizable` | Must call `document.documentElement.classList.toggle('dark')` |
| `LanguageContext.tsx` | 🔴 `not-customizable` | Must call `i18n.changeLanguage()` |

## AuthContext

```typescript
// Provided values
const { user, isAuthenticated, login, logout, changePassword } = useAuth();

// user type
interface User {
  id: number;
  email: string;
  name: string;
  role?: string;
}
```

## ThemeContext

```typescript
const { theme, toggleTheme } = useTheme();
// theme: 'light' | 'dark'
```

## LanguageContext

```typescript
const { language, setLanguage, direction } = useLanguage();
// language: 'en' | 'ar' | 'fr'
// direction: 'ltr' | 'rtl'
```

## Reference

- [Auth Docs →](../../docs/back-env/) (auth flow)
- [i18n Conventions →](../../docs/i18n-conventions.md)
- [Design System →](../../docs/design-layout.md)
