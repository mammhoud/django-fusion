import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

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
  mode: Mode;
  variant: ThemeVariant;
  toggleMode: () => void;
  setMode: (mode: Mode) => void;
  setVariant: (variant: ThemeVariant) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [mode, setModeState] = useState<Mode>(() => {
    // Migrate from legacy 'theme' key (light/dark) if present
    const legacy = localStorage.getItem('theme') as Mode | null;
    if (legacy === 'light' || legacy === 'dark') {
      localStorage.removeItem('theme');
      return legacy;
    }
    const saved = localStorage.getItem('theme-mode') as Mode | null;
    if (saved === 'light' || saved === 'dark') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  const [variant, setVariantState] = useState<ThemeVariant>(() => {
    const saved = localStorage.getItem('theme-variant') as ThemeVariant | null;
    if (saved && THEME_VARIANTS.some(v => v.id === saved)) return saved;
    return 'default';
  });

  // Apply mode + variant to <html>
  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove('light', 'dark');
    root.classList.add(mode);
    root.setAttribute('data-theme', variant);
    localStorage.setItem('theme-mode', mode);
    localStorage.setItem('theme-variant', variant);
  }, [mode, variant]);

  const toggleMode = () => {
    setModeState(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  const setMode = (newMode: Mode) => setModeState(newMode);
  const setVariant = (newVariant: ThemeVariant) => setVariantState(newVariant);

  return (
    <ThemeContext.Provider value={{ mode, variant, toggleMode, setMode, setVariant }}>
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
