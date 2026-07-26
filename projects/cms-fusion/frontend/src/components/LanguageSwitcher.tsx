'use client';

import { useState } from 'react';
import { HiGlobe } from 'react-icons/hi';

export interface LanguageInfo {
  code: string;
  name: string;
}

interface LanguageSwitcherProps {
  onLanguageChange: (code: string) => void;
  currentLanguage: string;
  languages?: LanguageInfo[];
  className?: string;
}

const FALLBACK_LANGUAGES: LanguageInfo[] = [
  { code: 'en', name: 'English' },
  { code: 'fr', name: 'Français' },
  { code: 'es', name: 'Español' },
  { code: 'de', name: 'Deutsch' },
  { code: 'ar', name: 'العربيّة' },
];

const SHORT_LABELS: Record<string, string> = {
  en: 'EN',
  fr: 'FR',
  es: 'ES',
  de: 'DE',
  ar: 'ع',
};

export function LanguageSwitcher({
  onLanguageChange,
  currentLanguage,
  languages,
  className = '',
}: LanguageSwitcherProps) {
  const [open, setOpen] = useState(false);
  const items = languages ?? FALLBACK_LANGUAGES;

  if (items.length <= 1) return null;

  const handleSelect = (code: string) => {
    onLanguageChange(code);
    setOpen(false);
  };

  return (
    <div className={`relative ${className}`} data-component="language-switcher">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium
                   text-gray-600 hover:text-purple-700 hover:bg-purple-50
                   transition-colors"
        aria-label="Select language"
        aria-expanded={open}
      >
        <HiGlobe className="w-4 h-4" />
        <span>{SHORT_LABELS[currentLanguage] ?? currentLanguage.toUpperCase()}</span>
      </button>

      {open && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
            aria-hidden="true"
          />
          <div className="absolute right-0 mt-2 w-44 bg-white rounded-xl shadow-lg border border-gray-100 z-50 py-1.5">
            {items.map((lang) => (
              <button
                key={lang.code}
                onClick={() => handleSelect(lang.code)}
                className={`w-full text-left px-4 py-2 text-sm transition-colors
                  ${lang.code === currentLanguage
                    ? 'bg-purple-100 text-purple-700 font-medium'
                    : 'text-gray-600 hover:bg-gray-50'
                  }`}
              >
                {lang.name}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default LanguageSwitcher;
