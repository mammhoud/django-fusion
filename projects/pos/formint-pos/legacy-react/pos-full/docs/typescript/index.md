# TypeScript / React Docs — POS Full

> **Directory:** `docs/typescript/`
> **Languages:** TypeScript, TSX
> **Framework:** React 18 + Vite + Tailwind CSS + RTK Query
> **Project:** `projects/pos/pos-full/`

---

## Conventions

| Rule | Example |
|------|---------|
| Component files | `PascalCase.tsx` |
| Utility files | `camelCase.ts` |
| Props interfaces | `{ComponentName}Props` |
| RTK Query files | `src/store/api/endpoints/{resource}.ts` |
| Test files | `src/test/{path}/{Component}.test.tsx` |

## Import Aliases

```typescript
import { Component } from '@/components/Component';
import { hook } from '@/hooks/hook';
import { fusionDecoder } from '@/lib/fusion-decoder';
```

## State Handling

All components must handle: loading, error, empty, normal.

See `../PROMPTS.md#typescript--react-prompts` for code generation templates.

## Detailed Guides

| Guide | Description |
|-------|-------------|
| [Component Patterns](./component-patterns.md) | Standard page, CRUD modal, card grid, debounced search, status toast patterns |
