/**
 * Landing-Fusion site configuration.
 *
 * Single source of truth for branding, navigation, footer links and
 * contact metadata. Ported from the CMS-Fusion Next.js `site-content.ts`
 * adapter (see ASTRO_MIGRATION_PLAN §5).
 */

export const siteConfig = {
  name: 'Fusion CMS',
  tagline: 'Server-rendered HTML, delivered as a document. No heavy SPA.',
  description:
    'A CMS that renders every page as plain server-rendered HTML — Astro, HTMX and Alpine, with zero heavy JavaScript framework in the critical path.',
  url: 'https://landing.structa.cloud',
  author: 'mammhoud',
  ogImage: '/og-image.svg',
};

export interface NavLink {
  label: string;
  href: string;
  /** Open in a new tab (external links). */
  external?: boolean;
}

export const navLinks: NavLink[] = [
  { label: 'Home', href: '/' },
  { label: 'Features', href: '/features' },
  { label: 'Products', href: '/products' },
  { label: 'Projects', href: '/projects' },
  { label: 'About', href: '/about' },
  { label: 'FAQ', href: '/faq' },
  { label: 'Contact', href: '/contact' },
];

export interface FooterColumn {
  title: string;
  links: NavLink[];
}

export const footerColumns: FooterColumn[] = [
  {
    title: 'Platform',
    links: [
      { label: 'Features', href: '/features' },
      { label: 'Products', href: '/products' },
      { label: 'Projects', href: '/projects' },
      { label: 'About', href: '/about' },
    ],
  },
  {
    title: 'Support',
    links: [
      { label: 'Contact Us', href: '/contact' },
      { label: 'About Us', href: '/about' },
      { label: 'FAQ', href: '/faq' },
      { label: 'Privacy Policy', href: '/privacy' },
    ],
  },
  {
    title: 'Community',
    links: [
      { label: 'Get Started', href: '/#cta' },
      { label: 'GitHub', href: 'https://github.com/mammhoud', external: true },
      { label: 'Portfolio', href: 'https://mammhoud.github.io', external: true },
    ],
  },
];

export interface ContactMethod {
  type: 'email' | 'phone' | 'address' | 'hours';
  label: string;
  value: string;
  href?: string;
}

export const contactMethods: ContactMethod[] = [
  {
    type: 'email',
    label: 'Email',
    value: 'structa.cloud@gmail.com',
    href: 'mailto:structa.cloud@gmail.com',
  },
  {
    type: 'phone',
    label: 'Phone',
    value: '+1 (555) 010-2030',
    href: 'tel:+15550102030',
  },
  {
    type: 'address',
    label: 'Address',
    value: '123 Fusion Lane, Suite 400',
  },
  {
    type: 'hours',
    label: 'Working Hours',
    value: 'Mon – Fri, 9:00 – 18:00',
  },
];

/**
 * Backend base URL for HTMX fragment endpoints (Phase 1 – optional).
 *
 * Defaults to the empty string so requests are made to a same-origin
 * relative path (`/api/htmx/contact/`) and the reverse proxy routes them.
 * Set `PUBLIC_FUSION_API_URL` to point at a Django backend directly.
 */
export const fusionApiUrl: string =
  (import.meta.env.PUBLIC_FUSION_API_URL as string | undefined) ?? '';

/**
 * localStorage key for the persisted theme (ASTRO_MIGRATION_PLAN §5.1).
 *
 * Stored value is `'dark'` or `'light'`. Read in `Layout.astro`'s inline
 * head script (before first paint) and written by `ThemeToggle.astro`.
 */
export const THEME_STORAGE_KEY = 'fusion-theme';
