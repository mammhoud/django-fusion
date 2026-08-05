import { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { useTranslation } from 'react-i18next';
import AnimatePresence from '../../components/ui/AnimatePresence';

const langOptions = [
  { value: 'en' as const, label: 'English', flag: '🇬🇧' },
  { value: 'fr' as const, label: 'Français', flag: '🇫🇷' },
  { value: 'de' as const, label: 'Deutsch', flag: '🇩🇪' },
  { value: 'es' as const, label: 'Español', flag: '🇪🇸' },
  { value: 'ar' as const, label: 'العربية', flag: '🇸🇦' },
];

export default function LanguageToggle({ dropdownUp = true }: { dropdownUp?: boolean }) {
  const { language, setLanguage } = useLanguage();
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const current = langOptions.find(o => o.value === language) || langOptions[0];

  return (
    <div ref={dropdownRef} className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium
          bg-white/80 dark:bg-white/10 text-slate-700 dark:text-slate-300
          hover:bg-base-200/50
          border border-base-300/30
          shadow-sm transition-all active:scale-[0.95] min-w-[120px]"
        aria-label={t('language.selectLanguage')}
      >
        <span className="ri-translate ri-16px shrink-0 opacity-70" />
        <span className="flex-1 text-left">{current.flag} {current.label}</span>
        <span
          className={`ri-arrow-down-s-line ri-14px opacity-50 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          aria-hidden="true"
        />
      </button>

      <AnimatePresence>
        {isOpen && (
          <div
            className={`absolute ${dropdownUp ? 'bottom-full mb-2' : 'top-full mt-2'} left-0 right-0 max-h-[260px] overflow-y-auto
              bg-base-100 rounded-xl shadow-xl
              border border-base-300/30
              z-50`}
          >
            {langOptions.map((opt) => {
              const isActive = language === opt.value;
              return (
                <button
                  key={opt.value}
                  onClick={() => {
                    setLanguage(opt.value);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center gap-2.5 px-3 py-2.5 text-sm transition-colors ${
                    isActive
                      ? 'bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 font-semibold'
                      : 'text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/5'
                  }`}
                >
                  <span className="text-base">{opt.flag}</span>
                  <span className="flex-1 text-left">{opt.label}</span>
                  {isActive && (
                    <span className="ri-check-line ri-16px text-indigo-500" />
                  )}
                </button>
              );
            })}
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
