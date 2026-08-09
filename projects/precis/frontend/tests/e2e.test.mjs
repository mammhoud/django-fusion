import assert from 'node:assert/strict';
import test from 'node:test';

const BACKEND_URL = (process.env.E2E_BACKEND_URL || 'http://127.0.0.1:5074').replace(/\/$/, '');
const FRONTEND_URL = (process.env.E2E_FRONTEND_URL || 'http://127.0.0.1:3001').replace(/\/$/, '');
const PUBLIC_CTC_URL = (process.env.E2E_PUBLIC_URL || 'https://ctc-research.com').replace(/\/$/, '');
const REQUEST_TIMEOUT_MS = Number(process.env.E2E_REQUEST_TIMEOUT_MS || 10_000);

const MEDICAL_COURSES = {
  'clinical-trial-design-protocol-development': 'Clinical Trial Design & Protocol Development',
  'biostatistics-clinical-research': 'Biostatistics for Clinical Research',
  'systematic-reviews-evidence-synthesis': 'Systematic Reviews & Evidence Synthesis',
  'medical-ai-clinical-data-analytics': 'Medical AI & Clinical Data Analytics',
  'scientific-medical-manuscript-writing': 'Scientific & Medical Manuscript Writing',
  'research-ethics-gcp-publication-integrity': 'Research Ethics, GCP & Publication Integrity',
};

async function get(url) {
  try {
    return await fetch(url, {
      signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
      headers: { Accept: 'text/html,application/json' },
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(
      `Could not reach ${url}. Make sure the current LMS-Fusion Compose stack is running. ${message}`,
      { cause: error },
    );
  }
}

test('LMS-Fusion Compose E2E: backend health and API contract', async (t) => {
  await t.test('backend health endpoint returns operational JSON', async () => {
    const response = await get(`${BACKEND_URL}/health/`);
    assert.equal(response.status, 200);
    const body = await response.json();
    assert.equal(body.status, 'ok');
  });

  await t.test('pages API returns the expected collection shape', async () => {
    const response = await get(`${BACKEND_URL}/apis/pages/`);
    assert.equal(response.status, 200);
    const body = await response.json();
    assert.ok(Array.isArray(body.pages), 'pages should be an array');
    assert.equal(typeof body.total, 'number');
    assert.ok(body.total >= body.pages.length, 'total should include the returned page collection');
  });

  await t.test('fragment ping endpoint remains available for HTMX', async () => {
    const response = await get(`${BACKEND_URL}/fragment/ping/`);
    assert.equal(response.status, 200);
    const body = await response.text();
    assert.ok(body.trim().length > 0, 'fragment response should contain HTML');
  });

  await t.test('medical research course catalog is loaded and JSON-safe', async () => {
    const response = await get(`${BACKEND_URL}/api/courses/?per_page=50`);
    assert.equal(response.status, 200);
    const body = await response.json();
    assert.ok(Array.isArray(body.data), 'course data should be an array');
    assert.ok(body.pagination.total >= 14, 'generic and medical course seed data should be loaded');
    const medical = body.data.find((course) => course.slug === 'medical-ai-clinical-data-analytics');
    assert.ok(medical, 'medical AI course should be present');
    assert.match(medical.short_description, /clinical data/i);

    const detail = await get(`${BACKEND_URL}/api/courses/${medical.slug}/`);
    assert.equal(detail.status, 200);
    const detailBody = await detail.json();
    assert.equal(detailBody.slug, medical.slug);
    assert.equal(typeof detailBody.description, 'string');
    assert.ok(Array.isArray(detailBody.modules), 'course modules should be an array');
  });
});

test('LMS-Fusion Compose E2E: frontend serves the document shell', async (t) => {
  await t.test('frontend root returns HTML', async () => {
    const response = await get(`${FRONTEND_URL}/`);
    assert.equal(response.status, 200);
    const body = await response.text();
    assert.match(body, /<html\b/i);
    assert.match(body, /htmx|fusion-skeleton|structa/i);
  });

  await t.test('frontend serves a generated subpage', async () => {
    const response = await get(`${FRONTEND_URL}/about/`);
    assert.equal(response.status, 200);
    const body = await response.text();
    assert.match(body, /<html\b/i);
    assert.match(body, /<main\b/i);
  });

  await t.test('frontend serves the medical research course catalog preview', async () => {
    const response = await get(`${FRONTEND_URL}/courses/`);
    assert.equal(response.status, 200);
    const body = await response.text();
    assert.match(body, /<html\b/i);
    assert.match(body, /Clinical Trial Design|Medical AI|Research/i);
    assert.match(body, /course catalog|the catalog/i);
  });

  await t.test('frontend serves a medical course detail preview', async () => {
    const response = await get(`${FRONTEND_URL}/courses/medical-ai-clinical-data-analytics/`);
    assert.equal(response.status, 200);
    const body = await response.text();
    assert.match(body, /Medical AI &amp; Clinical Data Analytics|Medical AI/i);
    assert.match(body, /course overview|course facts/i);
    assert.match(body, /Learning objectives|Who it is for|Requirements/i);
  });
});

test('CTC Research public deployment E2E: all seeded course content is reachable', async () => {
  const catalogResponse = await get(`${PUBLIC_CTC_URL}/api/courses/?per_page=100&content_version=2026-08-08-medical-catalog-v2`);
  assert.equal(catalogResponse.status, 200);
  const catalog = await catalogResponse.json();
  assert.ok(catalog.pagination.total >= 14);
  const returned = new Map(catalog.data.map((course) => [course.slug, course.title]));
  for (const [slug, title] of Object.entries(MEDICAL_COURSES)) {
    assert.equal(returned.get(slug), title, `public API missing ${slug}`);
  }

  const catalogPage = await get(`${PUBLIC_CTC_URL}/courses/`);
  assert.equal(catalogPage.status, 200);
  const catalogHtml = await catalogPage.text();
  for (const title of Object.values(MEDICAL_COURSES)) {
    assert.match(catalogHtml, new RegExp(title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/&/g, '&amp;')));
  }

  for (const [slug, title] of Object.entries(MEDICAL_COURSES)) {
    const response = await get(`${PUBLIC_CTC_URL}/courses/${slug}/?content_version=2026-08-08-medical-catalog-v2`);
    assert.equal(response.status, 200, `public detail route failed for ${slug}`);
    const html = await response.text();
    assert.match(html, new RegExp(title.replace(/[.*+?^${}()|[\]\\]/g, '\\$&').replace(/&/g, '&amp;')));
    assert.match(html, /Learning objectives|Who it is for|Requirements/);
    assert.match(html, /Clinical|research|evidence|data|publication|ethics/i);
  }
});

console.log(`E2E targets: backend=${BACKEND_URL}, frontend=${FRONTEND_URL}, public=${PUBLIC_CTC_URL}`);
