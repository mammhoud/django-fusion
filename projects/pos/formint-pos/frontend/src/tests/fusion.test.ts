import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { describe, expect, it } from 'vitest';

const page = readFileSync(
  join(dirname(fileURLToPath(import.meta.url)), '..', 'pages', 'fusion.astro'),
  'utf8',
);

describe('Fusion page contract — PageHandler + FusionDecoder', () => {
  it('loads the PageHandler fragment via HTMX (hx-get=/fusion/page/)', () => {
    expect(page).toContain('hx-get="/fusion/page/"');
    expect(page).toContain('hx-target="#page-handler-content"');
    expect(page).toContain('hx-swap="innerHTML"');
  });

  it('fetches the encoded pointer from /fusion/pointer/', () => {
    expect(page).toContain("fetch('/fusion/pointer/'");
  });

  it('uses the FusionDecoder for pointer decoding', () => {
    expect(page).toContain(
      "import { fusionDecoder, FusionDecodeError } from '../lib/fusion-decoder';",
    );
    expect(page).toContain('fusionDecoder.decodeFragmentPointer(body.encoded)');
  });

  it('exposes a session-mode toggle that re-applies the effective strategy', () => {
    expect(page).toContain('id="toggle-mode"');
    expect(page).toContain('fusionDecoder.initSession(next)');
  });

  it('shows the effective strategy derived from pointer + session', () => {
    expect(page).toContain('data-field="strategy"');
    expect(page).toContain('shouldRenderFragmentFirst');
  });
});
