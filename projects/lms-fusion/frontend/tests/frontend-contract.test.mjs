import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const baseApi = readFileSync(new URL('../src/store/api/baseApi.ts', import.meta.url), 'utf8');
const coursesPage = readFileSync(new URL('../src/app/courses/page.tsx', import.meta.url), 'utf8');
const sessionSlice = readFileSync(new URL('../src/store/session/sessionSlice.ts', import.meta.url), 'utf8');

for (const key of ['results: T[]', 'count: number', 'next: string | null', 'previous: string | null']) {
  assert.match(baseApi, new RegExp(key.replace(/[\[\]|]/g, '\\$&')));
}

for (const key of ['setCourses(data.data || [])', 'setPagination(data.pagination ||']) {
  assert.match(coursesPage, new RegExp(key.replace(/[()[\\]|]/g, '\\$&')));
}

for (const key of ['hydrateFromRequest', 'hydrateFromCookieHeader', 'selectSessionCookies', 'selectSessionToken']) {
  assert.match(sessionSlice, new RegExp(key));
}
