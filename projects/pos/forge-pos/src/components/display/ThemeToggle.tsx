import { useState, useRef, useEffect } from 'react';
import { useTheme } from '../../contexts/ThemeContext';
import { iconClass } from '../../lib/icons';

type ThemeMode = 'light' | 'dark' | 'system';

interface ModeOption {
  value: ThemeMode;
  label: string;
  icon: string;
}

const MODE_OPTIONS: ModeOption[] = [
  { value: 'light', label: 'Light', icon: 'lucide:sun' },
  { value: 'dark', label: 'Dark', icon: 'lucide:moon' },
  { value: 'system', label: 'System', icon: 'lucide:monitor' },
];

export default function ThemeToggle() {
  const { mode: resolvedMode, setMode, setFollowSystem, followSystem } = useTheme();
  const currentMode: ThemeMode = followSystem ? 'system' : resolvedMode;

  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const activeOption = MODE_OPTIONS.find(o => o.value === currentMode) ?? MODE_OPTIONS[0];

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (mode: ThemeMode) => {
    setIsOpen(false);
    if (mode === 'system') {
      setFollowSystem(true);
    } else {
      setFollowSystem(false);
      setMode(mode);
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm
          bg-base-200/50 dark:bg-white/5 border border-base-300/50
          hover:bg-base-200 dark:hover:bg-white/10
          text-base-content/70 hover:text-base-content
          transition-all active:scale-[0.97] focus-visible:ring-2 focus-visible:ring-primary/50"
        aria-label={`Theme: ${activeOption.label}`}
      >
        <span className={iconClass(activeOption.icon, 'w-4 h-4')} />
        <span className="text-xs font-medium hidden sm:inline">{activeOption.label}</span>
        <span className={iconClass('lucide:chevron-down', `w-3.5 h-3.5 transition-transform duration-200 ml-0.5 ${isOpen ? 'rotate-180' : ''}`)} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-1.5 w-40 z-50 bg-base-100 border border-base-300 rounded-xl shadow-xl overflow-hidden">
          {MODE_OPTIONS.map(option => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleSelect(option.value)}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm transition-colors
                ${option.value === currentMode
                  ? 'bg-primary/10 text-primary font-medium'
                  : 'text-base-content/70 hover:bg-base-200/50 hover:text-base-content'
                }`}
            >
              <span className={iconClass(option.icon, 'w-4 h-4')} />
              <span>{option.label}</span>
              {option.value === currentMode && (
                <span className={iconClass('lucide:check', 'w-3.5 h-3.5 ml-auto')} />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
