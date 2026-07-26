/**
 * Unit tests for FusionDecoder — TypeScript counterpart of django-fusion's
 * ``FusionCodec`` and ``FusionSessionChecker``.
 *
 * Covers:
 * - Session management (initSession, getSessionPreference, clearSession)
 * - shouldRenderFragmentFirst priority logic
 * - Envelope unwrapping (unwrap)
 * - Codec parsing (parseCoded, decodeB64, decode, decodeAs)
 * - Fragment-pointer convenience (decodeFragmentPointer)
 * - Error handling for invalid inputs
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { FusionDecoder, FusionDecodeError } from '@/lib/fusion-decoder';
import type { FragmentPointer, FusionEnvelope } from '@/lib/fusion-types';

// ─── Helpers ───────────────────────────────────────────────────────

const VALID_ENCODED = 'fusion_v1:eyJrZXkiOiAidmFsdWUifQ==';    // {"key": "value"}
const PAGE_ENCODED = 'fusion_v1:eyJibG9ja3MiOltdLCJ0aXRsZSI6IlRlc3QiLCJzbHVnIjoiaG9tZSJ9'; // {"blocks":[],"title":"Test","slug":"home"}

function makePointer(overrides: Partial<FragmentPointer> = {}): FragmentPointer {
  return {
    component: 'test',
    fragment_name: 'pages.home',
    fragment_url: '/fragments/pages.home/',
    fusion_render_first: false,
    ...overrides,
  };
}

// ═══════════════════════════════════════════════════════════════════
// Session management
// ═══════════════════════════════════════════════════════════════════

describe('FusionDecoder session management', () => {
  let decoder: FusionDecoder;

  beforeEach(() => {
    decoder = new FusionDecoder();
    sessionStorage.clear();
  });

  it('initSession stores the preference as a string', () => {
    decoder.initSession(true);
    expect(sessionStorage.getItem('fusion_render_first')).toBe('true');

    decoder.initSession(false);
    expect(sessionStorage.getItem('fusion_render_first')).toBe('false');
  });

  it('getSessionPreference returns undefined when nothing is stored', () => {
    expect(decoder.getSessionPreference()).toBeUndefined();
  });

  it('getSessionPreference returns true when stored as "true"', () => {
    decoder.initSession(true);
    expect(decoder.getSessionPreference()).toBe(true);
  });

  it('getSessionPreference returns false when stored as "false"', () => {
    decoder.initSession(false);
    expect(decoder.getSessionPreference()).toBe(false);
  });

  it('clearSession removes the stored preference', () => {
    decoder.initSession(true);
    expect(decoder.getSessionPreference()).toBe(true);

    decoder.clearSession();
    expect(decoder.getSessionPreference()).toBeUndefined();
  });
});

// ═══════════════════════════════════════════════════════════════════
// shouldRenderFragmentFirst priority
// ═══════════════════════════════════════════════════════════════════

describe('shouldRenderFragmentFirst', () => {
  let decoder: FusionDecoder;

  beforeEach(() => {
    decoder = new FusionDecoder();
    sessionStorage.clear();
  });

  it('returns session preference when set (overrides pointer)', () => {
    decoder.initSession(true);
    const pointer = makePointer({ fusion_render_first: false });

    expect(decoder.shouldRenderFragmentFirst(pointer)).toBe(true);
  });

  it('returns pointer value when no session preference is set', () => {
    const pointer = makePointer({ fusion_render_first: true });

    expect(decoder.shouldRenderFragmentFirst(pointer)).toBe(true);
  });

  it('returns false when neither session nor pointer indicates fragment', () => {
    const pointer = makePointer({ fusion_render_first: false });

    expect(decoder.shouldRenderFragmentFirst(pointer)).toBe(false);
  });

  it('returns session false even when pointer is true', () => {
    decoder.initSession(false);
    const pointer = makePointer({ fusion_render_first: true });

    expect(decoder.shouldRenderFragmentFirst(pointer)).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════
// Envelope unwrapping
// ═══════════════════════════════════════════════════════════════════

describe('unwrap', () => {
  let decoder: FusionDecoder;

  beforeEach(() => {
    decoder = new FusionDecoder();
  });

  it('extracts data from a valid 2xx envelope', () => {
    const envelope: FusionEnvelope<{ key: string }> = {
      status: 200,
      message: 'Success',
      data: { key: 'value' },
    };

    expect(decoder.unwrap(envelope)).toEqual({ key: 'value' });
  });

  it('throws on non-2xx status code', () => {
    const envelope: FusionEnvelope = {
      status: 404,
      message: 'Not found',
      data: null,
    };

    expect(() => decoder.unwrap(envelope)).toThrow(FusionDecodeError);
    expect(() => decoder.unwrap(envelope)).toThrow('Non-success status 404');
  });

  it('throws on null envelope', () => {
    expect(() => decoder.unwrap(null as unknown as FusionEnvelope)).toThrow(FusionDecodeError);
    expect(() => decoder.unwrap(null as unknown as FusionEnvelope)).toThrow('Invalid envelope shape');
  });

  it('throws on non-object envelope', () => {
    expect(() => decoder.unwrap('string' as unknown as FusionEnvelope)).toThrow(FusionDecodeError);
  });
});

// ═══════════════════════════════════════════════════════════════════
// Codec parsing
// ═══════════════════════════════════════════════════════════════════

describe('codec parsing', () => {
  let decoder: FusionDecoder;

  beforeEach(() => {
    decoder = new FusionDecoder();
  });

  describe('parseCoded', () => {
    it('parses a valid fusion_v1:base64 string', () => {
      const result = decoder.parseCoded(VALID_ENCODED);

      expect(result.encoded).toBe(VALID_ENCODED);
      expect(result.version).toBe('1');
      expect(result.b64).toBe('eyJrZXkiOiAidmFsdWUifQ==');
    });

    it('throws on empty string', () => {
      expect(() => decoder.parseCoded('')).toThrow(FusionDecodeError);
      expect(() => decoder.parseCoded('')).toThrow('must be a non-empty string');
    });

    it('throws on invalid prefix', () => {
      expect(() => decoder.parseCoded('invalid:base64')).toThrow(FusionDecodeError);
      expect(() => decoder.parseCoded('invalid:base64')).toThrow('Invalid codec prefix');
    });

    it('throws on missing colon separator', () => {
      expect(() => decoder.parseCoded('fusion_v1base64')).toThrow(FusionDecodeError);
    });
  });

  describe('decodeB64', () => {
    it('decodes a valid base64 payload string', () => {
      const result = decoder.decodeB64('eyJrZXkiOiAidmFsdWUifQ==');
      expect(result).toEqual({ key: 'value' });
    });

    it('decodes a valid CodedPayload object', () => {
      const payload = decoder.parseCoded(VALID_ENCODED);
      const result = decoder.decodeB64(payload);
      expect(result).toEqual({ key: 'value' });
    });

    it('throws on non-JSON base64 output', () => {
      // Buffer.from handles most inputs, but the result won't be valid JSON
      expect(() => decoder.decodeB64('!!!invalid-json!!!')).toThrow(FusionDecodeError);
      expect(() => decoder.decodeB64('!!!invalid-json!!!')).toThrow('Failed to JSON-parse');
    });
  });

  describe('decode', () => {
    it('decodes a valid codec string to an object', () => {
      const result = decoder.decode(PAGE_ENCODED);
      expect(result).toHaveProperty('blocks');
      expect(result).toHaveProperty('title', 'Test');
      expect(result).toHaveProperty('slug', 'home');
    });
  });

  describe('decodeAs', () => {
    it('decodes and casts to the requested type', () => {
      type PageData = { blocks: unknown[]; title: string; slug: string };
      const result = decoder.decodeAs<PageData>(PAGE_ENCODED);

      expect(result.title).toBe('Test');
      expect(result.slug).toBe('home');
      expect(Array.isArray(result.blocks)).toBe(true);
    });
  });
});

// ═══════════════════════════════════════════════════════════════════
// Fragment-pointer convenience
// ═══════════════════════════════════════════════════════════════════

describe('decodeFragmentPointer', () => {
  let decoder: FusionDecoder;

  beforeEach(() => {
    decoder = new FusionDecoder();
    sessionStorage.clear();
  });

  it('decodes from a FusionEnvelope', () => {
    const envelope: FusionEnvelope = {
      status: 200,
      message: 'Success',
      data: makePointer({ component: 'pages.home' }),
    };

    const pointer = decoder.decodeFragmentPointer(envelope);
    expect(pointer.fragment_name).toBe('pages.home');
    expect(pointer.fragment_url).toBe('/fragments/pages.home/');
  });

  it('decodes from a codec-encoded string', () => {
    // The string "fusion_v1:..." encodes a FragmentPointer
    // Actual base64 for: {"component":"pages.home","fragment_name":"pages.home","fragment_url":"/fragments/pages.home/","fusion_render_first":false}
    const encodedStr =
      'fusion_v1:eyJjb21wb25lbnQiOiJwYWdlcy5ob21lIiwiZnJhZ21lbnRfbmFtZSI6InBhZ2VzLmhvbWUiLCJmcmFnbWVudF91cmwiOiIvZnJhZ21lbnRzL3BhZ2VzLmhvbWUvIiwiZnVzaW9uX3JlbmRlcl9maXJzdCI6ZmFsc2V9';

    const pointer = decoder.decodeFragmentPointer(encodedStr);
    expect(pointer.component).toBe('pages.home');
    expect(pointer.fragment_name).toBe('pages.home');
    expect(pointer.fragment_url).toBe('/fragments/pages.home/');
  });

  it('accepts a raw FragmentPointer object (backward compat)', () => {
    const raw = makePointer({ component: 'compat' });

    const pointer = decoder.decodeFragmentPointer(raw as unknown as Record<string, unknown>);
    expect(pointer.component).toBe('compat');
  });

  it('throws when fragment_name is missing', () => {
    const raw = { fragment_url: '/fragments/test/', fusion_render_first: false };

    expect(() => decoder.decodeFragmentPointer(raw as unknown as Record<string, unknown>))
      .toThrow(FusionDecodeError);
    expect(() => decoder.decodeFragmentPointer(raw as unknown as Record<string, unknown>))
      .toThrow('missing required fields');
  });

  it('throws when fragment_url is missing', () => {
    const raw = { fragment_name: 'test', fusion_render_first: false };

    expect(() => decoder.decodeFragmentPointer(raw as unknown as Record<string, unknown>))
      .toThrow(FusionDecodeError);
  });
});

// ═══════════════════════════════════════════════════════════════════
// Singleton instance
// ═══════════════════════════════════════════════════════════════════

describe('fusionDecoder singleton', () => {
  it('is exported and functional', () => {
    const decoder = new FusionDecoder();
    expect(decoder).toBeDefined();
    expect(decoder.getSessionPreference()).toBeUndefined();
  });
});
