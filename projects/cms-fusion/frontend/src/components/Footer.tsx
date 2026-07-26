'use client';

import React from 'react';
import Link from 'next/link';
import { fusionApi } from '@/lib/api-client';
import type { FusionBranding } from '@/lib/fusion-types';

const FOOTER_LINKS = {
  Pages: [
    { href: '/', label: 'Home' },
    { href: '/about', label: 'About' },
    { href: '/services', label: 'Services' },
    { href: '/team', label: 'Team' },
    { href: '/contact', label: 'Contact' },
  ],
  Content: [
    { href: '/blog', label: 'Blog' },
    { href: '/courses', label: 'Courses' },
    { href: '/products', label: 'Products' },
  ],
  Legal: [
    { href: '/privacy', label: 'Privacy Policy' },
    { href: '/faq', label: 'FAQ' },
  ],
};

export default function Footer() {
  const [branding, setBranding] = React.useState<FusionBranding>({
    site_name: 'Fusion CMS', company_name: 'Fusion Inc.',
    creator_name: 'Fusion Team', primary_color: '#7c3aed',
  });

  React.useEffect(() => {
    fusionApi.fetchBranding().then(setBranding).catch(() => {});
  }, []);

  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2 mb-3">
              <div
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
                style={{ backgroundColor: branding.primary_color }}
              >
                F
              </div>
              <h3 className="text-white font-semibold text-lg">{branding.site_name}</h3>
            </div>
            <p className="text-sm text-gray-400">
              {branding.company_name} — CMS powered by django-fusion &amp; django-bolt
            </p>
          </div>

          {/* Links */}
          {Object.entries(FOOTER_LINKS).map(([title, links]) => (
            <div key={title}>
              <h4 className="text-white font-medium mb-3">{title}</h4>
              <ul className="space-y-2 text-sm">
                {links.map(link => (
                  <li key={link.href}>
                    <Link href={link.href} className="text-gray-400 hover:text-white transition-colors">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-10 pt-8 border-t border-gray-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500">
          <p>&copy; {new Date().getFullYear()} {branding.company_name}. All rights reserved.</p>
          <p>Created by {branding.creator_name}</p>
        </div>
      </div>
    </footer>
  );
}
