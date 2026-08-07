import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "../assets/styles/index.css";
import "./i18n";

// FlyonUI interactive components (modals, dropdowns, toggles, etc.)
import "flyonui/flyonui";
import { ThemeProvider } from "./contexts/ThemeContext";
import { LanguageProvider } from "./contexts/LanguageContext";
import { AuthProvider } from "./contexts/AuthContext";
import { CurrencyProvider } from "./contexts/CurrencyContext";
import { ModalProvider } from "./components/ui/ModalProvider";
// API stores: import { useProducts } from "./stores/products";

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
    <ThemeProvider>
      <CurrencyProvider>
        <LanguageProvider>
          <AuthProvider>
            <ModalProvider>
              <App />
            </ModalProvider>
          </AuthProvider>
        </LanguageProvider>
      </CurrencyProvider>
    </ThemeProvider>
  </React.StrictMode>,
);
