/**
 * FusionMiddleware — React context provider that manages the
 * fragment-vs-data rendering decision for all POS pages.
 *
 * Uses the async ``fusionStore`` adapter that supports Tauri's
 * ``@tauri-apps/plugin-store`` as a persistence backend, falling
 * back to an in-memory map.
 *
 * Usage in a layout::
 *
 *     <FusionMiddleware>
 *       <App />
 *     </FusionMiddleware>
 *
 * Usage in any component::
 *
 *     import { useFusionMode } from './FusionMiddleware';
 *     const { mode, fallbackToData } = useFusionMode();
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import { fusionStore } from '../lib/fusion-store';

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
   * If not provided, the provider reads from ``fusionStore``.
   */
  initialMode?: FusionMode;
}

/**
 * React context provider that centralises the fragment-vs-data rendering
 * decision for all pages in the subtree.
 *
 * On mount, reads the cached preference from ``fusionStore`` (which was
 * populated by the health-check in ``main.tsx``).  If no preference is
 * cached yet, defaults to data mode.
 */
export function FusionMiddleware({
  children,
  initialMode,
}: FusionMiddlewareProps) {
  const [mode, setMode] = useState<FusionMode>(initialMode ?? 'loading');

  // Initialise from fusionStore on mount (async health-check result)
  useEffect(() => {
    if (initialMode) return; // caller-specified override wins

    fusionStore.getSessionPreference().then((pref) => {
      if (pref === true) {
        setMode('fragment');
      } else {
        // Default to data mode (false or undefined)
        setMode('data');
      }
    });
  }, [initialMode]);

  const fallbackToData = useCallback(() => {
    fusionStore.initSession(false).then(() => {
      setMode('data');
    }).catch(() => {
      setMode('data');
    });
  }, []);

  const enableFragments = useCallback(() => {
    fusionStore.initSession(true).then(() => {
      setMode('fragment');
    }).catch(() => {
      setMode('fragment');
    });
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
