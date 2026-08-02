'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { HiMenu, HiX } from 'react-icons/hi';
import { fusionApi } from '@/lib/api-client';
import type { FusionBranding } from '@/lib/fusion-types';
import LanguageSwitcher from './LanguageSwitcher';

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/about', label: 'About' },
  { href: '/services', label: 'Services' },
  { href: '/contact', label: 'Contact' },
];

export default function Header() {
  const [branding, setBranding] = React.useState<FusionBranding | null>(null);
  const [language, setLanguage] = React.useState('en');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  React.useEffect(() => {
    fusionApi.fetchBranding().then((data) => {
      if (data && typeof data.primary_color === 'string') {
        setBranding(data);
      }
    }).catch(() => {});
  }, []);

  // Reflect the browser locale in the <html lang> attribute on first load.
  // The root layout renders with a server-side default of "en"; this effect
  // reconciles it with the client's actual locale so screen readers and the
  // language routing tests see the correct language.
  React.useEffect(() => {
    const browserLang = (navigator.language || 'en').split('-')[0];
    document.documentElement.lang = browserLang;
    setLanguage(browserLang);
  }, []);

  const handleLanguageChange = (code: string) => {
    setLanguage(code);
    // Keep the <html lang> attribute in sync with the active language.
    document.documentElement.lang = code;
    try {
      fetch('/apis/i18n/setlang/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `language=${code}`,
      }).then(() => { window.location.reload(); }).catch(() => {});
    } catch { /* ignore */ }
  };

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-2">
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
              style={{ backgroundColor: branding?.primary_color ?? '#7c3aed' }}
            >
              F
            </div>
            <span className="font-semibold text-lg text-gray-900">
              {branding?.site_name ?? 'Fusion LMS'}
            </span>
          </Link>
          <nav className="hidden md:flex items-center gap-6">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-gray-600 hover:text-fu-primary transition-colors"
              >
                {link.label}
              </Link>
            ))}
            <LanguageSwitcher
              currentLanguage={language}
              onLanguageChange={handleLanguageChange}
            />
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden text-gray-600 hover:text-fu-primary"
            aria-label="Toggle menu"
          >
            {mobileMenuOpen ? <HiX className="w-6 h-6" /> : <HiMenu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white/95 backdrop-blur">
          <div className="px-4 py-3 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="block px-3 py-2 text-gray-600 hover:text-fu-primary hover:bg-fu-primary/5 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                {link.label}
              </Link>
            ))}
            <hr className="my-2 border-gray-200" />
            <div className="px-3 py-2">
              <LanguageSwitcher
                currentLanguage={language}
                onLanguageChange={handleLanguageChange}
              />
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
