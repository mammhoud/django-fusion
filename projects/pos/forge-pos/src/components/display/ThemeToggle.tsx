import { useState, useRef, useEffect } from 'react';
import { useTheme, THEME_VARIANTS, type ThemeVariant } from '../../contexts/ThemeContext';
import AnimatePresence from '../ui/AnimatePresence';

type ThemeMode = 'light' | 'dark' | 'system';

const MODE_OPTIONS: { value: ThemeMode; label: string; icon: string }[] = [
  { value: 'light',  label: 'Light',  icon: 'tabler--sun' },
  { value: 'dark',   label: 'Dark',   icon: 'tabler--moon' },
  { value: 'system', label: 'System', icon: 'tabler--monitor' },
];

export default function ThemeToggle() {
  const {
    mode: resolvedMode, setMode, setFollowSystem, followSystem,
    variant, setVariant,
  } = useTheme();
  const currentMode: ThemeMode = followSystem ? 'system' : resolvedMode;

  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const activeMode = MODE_OPTIONS.find(o => o.value === currentMode) ?? MODE_OPTIONS[0];
  const activeVariant = THEME_VARIANTS.find(v => v.id === variant) ?? THEME_VARIANTS[0];

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleModeSelect = (mode: ThemeMode) => {
    if (mode === 'system') setFollowSystem(true);
    else { setFollowSystem(false); setMode(mode); }
    setIsOpen(false);
  };

  const handleVariantSelect = (v: ThemeVariant) => {
    setVariant(v);
    setIsOpen(false);
  };

  return (
    <div ref={dropdownRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium
          bg-white/80 dark:bg-white/10 text-slate-700 dark:text-slate-300
          hover:bg-base-200/50
          border border-base-300/30
          shadow-sm transition-all active:scale-[0.95] min-w-[130px]"
        aria-label={`Theme: ${activeVariant.label} · ${activeMode.label}`}
      >
        <span className={`icon-[${activeVariant.icon}] w-4 h-4 shrink-0 opacity-70`} />
        <span className="flex-1 text-left text-xs">{activeVariant.label}</span>
        <svg
          className={`w-3.5 h-3.5 opacity-50 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>

      <AnimatePresence>
        {isOpen && (
          <div
            className="absolute bottom-full mb-2 left-0 right-0 max-h-[340px] overflow-y-auto
              bg-base-100 rounded-xl shadow-xl border border-base-300/30 z-50"
          >
            {/* ── Mode section ── */}
            <div className="px-2 pt-2 pb-1">
              <p className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-base-content/40">
                Mode
              </p>
              {MODE_OPTIONS.map(opt => {
                const isActive = currentMode === opt.value;
                return (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => handleModeSelect(opt.value)}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary/10 text-primary font-semibold'
                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/5'
                    }`}
                  >
                    <span className={`icon-[${opt.icon}] w-4 h-4 shrink-0`} />
                    <span className="flex-1 text-left">{opt.label}</span>
                    {isActive && (
                      <span className="icon-[tabler--check] w-4 h-4 text-primary" />
                    )}
                  </button>
                );
              })}
            </div>

            {/* ── Divider ── */}
            <div className="border-t border-base-300/30 mx-3" />

            {/* ── Variant section ── */}
            <div className="px-2 pt-1 pb-2">
              <p className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-base-content/40">
                Variant
              </p>
              {THEME_VARIANTS.map(v => {
                const isActive = variant === v.id;
                return (
                  <button
                    key={v.id}
                    type="button"
                    onClick={() => handleVariantSelect(v.id)}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary/10 text-primary font-semibold'
                        : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/5'
                    }`}
                  >
                    <span className={`icon-[${v.icon}] w-4 h-4 shrink-0`} />
                    <span className="flex-1 text-left">{v.label}</span>
                    {isActive && (
                      <span className="icon-[tabler--check] w-4 h-4 text-primary" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
