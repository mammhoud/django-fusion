/**
 * FusionProxy — POS Tauri component that fetches a server-rendered HTML
 * fragment from the sidecar (via ``/fusion/health`` or a custom endpoint)
 * and injects it into the React tree using ``dangerouslySetInnerHTML``.
 *
 * Adapted from the LMS version — uses the POS ``Skeleton`` component for
 * loading state instead of ``LoadingSkeleton``, and fetches from the
 * sidecar URL via the local ``fusionStore``.
 *
 * Usage::
 *
 *     <FusionProxy
 *       fragmentUrl="http://127.0.0.1:8765/fusion/render/dashboard"
 *       onError={() => setMode('data')}
 *     />
 */

import { useEffect, useRef, useState } from 'react';
import { SkeletonText } from './Skeleton';

interface FusionProxyProps {
  /** URL that returns the server-rendered HTML fragment. */
  fragmentUrl: string;
  /** Called when fetching or rendering the fragment fails. */
  onError?: () => void;
  /** When true, inline ``<script>`` tags in the fragment are re-evaluated. */
  enableScripts?: boolean;
  /** Optional content to show on error. */
  errorFallback?: React.ReactNode;
}

export function FusionProxy({
  fragmentUrl,
  onError,
  enableScripts = false,
  errorFallback,
}: FusionProxyProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [html, setHtml] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    fetch(fragmentUrl, { headers: { Accept: 'text/html' } })
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

  if (isLoading) {
    return (
      <div className="p-4 space-y-3">
        <SkeletonText lines={3} />
        <SkeletonText lines={2} />
      </div>
    );
  }

  if (hasError || html === null) {
    return (
      <>
        {errorFallback !== undefined ? (
          errorFallback
        ) : (
          <div className="p-4 text-sm text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-800">
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

export default FusionProxy;
