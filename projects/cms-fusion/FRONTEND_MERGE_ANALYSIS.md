# 📊 Frontend Comparison & Merge Analysis

**Path:** `projects/cms-fusion/`
**Date:** 2026-07-26

---

## Overview

Three frontend implementations exist under `projects/cms-fusion/`:

| Directory | Source Files | Tech Stack | Primary Purpose |
|-----------|:-----------:|------------|-----------------|
| `frontend/` | **36** | Next.js 14 + React 18 + Redux + Tailwind | **Fusion CMS** — Modern fusion-integrated frontend |
| `lms/` | **112** | Next.js 14 + React 18 + Redux + Stripe | **LMS** — Full learning management frontend |
| `front-end/` | **1,114** | Next.js 14 + React 18 + Redux + SCSS | **CTC Research** — Most comprehensive, includes dashboards + charts |

---

## Feature Comparison

| Feature | `frontend/` | `lms/` | `front-end/` |
|---------|:-----------:|:------:|:------------:|
| **Routes** | | | |
| Home page | ✅ | ✅ | ✅ |
| Dynamic pages `[slug]` | ✅ | ❌ | ❌ |
| Blog | ✅ | ✅ | ✅ |
| Blog detail | ✅ | ✅ | ✅ |
| Courses catalog | ✅ | ✅ | ✅ |
| Course detail | ✅ | ✅ | ✅ |
| Products | ✅ | ❌ | ❌ |
| About page | ❌ | ✅ | ✅ |
| Contact page | ❌ | ✅ | ✅ |
| FAQ page | ❌ | ✅ | ✅ |
| Events page | ❌ | ✅ | ✅ |
| Cart | ❌ | ✅ | ✅ |
| Checkout | ❌ | ✅ | ✅ |
| Shop | ❌ | ✅ | ✅ |
| Login/Auth | ❌ | ✅ | ✅ |
| Registration | ❌ | ✅ | ✅ |
| Instructor Dashboard | ❌ | ✅ | ✅ |
| Student Dashboard | ❌ | ✅ | ✅ |
| Profile/Settings | ❌ | ❌ | ✅ |
| Notifications | ❌ | ❌ | ✅ |
| Withdraw | ❌ | ❌ | ✅ |
| **Components** | | | |
| Header | ✅ | ✅ | ✅ |
| Footer | ✅ | ✅ | ✅ |
| ErrorBoundary | ✅ | ✅ | ✅ |
| AuthGuard | ✅ | ✅ | ✅ |
| Providers | ✅ | ✅ | ✅ |
| DashboardRedirect | ✅ | ✅ | ✅ |
| LanguageSwitcher | ✅ | ❌ | ✅ |
| PageNavigation | ✅ | ❌ | ❌ |
| FusionLayout | ✅ | ❌ | ❌ |
| FusionProxy | ✅ | ❌ | ❌ |
| FusionWagtailPage | ✅ | ❌ | ❌ |
| FusionPage | ❌ | ✅ | ✅ |
| FusionMiddleware | ❌ | ✅ | ❌ |
| LoadingSkeleton | ✅ | ❌ | ✅ |
| EmptyState | ❌ | ❌ | ✅ |
| StripePaymentForm | ❌ | ✅ | ❌ |
| RevenueChart | ❌ | ❌ | ✅ |
| EnrollmentTrendChart | ❌ | ❌ | ✅ |
| CompletionRateChart | ❌ | ❌ | ✅ |
| Quiz components | ❌ | ❌ | ✅ |
| **State Management** | | | |
| Redux Toolkit | ✅ | ✅ | ✅ |
| RTK Query - Auth | ❌ | ✅ | ✅ |
| RTK Query - Courses | ❌ | ✅ | ✅ |
| RTK Query - Blog | ❌ | ✅ | ✅ |
| RTK Query - Instructors | ❌ | ✅ | ✅ |
| RTK Query - Events | ❌ | ✅ | ✅ |
| RTK Query - Shop/Cart | ❌ | ✅ | ✅ |
| RTK Query - Payments | ❌ | ✅ | ❌ |
| RTK Query - Students | ❌ | ❌ | ✅ |
| RTK Query - Quizzes | ❌ | ❌ | ✅ |
| RTK Query - Notifications | ❌ | ❌ | ✅ |
| **Libraries** | | | |
| api-client.ts | ✅ | ❌ | ❌ |
| fusion-decoder.ts | ✅ | ✅ | ✅ |
| fusion-store.ts | ✅ | ❌ | ❌ |
| fusion-types.ts | ✅ | ✅ | ✅ |
| site-content.ts | ✅ | ❌ | ❌ |
| useCheckout hook | ❌ | ✅ | ❌ |
| **Styling** | | | |
| Tailwind CSS | ✅ | ✅ | ✅ |
| SCSS/SASS | ✅ | ❌ | ✅ |
| Fusion theme (shared with Django) | ✅ | ❌ | ❌ |
| **Testing** | | | |
| Unit tests (Vitest) | ❌ | ✅ | ✅ |
| E2E tests (Playwright) | ✅ | ✅ | ✅ |
| Visual regression tests | ❌ | ❌ | ✅ |
| Contract tests | ❌ | ✅ | ❌ |
| **Integrations** | | | |
| Stripe payments | ❌ | ✅ | ❌ |
| MSW (API mocking) | ❌ | ✅ | ❌ |
| Framer Motion animations | ✅ | ✅ | ✅ |
| Recharts | ✅ | ✅ | ✅ |
| **Fusion Integration** | | | |
| django-fusion layout | ✅ | ❌ | ❌ |
| FusionProxy fallback chain | ✅ | ✅ | ❌ |
| FusionWagtailPage | ✅ | ❌ | ❌ |
| FusionPage (component) | ❌ | ✅ | ✅ |
| SCSS theme shared with Django | ✅ | ❌ | ❌ |

