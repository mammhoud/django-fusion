'use client';

import React, { useEffect, useState } from 'react';
import { fusionApi } from '@/lib/api-client';
import type { FusionWagtailPage as WagtailPage } from '@/lib/fusion-types';

interface FusionWagtailPageProps {
  slug: string;
  /** If true, fetch page data directly instead of using fragment pointer. */
  direct?: boolean;
  /** Pre-fetched page data — avoids redundant API call. */
  page?: WagtailPage | null;
}

/**
 * FusionWagtailPage — renders a Wagtail FusionPage with full layout awareness.
 *
 * Displays:
 * - Hero heading/subheading (home pages)
 * - Featured image (content pages)
 * - Richtext body content (injected via dangerouslySetInnerHTML)
 * - Custom CSS (if any)
 * - Loading/error states
 */
export default function FusionWagtailPage({ slug, direct = true, page: initialPage }: FusionWagtailPageProps) {
  const [page, setPage] = useState<WagtailPage | null>(initialPage ?? null);
  const [loading, setLoading] = useState(!initialPage);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialPage) {
      setPage(initialPage);
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    async function load() {
      try {
        const data = direct
          ? await fusionApi.fetchWagtailPage(slug)
          : await fusionApi.fetchWagtailPageDecoded(slug);
        if (cancelled) return;
        setPage(data);
        setLoading(false);
      } catch (err) {
        if (cancelled) return;
        try {
          const data = await fusionApi.fetchWagtailPageDecoded(slug);
          if (cancelled) return;
          setPage(data);
          setLoading(false);
        } catch {
          if (cancelled) return;
          setError(err instanceof Error ? err.message : 'Failed to load page');
          setLoading(false);
        }
      }
    }

    load();
    return () => { cancelled = true; };
  }, [slug, direct, initialPage]);

  if (loading) {
    return (
      <div className="fu-page fu-page--loading" aria-busy="true">
        <div className="fusion-skeleton h-64 w-full rounded-lg mb-6" />
        <div className="fusion-skeleton h-8 w-2/3 mb-4" />
        <div className="fusion-skeleton h-4 w-full mb-2" />
        <div className="fusion-skeleton h-4 w-5/6 mb-2" />
        <div className="fusion-skeleton h-4 w-3/4" />
      </div>
    );
  }

  if (error || !page) {
    return (
      <div className="fusion-error" role="alert">
        <h2 className="text-xl font-semibold text-red-600 mb-2">Failed to Load Page</h2>
        <p className="text-gray-500 mb-4">{error || 'Page not found'}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-fu-primary text-white rounded-lg hover:opacity-90"
        >
          Retry
        </button>
      </div>
    );
  }

  const isHome = page.type === 'FusionHomePage';

  return (
    <article
      className={`fu-page fu-page--${page.type.toLowerCase()} fu-layout-${page.layout}`}
      data-fusion-page-slug={page.slug}
      data-fusion-page-layout={page.layout}
    >
      {page.custom_css && <style dangerouslySetInnerHTML={{ __html: page.custom_css }} />}

      {isHome && page.hero_heading && (
        <section className="fu-hero">
          <div className="fu-hero__inner max-w-4xl mx-auto px-4 py-20 text-center">
            <h1 className="fu-hero__heading text-4xl md:text-5xl font-bold mb-4">{page.hero_heading}</h1>
            {page.hero_subheading && (
              <p className="fu-hero__subheading text-lg text-gray-600 max-w-2xl mx-auto">{page.hero_subheading}</p>
            )}
          </div>
        </section>
      )}

      {!isHome && page.featured_image_url && (
        <div className="fu-featured-image mb-8">
          <img src={page.featured_image_url} alt={page.title} className="w-full h-64 md:h-96 object-cover rounded-lg" />
        </div>
      )}

      {!isHome && <h1 className="text-3xl md:text-4xl font-bold mb-6">{page.title}</h1>}

      {page.body && <div className="fu-prose prose max-w-none" dangerouslySetInnerHTML={{ __html: page.body }} />}

      {page.children && page.children.length > 0 && (
        <nav className="fu-child-pages mt-12 pt-8 border-t border-gray-200">
          <h2 className="text-xl font-semibold mb-4">In This Section</h2>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {page.children.map((child) => (
              <li key={child.id}>
                <a href={`/${child.slug}`} className="block p-4 rounded-lg border border-gray-200 hover:border-fu-primary hover:shadow-sm transition-all">
                  <span className="font-medium text-fu-primary">{child.title}</span>
                </a>
              </li>
            ))}
          </ul>
        </nav>
      )}
    </article>
  );
}
