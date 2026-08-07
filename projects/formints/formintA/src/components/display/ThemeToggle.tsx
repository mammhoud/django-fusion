import { useState, useRef, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { useTranslation } from 'react-i18next';
import AnimatePresence from '../ui/AnimatePresence';

type ThemeMode = 'light' | 'dark' | 'system';

export default function ThemeToggle() {
  const {
    mode: resolvedMode, setMode, setFollowSystem, followSystem,
  } = useTheme();
  const { t } = useTranslation();

  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const MODE_OPTIONS: { value: ThemeMode; label: string; icon: string }[] = [
    { value: 'light', label: t('settings.appearanceTab.lightLabel') || 'Light', icon: 'ri-sun-line' },
    { value: 'dark',  label: t('settings.appearanceTab.darkLabel')  || 'Dark',  icon: 'ri-moon-line' },
    { value: 'system', label: t('settings.appearanceTab.systemMode') || 'System', icon: 'ri-computer-line' },
  ];

  const activeValue: ThemeMode = followSystem ? 'system' : resolvedMode;
  const activeMode = MODE_OPTIONS.find(o => o.value === activeValue) ?? MODE_OPTIONS[0];

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
    if (mode === 'system') {
      setFollowSystem(true);
    } else {
      setFollowSystem(false);
      setMode(mode);
    }
    setIsOpen(false);
  };

  return (
    <div ref={dropdownRef} className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium
          bg-base-100/70 backdrop-blur-md text-base-content/80
          hover:bg-base-200/50
          border border-base-300/30
          shadow-sm transition-all active:scale-[0.95] min-w-[130px]"
        aria-label={`Theme: ${activeMode.label}`}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span className={`${activeMode.icon} ri-16px shrink-0 opacity-70`} />
        <span className="flex-1 text-left text-xs">{activeMode.label}</span>
        <span
          className={`ri-arrow-down-s-line ri-14px opacity-50 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          aria-hidden="true"
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <div
            className="absolute bottom-full mb-2 left-0 right-0 max-h-[340px] overflow-y-auto
              bg-base-100 rounded-xl shadow-xl border border-base-300/30 z-50"
            role="listbox"
            aria-label="Color mode"
          >
            {/* ── Mode section (Light / Dark / System) ── */}
            <div className="px-2 pt-2 pb-2">
              <p className="px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-base-content/40">
                {t('settings.appearanceTab.modeTitle') || 'Mode'}
              </p>
              {MODE_OPTIONS.map(opt => {
                const isActive = activeValue === opt.value;
                return (
                  <button
                    key={opt.value}
                    type="button"
                    role="option"
                    aria-selected={isActive}
                    onClick={() => handleModeSelect(opt.value)}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 text-sm rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary/10 text-primary font-semibold'
                        : 'text-base-content/70 hover:bg-base-200/50'
                    }`}
                  >
                    <span className={`${opt.icon} ri-16px shrink-0`} />
                    <span className="flex-1 text-left">{opt.label}</span>
                    {isActive && (
                      <span className="ri-check-line ri-16px text-primary" />
                    )}
                  </button>
                );
              })}
            </div>

            {followSystem && (
              <p className="px-5 pb-2 text-[10px] text-base-content/40">
                {t('settings.appearanceTab.systemControlled') || 'Following system preference'}
              </p>
            )}
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
