import { describe, expect, it } from 'vitest';

import { FusionDecoder, FusionDecodeError } from './fusion-decoder';

/**
 * Real payload produced by the formint sidecar's ``FusionCodec.encode``:
 *   {"component": "formint.branch_summary", "fusion_render_first": true, "htmx": false}
 */
const REAL_ENCODED_POINTER =
  'fusion_v1:eyJjb21wb25lbnQiOiJmb3JtaW50LmJyYW5jaF9zdW1tYXJ5IiwiZnVzaW9uX3JlbmRlcl9maXJzdCI6dHJ1ZSwiaHRteCI6ZmFsc2V9';

describe('FusionDecoder — Formint pointer round-trip', () => {
  const decoder = new FusionDecoder();

  it('decodes a real backend-encoded fragment pointer', () => {
    const pointer = decoder.decodeFragmentPointer(REAL_ENCODED_POINTER);
    expect(pointer.component).toBe('formint.branch_summary');
    expect(pointer.fusion_render_first).toBe(true);
    expect(pointer.htmx).toBe(false);
  });

  it('decodes a PointerResponse body via its encoded field', () => {
    const pointer = decoder.decodeFragmentPointer({ encoded: REAL_ENCODED_POINTER });
    expect(pointer.component).toBe('formint.branch_summary');
  });

  it('accepts an already-decoded pointer object', () => {
    const pointer = decoder.decodeFragmentPointer({
      component: 'formint.tables.products',
      fusion_render_first: false,
    });
    expect(pointer.component).toBe('formint.tables.products');
  });

  it('rejects a decoded object missing the component field', () => {
    expect(() => decoder.decodeFragmentPointer({ foo: 'bar' })).toThrow(FusionDecodeError);
    expect(() => decoder.decodeFragmentPointer({ foo: 'bar' })).toThrow(/component/);
  });

  it('rejects a payload with an invalid codec prefix', () => {
    expect(() => decoder.decode('fusion_v1-base64-junk')).toThrow(FusionDecodeError);
    expect(() => decoder.parseCoded('nope')).toThrow(/fusion_v<version>/);
  });

  it('rejects malformed base64', () => {
    expect(() => decoder.decode('fusion_v1:!!!not-base64@@@')).toThrow(FusionDecodeError);
  });

  it('parses the codec metadata (version + b64)', () => {
    const parsed = decoder.parseCoded(REAL_ENCODED_POINTER);
    expect(parsed.version).toBe('1');
    expect(parsed.b64).toBeTruthy();
    expect(parsed.encoded).toBe(REAL_ENCODED_POINTER);
  });
});

describe('FusionDecoder — session preference', () => {
  const decoder = new FusionDecoder();

  it('returns undefined session preference when unset', () => {
    decoder.clearSession();
    expect(decoder.getSessionPreference()).toBeUndefined();
  });

  it('stores and reads the session preference', () => {
    decoder.initSession(false);
    expect(decoder.getSessionPreference()).toBe(false);
    decoder.clearSession();
  });

  it('session preference wins over the pointer flag', () => {
    decoder.clearSession();
    const pointer = decoder.decodeFragmentPointer(REAL_ENCODED_POINTER);
    // pointer says render-first (true)
    expect(pointer.fusion_render_first).toBe(true);
    expect(decoder.shouldRenderFragmentFirst(pointer)).toBe(true);

    // session says data-api → wins
    decoder.initSession(false);
    expect(decoder.shouldRenderFragmentFirst(pointer)).toBe(false);
    decoder.clearSession();
  });
});
