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
  /** Currently active language code (e.g. 'en', 'fr'). */
  language: string;
  /** Switch to a different language. Persisted in sessionStorage and cookie. */
  setLanguage: (code: string) => void;
}

// ─── Constants ──────────────────────────────────────────────────────

const LANGUAGE_KEY = 'django_language';
const FALLBACK_LANGUAGES = ['en', 'fr', 'es', 'de', 'ar'];
const DEFAULT_LANGUAGE = 'en';

// ─── Helpers ────────────────────────────────────────────────────────

function getStoredLanguage(): string {
  if (typeof sessionStorage === 'undefined') return DEFAULT_LANGUAGE;
  try {
    const stored = sessionStorage.getItem(LANGUAGE_KEY);
    if (stored && FALLBACK_LANGUAGES.includes(stored)) return stored;
  } catch { /* ignore */ }
  return DEFAULT_LANGUAGE;
}

function setStoredLanguage(code: string): void {
  if (typeof sessionStorage === 'undefined') return;
  try {
    sessionStorage.setItem(LANGUAGE_KEY, code);
  } catch { /* ignore */ }
}

function setLanguageCookie(code: string): void {
  // Set a cookie so SSR and initial page loads inherit the language
  try {
    document.cookie = `${LANGUAGE_KEY}=${code}; path=/; max-age=${60 * 60 * 24 * 365}; SameSite=Lax`;
  } catch { /* ignore */ }
}

// ─── Context ────────────────────────────────────────────────────────

const FusionContext = createContext<FusionContextValue>({
  mode: 'loading',
  fallbackToData: () => {},
  enableFragments: () => {},
  language: DEFAULT_LANGUAGE,
  setLanguage: () => {},
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
  /** Optional initial language override. */
  initialLanguage?: string;
}

/**
 * React context provider that centralises the fragment-vs-data rendering
 * decision AND the active language for all pages in the subtree.
 *
 * Usage in a layout::
 *
 *     <FusionMiddleware>
 *       <App />
 *     </FusionMiddleware>
 *
 * Usage in any component::
 *
 *     const { mode, language, setLanguage, fallbackToData } = useFusionMode();
 */
export function FusionMiddleware({
  children,
  initialMode,
  initialLanguage,
}: FusionMiddlewareProps) {
  const [mode, setMode] = useState<FusionMode>(initialMode ?? 'loading');
  const [language, setLanguageState] = useState<string>(
    initialLanguage ?? (typeof window !== 'undefined' ? getStoredLanguage() : DEFAULT_LANGUAGE)
  );

  // Initialise from sessionStorage on mount
  useEffect(() => {
    if (!initialMode) {
      const pref = fusionDecoder.getSessionPreference();
      setMode(pref === true ? 'fragment' : 'data');
    }
    if (!initialLanguage) {
      setLanguageState(getStoredLanguage());
    }
  }, [initialMode, initialLanguage]);

  const fallbackToData = useCallback(() => {
    fusionDecoder.clearSession();
    fusionDecoder.initSession(false);
    setMode('data');
  }, []);

  const enableFragments = useCallback(() => {
    fusionDecoder.initSession(true);
    setMode('fragment');
  }, []);

  const setLanguage = useCallback((code: string) => {
    setStoredLanguage(code);
    setLanguageCookie(code);
    setLanguageState(code);
    // Notify the backend via the setlang API
    try {
      fetch('/apis/i18n/setlang/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: code }),
      }).catch(() => { /* best-effort */ });
    } catch { /* ignore */ }
  }, []);

  return (
    <FusionContext.Provider value={{ mode, fallbackToData, enableFragments, language, setLanguage }}>
      {children}
    </FusionContext.Provider>
  );
}

// ─── Hook ───────────────────────────────────────────────────────────

/**
 * Hook to read the current fusion rendering mode, language, and toggle functions.
 *
 * Must be called within a ``<FusionMiddleware>`` provider.
 */
export function useFusionMode(): FusionContextValue {
  return useContext(FusionContext);
}

export default FusionMiddleware;
