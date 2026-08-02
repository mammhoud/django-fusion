'use client';

import React, { useEffect, useState } from 'react';
import { fusionApi } from '@/lib/api-client';

interface LayoutInfo {
  available: string[];
  default: string;
}

interface FusionLayoutProps {
  children: React.ReactNode;
  layout?: string;
}

/**
 * FusionLayout — wraps page content in a server-rendered or client layout.
 *
 * Reads layout from server HTML or fetches available layouts from the
 * backend API. The layout name determines the CSS grid/flex structure.
 */
export default function FusionLayout({ children, layout = 'default' }: FusionLayoutProps) {
  const [layoutInfo, setLayoutInfo] = useState<LayoutInfo>({
    available: ['default', 'full_width', 'sidebar', 'blank'],
    default: 'default',
  });
  const [activeLayout, setActiveLayout] = useState(layout);

  useEffect(() => {
    fusionApi.fetchJson<LayoutInfo>('/layouts/')
      .then((envelope) => {
        const data = envelope.data;
        if (data && data.available) {
          setLayoutInfo(data);
          if (data.default) setActiveLayout(data.default);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (typeof document !== 'undefined') {
      const serverLayout = document.body.getAttribute('data-fusion-layout');
      if (serverLayout && layoutInfo.available.includes(serverLayout)) {
        setActiveLayout(serverLayout);
      }
    }
  }, [layoutInfo.available]);

  const layoutClass = `fusion-layout fusion-layout--${activeLayout}`;

  return (
    <div className={layoutClass} data-fusion-layout={activeLayout}>
      {activeLayout !== 'blank' && (
        <header className="fusion-layout__header">
          {/* Rendered by Header component or server-side */}
        </header>
      )}

      <div className={`fusion-layout__body ${activeLayout === 'sidebar' ? 'fusion-layout__body--with-sidebar' : ''}`}>
        {activeLayout === 'sidebar' && (
          <aside className="fusion-layout__sidebar">
            <nav className="fusion-sidebar-nav">
              <h3>Navigation</h3>
              <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/services">Services</a></li>
                <li><a href="/contact">Contact</a></li>
              </ul>
            </nav>
          </aside>
        )}

        <main className="fusion-layout__main" data-fusion-region="main">
          {children}
        </main>
      </div>

      {activeLayout !== 'blank' && (
        <footer className="fusion-layout__footer">
          <p>&copy; {new Date().getFullYear()} Fusion CMS. Powered by django-fusion + django-bolt.</p>
        </footer>
      )}
    </div>
  );
}
