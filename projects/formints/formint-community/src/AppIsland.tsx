import AppShell from './components/AppShell';
import { ThemeProvider } from './contexts/ThemeContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { AuthProvider } from './contexts/AuthContext';
import { CurrencyProvider } from './contexts/CurrencyContext';
import { ModalProvider } from './components/ui/ModalProvider';
import './i18n';

/**
 * The Astro island entry point.
 *
 * The SPA-era provider stack (auth, theme, language, currency, modals) was
 * dropped when the app migrated to Astro's `client:only` islands, which broke
 * every page in the browser (`useAuth must be used within an AuthProvider`).
 * This wrapper restores the exact provider order the old `App.tsx` used, so
 * `<AppIsland route={...} client:only="react" />` mounts a healthy tree.
 */
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
