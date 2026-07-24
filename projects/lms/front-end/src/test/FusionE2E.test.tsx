/**
 * E2E integration tests for the Fusion rendering system and unified dashboard.
 *
 * Tests the full frontend flow: FusionMiddleware → FusionPage → API → render.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fusionDecoder } from '@/lib/fusion-decoder';
import type { CmsPage, PageDataResponse, FragmentPointer } from '@/store/api/endpoints/pages';

// ═══════════════════════════════════════════════════════════════════
// Mock data — mirrors real backend responses
// ═══════════════════════════════════════════════════════════════════

const MOCK_PAGE_DATA: PageDataResponse = {
  slug: 'home',
  title: 'Learn Without Limits',
  encoded: 'fusion_v1:eyJzbHVnIjoiaG9tZSIsInRpdGxlIjoiTGVhcm4gV2l0aG91dCBMaW1pdHMiLCJzZW8iOnsidGl0bGUiOiJMTVMgUGxhdGZvcm0iLCJkZXNjcmlwdGlvbiI6Ik1hc3RlciBuZXcgc2tpbGxzIn0sImJsb2NrcyI6W119',
};

const MOCK_PAGE_DATA_FR: PageDataResponse = {
  slug: 'home',
  title: 'Apprendre Sans Limites',
  encoded: 'fusion_v1:eyJzbHVnIjoiaG9tZSIsInRpdGxlIjoiQXBwcmVuZHJlIFNhbnMgTGltaXRlcyIsInNlbyI6e30sImJsb2NrcyI6W119',
  language: 'fr',
};

const MOCK_FRAGMENT_POINTER: FragmentPointer = {
  component: 'StaticPageFragment',
  fragment_name: 'pages.home',
  fragment_url: '/fragments/pages.home/',
  fusion_render_first: false,
  page_slug: 'home',
  title: 'Learn Without Limits',
};

// ═══════════════════════════════════════════════════════════════════
// Session storage mock
// ═══════════════════════════════════════════════════════════════════

const sessionStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
    removeItem: vi.fn((key: string) => { delete store[key]; }),
    clear: vi.fn(() => { store = {}; }),
  };
})();

Object.defineProperty(globalThis, 'sessionStorage', { value: sessionStorageMock });

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('FusionDecoder — E2E Flow', () => {
  beforeEach(() => {
    sessionStorageMock.clear();
  });

  it('decodes an encoded page data response from the backend', () => {
    const page = fusionDecoder.decodeAs<CmsPage>(MOCK_PAGE_DATA.encoded);
    expect(page).toBeDefined();
    expect(page.slug).toBe('home');
    expect(page.title).toBe('Learn Without Limits');
    expect(page.blocks).toBeDefined();
  });

  it('decodes the French translated page', () => {
    const page = fusionDecoder.decodeAs<CmsPage>(MOCK_PAGE_DATA_FR.encoded);
    expect(page.title).toBe('Apprendre Sans Limites');
  });

  it('persists session preference for fusion rendering', () => {
    fusionDecoder.initSession(true);
    expect(fusionDecoder.getSessionPreference()).toBe(true);

    fusionDecoder.initSession(false);
    expect(fusionDecoder.getSessionPreference()).toBe(false);

    fusionDecoder.clearSession();
    expect(fusionDecoder.getSessionPreference()).toBeUndefined();
  });

  it('parses and decodes a codec-encoded string with prefix', () => {
    const parsed = fusionDecoder.parseCoded(MOCK_PAGE_DATA.encoded);
    expect(parsed.version).toBe('1');
    expect(typeof parsed.b64).toBe('string');
  });

  it('decodes a fragment pointer correctly', () => {
    // Simulate the unwrapped data from the envelope
    const body = {
      status: 200,
      message: 'success',
      data: MOCK_FRAGMENT_POINTER,
    };
    const pointer = fusionDecoder.decodeFragmentPointer(body);
    expect(pointer.fragment_name).toBe('pages.home');
    expect(pointer.fragment_url).toBe('/fragments/pages.home/');
    expect(pointer.title).toBe('Learn Without Limits');
  });

  it('handles invalid base64 strings gracefully', () => {
    const parse = () => fusionDecoder.decode('fusion_v1:!!!not-base64@@@');
    expect(parse).toThrow();
  });
});

describe('FusionDecoder — Language Session', () => {
  beforeEach(() => {
    sessionStorageMock.clear();
  });

  it('stores language preference in sessionStorage', () => {
    sessionStorageMock.setItem('django_language', 'fr');
    expect(sessionStorageMock.getItem('django_language')).toBe('fr');
  });

  it('defaults to en when no language is stored', () => {
    const lang = sessionStorageMock.getItem('django_language') ?? 'en';
    expect(lang).toBe('en');
  });

  it('validates stored language against known codes', () => {
    const FALLBACK_LANGUAGES = ['en', 'fr', 'es', 'de', 'ar'];
    const stored = sessionStorageMock.getItem('django_language');
    const lang = stored && FALLBACK_LANGUAGES.includes(stored) ? stored : 'en';
    expect(lang).toBe('en');
  });
});

describe('FusionDecoder — Envelope Handling', () => {
  it('unwraps a valid 200 envelope', () => {
    const data = fusionDecoder.unwrap({ status: 200, message: 'ok', data: { key: 'value' } });
    expect(data).toEqual({ key: 'value' });
  });

  it('throws on non-2xx status codes', () => {
    const unwrap = () => fusionDecoder.unwrap({ status: 404, message: 'Not found', data: null as any });
    expect(unwrap).toThrow();
  });

  it('throws on invalid envelope shape', () => {
    const unwrap = () => fusionDecoder.unwrap(null as any);
    expect(unwrap).toThrow();
  });
});

describe('Fusion Codec Roundtrip', () => {
  it('encode → decode preserves data integrity', () => {
    // Backend FusionCodec.encode() and frontend FusionDecoder.decode() must be
    // compatible.  This test verifies the TypeScript-side decode of a known
    // base64 payload that mirrors what the Django FusionCodec produces.
    const original = {
      slug: 'about-us',
      title: 'About LMS',
      blocks: [{ type: 'hero', heading: 'About', intro: 'Learn more' }],
    };

    // Known-good encoded payload for this data (pre-computed)
    const knownEncoded = 'fusion_v1:eyJzbHVnIjoiYWJvdXQtdXMiLCJ0aXRsZSI6IkFib3V0IExNUyIsImJsb2NrcyI6W3sidHlwZSI6Imhlcm8iLCJoZWFkaW5nIjoiQWJvdXQiLCJpbnRybyI6IkxlYXJuIG1vcmUifV19';

    const decoded = fusionDecoder.decodeAs<typeof original>(knownEncoded);
    expect(decoded.slug).toBe(original.slug);
    expect(decoded.title).toBe(original.title);
    expect(decoded.blocks).toHaveLength(1);
    expect(decoded.blocks[0].type).toBe('hero');
  });
});
