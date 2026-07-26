'use client';

import { useEffect, useRef, useState } from 'react';
import LoadingSkeleton from '@/components/ui/LoadingSkeleton';

interface FusionProxyProps {
  /** URL that returns the server-rendered HTML fragment. */
  fragmentUrl: string;
  /** Called when fetching or rendering the fragment fails. */
  onError?: () => void;
  /** When true, inline ``<script>`` tags in the fragment are re-evaluated. */
  enableScripts?: boolean;
  /** Optional content to show on error. */
  errorFallback?: React.ReactNode;
  /** Optional request headers to pass to the fetch call. */
  headers?: Record<string, string>;
}

/**
 * Fetch a django-fusion server-rendered HTML fragment and inject it into the
 * React tree. The component handles loading, error, and optionally re-injects
 * inline ``<script>`` tags so that widgets / HTMX inside the fragment keep
 * working after the initial render.
 */
export function FusionProxy({
  fragmentUrl,
  onError,
  enableScripts = false,
  errorFallback,
  headers,
}: FusionProxyProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [html, setHtml] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    fetch(fragmentUrl, { headers: { Accept: 'text/html', ...headers } })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Fragment returned ${res.status}`);
        }
        return res.text();
      })
      .then((text) => {
        if (!cancelled) {
          setHtml(text);
          setIsLoading(false);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setHasError(true);
          setIsLoading(false);
          onError?.();
        }
      });

    return () => {
      cancelled = true;
    };
  }, [fragmentUrl, onError]);

  // Re-evaluate inline <script> tags on demand so that HTMX / widgets work.
  useEffect(() => {
    if (!enableScripts || !html || !ref.current) return;

    const scripts = ref.current.querySelectorAll<HTMLScriptElement>('script');
    scripts.forEach((oldScript) => {
      const newScript = document.createElement('script');
      Array.from(oldScript.attributes).forEach((attr) => {
        newScript.setAttribute(attr.name, attr.value);
      });
      // Only copy inline script text; external scripts rely on the copied
      // ``src`` attribute and do not need a text node.
      if (!oldScript.src && oldScript.innerHTML) {
        newScript.appendChild(document.createTextNode(oldScript.innerHTML));
      }
      oldScript.parentNode?.replaceChild(newScript, oldScript);
    });
  }, [html, enableScripts]);

  if (isLoading) return <LoadingSkeleton />;
  if (hasError || html === null) {
    return (
      <>
        {errorFallback !== undefined ? (
          errorFallback
        ) : (
          <div className="p-4 text-sm text-red-600 bg-red-50 rounded-lg">
            Unable to render this section. Please try refreshing the page.
          </div>
        )}
      </>
    );
  }

  return (
    <div
      ref={ref}
      // eslint-disable-next-line react/no-danger
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
