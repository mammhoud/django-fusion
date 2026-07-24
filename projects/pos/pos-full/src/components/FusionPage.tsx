/**
 * FusionPage — POS Tauri page-level wrapper that implements the
 * fusion_render_first contract.
 *
 * Unlike the LMS version (which uses RTK Query), the POS version
 * accepts page data and a fetch function via props since POS pages
 * have diverse data sources (sidecar CRUD endpoints, Redux store, etc.).
 *
 * Usage in a page::
 *
 *     import { FusionPage } from '../components/FusionPage';
 *     import { FusionProxy } from '../components/FusionProxy';
 *
 *     function DashboardPage() {
 *       return (
 *         <FusionPage
 *           fragmentUrl="http://127.0.0.1:8765/fusion/render/dashboard"
 *           data={dashboardData}
 *           isLoading={isLoading}
 *           error={error}
 *         >
 *           {(data) => <DashboardContent data={data} />}
 *         </FusionPage>
 *       );
 *     }
 */

import { useFusionMode, type FusionMode } from './FusionMiddleware';
import { FusionProxy } from './FusionProxy';
import { SkeletonText, SkeletonCard } from './Skeleton';
import type { ReactNode } from 'react';

// ─── Types ──────────────────────────────────────────────────────────

export interface FusionPageFallbackState {
  isLoading: boolean;
  hasError: boolean;
}

interface FusionPageProps<T = unknown> {
  /**
   * URL that returns the server-rendered HTML fragment.
   * When provided, the page will render the fragment in fragment mode.
   */
  fragmentUrl?: string;
  /** Page data used in data mode. */
  data?: T;
  /** Whether data is still loading. */
  isLoading?: boolean;
  /** Error state from data fetching. */
  error?: unknown;
  /** Render prop receiving the data and fallback state. */
  children: (data: T | undefined, fallback: FusionPageFallbackState) => ReactNode;
  /**
   * When true, use standalone mode (read session preference directly
   * from fusionStore) instead of reading from FusionMiddleware context.
   */
  standalone?: boolean;
  /** When true, inline <script> tags in the server fragment are re-evaluated. */
  enableScripts?: boolean;
  /** Optional content to show if the server fragment fails to load. */
  errorFallback?: React.ReactNode;
  /**
   * Optional skeleton variant to show during loading.
   * Defaults to 'text'.
   */
  skeletonVariant?: 'text' | 'card' | 'detail';
}

// ═══════════════════════════════════════════════════════════════════
// FusionPage
// ═══════════════════════════════════════════════════════════════════

/**
 * Page-level wrapper that implements the fusion_render_first contract.
 *
 * **Middleware mode** (default):
 * - Reads the rendering mode from FusionMiddleware context via useFusionMode()
 * - Fragment mode: renders FusionProxy with the provided fragmentUrl
 * - Data mode: renders children with data props
 *
 * **Standalone mode** (standalone=true):
 * - Uses default data mode (no fragment fetching)
 *
 * Usage::
 *
 *     <FusionPage
 *       fragmentUrl={`${SIDECAR_BASE}/fusion/render/dashboard`}
 *       data={dashboard}
 *       isLoading={loading}
 *       error={err}
 *     >
 *       {(data) => <DashboardContent data={data} />}
 *     </FusionPage>
 */
export function FusionPage<T = unknown>({
  fragmentUrl,
  data,
  isLoading = false,
  error,
  children,
  standalone,
  enableScripts,
  errorFallback,
  skeletonVariant = 'text',
}: FusionPageProps<T>) {
  if (standalone) {
    // Standalone mode — always use data mode
    return renderDataMode(data, isLoading, error, children, skeletonVariant);
  }

  return (
    <FusionPageMiddleware
      fragmentUrl={fragmentUrl}
      data={data}
      isLoading={isLoading}
      error={error}
      children={children}
      enableScripts={enableScripts}
      errorFallback={errorFallback}
      skeletonVariant={skeletonVariant}
    />
  );
}

// ═══════════════════════════════════════════════════════════════════
// Middleware mode — reads mode from FusionMiddleware context
// ═══════════════════════════════════════════════════════════════════

function FusionPageMiddleware<T = unknown>({
  fragmentUrl,
  data,
  isLoading,
  error,
  children,
  enableScripts,
  errorFallback,
  skeletonVariant,
}: FusionPageProps<T>) {
  const { mode, fallbackToData } = useFusionMode();

  if (mode === 'loading') {
    return <LoadingSkeleton variant={skeletonVariant ?? 'text'} />;
  }

  if (mode === 'fragment') {
    if (!fragmentUrl) {
      // No fragment URL available — fall back to data mode
      return renderDataMode(data, isLoading, error, children, skeletonVariant);
    }
    return (
      <FusionProxy
        fragmentUrl={fragmentUrl}
        onError={fallbackToData}
        enableScripts={enableScripts}
        errorFallback={errorFallback}
      />
    );
  }

  // Data mode
  return renderDataMode(data, isLoading, error, children, skeletonVariant);
}

// ═══════════════════════════════════════════════════════════════════
// Shared data rendering logic
// ═══════════════════════════════════════════════════════════════════

function renderDataMode<T>(
  data: T | undefined,
  isLoading: boolean | undefined,
  error: unknown,
  children: (data: T | undefined, fallback: FusionPageFallbackState) => ReactNode,
  skeletonVariant?: 'text' | 'card' | 'detail',
) {
  if (isLoading) {
    return <LoadingSkeleton variant={skeletonVariant ?? 'text'} />;
  }

  if (error) {
    return (
      <div className="p-4 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800">
        Unable to load page content. Please try again.
      </div>
    );
  }

  return (
    <>
      {children(data, { isLoading: isLoading ?? false, hasError: !!error })}
    </>
  );
}

// ═══════════════════════════════════════════════════════════════════
// Loading skeleton variants
// ═══════════════════════════════════════════════════════════════════

function LoadingSkeleton({ variant }: { variant: 'text' | 'card' | 'detail' }) {
  switch (variant) {
    case 'card':
      return (
        <div className="p-6">
          <SkeletonCard count={4} />
        </div>
      );
    case 'detail':
      return (
        <div className="p-6 space-y-6">
          <SkeletonText lines={1} className="w-1/3" />
          <SkeletonText lines={4} />
          <SkeletonText lines={3} />
          <SkeletonCard count={3} />
        </div>
      );
    case 'text':
    default:
      return (
        <div className="p-6 space-y-3">
          <SkeletonText lines={2} />
          <SkeletonText lines={3} />
        </div>
      );
  }
}

export default FusionPage;
