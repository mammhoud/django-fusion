'use client';

import { Provider } from 'react-redux';
import { store } from '@/store';
import { FusionMiddleware, useFusionMode } from '@/components/FusionMiddleware';
import { LanguageSwitcher } from '@/components/LanguageSwitcher';

function LanguageWrapper({ children }: { children: React.ReactNode }) {
  const { language, setLanguage } = useFusionMode();

  return (
    <>
      {children}
      {/* Fixed language switcher — positioned top-right */}
      <div className="fixed top-4 right-4 z-50">
        <LanguageSwitcher
          currentLanguage={language}
          onLanguageChange={setLanguage}
        />
      </div>
    </>
  );
}

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Provider store={store}>
      <FusionMiddleware>
        <LanguageWrapper>
          {children}
        </LanguageWrapper>
      </FusionMiddleware>
    </Provider>
  );
}
