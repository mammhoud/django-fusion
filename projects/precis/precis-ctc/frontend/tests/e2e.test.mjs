import assert from 'node:assert/strict';
import test from 'node:test';

const BACKEND_URL = (process.env.E2E_BACKEND_URL || 'http://127.0.0.1:5070').replace(/\/$/, '');
const FRONTEND_URL = (process.env.E2E_FRONTEND_URL || 'http://127.0.0.1:3003').replace(/\/$/, '');
const PUBLIC_CTC_URL = (process.env.E2E_PUBLIC_URL || 'https://ctc-research.com').replace(/\/$/, '');
const REQUEST_TIMEOUT_MS = Number(process.env.E2E_REQUEST_TIMEOUT_MS || 10_000);

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

  await t.test('published course catalog is loaded and JSON-safe', async () => {
    const response = await get(`${BACKEND_URL}/api/courses/?per_page=50`);
    assert.equal(response.status, 200);
    const body = await response.json();
    assert.ok(Array.isArray(body.data), 'course data should be an array');
    assert.ok(body.data.length > 0, 'at least one published course should be present');
    const course = body.data[0];
    assert.match(course.slug, /^[a-z0-9][a-z0-9-]*$/);
    assert.ok(String(course.title).length > 5);
    assert.ok(String(course.short_description).length > 10);

    const detail = await get(`${BACKEND_URL}/api/courses/${encodeURIComponent(course.slug)}/`);
    assert.equal(detail.status, 200);
    const detailBody = await detail.json();
    assert.equal(detailBody.slug, course.slug);
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

  await t.test('frontend serves a live course detail preview', async () => {
    const catalogResponse = await get(`${BACKEND_URL}/api/courses/?per_page=1`);
    assert.equal(catalogResponse.status, 200);
    const catalog = await catalogResponse.json();
    const course = catalog.data[0];
    assert.ok(course?.slug, 'the backend should provide a course slug');
    const response = await get(`${FRONTEND_URL}/courses/${encodeURIComponent(course.slug)}/`);
    assert.equal(response.status, 200);
    const body = await response.text();
    assert.match(body, /<h1\b/i);
    assert.match(body, /course overview|course facts/i);
    assert.match(body, /learning path|syllabus|requirements/i);
  });
});

const PUBLIC_PAGES = [
  '/',
  '/about/',
  '/about/research/',
  '/about/education/',
  '/blog/',
  '/courses/',
  '/pricing/',
  '/features/',
  '/products/',
  '/services/',
  '/team/',
  '/events/',
  '/faq/',
  '/contact/',
  '/privacy/',
  '/documents/',
  '/projects/',
  '/profile/',
];

test('CTC Research public deployment E2E: all public pages return complete HTML', async () => {
  const failures = [];
  for (const path of PUBLIC_PAGES) {
    const response = await get(`${PUBLIC_CTC_URL}${path}`);
    const body = await response.text();
    if (response.status !== 200) {
      failures.push(`${path}: HTTP ${response.status}`);
      continue;
    }
    if (!/<h1\b/i.test(body)) failures.push(`${path}: missing h1`);
    if (/(?:>503<|content is unavailable|catalog is not available|has not published)/i.test(body)) {
      failures.push(`${path}: backend content fallback visible`);
    }
  }
  assert.deepEqual(failures, [], `public page failures: ${failures.join('; ')}`);
});

test('CTC Research public deployment E2E: live course content is reachable', async () => {
  const catalogResponse = await get(`${PUBLIC_CTC_URL}/api/courses/?per_page=100&content_version=2026-08-08-medical-catalog-v2`);
  assert.equal(catalogResponse.status, 200);
  const catalog = await catalogResponse.json();
  assert.ok(Array.isArray(catalog.data));
  assert.ok(catalog.data.length > 0, 'public API should publish at least one course');
  const sampleCourses = catalog.data.slice(0, 6);

  const catalogPage = await get(`${PUBLIC_CTC_URL}/courses/`);
  assert.equal(catalogPage.status, 200);
  const catalogHtml = await catalogPage.text();
  assert.match(catalogHtml, /course|research|evidence/i);

  for (const course of sampleCourses) {
    assert.match(course.slug, /^[a-z0-9][a-z0-9-]*$/);
    assert.ok(String(course.title).length > 5);
    const response = await get(`${PUBLIC_CTC_URL}/api/courses/${encodeURIComponent(course.slug)}/?content_version=2026-08-08-medical-catalog-v2`);
    assert.equal(response.status, 200, `public API detail failed for ${course.slug}`);
    const detail = await response.json();
    assert.equal(detail.slug, course.slug);
    assert.equal(typeof detail.description, 'string');
    assert.ok(Array.isArray(detail.modules), `modules missing for ${course.slug}`);
  }
});

console.log(`E2E targets: backend=${BACKEND_URL}, frontend=${FRONTEND_URL}, public=${PUBLIC_CTC_URL}`);
