'use client';

import React from 'react';
import Link from 'next/link';
import { fusionApi } from '@/lib/api-client';
import type { FusionBranding } from '@/lib/fusion-types';

export default function Footer() {
  const [branding, setBranding] = React.useState<FusionBranding>({
    site_name: 'Fusion LMS',
    company_name: 'mammhoud',
    creator_name: 'Mahmoud Ezzat',
    primary_color: '#00a1b3',
  });

  React.useEffect(() => {
    fusionApi.fetchBranding().then(setBranding).catch(() => {});
  }, []);

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-white font-semibold text-lg mb-3">
              {branding.site_name}
            </h3>
            <p className="text-sm text-gray-400">
              {branding.company_name} — Powered by django-fusion &amp; django-bolt
            </p>
          </div>
          <div>
            <h4 className="text-white font-medium mb-3">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><Link href="/" className="hover:text-white transition-colors">Home</Link></li>
              <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
              <li><Link href="/services" className="hover:text-white transition-colors">Services</Link></li>
              <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-medium mb-3">Contact</h4>
            <p className="text-sm">
              Created by {branding.creator_name}
            </p>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm text-gray-500">
          &copy; {new Date().getFullYear()} mammhoud. All rights reserved.{' '}
          <a href="https://github.com/mammhoud" className="hover:text-white transition-colors" target="_blank" rel="noopener">GitHub</a>
          {' · '}
          <a href="https://mammhoud.github.io" className="hover:text-white transition-colors" target="_blank" rel="noopener">Portfolio</a>
        </div>
      </div>
    </footer>
  );
}
