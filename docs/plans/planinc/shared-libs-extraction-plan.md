# Plan: Shared Libraries Extraction for PlanInc & Formint

## Status: Separate Plan · Version: 2.1 · Date: 2026-09-20

This plan handles the extraction of all shared code into standalone libraries. This is a companion to the [Unified Development Organization Plan](../unified-dev-organization.md).

### FlyonUI Note
FlyonUI (`flyonui` v2.4.1) has been added as a Tailwind CSS v4 plugin in PlanInc. When extracting shared UI components into `libs/shared-ui-components/`, consider using FlyonUI's semantic classes as the foundation instead of HeroUI components. See §10 of the unified plan for migration strategy.

---

## Objective

Extract shared code from PlanInc and Formint into reusable library packages that both products consume. No symlinks are used — all libraries are consumed via Bun workspace package references.

---

## Libraries to Extract

### 1. Shared UI Components (`libs/shared-ui-components/`)

**Workspace package name:** `@structa/shared-ui-components`

**Contents:**
- Theme-agnostic BEM components (Button, Card, Table, Form, Modal, Alert, Nav, Input)
- Shared React hooks (useAuth, useI18n, useMobx, usePlatform, useTauri, useWebSocket, useTheme)
- PlanInc-specific component group (Planning, Tickets, Study, Graph)
- Formint-specific component group (Pos, Inventory, Orders)

**Source locations to extract from:**
- PlanInc: `projects/planinc/frontend/src/components/`
- Formint: `projects/formint-dev/formint/frontend/src/components/` (when created)

**Directory structure:**
```
libs/shared-ui-components/
├── src/
│   ├── common/
│   │   ├── Button/
│   │   ├── Card/
│   │   ├── Table/
│   │   ├── Form/
│   │   ├── Modal/
│   │   ├── Alert/
│   │   ├── Nav/
│   │   └── Input/
│   ├── planinc/
│   │   ├── Planning/
│   │   ├── Tickets/
│   │   ├── Study/
│   │   └── Graph/
│   ├── formint/
│   │   ├── Pos/
│   │   ├── Inventory/
│   │   └── Orders/
│   ├── hooks/
│   │   ├── useAuth/
│   │   ├── useI18n/
│   │   ├── useMobx/
│   │   ├── usePlatform/
│   │   ├── useTauri/
│   │   ├── useWebSocket/
│   │   └── useTheme/
│   └── index.ts
├── package.json
├── tsconfig.json
└── AGENTS.md
```

**Convention:** Components use BEM naming (`fu-<block>`, `fu-<block>__element`, `fu-<block>--modifier`). Theme-agnostic components consume `--fu-token-*` aliases only.

### 2. Shared Design Tokens (`libs/shared-design-tokens/`)

**Workspace package name:** `@structa/shared-design-tokens`

**Contents:**
- OKLCH four-tier token system (base palette, semantic aliases, helpers)
- Token manipulation utilities (oklch.ts, theme-lookup.ts, token-generator.ts)
- TypeScript type definitions (colors.ts, spacing.ts, typography.ts)
- **Responsive edge/curve/radius system** — 8-tier responsive border-radius, motion curves, and component edge attributes

**Responsive Design Tokens included:**
- `--radius` and derived scale (`--pi-radius-sm` through `--pi-radius-3xl`) scaling from xs (360px) to 4xl (2560px)
- Component edge attributes (`--chip-radius`, `--contextmenu-radius`, `--card-radius`, `--modal-radius`, `--sheet-radius`, `--input-radius`, `--button-radius`, `--avatar-radius`, `--image-radius`, `--dropdown-radius`, `--tooltip-radius`, `--progress-radius`, `--skeleton-radius`, `--scrollbar-radius`)
- Motion curves (`--motion-fast`, `--motion-base`, `--motion-ease`, `--curve-enter`, `--curve-exit`, `--curve-sharp`, `--curve-smooth`, `--curve-bounce`, `--curve-elastic`)
- All values are `html[data-tier="..."]` gated for responsive scaling

**Source locations to extract from:**
- `projects/assets/theme/` (existing theme infrastructure)
- `src/frontend/src/styles/tokens.css` (responsive edge system)
- `src/frontend/src/styles/globals.css` (component edge attributes)
- `src/frontend/tailwind.config.js` (radius utility mapping)
- PlanInc: `projects/planinc/frontend/src/styles/`
- Formint: `projects/formint-dev/formint/frontend/src/styles/` (when created)

**Directory structure:**
```
libs/shared-design-tokens/
├── src/
│   ├── tokens/
│   │   ├── _fu-default-theme.scss
│   │   ├── _fu-token-aliases.scss
│   │   └── _fu-helpers.scss
│   ├── functions/
│   │   ├── oklch.ts
│   │   ├── theme-lookup.ts
│   │   └── token-generator.ts
│   ├── types/
│   │   ├── colors.ts
│   │   ├── spacing.ts
│   │   └── typography.ts
│   └── index.ts
├── package.json
└── AGENTS.md
```

**Convention:** Each product theme extends the base tokens. PlanInc's brand theme and Formint's `pos` theme are defined as separate SCSS files that import `@structa/shared-design-tokens`.

### 3. Shared Tauri Plugin (`libs/shared-tauri-plugin/`)

**Workspace package name:** `@structa/shared-tauri-plugin`

**Contents:**
- Core plugin functionality (fs, dialog, shortcut, process, updater, os)
- PlanInc-specific extensions (planning, surrealdb)
- Formint-specific extensions (pos, sqlite)

**Source locations to extract from:**
- PlanInc: `projects/planinc/frontend/tauri-plugin-planinc/`
- Formint: `projects/formint-dev/formint/frontend/tauri-plugin-formint/` (when created)

