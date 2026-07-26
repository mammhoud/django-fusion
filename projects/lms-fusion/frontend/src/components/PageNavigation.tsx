'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { fusionApi } from '@/lib/api-client';
import type { FusionWagtailPage } from '@/lib/fusion-types';

export default function PageNavigation({ currentSlug }: { currentSlug?: string }) {
  const [pages, setPages] = useState<FusionWagtailPage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fusionApi.fetchPageList().then((d) => { setPages(d.pages); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <nav className="fu-page-nav fu-page-nav--loading" aria-label="Page navigation">
        <div className="flex gap-2">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="fusion-skeleton h-6 w-20 rounded" />
          ))}
        </div>
      </nav>
    );
  }

  if (pages.length === 0) return null;

  return (
    <nav className="fu-page-nav" aria-label="Page navigation">
      <ul className="flex flex-wrap gap-2">
        {pages.filter((p) => p.show_in_nav).map((page) => {
          const href = page.slug === 'home' ? '/' : `/${page.slug}`;
          const isActive = currentSlug === page.slug || (!currentSlug && page.slug === 'home');
          return (
            <li key={page.id}>
              <Link href={href}
                className={`inline-block px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-fu-primary text-white' : 'text-gray-600 hover:bg-gray-100 hover:text-fu-primary'
                }`}
                aria-current={isActive ? 'page' : undefined}>
                {page.title}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
