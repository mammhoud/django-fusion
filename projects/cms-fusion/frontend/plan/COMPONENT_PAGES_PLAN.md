# LMS Front-End — Component / Pages Architecture Plan

> **Plan file:** `projects/lms/front-end/plan/COMPONENT_PAGES_PLAN.md`
> **Created:** 2026-07-25 | **Branch:** `generic`
> **Parent plan:** [`FRONTEND_ENHANCEMENT_MASTER_PLAN.md`](./FRONTEND_ENHANCEMENT_MASTER_PLAN.md) — Phase 6

---

## Overview

This plan defines the `components/pages/` architecture — a standardized
way to extract page-level content into reusable, testable components with
consistent props, loading/error/empty states, and responsive variants.

---

## 1. Directory Structure

```
src/
  components/
    backgrounds/                    # Phase 4
      AnimatedHeroBackground.tsx
    layouts/                        # Phase 5
      PublicLayout.tsx
      DashboardLayout.tsx
      AuthLayout.tsx
      MobileBottomNav.tsx
      MobileSidebar.tsx
      CollapsibleSidebar.tsx
      DesktopSidebar.tsx
    pages/                          # NEW — Phase 6
      home/
        HomeHero.tsx
        HomeStats.tsx
        HomeFeaturedCourses.tsx
        HomeCTA.tsx
        HomeInstructors.tsx
      auth/
        LoginForm.tsx
        RegistrationForm.tsx
        PasswordResetForm.tsx
      courses/
        CourseCard.tsx
        CourseGrid.tsx
        CourseFilters.tsx
        CourseSearch.tsx
      about/
        AboutHero.tsx
        AboutMission.tsx
        AboutTeam.tsx
        AboutTimeline.tsx
      contact/
        ContactForm.tsx
        ContactInfo.tsx
        ContactMap.tsx
      faq/
        FaqAccordion.tsx
        FaqCategory.tsx
      blog/
        BlogCard.tsx
        BlogGrid.tsx
        BlogSidebar.tsx
      shop/
        ProductCard.tsx
        ProductGrid.tsx
        CartSummary.tsx
      dashboard/
        instructor/
          InstructorStats.tsx
          InstructorCharts.tsx
          InstructorCourses.tsx
          InstructorQuickLinks.tsx
        student/
          StudentStats.tsx
          StudentEnrollments.tsx
          StudentProgress.tsx
        admin/
          AdminWithdrawals.tsx
          AdminStats.tsx
      shared/
        StatCard.tsx
        FeatureCard.tsx
        TestimonialCard.tsx
        CtaSection.tsx
        SectionHeader.tsx
```

---

## 2. Component Interface Standard

Every page component implements this interface:

```tsx
/**
 * Standard page component props.
 *
 * All data-driven components MUST handle:
 *   1. Loading state  (isLoading === true)
 *   2. Error state    (error !== undefined)
 *   3. Empty state    (data is empty/null)
 *   4. Normal state   (data is present)
 */
interface PageComponentProps<T = unknown> {
  /** Responsive layout variant */
  variant?: 'mobile' | 'tablet' | 'desktop';

  /** Component data from CMS, API, or static source */
  data?: T;

  /** Whether data is currently loading */
  isLoading?: boolean;

  /** Error object from API call */
  error?: unknown;

  /** Callback to retry failed data fetch */
  onRetry?: () => void;

  /** Additional CSS classes */
  className?: string;

  /** Slot for child content */
  children?: React.ReactNode;
}
```

---

## 3. State Handling Convention

### 3.1 Four-State Pattern

```tsx
function CourseGrid({
  data,
  isLoading,
  error,
  onRetry,
  variant = 'desktop',
}: PageComponentProps<Course[]>) {
  // 1. Loading
  if (isLoading) {
    return <LoadingSkeleton variant="card" count={colsForVariant(variant)} />;
  }

  // 2. Error
  if (error) {
    return <ErrorState message={extractErrorMessage(error)} onRetry={onRetry} />;
  }

  // 3. Empty
  if (!data || data.length === 0) {
    return <EmptyState icon="courses" />;
  }

  // 4. Normal
  return (
    <div className={`grid ${gridColsForVariant(variant)} gap-6`}>
      {data.map((course) => (
        <CourseCard key={course.id} course={course} variant={variant} />
      ))}
    </div>
  );
}
```

### 3.2 Grid Columns by Variant

