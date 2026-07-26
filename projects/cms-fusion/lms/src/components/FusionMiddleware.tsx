'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import { fusionDecoder } from '@/lib/fusion-decoder';

// ─── Types ──────────────────────────────────────────────────────────

/** Rendering mode, used by FusionMiddleware to decide fragment vs data. */
export type FusionMode = 'fragment' | 'data' | 'loading';

/** Value exposed by the FusionContext. */
export interface FusionContextValue {
  /** Current rendering mode. */
  mode: FusionMode;
  /** Switch from fragment mode to data mode (e.g. after a fragment error). */
  fallbackToData: () => void;
  /** Switch from data mode to fragment mode (e.g. user preference toggle). */
  enableFragments: () => void;
}

// ─── Context ────────────────────────────────────────────────────────

const FusionContext = createContext<FusionContextValue>({
  mode: 'loading',
  fallbackToData: () => {},
  enableFragments: () => {},
});

// ─── Provider ───────────────────────────────────────────────────────

interface FusionMiddlewareProps {
  /** Children to wrap with fusion mode context. */
  children: ReactNode;
  /**
   * Optional initial mode override.
   * If not provided, the provider reads from ``sessionStorage`` via
   * ``fusionDecoder.getSessionPreference()``.
   */
  initialMode?: FusionMode;
}

/**
 * React context provider that centralises the fragment-vs-data rendering
 * decision for all pages in the subtree.
 *
 * Usage in a layout::
 *
 *     <FusionMiddleware>
 *       <App />
 *     </FusionMiddleware>
 *
 * Usage in any component::
 *
 *     const { mode, fallbackToData, enableFragments } = useFusionMode();
 *
 *     if (mode === 'fragment') {
 *       return <FusionProxy ... onError={fallbackToData} />;
 *     }
 *     return <PageContent ... />;
 */
export function FusionMiddleware({
  children,
  initialMode,
}: FusionMiddlewareProps) {
  const [mode, setMode] = useState<FusionMode>(initialMode ?? 'loading');

  // Initialise from sessionStorage on mount
  useEffect(() => {
    if (initialMode) return; // caller-specified override wins

    const pref = fusionDecoder.getSessionPreference();
    if (pref === true) {
      setMode('fragment');
    } else {
      // Default to data mode (false or undefined)
      setMode('data');
    }
  }, [initialMode]);

  const fallbackToData = useCallback(() => {
    fusionDecoder.clearSession();
    fusionDecoder.initSession(false);
    setMode('data');
  }, []);

  const enableFragments = useCallback(() => {
    fusionDecoder.initSession(true);
    setMode('fragment');
  }, []);

  return (
    <FusionContext.Provider value={{ mode, fallbackToData, enableFragments }}>
      {children}
    </FusionContext.Provider>
  );
}

// ─── Hook ───────────────────────────────────────────────────────────

/**
 * Hook to read the current fusion rendering mode and toggle functions.
 *
 * Must be called within a ``<FusionMiddleware>`` provider.
 */
export function useFusionMode(): FusionContextValue {
  return useContext(FusionContext);
}

export default FusionMiddleware;
