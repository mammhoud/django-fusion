/**
 * Section-placement & seeded-content tests.
 *
 * Proves, against the *built* HTML (the real artifact the browser gets),
 * that the static site renders the content seeded by the Wagtail backend
 * (backend/assets/fixtures/dump-data.json + apps/learning/fixtures/
 * medical_research_catalog.json) and that each page shows exactly the
 * sections its design intends:
 *
 *   - `/`       (Home)    — slim hero + methods + program pillars + CTA
 *   - `/about`  (About)   — seeded experience, gallery, methods, CTA
 *   - `/team`   (Team)    — the seeded researcher roster
 *   - `/contact`          — the seeded contact form fields
 *   - `/courses`          — the seeded medical-research catalog
 *   - `/courses/<slug>`   — seeded course detail pages
 *
 * Because the frontend is API-driven (src/lib/api.ts), the build bakes the
 * backend's seeded content in at build time. The Django backend must be
 * reachable on :5070 (the CTC Research Compose backend port) so the build
 * fetches real seeded data — otherwise this suite fails with a clear message.
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
    const res = execSync('curl -sf -o /dev/null http://localhost:5070/apis/pages/home/', { stdio: 'pipe' });
    return res !== null;
  } catch {
    return false;
  }
}
if (!backendReachable()) {
  throw new Error(
    'The Django backend is not reachable on http://localhost:5070. ' +
    'Start it first (docker compose -f projects/precis/precis-ctc/docker-compose.yml up -d backend) so the build bakes seeded content.',
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
const team = readPage('team', 'index.html');
const contact = readPage('contact', 'index.html');
const courses = readPage('courses', 'index.html');
const courseTrial = readPage('courses', 'clinical-trial-design-protocol-development', 'index.html');
const courseBio = readPage('courses', 'biostatistics-clinical-research', 'index.html');
const services = readPage('services', 'index.html');
const products = readPage('products', 'index.html');
const blog = readPage('blog', 'index.html');
const events = readPage('events', 'index.html');
const faq = readPage('faq', 'index.html');
const privacy = readPage('privacy', 'index.html');

// Content that must never appear anywhere in the CTC Research build — stale
// branding from the pre-merge structa.cloud / Fusion LMS era.
const staleTechMarkers = [
  'structa.cloud',
  'Fusion LMS',
  'Fusion CMS',
  'Forge POS',
  'One monorepo',
  'What we ship',
  'This page is the framework',
  'HTMX: Fragment Swap',
];

test('home is a slim hero + methods + programs entry page with seeded content', () => {
  // Seeded hero fallback: title "Turn clinical data into" + accent "trusted evidence".
  assert.match(home, /Turn clinical data into/);
  assert.match(home, /trusted evidence/);
  // Backend-provided hero badge (apps/pages/pages/landing_api.py).
  assert.match(home, /ctc research · medical research learning/);
  // Seeded methods (HomePage.CTA → why_choose_section → methods).
  assert.match(home, /Our methods/);
  assert.match(home, /cross-disciplinary research in AI/);
  assert.match(home, /medical data analytics/);
  // Seeded program pillars (HomePage.summary → about → service_items).
  assert.match(home, /The Mastery Pillar/);
  assert.match(home, /The Capability Pillar/);
  assert.match(home, /The Impact Pillar/);
  // Seeded vision copy.
  assert.match(home, /Our Vision/);
  // Seeded CTA.
  assert.match(home, /Advance health through research/);
  // Slim page — no full-document sections, no error cards, no stale tech demos.
  assert.ok(!home.includes('unavailable'), 'home should not render error cards');
  for (const marker of staleTechMarkers) {
    assert.ok(!home.includes(marker), `home should NOT contain: ${marker}`);
  }
});

test('about carries the seeded experience, gallery, and methods', () => {
  // Seeded hero.
  assert.match(about, /CTC Research/);
  assert.match(about, /medical research center/);
  // Seeded welcome text + experience description (AboutPage.facts → about).
  assert.match(about, /WHO WE ARE/);
  assert.match(about, /Over two decades of pioneering research/);
  // Seeded gallery (media_items with a Dr. yasir image).
  assert.match(about, /Snapshots/);
  assert.match(about, /Dr\. yasir/);
  // Seeded capability copy (methods section renders only when the backend
  // seeds an `methods` array for the About page).
  assert.match(about, /What we do, in detail/);
  // No error cards on a seeded page.
  assert.ok(!about.includes('unavailable'), 'about should not render error cards');
  for (const marker of staleTechMarkers) {
    assert.ok(!about.includes(marker), `about should NOT contain: ${marker}`);
  }
});

test('team renders the seeded researcher roster', () => {
  // Seeded team members (TeamPage.body → team_section → team_members).
  assert.match(team, /Laurens van Kleef/);
  assert.match(team, /Postdoctoral Researcher and Resident/);
  assert.match(team, /Dr\. Niks/);
  assert.match(team, /Consultant Anaesthetist/);
  assert.ok(!team.includes('Team data unavailable'), 'team should render seeded members, not an error card');
  for (const marker of staleTechMarkers) {
    assert.ok(!team.includes(marker), `team should NOT contain: ${marker}`);
  }
});

test('contact renders the seeded form fields and contact methods', () => {
  // Seeded ContactPage form fields.
  assert.match(contact, /Send us a message/);
  assert.match(contact, /Full Name/);
  assert.match(contact, /Email Address/);
  assert.match(contact, /Message/);
  // Seeded/fallback contact method.
  assert.match(contact, /support@ctc-research\.com/);
  for (const marker of staleTechMarkers) {
    assert.ok(!contact.includes(marker), `contact should NOT contain: ${marker}`);
  }
});

test('courses index shows the seeded medical-research catalog', () => {
  // Seeded catalog (medical_research_catalog.json — 8 English courses). The
  // static build HTML-escapes `&` as `&amp;`, so assert the escaped artifact
  // text. The catalog page also carries the search/filter/sort toolbar.
  for (const title of [
    'Clinical Trial Design &amp; Protocol Development',
    'Biostatistics for Clinical Research',
    'Systematic Review &amp; Meta-Analysis',
    'Medical AI &amp; Clinical Applications',
    'Clinical Data Management',
    'Evidence Synthesis for HTA',
    'Research Ethics &amp; Integrity',
    'Scientific Writing for Medical Manuscripts',
  ]) {
    assert.ok(courses.includes(title), `courses should contain: ${title}`);
  }
  assert.match(courses, /Research, from protocol to publication/);
  assert.match(courses, /courseCatalog\(\)/);
  assert.match(courses, /catalog__toolbar/);
  assert.match(courses, /catalog__filters/);
  for (const marker of staleTechMarkers) {
    assert.ok(!courses.includes(marker), `courses should NOT contain: ${marker}`);
  }
});

test('course detail pages render seeded course facts and pricing', () => {
  // Clinical trial design course (seeded + certificate). Prices are computed
  // server-side (discounts may apply), so assert the stable facts only.
  assert.match(courseTrial, /Clinical Trial Design &amp; Protocol Development/);
  assert.match(courseTrial, /Certificate included/);
  assert.match(courseTrial, /Enroll now/);
  assert.match(courseTrial, /sidebar-price/);
  // Biostatistics course.
  assert.match(courseBio, /Biostatistics for Clinical Research/);
  assert.match(courseBio, /Certificate included/);
});

test('services page renders its seeded hero without stale tech copy', () => {
  assert.match(services, /Our Capabilities/);
  assert.match(services, /Start learning with CTC Research/);
  for (const marker of staleTechMarkers) {
    assert.ok(!services.includes(marker), `services should NOT contain: ${marker}`);
  }
});

test('products page renders the program-line hero (no stale product lines)', () => {
  assert.match(products, /Programs &amp; services/);
  assert.match(products, /for health innovation/);
  for (const marker of staleTechMarkers) {
    assert.ok(!products.includes(marker), `products should NOT contain: ${marker}`);
  }
  // No stale product detail routes should have been built (fallback slugs emptied).
  assert.throws(() => readPage('products', 'forge-pos', 'index.html'));
});

test('blog page renders its seeded hero without stale posts', () => {
  assert.match(blog, /The Blog/);
  for (const marker of staleTechMarkers) {
    assert.ok(!blog.includes(marker), `blog should NOT contain: ${marker}`);
  }
  // No stale blog detail routes should have been built (fallback slugs emptied).
  assert.throws(() => readPage('blog', 'why-landing-pages-as-documents', 'index.html'));
});

test('events page renders the CTC events shell', () => {
  assert.match(events, /Upcoming Events/);
  for (const marker of staleTechMarkers) {
    assert.ok(!events.includes(marker), `events should NOT contain: ${marker}`);
  }
});

test('faq and privacy pages render their CTC-branded documents', () => {
  assert.match(faq, /Frequently asked questions/);
  assert.match(privacy, /Information we collect/);
  assert.match(privacy, /Cookies and tracking/);
  assert.match(privacy, /Your rights/);
  for (const marker of staleTechMarkers) {
    assert.ok(!faq.includes(marker), `faq should NOT contain: ${marker}`);
    assert.ok(!privacy.includes(marker), `privacy should NOT contain: ${marker}`);
  }
});
