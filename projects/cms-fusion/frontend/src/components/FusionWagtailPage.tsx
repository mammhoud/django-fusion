'use client';

import React, { useEffect, useState } from 'react';
import { fusionApi } from '@/lib/api-client';
import type { FusionWagtailPage as WagtailPage } from '@/lib/fusion-types';

interface Props { slug: string; direct?: boolean; page?: WagtailPage | null; }

export default function FusionWagtailPage({ slug, direct = true, page: initialPage }: Props) {
  const [page, setPage] = useState<WagtailPage | null>(initialPage ?? null);
  const [loading, setLoading] = useState(!initialPage);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialPage) { setPage(initialPage); setLoading(false); return; }
    let cancelled = false;
    setLoading(true); setError(null);
    (async () => {
      try {
        const data = direct ? await fusionApi.fetchWagtailPage(slug) : await fusionApi.fetchWagtailPageDecoded(slug);
        if (cancelled) return;
        setPage(data); setLoading(false);
      } catch {
        try {
          const data = await fusionApi.fetchWagtailPageDecoded(slug);
          if (cancelled) return;
          setPage(data); setLoading(false);
        } catch (err) {
          if (cancelled) return;
          setError(err instanceof Error ? err.message : 'Failed'); setLoading(false);
        }
      }
    })();
    return () => { cancelled = true; };
  }, [slug, direct, initialPage]);

  if (loading) return (<div className="fu-page"><div className="fusion-skeleton h-64 w-full rounded-lg mb-6"/></div>);
  if (error||!page) return (<div className="fusion-error"><h2>Failed</h2><p>{error}</p><button onClick={()=>window.location.reload()}>Retry</button></div>);

  const isHome = page.type === 'FusionHomePage';
  return (
    <article className={`fu-page fu-layout-${page.layout}`}>
      {page.custom_css && <style dangerouslySetInnerHTML={{__html:page.custom_css}}/>}
      {isHome && page.hero_heading && (<section className="fu-hero"><div className="max-w-4xl mx-auto px-4 py-20 text-center"><h1 className="text-4xl font-bold mb-4">{page.hero_heading}</h1>{page.hero_subheading && <p className="text-lg text-gray-600">{page.hero_subheading}</p>}</div></section>)}
      {!isHome && page.featured_image_url && <img src={page.featured_image_url} alt={page.title} className="w-full h-64 object-cover rounded-lg mb-8"/>}
      {!isHome && <h1 className="text-3xl font-bold mb-6">{page.title}</h1>}
      {page.body && <div className="fu-prose prose" dangerouslySetInnerHTML={{__html:page.body}}/>}
      {page.children && page.children.length>0 && (<nav className="mt-12 pt-8 border-t"><h2 className="text-xl font-semibold mb-4">In This Section</h2><ul className="grid grid-cols-1 md:grid-cols-2 gap-4">{page.children.map(c=><li key={c.id}><a href={`/${c.slug}`} className="block p-4 rounded-lg border hover:border-fu-primary">{c.title}</a></li>)}</ul></nav>)}
    </article>
  );
}
