'use client';

import React, { useEffect, useRef, useState } from 'react';
import { fusionApi } from '@/lib/api-client';
import { fusionStore } from '@/lib/fusion-store';
import { fusionDecoder } from '@/lib/fusion-decoder';
import FusionWagtailPage from './FusionWagtailPage';
import type { FragmentPointer, FusionWagtailPage as WagtailPage } from '@/lib/fusion-types';

interface FusionProxyProps {
  slug: string;
  fallback?: React.ReactNode;
}

/**
 * FusionProxy — renders page content with bolt API + fusion fallback.
 *
 * Strategy:
 * 1. Try fragment pointer → fetch HTML if render-first
 * 2. Try Wagtail page data (bolt API) → render with FusionWagtailPage
 * 3. Fallback to fusion_render_first (HTML directly)
 * 4. Show error boundary on complete failure
 */
export default function FusionProxy({ slug, fallback }: FusionProxyProps) {
  const [pointer, setPointer] = useState<FragmentPointer | null>(null);
  const [wagtailPage, setWagtailPage] = useState<WagtailPage | null>(null);
  const [html, setHtml] = useState<string | null>(null);
  const [mode, setMode] = useState<'loading' | 'fragment' | 'data' | 'wagtail' | 'error'>('loading');
  const [error, setError] = useState<string | null>(null);
  const healthChecked = useRef(false);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        // 1. Try fragment pointer
        const ptr = await fusionApi.fetchFragment(slug);
        if (cancelled) return;
        setPointer(ptr);
        fusionStore.setRenderFirst(ptr.fusion_render_first);

        if (fusionDecoder.shouldRenderFragmentFirst(ptr)) {
          const renderedHtml = await fusionApi.fetchPageHtml(slug);
          if (cancelled) return;
          setHtml(renderedHtml);
          setMode('fragment');
        } else {
          // 2. Try Wagtail page data
          try {
            const wp = await fusionApi.fetchWagtailPage(slug);
            if (cancelled) return;
            setWagtailPage(wp);
            setMode('wagtail');
          } catch {
            if (cancelled) return;
            setMode('data');
          }
        }
      } catch (err) {
        if (cancelled) return;
        // 3. Fallback: try Wagtail directly
        try {
          const wp = await fusionApi.fetchWagtailPage(slug);
          if (cancelled) return;
          setWagtailPage(wp);
          setMode('wagtail');
        } catch {
          // 4. Fallback: try fusion_render_first HTML
          try {
            const renderedHtml = await fusionApi.fetchPageHtml(slug);
            if (cancelled) return;
            setHtml(renderedHtml);
            setMode('fragment');
          } catch (fallbackErr) {
            if (cancelled) return;
            setError(err instanceof Error ? err.message : 'Failed to load page content');
            setMode('error');
          }
        }
      }
    }

    load();
    return () => { cancelled = true; };
  }, [slug]);

  useEffect(() => {
    if (healthChecked.current) return;
    healthChecked.current = true;
    fusionApi.checkHealth().then((health) => {
      fusionStore.initFromHealth(health.fusion_render_first);
    }).catch(() => fusionStore.setMode('data'));
  }, []);

  // ── Loading ──
  if (mode === 'loading') {
    return (
      <div className="fusion-page p-8 space-y-4" data-testid="fusion-loading">
        <div className="fusion-skeleton h-8 w-2/3" />
        <div className="fusion-skeleton h-4 w-full" />
        <div className="fusion-skeleton h-4 w-5/6" />
        <div className="fusion-skeleton h-64 w-full" />
      </div>
    );
  }

  // ── Error ──
  if (mode === 'error') {
    return (
      <div className="fusion-error" data-testid="fusion-error">
        {fallback || (
          <>
            <h2>Something went wrong</h2>
            <p>{error || 'An unexpected error occurred'}</p>
            <button onClick={() => window.location.reload()}>Try Again</button>
          </>
        )}
      </div>
    );
  }

  // ── Fragment mode (server-rendered HTML) ──
  if (mode === 'fragment' && html) {
    return (
      <div className="fusion-page" data-testid="fusion-fragment"
        dangerouslySetInnerHTML={{ __html: html }} />
    );
  }

  // ── Wagtail mode (model-backed page data) ──
  if (mode === 'wagtail' && wagtailPage) {
    return <FusionWagtailPage slug={slug} direct={false} page={wagtailPage} />;
  }

  // ── Data mode (fragment pointer only, no Wagtail data) ──
  if (mode === 'data' && pointer) {
    return (
      <div className="fusion-page" data-testid="fusion-data">
        <h1 className="text-3xl font-bold mb-6">{pointer.title || slug}</h1>
        <p className="text-gray-500">Component: {pointer.component} | Fragment: {pointer.fragment_name}</p>
        <p className="text-sm text-gray-400 mt-2">URL: {pointer.fragment_url}</p>
      </div>
    );
  }

  return null;
}
