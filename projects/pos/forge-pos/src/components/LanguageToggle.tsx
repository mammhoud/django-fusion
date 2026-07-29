import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';
import { useTranslation } from 'react-i18next';

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
        <span className="icon-[tabler--language] w-4 h-4 shrink-0 opacity-70" />
        <span className="flex-1 text-left">{current.flag} {current.label}</span>
        <motion.svg
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="w-3.5 h-3.5 opacity-50"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <polyline points="6 9 12 15 18 9" />
        </motion.svg>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -8, scale: 0.95 }}
            transition={{ duration: 0.15 }}
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
                    <span className="icon-[tabler--check] w-4 h-4 text-indigo-500" />
                  )}
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
