'use client';

import React, { useEffect, useRef, useState } from 'react';
import { fusionApi } from '@/lib/api-client';
import { fusionStore } from '@/lib/fusion-store';
import { fusionDecoder } from '@/lib/fusion-decoder';
import FusionWagtailPage from './FusionWagtailPage';
import type { FragmentPointer, FusionWagtailPage as WagtailPage } from '@/lib/fusion-types';

interface FusionProxyProps { slug: string; fallback?: React.ReactNode; }

export default function FusionProxy({ slug, fallback }: FusionProxyProps) {
  const [pointer, setPointer] = useState<FragmentPointer | null>(null);
  const [wagtailPage, setWagtailPage] = useState<WagtailPage | null>(null);
  const [html, setHtml] = useState<string | null>(null);
  const [mode, setMode] = useState<'loading'|'fragment'|'data'|'wagtail'|'error'>('loading');
  const [error, setError] = useState<string | null>(null);
  const healthChecked = useRef(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const ptr = await fusionApi.fetchFragment(slug);
        if (cancelled) return;
        setPointer(ptr); fusionStore.setRenderFirst(ptr.fusion_render_first);
        if (fusionDecoder.shouldRenderFragmentFirst(ptr)) {
          const h = await fusionApi.fetchPageHtml(slug);
          if (cancelled) return;
          setHtml(h); setMode('fragment');
        } else {
          try {
            const wp = await fusionApi.fetchWagtailPage(slug);
            if (cancelled) return;
            setWagtailPage(wp); setMode('wagtail');
          } catch { if (cancelled) return; setMode('data'); }
        }
      } catch {
        try {
          const wp = await fusionApi.fetchWagtailPage(slug);
          if (cancelled) return;
          setWagtailPage(wp); setMode('wagtail');
        } catch {
          try {
            const h = await fusionApi.fetchPageHtml(slug);
            if (cancelled) return;
            setHtml(h); setMode('fragment');
          } catch (err) {
            if (cancelled) return;
            setError(err instanceof Error ? err.message : 'Failed to load'); setMode('error');
          }
        }
      }
    })();
    return () => { cancelled = true; };
  }, [slug]);

  useEffect(() => {
    if (healthChecked.current) return;
    healthChecked.current = true;
    fusionApi.checkHealth().then(h=>fusionStore.initFromHealth(h.fusion_render_first)).catch(()=>fusionStore.setMode('data'));
  }, []);

  if (mode === 'loading') return (<div className="fusion-page p-8 space-y-4"><div className="fusion-skeleton h-8 w-2/3"/><div className="fusion-skeleton h-4 w-full"/></div>);
  if (mode === 'error') return (<div className="fusion-error">{fallback||<><h2>Error</h2><p>{error}</p><button onClick={()=>window.location.reload()}>Retry</button></>}</div>);
  if (mode === 'fragment' && html) return (<div className="fusion-page" dangerouslySetInnerHTML={{__html:html}}/>);
  if (mode === 'wagtail' && wagtailPage) return <FusionWagtailPage slug={slug} direct={false} page={wagtailPage}/>;
  if (mode === 'data' && pointer) return (<div className="fusion-page"><h1 className="text-3xl font-bold mb-6">{pointer.title||slug}</h1><p className="text-gray-500">{pointer.component}</p></div>);
  return null;
}
