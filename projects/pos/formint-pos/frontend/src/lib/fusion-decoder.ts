/**
 * FusionDecoder — TypeScript counterpart of django-fusion's ``FusionCodec``,
 * adapted for the Formint POS pointer shape served by ``/fusion/pointer/``.
 *
 * Usage::
 *
 *     import { fusionDecoder } from '@/lib/fusion-decoder';
 *     const res = await fetch('/fusion/pointer/');
 *     const body = await res.json();
 *     const pointer = fusionDecoder.decodeFragmentPointer(body.encoded);
 *     if (fusionDecoder.shouldRenderFragmentFirst(pointer)) {
 *       // server HTML (/fusion/page/) is the source of truth
 *     }
 */

import type { CodedPayload, FragmentPointer } from './fusion-types';

export class FusionDecodeError extends Error {
  constructor(message: string, public readonly raw?: unknown) {
    super(`FusionDecodeError: ${message}`);
    this.name = 'FusionDecodeError';
  }
}

const SESSION_KEY = 'fusion_render_first';
const CODEC_PREFIX_RE = /^fusion_v(\d+):(.+)$/;

export class FusionDecoder {
  /** In-memory fallback for non-browser environments (node tests, SSR).
   * Kept in sync with the sessionStorage preference when available. */
  private memoryPreference: boolean | undefined;

  initSession(value: boolean): void {
    this.memoryPreference = value;
    if (typeof sessionStorage !== 'undefined') {
      try { sessionStorage.setItem(SESSION_KEY, String(value)); } catch { /* ignore */ }
    }
  }

  getSessionPreference(): boolean | undefined {
    if (this.memoryPreference !== undefined) return this.memoryPreference;
    if (typeof sessionStorage === 'undefined') return undefined;
    try {
      const raw = sessionStorage.getItem(SESSION_KEY);
      if (raw === null) return undefined;
      return raw === 'true';
    } catch { return undefined; }
  }

  clearSession(): void {
    this.memoryPreference = undefined;
    if (typeof sessionStorage !== 'undefined') {
      try { sessionStorage.removeItem(SESSION_KEY); } catch { /* ignore */ }
    }
  }

  /** Session preference wins over the pointer's own flag (mirrors the
   * backend's header → session → default precedence). */
  shouldRenderFragmentFirst(pointer: FragmentPointer): boolean {
    const sessionValue = this.getSessionPreference();
    if (sessionValue !== undefined) return sessionValue;
    return pointer.fusion_render_first === true;
  }

  decode(encoded: string): unknown {
    return this.decodeB64(this.parseCoded(encoded));
  }

  decodeAs<T>(encoded: string): T {
    return this.decode(encoded) as T;
  }

  parseCoded(encoded: string): CodedPayload {
    if (!encoded || typeof encoded !== 'string') {
      throw new FusionDecodeError('Encoded value must be a non-empty string', encoded);
    }
    const match = CODEC_PREFIX_RE.exec(encoded);
    if (!match) {
      throw new FusionDecodeError(
        `Invalid codec prefix — expected "fusion_v<version>:<base64>"`,
        encoded.slice(0, 30),
      );
    }
    return { encoded, version: match[1], b64: match[2] };
  }

  decodeB64(payload: CodedPayload | string): unknown {
    const b64 = typeof payload === 'string' ? payload : payload.b64;
    let jsonStr: string;
    if (typeof Buffer !== 'undefined') {
      // Node/SSR — Buffer accepts URL-safe base64 natively.
      jsonStr = Buffer.from(b64, 'base64').toString('utf-8');
    } else {
      // Browser — map URL-safe alphabet back to standard before atob.
      try {
        jsonStr = atob(b64.replace(/-/g, '+').replace(/_/g, '/'));
      } catch {
        throw new FusionDecodeError('Failed to base64-decode payload', b64);
      }
    }
    try {
      return JSON.parse(jsonStr);
    } catch {
      throw new FusionDecodeError('Failed to JSON-parse decoded payload', jsonStr);
    }
  }

  /** Decode a Formint fragment pointer from its encoded string (or a raw
   * envelope / object). Validates the ``component`` field that the formint
   * sidecar always includes. */
  decodeFragmentPointer(body: string | Record<string, unknown>): FragmentPointer {
    let pointer: unknown;
    if (typeof body === 'string') {
      pointer = this.decode(body);
    } else if ('encoded' in body && typeof body.encoded === 'string') {
      pointer = this.decode(body.encoded);
    } else {
      pointer = body;
    }
    const p = pointer as FragmentPointer;
    if (!p || typeof p !== 'object' || !p.component) {
      throw new FusionDecodeError(
        'Decoded pointer missing required field "component"', pointer);
    }
    return p;
  }
}

/** Global singleton FusionDecoder instance. */
export const fusionDecoder = new FusionDecoder();
export default FusionDecoder;