---

## Most Feature-Rich: `front-end/` 🏆

With **1,114 source files**, the `front-end/` directory is the most comprehensive:
- Full dashboard system (instructor + student) with charts
- Complete Redux store with many endpoints
- Comprehensive SCSS styling system
- Extensive test suite (unit + E2E + visual regression)
- Profile, notifications, withdraw features
- Quiz and assignment management

## Most Fusion-Integrated: `frontend/` 🎯

The `frontend/` directory has the **best Fusion CMS integration**:
- FusionLayout, FusionProxy, FusionWagtailPage
- Fusion Store + Decoder + Types
- Shared SCSS theme with Django backend
- API client with proper fallback chain

---

## Merge Strategy

The merged result will live in: **`projects/cms-fusion/frontend/`**

### Merge Targets

| From | What to Merge |
|------|---------------|
| `lms/` | All remaining routes, Stripe integration, RTK Query endpoints, useCheckout hook, MSW setup, contract tests |
| `front-end/` | Dashboard components with charts, comprehensive Redux store, SCSS architecture, EmptyState, comprehensive tests |
| `frontend/` | **Keep as base** — Fusion architecture (FusionLayout, FusionProxy, FusionWagtailPage, fusion-store, fusion-types, fusion-decoder, api-client) |

### What to Keep From `frontend/`
✅ FusionLayout, FusionProxy, FusionWagtailPage
✅ fusion-store, fusion-types, fusion-decoder
✅ api-client, site-content
✅ LanguageSwitcher, PageNavigation
✅ Shared SCSS theme link (fusion-theme.scss)
✅ Dynamic `[slug]/page.tsx` routing
✅ Products page

### What to Merge From `lms/`
✅ All extra routes (about, contact, events, faq, cart, checkout, shop, login, registration, instructor-dashboard, student-dashboard)
✅ Stripe integration (@stripe/react-stripe-js, @stripe/stripe-js)
✅ RTK Query endpoints (auth, blog, courses, events, instructors, shop, carts, payments)
✅ useCheckout hook
✅ Contract tests
✅ MSW dev dependency

### What to Merge From `front-end/`
✅ Dashboard charts (RevenueChart, EnrollmentTrendChart, CompletionRateChart)
✅ EmptyState component
✅ Quiz components
✅ Comprehensive SCSS architecture
✅ Additional RTK Query endpoints (students, quizzes, notifications)
✅ Profile/settings page
✅ Notifications page
✅ Withdraw page
✅ Visual regression tests
✅ Comprehensive unit tests
