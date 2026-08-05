import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { describe, expect, it } from 'vitest';

// Vite rewrites import.meta.url to a /@fs/... URL when running through the
// unified vitest config, so resolve the page path via fileURLToPath.
const page = readFileSync(join(dirname(fileURLToPath(import.meta.url)), '..', 'pages', 'index.astro'), 'utf8');

describe('Formint shell contract', () => {
  it('owns the skeleton and targets a data-only HTMX endpoint', () => {
    expect(page).toContain('data-skeleton-label="Branch summary"');
    expect(page).toContain('hx-get="/htmx/branches/summary/"');
    expect(page).toContain('hx-target="#branch-summary-content"');
    expect(page).toContain('hx-swap="innerHTML"');
  });

  it('requests fusion render-first on first load', () => {
    expect(page).toContain('"X-Fusion-Render-First":"true"');
  });

  it('renders its own skeleton + sr-only loading note', () => {
    expect(page).toContain('variant="branch-summary"');
    expect(page).toContain("import Skeleton from '../components/ui/Skeleton.astro'");
    expect(page).toContain('Loading branch summary');
  });
});
