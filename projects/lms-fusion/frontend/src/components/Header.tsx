'use client';

import React from 'react';
import Link from 'next/link';
import { fusionApi } from '@/lib/api-client';
import type { FusionBranding } from '@/lib/fusion-types';
import LanguageSwitcher from './LanguageSwitcher';

export default function Header() {
  const [branding, setBranding] = React.useState<FusionBranding>({
    site_name: 'Fusion LMS',
    company_name: 'Fusion Inc.',
    creator_name: 'Fusion Team',
    primary_color: '#7c3aed',
  });
  const [language, setLanguage] = React.useState('en');

  React.useEffect(() => {
    fusionApi.fetchBranding().then(setBranding).catch(() => {});
  }, []);

  const handleLanguageChange = (code: string) => {
    setLanguage(code);
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
              style={{ backgroundColor: branding.primary_color }}
            >
              F
            </div>
            <span className="font-semibold text-lg text-gray-900">
              {branding.site_name}
            </span>
          </Link>
          <nav className="hidden md:flex items-center gap-6">
            <Link href="/" className="text-gray-600 hover:text-fu-primary transition-colors">
              Home
            </Link>
            <Link href="/about" className="text-gray-600 hover:text-fu-primary transition-colors">
              About
            </Link>
            <Link href="/services" className="text-gray-600 hover:text-fu-primary transition-colors">
              Services
            </Link>
            <Link href="/contact" className="text-gray-600 hover:text-fu-primary transition-colors">
              Contact
            </Link>
            <LanguageSwitcher
              currentLanguage={language}
              onLanguageChange={handleLanguageChange}
            />
          </nav>
        </div>
      </div>
    </header>
  );
}
