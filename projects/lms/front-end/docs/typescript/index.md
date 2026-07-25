# TypeScript / React Docs — LMS Front-End

> **Directory:** `docs/typescript/`
> **Languages:** TypeScript, TSX
> **Framework:** Next.js 14 + React 18 + Tailwind CSS 3 + RTK Query + Framer Motion
> **Project:** `projects/lms/front-end/`

---

## Conventions

| Rule | Example |
|------|---------|
| Component files | `PascalCase.tsx` |
| Utility files | `camelCase.ts` |
| Props interfaces | `{ComponentName}Props` |
| Page routes | `src/app/{route}/page.tsx` |
| Test files | `src/test/{Component}.test.tsx` |

## Four-State Convention

Every data-driven component must handle:
1. **Loading** → `<LoadingSkeleton variant="..." />`
2. **Error** → `<ErrorState message={...} onRetry={...} />`
3. **Empty** → `<EmptyState icon="..." />`
4. **Normal** → Render data

## Import Aliases

```typescript
import { Component } from '@/components/Component';
import { useGetData } from '@/store/api/endpoints/resource';
import { fusionDecoder } from '@/lib/fusion-decoder';
```

## CTC Teal Theme

```css
text-[rgb(var(--ctc-primary))]     /* Primary teal */
bg-[rgb(var(--ctc-primary))]/10    /* Primary teal at 10% opacity */
card-gradient                      /* Gradient teal card bg */
section-hero                       /* Hero section gradient */
btn-primary                        /* Primary button */
```

See `../PROMPTS.md#typescript--react-prompts` for code generation templates.
