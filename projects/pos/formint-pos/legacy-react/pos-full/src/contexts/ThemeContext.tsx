import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react';

type Mode = 'light' | 'dark';
export type ThemeVariant = 'default' | 'corporate' | 'luxury' | 'pastel' | 'cyberpunk';

export const THEME_VARIANTS: { id: ThemeVariant; label: string; icon: string; description: string }[] = [
  { id: 'default', label: 'Default', icon: '🎨', description: 'Clean slate & indigo' },
  { id: 'corporate', label: 'Corporate', icon: '💼', description: 'Professional blue tones' },
  { id: 'luxury', label: 'Luxury', icon: '👑', description: 'Rich gold & warm hues' },
  { id: 'pastel', label: 'Pastel', icon: '🌸', description: 'Soft candy colors' },
  { id: 'cyberpunk', label: 'Cyberpunk', icon: '⚡', description: 'Neon futuristic glow' },
];

interface ThemeContextType {
  /** The resolved visual mode (always 'light' or 'dark') */
  mode: Mode;
  /** The active theme variant */
  variant: ThemeVariant;
  /** Whether the mode follows the OS preference */
  followSystem: boolean;
  /** Toggle between light and dark (disables followSystem) */
  toggleMode: () => void;
  /** Set a specific mode and disable followSystem */
  setMode: (mode: Mode) => void;
  /** Set theme variant */
  setVariant: (variant: ThemeVariant) => void;
  /** Enable or disable OS preference following */
  setFollowSystem: (follow: boolean) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

function getSystemPreference(): Mode {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [followSystem, setFollowSystemState] = useState<boolean>(() => {
    const saved = localStorage.getItem('theme-follow-system');
    return saved === 'true';
  });

  const [mode, setModeState] = useState<Mode>(() => {
    // Migrate from legacy 'theme' key (light/dark) if present
    const legacy = localStorage.getItem('theme') as Mode | null;
    if (legacy === 'light' || legacy === 'dark') {
      localStorage.removeItem('theme');
      return legacy;
    }
    const saved = localStorage.getItem('theme-mode') as Mode | null;
    if (saved === 'light' || saved === 'dark') return saved;
    return getSystemPreference();
  });

  const [variant, setVariantState] = useState<ThemeVariant>(() => {
    const saved = localStorage.getItem('theme-variant') as ThemeVariant | null;
    if (saved && THEME_VARIANTS.some(v => v.id === saved)) return saved;
    return 'default';
  });

  // Listen for OS preference changes when followSystem is active
  useEffect(() => {
    if (!followSystem) return;
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e: MediaQueryListEvent) => {
      setModeState(e.matches ? 'dark' : 'light');
    };
    mq.addEventListener('change', handler);
    // Sync immediately in case preference changed since initial load
    setModeState(mq.matches ? 'dark' : 'light');
    return () => mq.removeEventListener('change', handler);
  }, [followSystem]);

  // Apply mode + variant to <html>
  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(mode);
    root.setAttribute('data-theme', variant);
    localStorage.setItem('theme-mode', mode);
    localStorage.setItem('theme-variant', variant);
    localStorage.setItem('theme-follow-system', String(followSystem));
  }, [mode, variant, followSystem]);

  const toggleMode = useCallback(() => {
    setFollowSystemState(false);
    setModeState(prev => (prev === 'light' ? 'dark' : 'light'));
  }, []);

  const setMode = useCallback((newMode: Mode) => {
    setFollowSystemState(false);
    setModeState(newMode);
  }, []);

  const setVariant = useCallback((newVariant: ThemeVariant) => {
    setVariantState(newVariant);
  }, []);

  const setFollowSystem = useCallback((follow: boolean) => {
    setFollowSystemState(follow);
    if (follow) {
      setModeState(getSystemPreference());
    }
  }, []);

  return (
    <ThemeContext.Provider value={{ mode, variant, followSystem, toggleMode, setMode, setVariant, setFollowSystem }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
