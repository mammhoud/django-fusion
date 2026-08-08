/**
 * Section-placement & seeded-content tests.
 *
 * Proves, against the *built* HTML (the real artifact the browser gets),
 * that the static site renders the content seeded by the Wagtail backend
 * (apps/pages/management/commands/seed_pages.py) and that each page shows
 * exactly the sections its design intends:
 *
 *   - `/`        (Home)    — slim hero + CTA entry; no section stack, no error cards
 *   - `/about`   (About)   — full document: stats, features, testimonials, faq, cta
 *   - `/features`          — capabilities + testimonials + faq
 *   - `/products`          — stats + the six product lines
 *   - `/projects`          — the repo project grid (editions + shared/own flags)
 *   - `/contact`, `/faq`, `/privacy` — seeded contact methods / FAQ items / body
 *
 * Because the frontend is API-driven (src/lib/api.ts), the build bakes the
 * backend's seeded content in at build time. The Django backend must be
 * reachable on :8074 (`cd backend && make dev`) so the build fetches real
 * seeded data — otherwise this suite fails with a clear message.
 *
 * Run:  npm test
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// The Astro build fetches all content from the backend. Require it so the
// assertions run against seeded data, not silent fallbacks.
function backendReachable() {
  try {
    const res = execSync('curl -sf -o /dev/null http://localhost:8074/apis/pages/home/', { stdio: 'pipe' });
    return res !== null;
  } catch {
    return false;
  }
}
if (!backendReachable()) {
  throw new Error(
    'The Django backend is not reachable on http://localhost:8074. ' +
    'Start it first (cd projects/landing-fusion/backend && make dev) so the build bakes seeded content.',
  );
}

// Build once before the suite so assertions run against a fresh dist/.
execSync('npm run build', { cwd: root, stdio: 'pipe' });

const dist = join(root, 'dist');
function readPage(...segments) {
  return readFileSync(join(dist, ...segments), 'utf8');
}

const home = readPage('index.html');
const about = readPage('about', 'index.html');
const features = readPage('features', 'index.html');
const products = readPage('products', 'index.html');
const projects = readPage('projects', 'index.html');
const contact = readPage('contact', 'index.html');
const faq = readPage('faq', 'index.html');
const privacy = readPage('privacy', 'index.html');
const blog = readPage('blog', 'index.html');
const pricing = readPage('pricing', 'index.html');
const services = readPage('services', 'index.html');
const brand = readPage('brand', 'index.html');
const formintsPos = readPage('products', 'formint-pos', 'index.html');
const legacyForgePos = readPage('products', 'forge-pos', 'index.html');
const lms = readPage('products', 'lms', 'index.html');
const cms = readPage('products', 'cms', 'index.html');
const blogDoc = readPage('blog', 'why-landing-pages-as-documents', 'index.html');
const blogHtmx = readPage('blog', 'htmx-fragments-vs-json-apis', 'index.html');

// Sections seeded only for the full-document pages — must NOT appear on the
// slim home page. ("data unavailable" cards are a defect, not a section.)
const fullDocumentMarkers = [
  'Numbers that speak for themselves', // stats section title
  'Everything you need to launch',     // features section title
  'Trusted by developers',             // testimonials section title
  'Sarah Mitchell',                    // seeded testimonial author
  'What is structa.cloud?',            // seeded FAQ question
  '>503<',                             // ContentError cards must never render
];

test('home is a slim hero + CTA entry page with seeded hero/CTA', () => {
  // Seeded hero: title "Digital products, shipped as" + accent "documents".
  assert.match(home, /Digital products, shipped as/);
  assert.match(home, /documents/);
  assert.match(home, /structa\.cloud · digital product partner/);
  // Seeded CTA.
  assert.match(home, /A useful first release beats a noisy roadmap/);
  // Products preview section (frontend design).
  assert.match(home, /tag-marker mb-4">products/);
  // Slim page — none of the full-document markers or error cards.
  for (const marker of fullDocumentMarkers) {
    assert.ok(!home.includes(marker), `home should NOT contain: ${marker}`);
  }
});

test('about carries the full seeded document', () => {
  // Seeded hero: title "A clearer path to market" (founder/company story).
  assert.match(about, /A clearer path to market/);
  // Seeded stats (values animate client-side; labels are server-rendered).
  for (const label of ['Open-source repos', 'Blog posts', 'Production sites', 'Years building']) {
    assert.ok(about.includes(label), `about should contain stat label: ${label}`);
  }
  // Seeded features reframed around the founder + company.
  assert.match(about, /A founder who ships/);
  assert.match(about, /Your team owns the content/);
  assert.match(about, /Arabic and English by design/);
  assert.match(about, /A system that can be handed over/);
  // Seeded testimonials (the Astro component renders its own section heading;
  // the seeded authors/quotes are what the page must show).
  for (const author of ['Sarah Mitchell', 'David Chen', 'Amira Hassan']) {
    assert.ok(about.includes(author), `about should contain testimonial author: ${author}`);
  }
  // FAQ is deduplicated onto /faq/ — About carries no duplicate FAQ section,
  // and instead links to the team subpage.
  assert.ok(!about.includes('Frequently asked questions'), 'about should NOT contain a duplicate FAQ section');
  assert.match(about, /Meet the team/);
  assert.match(about, /\/about\/team\//);
  // Seeded CTA.
  assert.match(about, /Built in the open, shipped as HTML/);
});

test('features is a full document like about', () => {
  // Seeded hero: "Built to ship as" + accent "documents".
  assert.match(features, /Built to ship as/);
  // Seeded capabilities (features section item cards — shared about section).
  assert.match(features, /A founder who ships/);
  assert.match(features, /Your team owns the content/);
  assert.match(features, /Arabic and English by design/);
  // Seeded testimonials. FAQ is deduplicated onto /faq/ only.
  assert.match(features, /Sarah Mitchell/);
  assert.ok(!features.includes('Frequently asked questions'), 'features should NOT contain a duplicate FAQ section');
  // Seeded CTA.
  assert.match(features, /Built in the open, shipped as HTML/);
});

test('products is the merged catalog: renamed product cards with logos, status, monorepo link', () => {
  // Seeded hero: "Most of what we build, shipped as" + accent "open source".
  assert.match(products, /Most of what we build, shipped as/);
  assert.match(products, /open source/);
  // Seeded stats.
  assert.ok(products.includes('Open-source repos'), 'products should contain seeded stat label');
  // The merged section heading + monorepo link (product line + project grid folded together).
  assert.match(products, /Projects in this repo/);
  assert.match(products, /Browse the monorepo on GitHub/);
  // Data-driven catalog — renamed products, no removed/hidden ones.
  for (const name of ['Formints', 'Precis LMS', 'Loop', 'Syntara', 'vResume']) {
    assert.ok(products.includes(name), `products should contain product: ${name}`);
  }
  // Removed/hidden products get no card and no link (prose mentions in the
  // shared FAQ are fine — ceptor-ai is still the AI library).
  assert.ok(!products.includes('django-bolt'), 'products should NOT contain: django-bolt');
  assert.ok(!products.includes('/products/ceptor-ai/'), 'products should NOT link to hidden ceptor-ai');
  assert.ok(!products.includes('The product line'), 'products should NOT contain: The product line');
  // The flagship card shows the Formints editions + pricing inline.
  for (const marker of ['Community', 'Standard', 'Pro', 'Cloud']) {
    assert.ok(products.includes(marker), `products should show POS edition: ${marker}`);
  }
  // Category badges render on the cards.
  assert.match(products, /application/);
  assert.match(products, /platform/);
  // Logo marks + edition chips render (the merged-card design).
  assert.match(products, /product-logo/);
  assert.match(products, /edition-chip/);
  // Each product renders its own brand-identity chip (no shared generic mark).
  for (const chip of ['data-brand="formints"', 'data-brand="precis"', 'data-brand="loop"', 'data-brand="syntara"', 'data-brand="vresume"']) {
    assert.ok(products.includes(chip), `products should render mark chip: ${chip}`);
  }
  // Seeded CTA (full-document pages close with the about-style CTA).
  assert.match(products, /Built in the open, shipped as HTML/);
});

test('legacy product slug redirects to canonical Formints route', () => {
  // Static Astro output emits a redirect document; the dev server/proxy also
  // serves it as a 301, covered by the live smoke test.
  assert.match(legacyForgePos, /redirect/i);
  assert.match(legacyForgePos, /\/products\/formint-pos\//);
});

test('projects is a permanent redirect to the merged products catalog', () => {
  // The legacy route now redirects — Astro emits a meta-refresh document.
  assert.match(projects, /redirect/i);
  assert.match(projects, /\/products/);
});

test('contact shows seeded contact methods + topic choices', () => {
  assert.match(contact, /We'd love to hear from you/);
  assert.match(contact, /structa\.cloud@gmail\.com/);
  assert.match(contact, /\+1 \(555\) 010-2030/);
  // The topic select offers the product/service choices.
  assert.match(contact, /Formints POS/);
  assert.match(contact, /Precis LMS/);
  assert.match(contact, /Loop CMS/);
  assert.match(contact, /Syntara/);
});

test('faq page shows seeded FAQ items', () => {
  assert.match(faq, /Frequently asked questions/);
  assert.match(faq, /What is structa\.cloud\?/);
  assert.match(faq, /How do I get started\?/);
});

test('privacy page renders its legal document', () => {
  // The Astro privacy page ships its own full legal policy (8 sections); the
  // backend seeds a short RichText body used by the backend render only.
  assert.match(privacy, /Information we collect/);
  // The restructured policy has a dedicated cookies/consent section (section 3)
  // covering what data is collected and what accepting consent enables.
  assert.match(privacy, /Cookies and consent/);
  assert.match(privacy, /What accepting consent does/);
  assert.match(privacy, /Your rights/);
});

test('blog page shows the seeded post grid', () => {
  assert.match(blog, /Ideas from real launches/);
  assert.match(blog, /From the blog/);
  assert.match(blog, /Why we ship landing pages as documents/);
  assert.match(blog, /HTMX fragments vs\. JSON APIs/);
  assert.match(blog, /monorepo-six-products/);
});

test('pricing page shows per-product tabs + faq', () => {
  assert.match(pricing, /Pick a product, see its editions/);
  for (const product of ['Formints', 'Precis LMS', 'Loop', 'Syntara', 'vResume']) {
    assert.ok(pricing.includes(product), `pricing should contain product tab: ${product}`);
  }
  // The default tab shows Formints' four editions incl. the new pricing.
  for (const marker of ['Community', 'Standard', 'Pro', 'Cloud', '$119', '$79']) {
    assert.ok(pricing.includes(marker), `pricing should contain: ${marker}`);
  }
  // Syntara's development caution badge renders in its tab.
  assert.match(pricing, /under development/);
  // Hidden products are not tabbed.
  assert.ok(!pricing.includes('/products/ceptor-ai/'), 'pricing should not link to hidden products');
  // FAQ is deduplicated — pricing points buyers to the dedicated page.
  assert.ok(!pricing.includes('Frequently asked questions'), 'pricing should NOT contain a duplicate FAQ section');
  assert.match(pricing, /Read the FAQ/);
  assert.match(pricing, /\/faq\//);
});

test('services page shows the three service lines + build-as-you-go process', () => {
  assert.match(services, /From marketing sites to full products/);
  for (const line of ['Market-ready websites', 'Digital product delivery', 'Improve what already works']) {
    assert.ok(services.includes(line), `services should contain: ${line}`);
  }
  assert.match(services, /From brief to shipped, in four steps/);
  assert.match(services, /Discover/);
  assert.match(services, /Ship &amp; grow/);  // `&` is HTML-escaped in the build
});

test('brand page renders the identity system: one board per product with its constructed mark', () => {
  assert.match(brand, /One family, five marks/);
  // Each brand's essence line + its own data-brand mark chip.
  for (const essence of ['The till, made trustworthy.', 'Learning, precisely.', 'Content, composed.', 'Chat, routed around your brand.', 'Your career, on the record.']) {
    assert.ok(brand.includes(essence), `brand should contain essence: ${essence}`);
  }
  for (const chip of ['data-brand="formints"', 'data-brand="precis"', 'data-brand="loop"', 'data-brand="syntara"', 'data-brand="vresume"']) {
    assert.ok(brand.includes(chip), `brand should render mark chip: ${chip}`);
  }
  // Brand story labels + construction notes are present.
  assert.match(brand, /construction/);
  assert.match(brand, /palette/);
  // The palette is driven by the spec — brand accent swatch + shared system
  // tokens render on every board (brand-swatch chips with token titles).
  assert.match(brand, /brand-swatch/);
  assert.match(brand, /title="paper"/);
  assert.match(brand, /title="ink"/);
  assert.match(brand, /title="line"/);
});

test('products page lists every product page card', () => {
  assert.match(products, /Projects in this repo/);
  for (const href of ['/products/formint-pos/', '/products/lms/', '/products/cms/', '/products/vresume/']) {
    assert.ok(products.includes(href), `products should link to: ${href}`);
  }
});

test('formints page shows all four tiered editions with per-edition pricing', () => {
  assert.match(formintsPos, /Formints/);
  for (const marker of ['Community', 'Standard', 'Pro', 'Cloud', '$0', '$119', '$79', 'Custom']) {
    assert.ok(formintsPos.includes(marker), `formints should contain: ${marker}`);
  }
  // The visual tiering system: outline Community, featured Pro, managed Cloud.
  assert.match(formintsPos, /edition__card--outline/);
  assert.match(formintsPos, /most shipped/);
  assert.match(formintsPos, /managed-ribbon/);
  // Product details use visual captures instead of public code/snippet blocks.
  assert.match(formintsPos, /See it in motion/);
  assert.match(formintsPos, /preview-gallery__item/);
  assert.match(formintsPos, /alt="Animated walkthrough of the Formints Standard point-of-sale interface"/);
  assert.doesNotMatch(formintsPos, /Models &amp; snippets/);
  assert.doesNotMatch(formintsPos, /CREATE TABLE sales/);
  assert.doesNotMatch(formintsPos, /Diesel migration \(up\.sql\)/);
  assert.doesNotMatch(formintsPos, /Tauri command \(invoice PDF\)/);
  // New capability chips + roadmap cards (the Astro road flattens feature
  // blocks into cards; the block title "Product roadmap" renders on Django).
  assert.match(formintsPos, /Offline-first mode/);
  assert.match(formintsPos, /Loyalty &amp; rewards program/);
  assert.match(formintsPos, /Loyalty &amp; rewards engine/);
  assert.match(formintsPos, /Multi-currency &amp; tax profiles/);
  assert.match(formintsPos, /Automatic cloud backups/);
});

test('formint-pos page ships the full feature-comparison table', () => {
  // The Wagtail-managed comparison block: ~26 capability rows across 4 editions.
  assert.match(formintsPos, /Compare editions/);
  assert.match(formintsPos, /Community vs Standard vs Pro vs Cloud/);
  for (const row of [
    'React 19 + TypeScript frontend',
    'Tauri 2 + Rust backend',
    'SQLite database',
    'High-end interface design',
    'Inventory adjustments + stock control',
    'Food &amp; beverage (F&amp;B) menu support',
    'Kitchen display system',
    'WebSocket real-time streaming',
    'High-throughput Rust API (60k+ RPS)',
    'Hosted deployment + managed backups',
    'Offline-first mode',
    'Refunds &amp; returns',
    'Loyalty &amp; rewards program',
    'Multi-currency &amp; tax profiles',
    'Custom roles &amp; permissions',
    'Data export (CSV/JSON)',
    'Automatic cloud backups',
  ]) {
    assert.ok(formintsPos.includes(row), `formint-pos comparison should contain row: ${row}`);
  }
  // Cells render as plain text where a note is present (not only Yes/No).
  assert.match(formintsPos, /cloud master/);
});

test('precis-lms and loop pages render their editions', () => {
  assert.match(lms, /Precis LMS/);
  assert.match(lms, /Solo/);
  assert.match(lms, /Business/);
  assert.match(lms, /SSO &amp; role management/);
  assert.match(lms, /Dedicated success manager/);
  assert.match(lms, /High-end learning experience design/);
  assert.doesNotMatch(lms, /For solo creators publishing their first course/);
  assert.doesNotMatch(lms, /Up to 3 courses/);
  assert.match(cms, /Loop/);
  assert.match(cms, /Community/);
  assert.match(cms, /Business/);
});

test('blog post detail pages render seeded bodies and link back to /blog', () => {
  // The index grid links to the detail pages.
  assert.match(blog, /\/blog\/why-landing-pages-as-documents\//);
  assert.match(blog, /\/blog\/htmx-fragments-vs-json-apis\//);
  // Detail pages render their own body copy (the seeded RichText).
  assert.match(blogDoc, /The document model/);
  assert.match(blogDoc, /No SPA shell, no hydration waterfall/);
  assert.match(blogHtmx, /The API contract tax/);
  assert.match(blogHtmx, /Half the frontend state/);
  // Meta row + back link present.
  assert.match(blogDoc, /All posts/);
  assert.match(blogDoc, /AHA stack/);
  assert.match(blogDoc, /6 min read/);
});