```tsx
function gridColsForVariant(variant: string): string {
  switch (variant) {
    case 'mobile':  return 'grid-cols-1';
    case 'tablet':  return 'grid-cols-2';
    case 'desktop': return 'grid-cols-3';
    default:        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
  }
}

function colsForVariant(variant: string): number {
  switch (variant) {
    case 'mobile':  return 1;
    case 'tablet':  return 2;
    case 'desktop': return 3;
    default:        return 3;
  }
}
```

---

## 4. Page Composition Example

### 4.1 Before (Monolithic Page)

```tsx
// src/app/page.tsx — 200+ lines, all inline
export default function HomePage() {
  return (
    <div>
      <section className="section-hero">...80 lines...</section>
      <section className="py-16">...60 lines...</section>
      <section className="py-20">...30 lines...</section>
      <section className="py-16">...40 lines...</section>
    </div>
  );
}
```

### 4.2 After (Composed with Page Components)

```tsx
// src/app/page.tsx — 30 lines, delegates to components
'use client';
import { useResponsiveVariant } from '@/hooks/useResponsiveVariant';
import PublicLayout from '@/components/layouts/PublicLayout';
import HomeHero from '@/components/pages/home/HomeHero';
import HomeStats from '@/components/pages/home/HomeStats';
import HomeFeaturedCourses from '@/components/pages/home/HomeFeaturedCourses';
import HomeCTA from '@/components/pages/home/HomeCTA';
import HomeInstructors from '@/components/pages/home/HomeInstructors';

export default function HomePage() {
  const variant = useResponsiveVariant();

  return (
    <PublicLayout variant={variant}>
      <HomeHero variant={variant} />
      <HomeStats variant={variant} />
      <HomeFeaturedCourses variant={variant} />
      <HomeCTA variant={variant} />
      <HomeInstructors variant={variant} />
    </PublicLayout>
  );
}
```

---

## 5. Shared Components

### 5.1 StatCard

```tsx
interface StatCardProps extends PageComponentProps {
  icon: IconType;
  label: string;
  value: string | number;
  suffix?: string;
  color?: string;
  bgColor?: string;
}

export default function StatCard({
  icon: Icon,
  label,
  value,
  suffix,
  color = 'text-[rgb(var(--ctc-primary))]',
  bgColor = 'bg-[rgb(var(--ctc-primary))]/10',
  variant = 'desktop',
}: StatCardProps) {
  const size = variant === 'mobile' ? 'w-10 h-10' : 'w-12 h-12';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-5"
    >
      <div className={`${bgColor} ${size} rounded-lg flex items-center justify-center mb-3`}>
        <Icon className={`${color} ${variant === 'mobile' ? 'w-5 h-5' : 'w-6 h-6'}`} />
      </div>
      <div className="text-2xl font-bold text-gray-900">
        {value}{suffix || ''}
      </div>
      <div className="text-sm text-gray-500 mt-1">{label}</div>
    </motion.div>
  );
}
```

### 5.2 SectionHeader

```tsx
interface SectionHeaderProps {
  heading: string;
  intro?: string;
  actionLabel?: string;
  actionHref?: string;
  className?: string;
}

export default function SectionHeader({
  heading,
  intro,
  actionLabel,
  actionHref,
  className = '',
}: SectionHeaderProps) {
  return (
    <div className={`flex items-center justify-between mb-10 ${className}`}>
      <div>
        <h2 className="text-3xl font-bold text-gray-900">{heading}</h2>
        {intro && <p className="text-gray-500 mt-2">{intro}</p>}
      </div>
      {actionLabel && actionHref && (
        <Link href={actionHref as any}
          className="text-[rgb(var(--ctc-primary))] font-medium flex items-center gap-1
                     hover:text-[rgb(var(--ctc-primary-dark))]">
          {actionLabel} <HiChevronRight className="w-4 h-4" />
        </Link>
      )}
    </div>
  );
}
```

---

## 6. Extendable Pages — Benefits

| Benefit | Description |
|---------|-------------|
| **Reusability** | `StatCard` used on homepage, dashboard, about page — once |
| **Testability** | Each component has isolated unit tests |
| **CMS Integration** | Components accept `data` from CMS, API, or static fallback |
| **Responsive Variants** | Single component renders differently per breakpoint |
| **Lazy Loading** | `dynamic(() => import('@/components/pages/home/HomeHero'))` for code splitting |
| **Storybook-Ready** | Flat prop interfaces → easy to document |
| **A/B Testing** | Swap components at page level without touching logic |
| **Composition** | Pages are thin orchestrators, components do the heavy lifting |

