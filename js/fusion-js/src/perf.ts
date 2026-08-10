/**
 * Skeleton performance metrics — Real User Monitoring (RUM).
 *
 * Captures skeleton rendering timing and exposes it via
 * ``window.__FUSION_PERF__`` so analytics / monitoring can
 * track perceived load times in production.
 *
 * Usage::
 *
 *   import { initSkeletonPerf } from 'fusion-js/perf';
 *   initSkeletonPerf();
 *
 * After initialisation, ``window.__FUSION_PERF__`` contains::
 *
 *   {
 *     skeletonCount: 5,
 *     skeletonRenderMs: 12.3,
 *     firstContentfulSkeletonMs: 45.7,
 *     pagePath: "pages/home.html",
 *     timestamp: "2026-08-10T14:00:00.000Z",
 *   }
 */

// ── types ─────────────────────────────────────────────────────────────

export interface SkeletonPerfEntry {
  /** Number of skeleton placeholders rendered. */
  skeletonCount: number;
  /** Time spent rendering all skeletons (ms). */
  skeletonRenderMs: number;
  /** Time from navigation start to first skeleton in the DOM (ms). */
  firstContentfulSkeletonMs: number;
  /** Page template path (from the manifest). */
  pagePath?: string;
  /** ISO-8601 timestamp of the measurement. */
  timestamp: string;
}

declare global {
  interface Window {
    __FUSION_PERF__?: SkeletonPerfEntry;
  }
}

// ── init ──────────────────────────────────────────────────────────────

export function initSkeletonPerf(): void {
  if (typeof window === 'undefined') return;

  const nav = performance?.getEntriesByType?.('navigation')?.[0] as
    | PerformanceNavigationTiming
    | undefined;
  const navStart = nav?.startTime ?? 0;

  const manifest = window.__FUSION_SKELETON_MANIFEST__;
  if (!manifest?.skeletons) return;

  let firstSkeletonTime = 0;
  const renderStart = performance.now();

  // Observe when the first skeleton element enters the DOM
  const observer = new MutationObserver(() => {
    const first = document.querySelector('[data-skeleton]');
    if (first && firstSkeletonTime === 0) {
      firstSkeletonTime = performance.now();
      observer.disconnect();
    }
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
  });

  // Collect after a short delay to allow render to complete
  setTimeout(() => {
    observer.disconnect();

    const renderEnd = performance.now();
    const entry: SkeletonPerfEntry = {
      skeletonCount: manifest.skeletons.length,
      skeletonRenderMs: Math.round((renderEnd - renderStart) * 10) / 10,
      firstContentfulSkeletonMs: Math.round(
        (firstSkeletonTime - navStart) * 10,
      ) / 10,
      pagePath: (manifest as unknown as Record<string, unknown>).pagePath as
        | string
        | undefined,
      timestamp: new Date().toISOString(),
    };

    window.__FUSION_PERF__ = entry;

    // Report to analytics if available
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'fusion_skeleton_perf', {
        skeleton_count: entry.skeletonCount,
        skeleton_render_ms: entry.skeletonRenderMs,
        first_contentful_skeleton_ms: entry.firstContentfulSkeletonMs,
      });
    }
  }, 100);
}

// ── auto-init ─────────────────────────────────────────────────────────

if (typeof window !== 'undefined' && window.__FUSION_SKELETON_MANIFEST__) {
  initSkeletonPerf();
}
