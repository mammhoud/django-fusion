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
 * reachable on :5074 (the current Precis Compose backend port) so the build fetches real
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
    const res = execSync('curl -sf -o /dev/null http://localhost:5074/apis/pages/home/', { stdio: 'pipe' });
    return res !== null;
  } catch {
    return false;
  }
}
if (!backendReachable()) {
  throw new Error(
    'The Django backend is not reachable on http://localhost:5074. ' +
    'Start it first (docker compose -f projects/precis/docker-compose.yml up -d backend) so the build bakes seeded content.',
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
const forgePos = readPage('products', 'forge-pos', 'index.html');
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
  'unavailable',                       // ContentError cards must never render
];

test('home is a slim hero + CTA entry page with seeded hero/CTA', () => {
  // Seeded hero: title "Platforms that ship as" + accent "documents".
  assert.match(home, /Platforms that ship as/);
  assert.match(home, /documents/);
  assert.match(home, /structa\.cloud · full-stack engineering/);
  // Seeded CTA.
  assert.match(home, /Everything is open source/);
  // Products preview section (frontend design).
  assert.match(home, /What we ship/);
  // Slim page — none of the full-document markers or error cards.
  for (const marker of fullDocumentMarkers) {
    assert.ok(!home.includes(marker), `home should NOT contain: ${marker}`);
  }
});

test('about carries the full seeded document', () => {
  // Seeded hero: title "Mahmoud Ezzat" + accent "Moustafa".
  assert.match(about, /Mahmoud Ezzat/);
  assert.match(about, /Moustafa/);
  // Seeded stats (values animate client-side; labels are server-rendered).
  for (const label of ['Open-source repos', 'Blog posts', 'Production sites', 'Years building']) {
    assert.ok(about.includes(label), `about should contain stat label: ${label}`);
  }
  // Seeded features (item cards from the features section).
  assert.match(about, /Django \+ Wagtail/);
  assert.match(about, /HTMX Fragment Rendering/);
  assert.match(about, /Monorepo Architecture/);
  // Seeded testimonials (the Astro component renders its own section heading;
  // the seeded authors/quotes are what the page must show).
  for (const author of ['Sarah Mitchell', 'David Chen', 'Amira Hassan']) {
    assert.ok(about.includes(author), `about should contain testimonial author: ${author}`);
  }
  // Seeded FAQ items.
  assert.match(about, /What is structa\.cloud\?/);
  assert.match(about, /What is the AHA stack\?/);
  // Seeded CTA.
  assert.match(about, /Built open-source, shipped as HTML/);
});

test('features is a full document like about', () => {
  // Seeded hero: "Built to ship as" + accent "documents".
  assert.match(features, /Built to ship as/);
  // Seeded capabilities (features section item cards).
  assert.match(features, /Django \+ Wagtail/);
  assert.match(features, /HTMX Fragment Rendering/);
  // Seeded testimonials + FAQ.
  assert.match(features, /Sarah Mitchell/);
  assert.match(features, /What is structa\.cloud\?/);
  // Seeded CTA.
  assert.match(features, /Built open-source, shipped as HTML/);
});

test('products is a full document with the six product lines', () => {
  // Seeded hero: "Everything we build, shipped as" + accent "open source".
  assert.match(products, /Everything we build, shipped as/);
  assert.match(products, /open source/);
  // Seeded stats.
  assert.ok(products.includes('Open-source repos'), 'products should contain seeded stat label');
  // Product lines (frontend design).
  assert.match(products, /From libraries to platforms/);
  for (const name of ['django-fusion', 'ceptor-ai', 'django-bolt', 'vResume', 'Forge POS', 'Cypercloud']) {
    assert.ok(products.includes(name), `products should contain product line: ${name}`);
  }
  // Seeded CTA (full-document pages close with the about-style CTA).
  assert.match(products, /Built open-source, shipped as HTML/);
});

test('projects is a full document with the seeded repo grid', () => {
  // Seeded hero: "Everything we build, shipped as" + accent "one monorepo".
  assert.match(projects, /Everything we build, shipped as/);
  assert.match(projects, /one monorepo/);
  assert.match(projects, /Projects in this repo/);
  // Seeded project cards: name + edition + description.
  const seededProjects = [
    ['Fusion CMS', 'Wagtail backend', 'The Wagtail content engine behind every landing page'],
    ['Fusion Sites', 'Astro frontend', 'The AHA shell'],
    ['Forge POS', 'Minimal · Solo · Full', 'desktop point-of-sale'],
    ['django-fusion', 'library · generic', 'component system'],
    ['ceptor-ai', 'library · generic', 'MCP server'],
    ['Cypercloud', 'AI platform', 'chat customizer'],
  ];
  for (const [name, edition, descriptionSnippet] of seededProjects) {
    assert.ok(projects.includes(name), `projects should contain: ${name}`);
    assert.ok(projects.includes(edition), `projects should contain edition: ${edition}`);
    assert.ok(projects.includes(descriptionSnippet), `projects should render description for: ${name}`);
  }
  // Shared/own feature flags.
  assert.match(projects, /shared/);
  assert.match(projects, /own/);
  // BEM classes present.
  assert.match(projects, /project__grid/);
  assert.match(projects, /project__feature--shared/);
});

test('contact shows seeded contact methods', () => {
  assert.match(contact, /We'd love to hear from you/);
  assert.match(contact, /structa\.cloud@gmail\.com/);
  assert.match(contact, /\+1 \(555\) 010-2030/);
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
  assert.match(privacy, /Cookies and tracking/);
  assert.match(privacy, /Your rights/);
});

test('blog page shows the seeded post grid', () => {
  assert.match(blog, /The Blog/);
  assert.match(blog, /From the blog/);
  assert.match(blog, /Why we ship landing pages as documents/);
  assert.match(blog, /HTMX fragments vs\. JSON APIs/);
  assert.match(blog, /monorepo-six-products/);
});

test('pricing page shows seeded tiers + faq', () => {
  assert.match(pricing, /Simple, transparent pricing/);
  for (const tier of ['Starter', 'Pro', 'Team']) {
    assert.ok(pricing.includes(tier), `pricing should contain tier: ${tier}`);
  }
  assert.match(pricing, /What is structa\.cloud\?/);
});

test('services page shows offering grid + build-as-you-go process', () => {
  assert.match(services, /Sites that ship as documents/);
  assert.match(services, /Django \+ Wagtail build/);
  assert.match(services, /From brief to shipped, in four steps/);
  assert.match(services, /Discover/);
  assert.match(services, /Ship &amp; grow/);  // `&` is HTML-escaped in the build
});

test('products page lists every product page card', () => {
  assert.match(products, /Every product, one page each/);
  for (const href of ['/products/forge-pos/', '/products/lms/', '/products/cms/']) {
    assert.ok(products.includes(href), `products should link to: ${href}`);
  }
});

test('forge-pos page shows all editions with per-edition pricing', () => {
  assert.match(forgePos, /Forge POS/);
  for (const marker of ['Minimal', 'Solo', 'Full', '$0', '$49', '$99']) {
    assert.ok(forgePos.includes(marker), `forge-pos should contain: ${marker}`);
  }
  // Reference snippets (SQLite schema + Rust model).
  assert.match(forgePos, /SQLite schema/);
  assert.match(forgePos, /Rust model/);
  assert.match(forgePos, /CREATE TABLE sales/);
});

test('lms and cms pages render their editions', () => {
  assert.match(lms, /Fusion LMS/);
  assert.match(lms, /Starter/);
  assert.match(cms, /Fusion CMS/);
  assert.match(cms, /Basic/);
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
  assert.match(blogDoc, /Architecture/);
  assert.match(blogDoc, /6 min read/);
});
