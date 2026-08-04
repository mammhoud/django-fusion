/**
 * Section-placement tests for the page expansion.
 *
 * Proves, against the *built* HTML (the real artifact the browser gets):
 *   - `/` (Home) is a slim hero + CTA entry — no features/pricing/etc.
 *   - `/about` is the full document: hero, mission, stats, features,
 *     pricing (folded into the features section), testimonials, faq, cta.
 *   - The pricing section renders *inside* the features section on About.
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

// Slim markers that should NOT appear on the home page anymore.
const movedSections = [
  'Everything is a document', // features heading
  'Pricing, printed clearly', // pricing heading
  'The stack, reviewed in production', // testimonials heading
  'Questions, answered in plain HTML', // faq heading
  'Total page weight', // stats label
];

test('home is a slim hero + CTA entry page', () => {
  assert.match(home, /Your website, delivered as/);
  assert.match(home, /See the whole story/); // secondary CTA points to /about
  assert.match(home, /Create free account/);
  for (const marker of movedSections) {
    assert.ok(
      !home.includes(marker),
      `home should NOT contain the moved section marker: ${marker}`,
    );
  }
});

test('about carries the full document', () => {
  // Hero + mission
  assert.match(about, /The web, shipped as/);
  assert.match(about, /Why we build this way/);
  // Moved sections all present on /about
  for (const marker of movedSections) {
    assert.ok(about.includes(marker), `about should contain: ${marker}`);
  }
  // Closing cta
  assert.match(about, /Ship the document, not the app/);
});

test('pricing is folded inside the features section on about', () => {
  const featuresIdx = about.indexOf('id="features"');
  const pricingIdx = about.indexOf('id="pricing"');
  const ctaIdx = about.indexOf('Ship the document, not the app');

  assert.ok(featuresIdx !== -1, 'features section present');
  assert.ok(pricingIdx !== -1, 'pricing section present');
  assert.ok(ctaIdx !== -1, 'cta present');

  // The features section opens before pricing…
  assert.ok(featuresIdx < pricingIdx, 'features renders before pricing');
  // …and pricing is inside the features <section> — the features section
  // must close after pricing starts (there is no closing </section> between
  // the two because Pricing renders as a folded div, not its own section).
  const featuresClose = about.indexOf('</section>', featuresIdx);
  assert.ok(featuresClose === -1 || featuresClose > pricingIdx, 'pricing sits inside the features section');
});

test('features is a full document like about', () => {
  // Hero + capabilities section
  assert.match(features, /The stack, shipped as/);
  assert.match(features, /What the stack does/);
  // Full document sections all present
  for (const marker of [...movedSections, 'The stack, reviewed in production', 'Ship the document, not the app']) {
    assert.ok(features.includes(marker), `features should contain: ${marker}`);
  }
  // BEM classes present
  assert.match(features, /capability__grid/);
  // HTMX live-fragment section requests the backend
  assert.match(features, /hx-get="[^"]*\/features\//);
  assert.match(features, /live · from the backend/);
});

test('products is a full document like about', () => {
  // Hero + product lines section
  assert.match(products, /Everything we ship, shipped as/);
  assert.match(products, /The line, end to end/);
  // Full document sections all present
  for (const marker of [...movedSections, 'The stack, reviewed in production', 'Ship the document, not the app']) {
    assert.ok(products.includes(marker), `products should contain: ${marker}`);
  }
  // BEM classes present
  assert.match(products, /product__grid/);
  // HTMX live-fragment section requests the backend
  assert.match(products, /hx-get="[^"]*\/products\//);
  assert.match(products, /live · from the backend/);
});

test('projects is a full document like about', () => {
  // Hero + projects grid section
  assert.match(projects, /Everything we build, shipped as/);
  assert.match(projects, /Projects in this repo/);
  // Repo projects with editions + shared/own feature flags
  assert.match(projects, /Forge POS/);
  assert.match(projects, /Minimal · Solo · Full/);
  assert.match(projects, /django-fusion/);
  assert.match(projects, /shared/);
  assert.match(projects, /own/);
  // Full document sections all present
  for (const marker of [...movedSections, 'The stack, reviewed in production', 'Ship the document, not the app']) {
    assert.ok(projects.includes(marker), `projects should contain: ${marker}`);
  }
  // BEM classes present
  assert.match(projects, /project__grid/);
  assert.match(projects, /project__feature--shared/);
  // HTMX live-fragment section requests the backend
  assert.match(projects, /hx-get="[^"]*\/projects\//);
  assert.match(projects, /live · from the backend/);
});
