/**
 * Unit tests for POS Solo FusionDecoder.
 *
 * Covers:
 * - Session management (initSession, getSessionPreference, clearSession)
 * - shouldRenderFragmentFirst priority logic
 * - Envelope unwrapping (unwrap)
 * - Codec parsing (parseCoded, decodeB64, decode, decodeAs)
 * - Fragment-pointer convenience (decodeFragmentPointer)
 */
import { describe, it, expect, beforeEach } from 'vitest';
import { FusionDecoder, FusionDecodeError } from '../lib/fusion-decoder';
import type { FragmentPointer, FusionEnvelope } from '../lib/fusion-types';

const PAGE_ENCODED = 'fusion_v1:eyJibG9ja3MiOltdLCJ0aXRsZSI6IlRlc3QiLCJzbHVnIjoiaG9tZSJ9';

describe('FusionDecoder session management', () => {
  let decoder: FusionDecoder;
  beforeEach(() => { decoder = new FusionDecoder(); sessionStorage.clear(); });

  it('initSession stores the preference', () => {
    decoder.initSession(true);
    expect(sessionStorage.getItem('fusion_render_first')).toBe('true');
  });

  it('getSessionPreference returns undefined initially', () => {
    expect(decoder.getSessionPreference()).toBeUndefined();
  });

  it('getSessionPreference returns stored boolean values', () => {
    decoder.initSession(true);
    expect(decoder.getSessionPreference()).toBe(true);
    decoder.initSession(false);
    expect(decoder.getSessionPreference()).toBe(false);
  });

  it('clearSession removes the stored preference', () => {
    decoder.initSession(true);
    decoder.clearSession();
    expect(decoder.getSessionPreference()).toBeUndefined();
  });
});

describe('shouldRenderFragmentFirst', () => {
  let decoder: FusionDecoder;
  beforeEach(() => { decoder = new FusionDecoder(); sessionStorage.clear(); });

  it('returns session preference over pointer', () => {
    decoder.initSession(true);
    expect(decoder.shouldRenderFragmentFirst({ fragment_name: 'x', fragment_url: '/', fusion_render_first: false } as FragmentPointer)).toBe(true);
  });

  it('returns pointer value when no session', () => {
    expect(decoder.shouldRenderFragmentFirst({ fragment_name: 'x', fragment_url: '/', fusion_render_first: true } as FragmentPointer)).toBe(true);
  });

  it('returns false as default', () => {
    expect(decoder.shouldRenderFragmentFirst({ fragment_name: 'x', fragment_url: '/', fusion_render_first: false } as FragmentPointer)).toBe(false);
  });
});

describe('unwrap', () => {
  let decoder: FusionDecoder;
  beforeEach(() => { decoder = new FusionDecoder(); });

  it('extracts data from valid envelope', () => {
    expect(decoder.unwrap({ status: 200, message: 'OK', data: { key: 'val' } })).toEqual({ key: 'val' });
  });

  it('throws on non-2xx', () => {
    expect(() => decoder.unwrap({ status: 500, message: 'Error', data: null })).toThrow('Non-success status');
  });
});

describe('codec parsing', () => {
  let decoder: FusionDecoder;
  beforeEach(() => { decoder = new FusionDecoder(); });

  it('parseCoded parses valid string', () => {
    const r = decoder.parseCoded(PAGE_ENCODED);
    expect(r.version).toBe('1');
  });

  it('parseCoded throws on invalid input', () => {
    expect(() => decoder.parseCoded('bad:input')).toThrow('Invalid codec prefix');
  });

  it('decode decodes valid codec string', () => {
    const r = decoder.decode(PAGE_ENCODED);
    expect(r).toHaveProperty('title', 'Test');
    expect(r).toHaveProperty('slug', 'home');
  });

  it('decodeB64 decodes valid base64', () => {
    expect(decoder.decodeB64('eyJrZXkiOiAidmFsdWUifQ==')).toEqual({ key: 'value' });
  });  it('decodeB64 throws on non-JSON base64 output', () => {
      expect(() => decoder.decodeB64('!!!invalid-json!!!')).toThrow(FusionDecodeError);
    });
});

describe('decodeFragmentPointer', () => {
  let decoder: FusionDecoder;
  beforeEach(() => { decoder = new FusionDecoder(); });

  it('decodes from envelope', () => {
    const env: FusionEnvelope = { status: 200, message: 'OK', data: { fragment_name: 'x', fragment_url: '/x/', fusion_render_first: false } };
    expect(decoder.decodeFragmentPointer(env).fragment_name).toBe('x');
  });

  it('throws when fragment_name missing', () => {
    expect(() => decoder.decodeFragmentPointer({ fragment_url: '/x/' } as unknown as Record<string, unknown>)).toThrow('missing required fields');
  });
});