**Directory structure:**
```
libs/shared-tauri-plugin/
├── src/
│   ├── core/
│   │   ├── fs.ts
│   │   ├── dialog.ts
│   │   ├── shortcut.ts
│   │   ├── process.ts
│   │   ├── updater.ts
│   │   └── os.ts
│   ├── planinc/
│   │   ├── planning.ts
│   │   └── surrealdb.ts
│   ├── formint/
│   │   ├── pos.ts
│   │   └── sqlite.ts
│   └── index.ts
├── package.json
├── tsconfig.json
└── AGENTS.md
```

**Convention:** Each product creates its own Tauri plugin (`tauri-plugin-planinc`, `tauri-plugin-formint`) that depends on `@structa/shared-tauri-plugin` as a workspace package. Product-specific extensions are added alongside the shared core.

### 4. Shared TypeScript Types (`libs/shared-types/`)

**Workspace package name:** `@structa/shared-types`

**Contents:**
- Common interfaces (User, Session, Config, Theme)
- Platform enums (Platform, OS, FormFactor)
- Error types and API response shapes

**Source locations to extract from:**
- PlanInc: `projects/planinc/shared/src/types.ts`
- Formint: `projects/formint-dev/shared/types/` (when created)

**Directory structure:**
```
libs/shared-types/
├── src/
│   ├── user.ts
│   ├── session.ts
│   ├── config.ts
│   ├── theme.ts
│   ├── platform.ts
│   ├── errors.ts
│   └── api.ts
├── package.json
├── tsconfig.json
└── AGENTS.md
```

---

## Workspace Integration

### `/home/bunfig.toml` additions:

```toml
[workspace]
members = [
  "libs/*",
  # ... existing members
]

[resolution]
"@structa/shared-ui-components" = "workspace:*"
"@structa/shared-design-tokens" = "workspace:*"
"@structa/shared-tauri-plugin" = "workspace:*"
"@structa/shared-types" = "workspace:*"
```

### Product `package.json` dependencies:

```json
{
  "dependencies": {
    "@structa/shared-ui-components": "workspace:*",
    "@structa/shared-design-tokens": "workspace:*",
    "@structa/shared-tauri-plugin": "workspace:*",
    "@structa/shared-types": "workspace:*"
  }
}
```

### Import conventions:

```typescript
// Always import from workspace packages
import { Button } from '@structa/shared-ui-components';
import { useAuth } from '@structa/shared-ui-components/hooks';
import { colors } from '@structa/shared-design-tokens';
import { invoke } from '@structa/shared-tauri-plugin/core';
import { User } from '@structa/shared-types';
```

---

## Migration Steps

### Phase 1: Scaffold Libraries (Week 1)

- [ ] Create `libs/shared-ui-components/` with directory structure and package.json
- [ ] Create `libs/shared-design-tokens/` with directory structure and package.json
- [ ] Create `libs/shared-tauri-plugin/` with directory structure and package.json
- [ ] Create `libs/shared-types/` with directory structure and package.json
- [ ] Add all four to `bunfig.toml` workspace members
- [ ] Add all four to root `package.json` workspaces array

### Phase 2: Extract and Populate (Week 2)

- [ ] Extract shared components from PlanInc frontend to `libs/shared-ui-components/src/common/`
- [ ] Extract PlanInc-specific components to `libs/shared-ui-components/src/planinc/`
- [ ] Extract shared hooks to `libs/shared-ui-components/src/hooks/`
- [ ] Create barrel exports and package.json for each library
- [ ] Migrate design tokens from `projects/assets/theme/` to `libs/shared-design-tokens/`
- [ ] Extract Tauri plugin core to `libs/shared-tauri-plugin/src/core/`
- [ ] Extract shared types to `libs/shared-types/src/`
- [ ] Configure `bun install` to resolve all workspace packages

### Phase 3: Product Integration (Week 3)

- [ ] Update PlanInc `package.json` to reference `@structa/*` workspace packages
- [ ] Remove duplicated code from PlanInc frontend
- [ ] Update PlanInc imports to use workspace packages
- [ ] Update PlanInc `tauri-plugin-planinc` to depend on `@structa/shared-tauri-plugin`
- [ ] Update Formint scaffolded editions (when created) to reference workspace packages
- [ ] Verify `bun install --check` passes

### Phase 4: Validation (Week 3)

- [ ] Run full test suite for all products
- [ ] Verify no symlinks exist in the repository
- [ ] Update CI to validate workspace integrity
- [ ] Create `WORKSPACES.md` documenting the shared library strategy
- [ ] Set up shared `.editorconfig`, `.prettierrc`, `.eslintrc`

---

## Rules

1. **Never use symlinks.** All shared code is consumed via `workspace:*` package references.
2. **Shared code lives in `libs/`.** If code is shared between products, it goes to `libs/`.
3. **Product-specific code stays in product directories.** Never put PlanInc-only code in `libs/`.
4. **Bun resolves workspace packages automatically.** No manual linking needed.
5. **Each library has its own `package.json`, `AGENTS.md`, and test suite.**
6. **All imports use `@structa/` scope.** Never use relative paths for shared code.

---

## File Reference Summary

| Library | Package Name | Location | Products |
|---|---|---|---|
| Shared UI Components | `@structa/shared-ui-components` | `libs/shared-ui-components/` | PlanInc, Formint |
| Design Tokens | `@structa/shared-design-tokens` | `libs/shared-design-tokens/` | PlanInc, Formint |
| Tauri Plugin | `@structa/shared-tauri-plugin` | `libs/shared-tauri-plugin/` | PlanInc, Formint |
| Shared Types | `@structa/shared-types` | `libs/shared-types/` | PlanInc, Formint |

---

## License

AGPL-3.0
