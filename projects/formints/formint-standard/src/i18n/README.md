# 📁 POS-KO i18n (`src/i18n/`)

> **Related Names:** `i18n`, `translations`, `locale`, `English`, `Arabic`, `French`, `i18next`, `MSA`, `RTL`
> **Tags:** #i18n #translations #arabic #french #i18next

Translation files and i18next configuration for 3 languages.

```
i18n/
├── index.ts               # 🔴 i18next configuration + initialization
├── en.json                # 🟢 English (canonical reference)
├── ar.json                # 🟢 Arabic (Modern Standard Arabic)
└── fr.json                # 🟢 French
```

## Customization Tags

| File | Tag | How to customize |
|------|-----|-----------------|
| `index.ts` | 🔴 `not-customizable` | i18next init must match LanguageContext |
| `en.json` | 🟢 `customizable` | Add/modify English keys freely |
| `ar.json` | 🟢 `customizable` | Add Arabic keys — follow [conventions](../../docs/i18n-conventions.md) |
| `fr.json` | 🟢 `customizable` | Add French keys freely |

## Adding a Translation Key

1. Add key to `en.json` (canonical reference)
2. Add to `ar.json` following MSA conventions
3. Add to `fr.json`
4. Run `make i18n-check` to verify completeness
5. Run `make i18n-audit` to refresh gap report

```typescript
// Usage in components
import { useTranslation } from 'react-i18next';
const { t } = useTranslation();

<h1>{t('myPage.title')}</h1>
```

## Arabic Conventions (MSA)

See [`docs/i18n-conventions.md`](../../docs/i18n-conventions.md) for the full register:
- Titles → Arabic plural form
- Action buttons → `إضافة` + indefinite singular
- Sort indicators → `الاسم (أ→ي)`
- RBAC permissions → `الصلاحيات`
- Numerals → Arabic-Indic (٠–٩) for counters, Latin for IDs
- Placeholders → Unicode ellipsis `…` (U+2026)

## i18next Configuration (`index.ts`)

```typescript
i18n.use(initReactI18next).init({
  resources: { en, ar, fr },
  lng: 'en',          // default language
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});
```

## Maintenance Scripts

```bash
make i18n-check       # CI gate — non-zero if gaps exist
make i18n-audit       # Regenerate docs/i18n-gaps.md
make i18n-fix         # Merge Arabic + regenerate gaps
make i18n-fix-check   # Fix + verify
```

## Reference

- [i18n Conventions →](../../docs/i18n-conventions.md)
- [i18n Gaps Report →](../../docs/i18n-gaps.md)
- [Language Context →](../contexts/README.md)
