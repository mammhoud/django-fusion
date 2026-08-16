import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import i18n from '../i18n';

type Language = 'en' | 'ar' | 'fr' | 'de' | 'es';

interface LanguageContextType {
  language: Language;
  toggleLanguage: () => void;
  setLanguage: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => {
    // Try saved preference first
    const saved = localStorage.getItem('language');
    if (saved === 'en' || saved === 'ar' || saved === 'fr' || saved === 'de' || saved === 'es') {
      return saved;
    }
    // Default to Arabic for this POS system
    return 'ar';
  });

  const syncLanguage = (lang: Language) => {
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
    localStorage.setItem('language', lang);
    setLanguageState(lang);
  };

  useEffect(() => {
    // Sync i18n with context on mount
    if (i18n.language !== language) {
      i18n.changeLanguage(language);
    }
    syncLanguage(language);

    const handleLanguageChanged = (lng: string) => {
      if (lng === 'en' || lng === 'ar' || lng === 'fr' || lng === 'de' || lng === 'es') {
        setLanguageState(lng);
        syncLanguage(lng as Language);
      }
    };

    i18n.on('languageChanged', handleLanguageChanged);
    return () => {
      i18n.off('languageChanged', handleLanguageChanged);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggleLanguage = () => {
    const langCycle: Language[] = ['en', 'ar', 'fr', 'de', 'es'];
    const currentIdx = langCycle.indexOf(language);
    const newLang: Language = langCycle[(currentIdx + 1) % langCycle.length];
    syncLanguage(newLang);
    i18n.changeLanguage(newLang);
  };

  const setLanguage = (newLang: Language) => {
    syncLanguage(newLang);
    i18n.changeLanguage(newLang);
  };

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
