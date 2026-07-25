# LMS Front-End — Prompt Variations

> **Project:** `projects/lms/front-end/`
> **Purpose:** Reusable AI prompts for code generation, organized by language

---

## TypeScript / React Prompts

### Add a new public page
```
Add a new public page at src/app/[route]/page.tsx:
- 'use client' directive
- useResponsiveVariant() hook for layout variant
- PublicLayout wrapper with variant prop
- Compose using components/pages/[feature]/ components
- RTK Query data fetching with all 4 states (loading, error, empty, normal)
- CTC teal theme classes: text-[rgb(var(--ctc-primary))]
- framer-motion entrance animations
```

### Add a new dashboard page
```
Add a new dashboard page at src/app/dashboard/[route]/page.tsx:
- Wrapped in DashboardLayout (role-based sidebar auto-applied)
- RTK Query data fetching
- All 4 states handled (LoadingSkeleton, ErrorState, EmptyState, normal)
- CTC teal theme with progress-fill, stat-card, card-gradient classes
```

### Extract a page section into a component
```
Extract [Section] from src/app/[page]/page.tsx into a standalone component:
- Create: src/components/pages/[page]/[Section].tsx
- Standardize props to PageComponentProps interface
- Handle all 4 states (isLoading, error, empty data, normal)
- Add variant prop for responsive rendering (mobile/tablet/desktop)
- Update page.tsx to import and compose the new component
- Add Vitest unit test at src/test/components/pages/[Section].test.tsx
```

### Add a new shared component
```
Create a new shared component at src/components/ui/NewComponent.tsx:
- PascalCase naming, NewComponentProps interface
- Tailwind CSS with CTC teal variables
- All 4 states if data-driven
- Accessibility: aria-label, role, keyboard nav
- Vitest unit test at src/test/components/ui/NewComponent.test.tsx
```

### Add a new RTK Query endpoint
```
Add a new RTK Query endpoint to src/store/api/endpoints/[resource].ts:
- Export query/mutation hooks
- Define TypeScript types inline or in src/lib/fusion-types.ts
- Follow existing endpoint patterns (transformResponse, providesTags)
- Register in store/api/index.ts if needed
```

### Add a new Playwright E2E test
```
Add a Playwright E2E test:
- File: tests/e2e/[feature].spec.ts
- Follow existing patterns (test.describe groups, beforeEach setup)
- Check CTC teal theme compliance (forbiddenClasses: ['indigo-', 'purple-'])
- Test on mobile + desktop viewports
```

---

## CSS / Tailwind Prompts

### Add a new component style
```
Add a new @layer component style to src/app/globals.css:
- Follow BEM-style naming: .component-name__element--modifier
- Use CTC teal CSS variables: rgb(var(--ctc-primary))
- Include hover, active, disabled, focus states
- Add dark mode variant if applicable
- Keep consistent with existing .btn-primary, .card, .input-field patterns
```

### Add a new theme variable
```
Add a new CSS variable to :root in globals.css:
- Name: --ctc-[name]
- Format: R G B (space-separated for rgb() usage)
- Document in docs/css/theme-variables.md
```

---

## Documentation Prompts

### Add a new component doc
```
Document a new component:
- File: docs/typescript/[ComponentName].md
- Include: purpose, props table, usage example, states, accessibility
- Follow existing docs/typescript/ patterns
```

### Add a new plan file
```
Create a new plan file at plan/[NAME].md:
- Follow existing plan structure (FRONTEND_ENHANCEMENT_MASTER_PLAN.md as template)
- Include: status, progress tracking, deliverable checklist
- Cross-reference related plans in plan/README.md
```
