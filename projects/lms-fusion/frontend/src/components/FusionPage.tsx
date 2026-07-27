'use client';

import { useMemo, type ReactNode } from 'react';
import {
  useGetPageDataQuery,
} from '@/store/api/endpoints/pages';
import { useFusionMode } from '@/components/FusionMiddleware';
import { fusionDecoder } from '@/lib/fusion-decoder';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';
import ErrorState from '@/components/ui/ErrorState';
import FusionProxy from './FusionProxy';
import type { CmsPage } from '@/store/api/endpoints/pages';

export interface FusionPageFallbackState {
  isLoading: boolean;
  error?: any;
}

interface FusionPageProps {
  /** CMS page slug (home, about-us, privacy, faq, contact, ...). */
  slug: string;
  /** Render prop receiving the JSON page and fallback state. */
  children: (page: CmsPage | undefined, fallback: FusionPageFallbackState) => ReactNode;
  /** Optional RTK Query options for the page data query. */
  pageDataQueryOptions?: Parameters<typeof useGetPageDataQuery>[1];
  /**
   * When true, use standalone mode (read session preference directly)
   * instead of reading from FusionMiddleware context.
   * Use this when FusionMiddleware is not available in the component tree.
   */
  standalone?: boolean;
  /** When true, inline <script> tags in the server fragment are re-evaluated. */
  enableScripts?: boolean;
  /** Optional content to show if the server fragment fails to load. */
  errorFallback?: React.ReactNode;
}

/**
 * Page-level wrapper that implements the fusion_render_first contract
 * with FusionMiddleware integration.
 *
 * **Middleware mode** (default):
 * - Reads the rendering mode from FusionMiddleware context via useFusionMode()
 * - Fragment mode: renders FusionProxy with the page_data endpoint
 * - Data mode: fetches /apis/pages/<slug>/data/, decodes with FusionDecoder
 *
 * **Standalone mode** (standalone=true):
 * - Reads session preference directly from FusionDecoder.getSessionPreference()
 * - Same behavior but without requiring FusionMiddleware in the component tree
 *
 * Usage in a page::
 *
 *     <FusionPage slug="home">
 *       {(page, fallback) => <HomePageContent page={page} fallback={fallback} />}
 *     </FusionPage>
 */
export function FusionPage({
  slug,
  children,
  pageDataQueryOptions,
  standalone,
  enableScripts,
  errorFallback,
}: FusionPageProps) {
  if (standalone) {
    return (
      <FusionPageStandalone
        slug={slug}
        children={children}
        pageDataQueryOptions={pageDataQueryOptions}
        enableScripts={enableScripts}
        errorFallback={errorFallback}
      />
    );
  }

  return (
    <FusionPageMiddleware
      slug={slug}
      children={children}
      pageDataQueryOptions={pageDataQueryOptions}
      enableScripts={enableScripts}
      errorFallback={errorFallback}
    />
  );
}

// ═══════════════════════════════════════════════════════════════════
// Middleware mode — reads mode from FusionMiddleware context
// ═══════════════════════════════════════════════════════════════════

function FusionPageMiddleware({
  slug,
  children,
  pageDataQueryOptions,
  enableScripts,
  errorFallback,
}: FusionPageProps) {
  const { mode } = useFusionMode();

  if (mode === 'loading') return <LoadingSkeleton />;

  if (mode === 'fragment') {
    return (
      <FusionProxy slug={slug} fallback={errorFallback} />
    );
  }

  // Data mode
  return (
    <FusionPageDataInner
      slug={slug}
      children={children}
      pageDataQueryOptions={pageDataQueryOptions}
    />
  );
}

// ═══════════════════════════════════════════════════════════════════
// Standalone mode — reads session preference directly
// ═══════════════════════════════════════════════════════════════════

function FusionPageStandalone({
  slug,
  children,
  pageDataQueryOptions,
  enableScripts,
  errorFallback,
}: FusionPageProps) {
  const sessionPref = fusionDecoder.getSessionPreference();
  const renderHtml = sessionPref === true;

  if (renderHtml) {
    return (
      <FusionProxy slug={slug} fallback={errorFallback} />
    );
  }

  return (
    <FusionPageDataInner
      slug={slug}
      children={children}
      pageDataQueryOptions={pageDataQueryOptions}
    />
  );
}

// ═══════════════════════════════════════════════════════════════════
// Shared data-fetching inner component
// ═══════════════════════════════════════════════════════════════════

function FusionPageDataInner({
  slug,
  children,
  pageDataQueryOptions,
}: {
  slug: string;
  children: (page: CmsPage | undefined, fallback: FusionPageFallbackState) => ReactNode;
  pageDataQueryOptions?: Parameters<typeof useGetPageDataQuery>[1];
}) {
  const {
    data: pageData,
    isLoading: dataLoading,
    error: dataError,
  } = useGetPageDataQuery(slug, {
    ...pageDataQueryOptions,
  });

  const page = useMemo<CmsPage | undefined>(() => {
    if (!pageData?.encoded) return undefined;
    try {
      return fusionDecoder.decodeAs<CmsPage>(pageData.encoded);
    } catch {
      return undefined;
    }
  }, [pageData]);

  if (dataLoading) return <LoadingSkeleton />;
  if (dataError) {
    return <ErrorState message="Unable to load page content." />;
  }
  return <>{children(page, { isLoading: dataLoading, error: dataError })}</>;
}
