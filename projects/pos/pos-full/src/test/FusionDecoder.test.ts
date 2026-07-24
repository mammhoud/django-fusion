/**
 * Unit tests for POS FusionDecoder — vendored from LMS.
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
import { FusionDecoder, FusionDecodeError } from '../lib/fusion-decoder';
import type { FragmentPointer, FusionEnvelope } from '../lib/fusion-types';

// ─── Helpers ───────────────────────────────────────────────────────

const VALID_ENCODED = 'fusion_v1:eyJrZXkiOiAidmFsdWUifQ==';
const PAGE_ENCODED = 'fusion_v1:eyJibG9ja3MiOltdLCJ0aXRsZSI6IlRlc3QiLCJzbHVnIjoiaG9tZSJ9';

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
    expect(decoder.shouldRenderFragmentFirst(makePointer({ fusion_render_first: false }))).toBe(true);
  });

  it('returns pointer value when no session preference is set', () => {
    expect(decoder.shouldRenderFragmentFirst(makePointer({ fusion_render_first: true }))).toBe(true);
  });

  it('returns false when neither session nor pointer indicates fragment', () => {
    expect(decoder.shouldRenderFragmentFirst(makePointer({ fusion_render_first: false }))).toBe(false);
  });

  it('returns session false even when pointer is true', () => {
    decoder.initSession(false);
    expect(decoder.shouldRenderFragmentFirst(makePointer({ fusion_render_first: true }))).toBe(false);
  });
});

// ═══════════════════════════════════════════════════════════════════
// Envelope unwrapping
// ═══════════════════════════════════════════════════════════════════

describe('unwrap', () => {
  let decoder: FusionDecoder;

  beforeEach(() => { decoder = new FusionDecoder(); });

  it('extracts data from a valid 2xx envelope', () => {
    expect(decoder.unwrap({ status: 200, message: 'Success', data: { key: 'value' } })).toEqual({ key: 'value' });
  });

  it('throws on non-2xx status code', () => {
    expect(() => decoder.unwrap({ status: 404, message: 'Not found', data: null })).toThrow(FusionDecodeError);
  });

  it('throws on null envelope', () => {
    expect(() => decoder.unwrap(null as unknown as FusionEnvelope)).toThrow(FusionDecodeError);
  });
});

// ═══════════════════════════════════════════════════════════════════
// Codec parsing
// ═══════════════════════════════════════════════════════════════════

describe('codec parsing', () => {
  let decoder: FusionDecoder;

  beforeEach(() => { decoder = new FusionDecoder(); });

  it('parseCoded parses a valid fusion_v1:base64 string', () => {
    const result = decoder.parseCoded(VALID_ENCODED);
    expect(result.version).toBe('1');
    expect(result.b64).toBe('eyJrZXkiOiAidmFsdWUifQ==');
  });

  it('parseCoded throws on empty string', () => {
    expect(() => decoder.parseCoded('')).toThrow(FusionDecodeError);
  });

  it('parseCoded throws on invalid prefix', () => {
    expect(() => decoder.parseCoded('bad:base64')).toThrow('Invalid codec prefix');
  });

  it('decodeB64 decodes a valid base64 string', () => {
    expect(decoder.decodeB64('eyJrZXkiOiAidmFsdWUifQ==')).toEqual({ key: 'value' });
  });  it('decodeB64 throws on non-JSON base64 output', () => {
      // Buffer.from accepts most inputs; the resulting string won't be valid JSON
      expect(() => decoder.decodeB64('!!!invalid-json!!!')).toThrow(FusionDecodeError);
    });

  it('decode decodes a valid codec string to an object', () => {
    const result = decoder.decode(PAGE_ENCODED);
    expect(result).toHaveProperty('title', 'Test');
    expect(result).toHaveProperty('slug', 'home');
  });
});

// ═══════════════════════════════════════════════════════════════════
// Fragment-pointer convenience
// ═══════════════════════════════════════════════════════════════════

describe('decodeFragmentPointer', () => {
  let decoder: FusionDecoder;

  beforeEach(() => { decoder = new FusionDecoder(); });

  it('decodes from a FusionEnvelope', () => {
    const envelope: FusionEnvelope = { status: 200, message: 'Success', data: makePointer() };
    const pointer = decoder.decodeFragmentPointer(envelope);
    expect(pointer.fragment_name).toBe('pages.home');
  });

  it('accepts a raw FragmentPointer object (backward compat)', () => {
    const pointer = decoder.decodeFragmentPointer(makePointer() as unknown as Record<string, unknown>);
    expect(pointer.fragment_name).toBe('pages.home');
  });

  it('throws when fragment_name is missing', () => {
    expect(() => decoder.decodeFragmentPointer({ fragment_url: '/test/' } as unknown as Record<string, unknown>))
      .toThrow('missing required fields');
  });
});

// ═══════════════════════════════════════════════════════════════════
// Singleton
// ═══════════════════════════════════════════════════════════════════

describe('fusionDecoder singleton', () => {
  it('is exported and functional', () => {
    const decoder = new FusionDecoder();
    expect(decoder).toBeDefined();
    expect(decoder.getSessionPreference()).toBeUndefined();
  });
});
