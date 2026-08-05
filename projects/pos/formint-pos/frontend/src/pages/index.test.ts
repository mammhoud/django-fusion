import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

const page = readFileSync(new URL('./index.astro', import.meta.url), 'utf8');

describe('Formint Phase 1 shell contract', () => {
  it('owns the skeleton and targets a data-only HTMX endpoint', () => {
    expect(page).toContain('data-skeleton="stats-row"');
    expect(page).toContain('hx-get="/htmx/branches/summary/"');
    expect(page).toContain('hx-target="#branch-summary-content"');
  });
});
