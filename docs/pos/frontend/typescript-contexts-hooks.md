# ⚛️ TypeScript — Contexts, Hooks & i18n

> **Related Names:** `React`, `contexts`, `hooks`, `i18n`, `i18next`, `language`, `theme`, `auth state`, `debounce`, `toast`
> **Tags:** #typescript #react #contexts #hooks #i18n #pos

Reference for POS's React context providers, custom hooks, and internationalization system.

---

## Contexts (🔴 Not Customizable)

All three context providers are framework-level — modify with caution.

### AuthContext (`contexts/AuthContext.tsx`)

Manages auth state, login/logout, session inactivity tracking.

```typescript
import { useAuth } from '../contexts/AuthContext';

const { user, isAuthRequired, login, logout, inactivityWarning, dismissInactivityWarning } = useAuth();

// user: AuthUser | null = { id: number, email: string, name: string }
// isAuthRequired: boolean — true when SUPERUSER_* env vars are set
// login(email, password): Promise<{ ok: boolean; error?: string }>
// logout(): void
// inactivityWarning: boolean — shown before session timeout
```

> ⚠️ **Warning:** The auth flow is security-critical. The `INACTIVITY_TIMEOUT_OPTIONS` array is configurable, but the auth state machine should not be modified.

### ThemeContext (`contexts/ThemeContext.tsx`)

Dark/light mode toggle. Persists preference in localStorage.

```typescript
import { useTheme } from '../contexts/ThemeContext';

const { theme, toggleTheme } = useTheme();
// theme: 'light' | 'dark'
```

### LanguageContext (`contexts/LanguageContext.tsx`)

Language switcher using i18next. Supports `en`, `fr`, `ar`.

```typescript
import { useLanguage } from '../contexts/LanguageContext';

const { language, changeLanguage } = useLanguage();
// language: 'en' | 'fr' | 'ar'
```

---

## Hooks (🟢 Customizable)

### useDebouncedSearch (`hooks/useDebouncedSearch.ts`)

Delays search input processing to reduce API calls.

```typescript
import { useDebouncedSearch } from '../hooks/useDebouncedSearch';

const { query, debouncedQuery, setQuery } = useDebouncedSearch({
  delayMs: 300,    // 🟢 Debounce delay
  minLength: 2,    // 🟢 Min chars before search fires
});
// query: string — current input value
// debouncedQuery: string — delayed value for API calls
```

### useStatusToast (`hooks/useStatusToast.ts`)

Manages toast notification state with auto-dismiss.

```typescript
import { useStatusToast } from '../hooks/useStatusToast';

const { toasts, addToast, dismissToast } = useStatusToast({
  durationMs: 5000,  // 🟢 Auto-dismiss delay
  maxToasts: 3,      // 🟢 Max concurrent toasts
});

addToast({ type: 'success', message: 'Saved!' });
addToast({ type: 'error', message: 'Failed!' });
addToast({ type: 'info', message: 'Updating...' });
```

---

## i18n System (`i18n/`)

### Translation Files (🔵 Template)

```
i18n/
├── index.ts        # i18next configuration
├── en.json         # English (reference — maintain all keys here)
├── fr.json         # French
└── ar.json         # Arabic (RTL)
```

### Adding a Translation Key

1. Add key to `en.json`:
```json
{ "myFeature": { "title": "My Feature", "save": "Save" } }
```

2. Add translations to `fr.json`, `ar.json`:
```json
{ "myFeature": { "title": "Ma Fonctionnalité", "save": "Enregistrer" } }
```

3. Use in components:
```tsx
import { useTranslation } from 'react-i18next';
const { t } = useTranslation();
<h1>{t('myFeature.title')}</h1>
```

> 💡 **Tip:** Run `node scripts/check-i18n.cjs` to audit translation gaps. Run `node scripts/fill-fr-translations.cjs` to auto-fill missing French keys.

### Language Toggle Component

The `LanguageToggle.tsx` component shows `🇬🇧 EN | 🇫🇷 FR | 🇦🇪 AR` and switches using `LanguageContext`.

---

## Styles (`styles/`)

### Structure (🔵 Template)

```
styles/
├── base/
│   ├── _variables.scss    # CSS variables, colors, spacing
│   └── _reset.scss        # CSS reset
├── components/
│   ├── _card.scss         # Card component styles
│   └── _receipt.scss      # Receipt print styles
└── utilities/
    ├── _animations.scss   # Transition/loading keyframes
    ├── _rtl.scss           # Right-to-left (Arabic) overrides
    └── _scrollbar.scss    # Custom scrollbar styles
```

> 💡 **Tip:** Override SCSS variables in `_variables.scss` to change the app's color scheme globally. Component styles use BEM naming: `.card--dark`, `.table__header--sortable`.

---

→ [Back to TypeScript docs](README.md) | [Components Docs](typescript-components.md) | [API Layer Docs](typescript-api.md)
