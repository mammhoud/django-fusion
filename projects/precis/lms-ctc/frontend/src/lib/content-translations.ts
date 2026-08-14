import type { PageData } from './api';

/**
 * Static content is a resilience layer, not a second CMS. Wagtail remains the
 * source of truth; these concise entries keep the Astro shell useful during an
 * API outage and — more importantly — give every frontend route a complete
 * document even when the seeded Wagtail tree has no page for that slug (e.g.
 * pricing, features, projects, faq, blog, products). They document the public
 * content contract so editors know what the Astro app expects per page.
 */
const CONTENT: Record<string, Partial<PageData>> = {
  home: {
    slug: 'home', title: 'Home', type: 'HomePage', show_in_nav: true,
    seo_title: 'Precis — medical research learning',
    search_description: 'Serious learning paths for medical research: clear content, visible progress, and a next useful action.',
    hero: {
      badge: 'Precis · medical research learning',
      title: 'Turn research intent into',
      accent: 'visible progress',
      subtitle: 'Follow serious learning paths with clear content, visible progress, and a next useful action — without a noisy platform getting in the way.',
      primary_cta: { label: 'Start your learning path', href: '/courses/' },
      secondary_cta: { label: 'Browse courses', href: '/courses/' },
    },
    stats: [
      { label: 'Courses', value: 6, suffix: '' },
      { label: 'Languages', value: 7, suffix: '' },
      { label: 'Open source', value: 100, suffix: '%' },
    ],
    features: [
      { icon: 'M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z', title: 'Astro', description: 'Every page ships as finished static HTML from one document-first build.' },
      { icon: 'M13 10V3L4 14h7v7l9-11h-7z', title: 'HTMX', description: 'Server-rendered fragments swap into live regions without a client framework.' },
      { icon: 'M3 3v18h18M7 15l4-4 3 3 5-6', title: 'Alpine.js', description: 'Small, local micro-interactions that degrade gracefully without JavaScript.' },
      { icon: 'M12 3v18M3 12h18M12 7l1.5 3 3 1.5-3 1.5L12 17l-1.5-3-3-1.5 3-1.5L12 7z', title: 'Wagtail', description: 'Editors own real content models — courses, events, and pages stay CMS-managed.' },
    ],
    products: [
      { title: 'Forge POS', slug: 'forge-pos', tagline: 'Desktop point-of-sale in three editions — Minimal, Solo, and Full.', href: '/products/forge-pos/' },
      { title: 'Precis LMS', slug: 'lms', tagline: 'Courses, enrollments, and a learning experience your team can own.', href: '/products/lms/' },
      { title: 'Loop', slug: 'cms', tagline: 'Build content-driven websites from Wagtail blocks.', href: '/products/cms/' },
    ],
    cta: {
      title: 'Built open-source, shipped as HTML',
      subtitle: 'The core libraries are public on GitHub. Explore the code, open issues, or contribute.',
      primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
    },
  },
  about: {
    slug: 'about', title: 'About', type: 'AboutPage', show_in_nav: true,
    seo_title: 'About · Precis',
    search_description: 'The engineer behind Precis — full-stack development, open source, and medical research learning.',
    hero: {
      badge: 'about · the engineer behind the code',
      title: 'Mahmoud Ezzat',
      accent: 'Moustafa',
      subtitle: 'Full-stack developer and open-source contributor building server-rendered learning platforms that ship as documents.',
      primary_cta: { label: 'View GitHub', href: 'https://github.com/mammhoud' },
      secondary_cta: { label: 'Read the blog', href: '/blog/' },
    },
    cta: {
      title: "Let's build together",
      subtitle: 'Open to collaboration, consulting, and new projects. Reach out through the contact form.',
      primary_cta: { label: 'Get in touch', href: '/contact/' },
    },
  },
  services: {
    slug: 'services', title: 'Services', type: 'ServicesPage', show_in_nav: true,
    seo_title: 'Services · Precis',
    search_description: 'Server-rendered sites, HTMX integrations, and Alpine-powered UX, built as you go.',
    hero: {
      badge: 'services · built as you go',
      title: 'Services',
      accent: 'built as you go',
      subtitle: 'Server-rendered sites, HTMX integrations, and Alpine-powered UX. From brief to shipped in four steps — each one delivers working HTML.',
      primary_cta: { label: 'See our products', href: '/products/' },
      secondary_cta: { label: 'Contact us', href: '/contact/' },
    },
    services: [
      {
        icon: 'M4 5h16v14H4z M4 12h16',
        title: 'Market-ready websites',
        description: 'Clear journeys for campaigns, services, and products — with editorial sections your team can own.',
        deliverables: ['Bilingual page structure', 'Editorial sections your team can own', 'Fast first visits on mobile networks', 'Hosting, domains + HTTPS setup'],
        cta_label: 'See the stack',
        cta_href: '/features/',
      },
      {
        icon: 'M13 10V3L4 14h7v7l9-11h-7z',
        title: 'Digital product delivery',
        description: 'Learning services, portals, and internal workflows shaped around how your team actually operates.',
        deliverables: ['Journey mapping and product direction', 'Web or desktop delivery', 'Arabic and English-ready interfaces', 'Cloud deployment and handover'],
        cta_label: 'See our products',
        cta_href: '/products/',
      },
      {
        icon: 'M3 3v18h18M7 15l4-4 3 3 5-6',
        title: 'Improve what already works',
        description: 'Make an existing service easier to use and faster to operate, without forcing a risky rewrite.',
        deliverables: ['Conversion and content review', 'Performance budget and Core Web Vitals', 'Safe content migration', 'Team training and ongoing support'],
        cta_label: 'Contact us',
        cta_href: '/contact/',
      },
    ],
    process: [
      { title: 'Discover', description: 'Turn the brief into a clear content model and a first-release scope.', icon: 'M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z' },
      { title: 'Build', description: 'Ship the smallest complete path as server-rendered HTML, then add enhancement where it serves the document.', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
      { title: 'Launch', description: 'Release with content parity, monitoring, and a handover your team can own.', icon: 'M3 3v18h18M7 15l4-4 3 3 5-6' },
      { title: 'Enhance', description: 'Improve the live system with measured changes to content, performance, and interactions.', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
    ],
    cta: {
      title: 'Everything is open source',
      subtitle: 'All structa.cloud libraries are public on GitHub. Explore the code, open issues, or contribute.',
      primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
    },
  },
  pricing: {
    slug: 'pricing', title: 'Pricing', type: 'PricingPage', show_in_nav: true,
    seo_title: 'Pricing · Precis',
    search_description: 'Simple, transparent pricing — start free and scale as you grow. No hidden fees, cancel anytime.',
    hero: {
      badge: 'pricing · printed clearly',
      title: 'Pricing',
      accent: 'printed clearly',
      subtitle: 'Simple, transparent pricing — start free and scale as you grow. No hidden fees, cancel anytime.',
      primary_cta: { label: 'Start free', href: '/courses/' },
      secondary_cta: { label: 'Contact sales', href: '/contact/' },
    },
    pricing: [
      {
        type: 'pricing',
        tiers: [
          {
            name: 'Open source', price: '$0', period: '/free', description: 'The core learning platform, public on GitHub for self-hosting teams.',
            features: ['Course catalog + enrollments', 'Progress tracking', 'Community support', 'Self-hosted documentation'],
            featured: false, cta_label: 'View on GitHub', cta_href: 'https://github.com/mammhoud',
          },
          {
            name: 'Solo', price: '$29', period: '/per month', description: 'A polished learning experience for active creators and small teams.',
            features: ['Everything in Open source', 'Priority support', 'Advanced analytics', 'Certificates', 'Offline downloads'],
            featured: true, cta_label: 'Get started', cta_href: '/contact/',
          },
          {
            name: 'Business', price: '$99', period: '/per month', description: 'Cohorts, staff, and connected systems for organizations.',
            features: ['Everything in Solo', 'Custom branding', 'SSO & role management', 'API access', 'Dedicated success manager'],
            featured: false, cta_label: 'Contact sales', cta_href: '/contact/',
          },
        ],
      },
    ],
    faq: [
      { question: 'Is the platform really open source?', answer: 'Yes — the core libraries and community editions are public on GitHub. Commercial editions add managed hosting, support, and advanced features.' },
      { question: 'Can I self-host?', answer: 'Absolutely. The open-source edition ships with the same Django + Wagtail + Astro stack used on this site, so you keep full ownership of the content and deployment.' },
      { question: 'What languages does the platform support?', answer: 'English, Swedish, French, German, Spanish, Arabic, and Portuguese (Brazil) — with full RTL support for Arabic.' },
    ],
    cta: {
      title: 'Everything is open source',
      subtitle: 'All structa.cloud libraries are public on GitHub. Explore the code, open issues, or contribute.',
      primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
    },
  },
  features: {
    slug: 'features', title: 'Features', type: 'FeaturesPage', show_in_nav: true,
    seo_title: 'Features · Precis',
    search_description: 'The full feature document — capabilities, server-rendered HTML, HTMX fragments, and the AHA stack.',
    hero: {
      badge: 'features · the full capability list',
      title: 'Built to ship as',
      accent: 'documents',
      subtitle: "No SPA, no JSON API, no hydration waterfall. Every page is finished HTML in one response. Here's what makes it work.",
      primary_cta: { label: 'See the products', href: '/products/' },
      secondary_cta: { label: 'Explore projects', href: '/projects/' },
    },
    features: [
      { icon: 'M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z', title: 'Astro static output', description: 'The document shell is built once at deploy time — zero client framework on the critical path.' },
      { icon: 'M13 10V3L4 14h7v7l9-11h-7z', title: 'HTMX fragment swaps', description: 'Dynamic regions stream finished HTML from Django instead of JSON the browser has to assemble.' },
      { icon: 'M3 3v18h18M7 15l4-4 3 3 5-6', title: 'Alpine micro-interactions', description: 'Small local state for menus, tabs, and toggles — no framework, no hydration waterfall.' },
      { icon: 'M12 3v18M3 12h18', title: 'Wagtail content models', description: 'Courses, events, pages, and blocks stay CMS-managed with a stable public API contract.' },
      { icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', title: 'Seven-language locale tree', description: 'English, Swedish, French, German, Spanish, Arabic, and Portuguese — with RTL and per-locale page trees.' },
      { icon: 'M14 4h6v6m-9 3l9-9M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4', title: 'REST + landing APIs', description: 'A single /api/ contract for courses, events, blog, and products plus the /apis/ Astro shell contract.' },
    ],
    cta: {
      title: 'Ship the document, not the app',
      subtitle: 'One HTTP response, finished HTML.',
      primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
    },
  },
  products: {
    slug: 'products', title: 'Products', type: 'ProductsPage', show_in_nav: true,
    seo_title: 'Products · Precis',
    search_description: 'Structa Cloud products — django-fusion, ceptor-ai, django-bolt, vResume, Forge POS, and Cypercloud.',
    hero: {
      badge: 'products · the full product line',
      title: 'Everything we build, shipped as',
      accent: 'open source',
      subtitle: 'Six products from one monorepo — three open-source libraries, two cloud platforms, and a desktop POS.',
      primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
      secondary_cta: { label: 'See projects', href: '/projects/' },
    },
    stats: [
      { label: 'Products', value: 6, suffix: '' },
      { label: 'Open source', value: 100, suffix: '%' },
      { label: 'Languages', value: 7, suffix: '' },
    ],
    products: [
      { title: 'Forge POS', slug: 'forge-pos', tagline: 'Desktop point-of-sale in three editions — Minimal, Solo, and Full.', href: '/products/forge-pos/' },
      { title: 'Precis LMS', slug: 'lms', tagline: 'Courses, enrollments, and a learning experience your team can own.', href: '/products/lms/' },
      { title: 'Loop', slug: 'cms', tagline: 'Build content-driven websites from Wagtail blocks.', href: '/products/cms/' },
      { title: 'Syntara', slug: 'cypercloud', tagline: 'AI chat customizer with an embeddable, branded experience.', href: '/products/cypercloud/' },
    ],
    faq: [
      { question: 'Which products are open source?', answer: 'The core libraries — django-fusion, ceptor-ai, django-bolt — are fully public, and every product ships a community edition.' },
      { question: 'How do the editions differ?', answer: 'Community editions are free and self-hosted; Standard, Pro, and Cloud editions add production workflows, support, and managed hosting.' },
    ],
    cta: {
      title: 'Everything is open source',
      subtitle: 'All structa.cloud libraries are public on GitHub. Explore the code, open issues, or contribute.',
      primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
    },
  },
  projects: {
    slug: 'projects', title: 'Projects', type: 'ProjectsPage', show_in_nav: true,
    seo_title: 'Projects · Precis',
    search_description: 'The full project document — the monorepo at a glance.',
    hero: {
      badge: 'projects · the monorepo inventory',
      title: 'Everything we build, shipped as',
      accent: 'one monorepo',
      subtitle: 'Every project in the structa.cloud repo, its edition, and what it shares.',
      primary_cta: { label: 'See the features', href: '/features/' },
      secondary_cta: { label: 'Read the FAQ', href: '/faq/' },
    },
    projects: [
      { name: 'django-fusion', edition: 'library', category: 'framework', path: 'libs/django-fusion', description: 'Shared Django/Wagtail components, routing, fragments, forms, and tables.', features: [{ label: 'Component registry', shared: true }, { label: 'HTMX fragment rendering', shared: true }, { label: 'Wagtail page integration', shared: true }] },
      { name: 'ceptor-ai', edition: 'library', category: 'AI', path: 'libs/ceptor-ai', description: 'AI chat client with a Model Context Protocol (MCP) server.', features: [{ label: 'MCP server', shared: true }, { label: 'Agent generation', shared: true }] },
      { name: 'django-bolt', edition: 'library', category: 'API', path: 'libs/django-bolt', description: 'High-performance Rust-backed API framework for Django.', features: [{ label: 'Rust-powered API', shared: true }, { label: 'Django ORM compatibility', shared: true }] },
      { name: 'Forge POS', edition: 'product', category: 'desktop', path: 'projects/formints', description: 'Desktop POS in three editions — Minimal, Solo, and Full.', features: [{ label: 'Tauri 2 + Rust core', shared: false }, { label: 'KPI dashboards', shared: false }] },
      { name: 'Precis', edition: 'product', category: 'learning', path: 'projects/precis/main',      description: 'Medical research learning platform with a seven-language page tree.', features: [{ label: 'Course catalog + enrollments', shared: false }, { label: 'Seven-language locales', shared: true }] },
      { name: 'Loop', edition: 'product', category: 'content', path: 'projects/precis/landi', description: 'Content-driven websites built from Wagtail blocks.', features: [{ label: 'Wagtail StreamField blocks', shared: true }, { label: 'HTMX forms', shared: true }] },
    ],
    cta: {
      title: 'Ship the document, not the app',
      subtitle: 'One HTTP response, finished HTML.',
      primary_cta: { label: 'Get started', href: '/products/' },
    },
  },
  blog: {
    slug: 'blog', title: 'Blog', type: 'BlogPage', show_in_nav: true,
    seo_title: 'Blog · Precis',
    search_description: 'Notes on the AHA stack — Astro, HTMX, Alpine — and shipping server-rendered sites that stay fast.',
    hero: {
      badge: 'insights · server-first rendering',
      title: 'The Blog',
      accent: 'server-first',
      subtitle: 'Notes on the AHA stack — Astro, HTMX, Alpine — and shipping server-rendered sites that stay fast.',
      primary_cta: { label: 'Explore projects', href: '/projects/' },
      secondary_cta: { label: 'Contact us', href: '/contact/' },
    },
    blog: [
      { title: 'A fast first visit is a product decision', slug: 'why-landing-pages-as-documents', excerpt: 'Performance is part of trust. A clear page that arrives quickly gives customers more confidence before the first conversation.', date: '2026-07-20', category: 'performance', read_time: '6 min' },
      { title: 'Designing bilingual journeys without duplication', slug: 'htmx-fragments-vs-json-apis', excerpt: 'A practical way to keep Arabic and English content aligned while letting each language sound natural.', date: '2026-07-25', category: 'content', read_time: '7 min' },
    ],
    cta: {
      title: 'Everything is open source',
      subtitle: 'All structa.cloud libraries are public on GitHub. Explore the code, open issues, or contribute.',
      primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
    },
  },
  contact: {
    slug: 'contact', title: 'Contact', type: 'ContactPage', show_in_nav: true,
    seo_title: 'Contact · Precis',
    search_description: 'Tell us what you are building.',
    hero: {
      badge: 'contact · human response',
      title: "Let's talk",
      accent: 'talk',
      subtitle: 'Send a message and we will get back to you within one business day.',
      primary_cta: { label: 'Browse courses', href: '/courses/' },
      secondary_cta: { label: 'Read the FAQ', href: '/faq/' },
    },
    cta: {
      title: 'Questions about the platform?',
      subtitle: 'Read the FAQ for the honest answers to the questions buyers ask.',
      primary_cta: { label: 'Read the FAQ', href: '/faq/' },
    },
  },
  faq: {
    slug: 'faq', title: 'FAQ', type: 'FaqPage', show_in_nav: false,
    seo_title: 'FAQ · Precis',
    search_description: 'Frequently asked questions about Precis, the AHA stack, and the product line.',
    hero: {
      badge: 'faq · honest answers',
      title: 'Frequently asked questions',
      accent: 'honest answers',
      subtitle: 'Clear answers about the stack, products, and editions.',
    },
    faq: [
      { question: 'What is the AHA stack?', answer: 'Astro, HTMX, and Alpine.js. Pages ship as finished server-rendered HTML, dynamic regions swap in HTML fragments, and small interactions stay local.' },
      { question: 'Is everything open source?', answer: 'The core libraries and community editions are public on GitHub. Standard, Pro, and Cloud editions are commercial.' },
      { question: 'Which languages does the site support?', answer: 'English, Swedish, French, German, Spanish, Arabic (RTL), and Portuguese (Brazil).' },
      { question: 'Can I self-host the learning platform?', answer: 'Yes — the open-source edition runs the same Django + Wagtail + Astro stack used here.' },
    ],
    cta: {
      title: 'Still deciding?',
      subtitle: 'Read the pricing sheet or contact us directly.',
      primary_cta: { label: 'See pricing', href: '/pricing/' },
      secondary_cta: { label: 'Contact us', href: '/contact/' },
    },
  },
  privacy: {
    slug: 'privacy', title: 'Privacy', type: 'PrivacyPage', show_in_nav: false,
    seo_title: 'Privacy · Precis',
    search_description: 'How Precis handles information.',
    hero: {
      badge: 'privacy · minimal by design',
      title: 'Privacy policy',
      accent: 'minimal by design',
      subtitle: 'We keep data collection minimal by design.',
    },
    body: '<p>We collect only the information needed to run the learning platform: account details, enrollment records, and optional marketing consent. We do not sell personal data.</p>',
    cta: {
      title: 'Any questions?',
      subtitle: 'Contact us about this policy at any time.',
      primary_cta: { label: 'Contact us', href: '/contact/' },
    },
  },
};

// Product detail pages — built for the seeded slugs (forge-pos, lms, cms)
// plus the broader catalog when the backend lists more.
const PRODUCT_DETAILS: Record<string, Partial<PageData>> = {
  'forge-pos': {
    slug: 'forge-pos', title: 'Forge POS', type: 'ProductPage', show_in_nav: false,
    seo_title: 'Forge POS · Precis',
    search_description: 'Desktop point-of-sale in three editions — Minimal, Solo, and Full.',
    hero: {
      badge: 'product · desktop POS',
      title: 'Forge POS',
      accent: 'desktop point-of-sale',
      subtitle: 'A desktop POS in three editions — Minimal (SQLite), Solo (embedded Python), and Full (multi-terminal + cloud CRM).',
      primary_cta: { label: 'See editions', href: '/pricing/' },
      secondary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
    },
    tech: ['Rust', 'Tauri 2', 'React', 'TypeScript', 'SQLite'],
    editions: [
      { name: 'Minimal', price: '$0', period: '/open source', tagline: 'Single terminal, offline-first.', features: ['Sales + receipting', 'SQLite storage', 'Refunds & returns'], featured: false, cta_label: 'Self-host', cta_href: 'https://github.com/mammhoud' },
      { name: 'Solo', price: '$119', period: '/one-time', tagline: 'A polished standalone terminal.', features: ['Everything in Minimal', 'Inventory adjustments', 'Invoice PDF generation'], featured: true, cta_label: 'Get started', cta_href: '/contact/' },
      { name: 'Full', price: '$79', period: '/per year', tagline: 'Multi-terminal with a cloud master.', features: ['Everything in Solo', 'Multi-terminal sync', 'WebSocket real-time streaming'], featured: false, cta_label: 'Contact sales', cta_href: '/contact/' },
    ],
    features: [
      { icon: 'M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z', title: 'Tauri 2 + Rust core', description: 'A fast, secure desktop shell with a Rust (Diesel) data layer.' },
      { icon: 'M13 10V3L4 14h7v7l9-11h-7z', title: 'Offline-first', description: 'Sales and inventory keep working without a network connection.' },
      { icon: 'M3 3v18h18M7 15l4-4 3 3 5-6', title: 'KPI dashboards', description: 'Time-bucketed sales, inventory, and transaction metrics.' },
    ],
    faq: [
      { question: 'Which editions are available?', answer: 'Minimal (free, open source), Solo (one-time license), and Full (annual, with a cloud master for multi-terminal sync).' },
      { question: 'Does it work offline?', answer: 'Yes — Minimal and Solo are fully offline-first; Full syncs to the cloud master when a connection is available.' },
    ],
    cta: { title: 'Ready to try Forge POS?', subtitle: 'Start with the free Minimal edition or contact sales for a demo.', primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' } },
  },
  lms: {
    slug: 'lms', title: 'Precis LMS', type: 'ProductPage', show_in_nav: false,
    seo_title: 'Precis LMS · Precis',
    search_description: 'Courses, enrollments, and a learning experience your team can own.',
    hero: {
      badge: 'product · learning platform',
      title: 'Precis LMS',
      accent: 'learning that ships',
      subtitle: 'A focused learning platform built with Django, Wagtail, and Astro — courses, enrollments, and progress your team can own.',
      primary_cta: { label: 'Browse courses', href: '/courses/' },
      secondary_cta: { label: 'See pricing', href: '/pricing/' },
    },
    tech: ['Django', 'Wagtail', 'Astro', 'HTMX', 'Alpine'],
    editions: [
      { name: 'Solo', price: '$29', period: '/per month', tagline: 'A polished learning experience for active creators.', features: ['Unlimited courses', 'Progress tracking', 'Certificates', 'Priority support'], featured: true, cta_label: 'Get started', cta_href: '/contact/' },
      { name: 'Business', price: '$99', period: '/per month', tagline: 'Cohorts, staff, and connected systems for organizations.', features: ['Everything in Solo', 'Custom branding', 'SSO & role management', 'API access'], featured: false, cta_label: 'Contact sales', cta_href: '/contact/' },
    ],
    features: [
      { icon: 'M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z', title: 'Server-rendered pages', description: 'Every course and catalog page ships as finished HTML.' },
      { icon: 'M13 10V3L4 14h7v7l9-11h-7z', title: 'Visible progress', description: 'Modules, lessons, and progress tracking keep learners moving.' },
      { icon: 'M3 3v18h18M7 15l4-4 3 3 5-6', title: 'Seven-language locales', description: 'A full Wagtail locale tree with Arabic RTL support.' },
    ],
    faq: [
      { question: 'Is Precis LMS free?', answer: 'The core platform is open source. Solo and Business are hosted editions with support, analytics, and advanced features.' },
      { question: 'Can I self-host?', answer: 'Yes — the community edition runs the same Django + Wagtail + Astro stack used on this site.' },
    ],
    cta: { title: 'Start your learning path', subtitle: 'Browse the live catalog or contact us about hosting.', primary_cta: { label: 'Browse courses', href: '/courses/' } },
  },
  cms: {
    slug: 'cms', title: 'Loop', type: 'ProductPage', show_in_nav: false,
    seo_title: 'Loop · Precis',
    search_description: 'Build content-driven websites from Wagtail blocks.',
    hero: {
      badge: 'product · content platform',
      title: 'Loop',
      accent: 'content-driven websites',
      subtitle: 'Build content-driven websites from Wagtail StreamField blocks — served as finished HTML with HTMX forms.',
      primary_cta: { label: 'See pricing', href: '/pricing/' },
      secondary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
    },
    tech: ['Django', 'Wagtail', 'Astro', 'HTMX'],
    editions: [
      { name: 'Community', price: '$0', period: '/open source', tagline: 'A landing page with the core section blocks.', features: ['Wagtail StreamField blocks', 'django-fusion rendering', 'HTMX fragments', 'MIT license'], featured: false, cta_label: 'View on GitHub', cta_href: 'https://github.com/mammhoud' },
      { name: 'Business', price: 'Custom', period: '/per project', tagline: 'A managed multi-site with custom blocks and analytics.', features: ['Custom StreamField blocks', 'Blog + FAQ sections', 'Analytics + SEO', 'Multi-site + roles'], featured: true, cta_label: 'Contact sales', cta_href: '/contact/' },
    ],
    features: [
      { icon: 'M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z', title: 'Wagtail StreamField', description: 'Editors compose pages from reusable content blocks.' },
      { icon: 'M13 10V3L4 14h7v7l9-11h-7z', title: 'HTMX fragments', description: 'Forms and dynamic regions swap finished HTML, not JSON.' },
      { icon: 'M3 3v18h18M7 15l4-4 3 3 5-6', title: 'Bilingual by default', description: 'Arabic + English editorial overlays with a stable API contract.' },
    ],
    cta: { title: 'Ship content as documents', subtitle: 'Community is free; Business is quoted per project.', primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' } },
  },
  cypercloud: {
    slug: 'cypercloud', title: 'Syntara', type: 'ProductPage', show_in_nav: false,
    seo_title: 'Syntara · Precis',
    search_description: 'AI chat customizer with an embeddable, branded experience.',
    hero: {
      badge: 'product · AI chat',
      title: 'Syntara',
      accent: 'embeddable AI chat',
      subtitle: 'AI chat customizer with an embeddable, branded experience — powered by ceptor-ai and its MCP server.',
      primary_cta: { label: 'See pricing', href: '/pricing/' },
      secondary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' },
    },
    tech: ['Python', 'Django', 'ceptor-ai', 'MCP'],
    editions: [
      { name: 'Community', price: '$0', period: '/open source', tagline: 'Self-hosted chat client with multi-model support.', features: ['ceptor-ai chat client', 'MCP server', 'Multi-model support'], featured: false, cta_label: 'Self-host', cta_href: 'https://github.com/mammhoud' },
      { name: 'Business', price: '$39', period: '/per month', tagline: 'Managed chat with branding, rules, and analytics.', features: ['Everything in Community', 'Branded widget', 'Behavior rules', 'Analytics'], featured: true, cta_label: 'Get started', cta_href: '/contact/' },
    ],
    features: [
      { icon: 'M12 2l8 4v6c0 5-3.5 8-8 10-4.5-2-8-5-8-10V6l8-4z', title: 'Embeddable widget', description: 'A branded chat experience drops into any site.' },
      { icon: 'M13 10V3L4 14h7v7l9-11h-7z', title: 'MCP server', description: 'Agents talk to your systems through the Model Context Protocol.' },
      { icon: 'M3 3v18h18M7 15l4-4 3 3 5-6', title: 'Multi-model', description: 'Route between providers with behavior rules per workspace.' },
    ],
    cta: { title: 'Embed chat your customers trust', subtitle: 'Community is free; Business is $39/month.', primary_cta: { label: 'View on GitHub', href: 'https://github.com/mammhoud' } },
  },
};

export function staticPageData(slug: string): PageData | null {
  const value = CONTENT[slug] || PRODUCT_DETAILS[slug];
  return value ? ({ id: 0, ...value } as PageData) : null;
}
