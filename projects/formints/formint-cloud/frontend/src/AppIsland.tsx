import AppShell from './components/AppShell';
import { ThemeProvider } from './contexts/ThemeContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { AuthProvider } from './contexts/AuthContext';
import { CurrencyProvider } from './contexts/CurrencyContext';
import { ModalProvider } from './components/ui/ModalProvider';
import './i18n';

/** Mount the Cloud Community UI with the providers required by AppShell. */
export default function AppIsland({ route }: { route: string }) {
  return (
    <ThemeProvider>
      <LanguageProvider>
        <AuthProvider>
          <CurrencyProvider>
            <ModalProvider>
              <AppShell route={route} />
            </ModalProvider>
          </CurrencyProvider>
        </AuthProvider>
      </LanguageProvider>
    </ThemeProvider>
  );
}
