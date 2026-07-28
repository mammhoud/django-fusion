'use client';

/**
 * FusionAssets — dynamically loads bottom (body-end) JS assets from the
 * django-fusion backend's ``/fusion/assets/manifest/`` endpoint.
 *
 * Top assets (CSS, fonts) are handled at build time via static imports in
 * layout.tsx (``fusion-theme.scss``, ``globals.css``). This component only
 * handles deferred JS scripts that load before ``</body>``.
 *
 * Usage (in root layout, before </body>)::
 *
 *   <FusionAssets />
 */
import React, { useEffect, useState } from 'react';
import { fusionApi } from '@/lib/api-client';

interface AssetManifest {
  bottom: {
    js: string[];
    inline_js: string[];
  };
}

export default function FusionAssets() {
  const [manifest, setManifest] = useState<AssetManifest | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Check if manifest was already injected server-side via django-fusion
    if (typeof window !== 'undefined' && (window as any).__FUSION_ASSETS__) {
      setManifest((window as any).__FUSION_ASSETS__);
      return;
    }

    fusionApi
      .fetchJson<AssetManifest>('/fusion/assets/manifest')
      .then((envelope) => {
        setManifest(envelope.data as AssetManifest);
      })
      .catch((err) => {
        console.warn('[FusionAssets] Failed to fetch asset manifest:', err);
        setError(err.message);
      });
  }, []);

  if (error || !manifest) {
    // Silently degrade — the app works without dynamic assets
    return null;
  }

  const bottom = manifest.bottom || { js: [], inline_js: [] };

  return (
    <>
      {/* JS scripts (deferred) */}
      {bottom.js.map((url) => (
        <script key={`js-${url}`} src={url} defer />
      ))}

      {/* Inline JS */}
      {bottom.inline_js.map((js, i) => (
        <script
          key={`inline-js-${i}`}
          dangerouslySetInnerHTML={{ __html: js }}
        />
      ))}
    </>
  );
}
