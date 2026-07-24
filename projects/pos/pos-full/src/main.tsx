import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import App from "./App";
import "./index.css";
import "./i18n";
import { store } from "./store";
import { ThemeProvider } from "./contexts/ThemeContext";
import { LanguageProvider } from "./contexts/LanguageContext";
import { AuthProvider } from "./contexts/AuthContext";
import { FusionMiddleware } from "./components/FusionMiddleware";
import { fusionStore } from "./lib/fusion-store";
import { SIDECAR_BASE } from "./api/sidecar";

// ── Fusion health check on startup (non-blocking) ────────────────
// Fetches /fusion/health from the sidecar and caches the rendering
// preference.  Falls back to data mode if the sidecar is unavailable.
fusionStore.initFromHealthCheck(SIDECAR_BASE).catch(() => {
  // Sidecar not reachable — default data mode will be used
});

// Set initial dir/lang from saved language
const savedLang = localStorage.getItem('language');
if (savedLang === 'ar') {
  document.documentElement.dir = 'rtl';
  document.documentElement.lang = 'ar';
} else if (savedLang === 'fr') {
  document.documentElement.dir = 'ltr';
  document.documentElement.lang = 'fr';
} else {
  document.documentElement.dir = 'ltr';
  document.documentElement.lang = 'en';
}

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <Provider store={store}>
      <ThemeProvider>
        <LanguageProvider>
          <AuthProvider>
            <FusionMiddleware>
              <App />
            </FusionMiddleware>
          </AuthProvider>
        </LanguageProvider>
      </ThemeProvider>
    </Provider>
  </React.StrictMode>,
);