---

## 7. How to Add a New Page

### Step-by-step

1. **Create page route:** `src/app/courses/page.tsx` (Next.js file-based routing)
2. **Create page components:** `src/components/pages/courses/CourseGrid.tsx`, `CourseFilters.tsx`, `CourseCard.tsx`
3. **Add RTK Query endpoint:** `src/store/api/endpoints/courses.ts` (if new data source)
4. **Compose in page:**

```tsx
// src/app/courses/page.tsx
'use client';
import { useResponsiveVariant } from '@/hooks/useResponsiveVariant';
import { useGetCoursesQuery } from '@/store/api/endpoints/courses';
import PublicLayout from '@/components/layouts/PublicLayout';
import CourseGrid from '@/components/pages/courses/CourseGrid';
import CourseFilters from '@/components/pages/courses/CourseFilters';
import SectionHeader from '@/components/pages/shared/SectionHeader';

export default function CoursesPage() {
  const variant = useResponsiveVariant();
  const { data, isLoading, error } = useGetCoursesQuery({ page: 1 });

  return (
    <PublicLayout variant={variant}>
      <div className="max-w-7xl mx-auto px-4 py-10">
        <SectionHeader heading="All Courses" intro="Browse our full catalog" />
        <CourseGrid data={data?.results} isLoading={isLoading} error={error} variant={variant} />
      </div>
    </PublicLayout>
  );
}
```

5. **Add tests:**

```tsx
// src/test/CourseGrid.test.tsx
import { render, screen } from '@testing-library/react';
import CourseGrid from '@/components/pages/courses/CourseGrid';

describe('CourseGrid', () => {
  it('shows loading skeleton when isLoading', () => { ... });
  it('shows error state when error is provided', () => { ... });
  it('shows empty state when data is empty', () => { ... });
  it('renders course cards when data is present', () => { ... });
  it('renders 1 column on mobile variant', () => { ... });
  it('renders 3 columns on desktop variant', () => { ... });
});
```

6. **Run tests:** `npm run test`

---

## 8. Build Targets & Platform Matrix

| Platform | Build Command | Output | Notes |
|----------|--------------|--------|-------|
| **Web (dev)** | `npm run dev` | `localhost:3457` | Hot reload, no optimization |
| **Web (prod)** | `npm run build && npm start` | `.next/` | Optimized, minified |
| **Static Export** | `next build` (with `output: 'export'`) | `out/` | For CDN/S3 hosting |
| **Docker** | `docker build -t lms-frontend .` | Container image | `Dockerfile` in `projects/lms/front-end/` |
| **Windows** | `npm run build` (Node 20+ native) | `.next/` | No WSL required |
| **macOS** | `npm run build` (Node 20+ native) | `.next/` | Apple Silicon native |
| **PWA** | `npm run build` + service worker | `.next/` | Offline-capable |

### Dockerfile (Future)

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./
EXPOSE 3457
CMD ["npm", "start"]
```

---

## Progress

| Task | Status | Notes |
|------|:------:|-------|
| Create `components/pages/` directories | ⬜ | All subdirectories |
| Extract `HomeHero` from `app/page.tsx` | ⬜ | Phase 1 dependent |
| Extract `HomeStats` | ⬜ | Uses `StatCard` |
| Extract `HomeFeaturedCourses` | ⬜ | Uses `CourseCard` |
| Extract `HomeCTA` | ⬜ | Uses `CtaSection` |
| Extract `HomeInstructors` | ⬜ | Uses `TeamCard` |
| Create `StatCard` shared component | ⬜ | First shared component |
| Create `SectionHeader` shared component | ⬜ | Used on most pages |
| Create `CourseCard` component | ⬜ | Used on courses + homepage |
| Create `CourseGrid` component | ⬜ | With 4-state handling |
| Create `LoginForm` component | ⬜ | Extracted from `app/login/` |
| Create `RegistrationForm` component | ⬜ | Extracted from `app/registration/` |
| Add tests for all page components | ⬜ | Vitest |
| Add E2E tests for composed pages | ⬜ | Playwright |
| Create `Dockerfile` | ⬜ | For CI deployment |

---

*Refer to [FRONTEND_ENHANCEMENT_MASTER_PLAN.md](./FRONTEND_ENHANCEMENT_MASTER_PLAN.md) for the full roadmap.*