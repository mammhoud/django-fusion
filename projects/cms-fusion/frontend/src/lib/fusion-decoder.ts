import type { CodedPayload, FragmentPointer, FusionEnvelope } from './fusion-types';

export class FusionDecodeError extends Error {
  constructor(message: string, public readonly raw?: unknown) {
    super(`FusionDecodeError: ${message}`);
    this.name = 'FusionDecodeError';
  }
}

const SESSION_KEY = 'fusion_render_first';
const CODEC_PREFIX_RE = /^fusion_v(\d+):(.+)$/;

export class FusionDecoder {
  initSession(value: boolean): void {
    if (typeof sessionStorage !== 'undefined') {
      try { sessionStorage.setItem(SESSION_KEY, String(value)); } catch { /* ignore */ }
    }
  }

  getSessionPreference(): boolean | undefined {
    if (typeof sessionStorage === 'undefined') return undefined;
    try {
      const raw = sessionStorage.getItem(SESSION_KEY);
      if (raw === null) return undefined;
      return raw === 'true';
    } catch { return undefined; }
  }

  shouldRenderFragmentFirst(pointer: FragmentPointer): boolean {
    const sessionValue = this.getSessionPreference();
    if (sessionValue !== undefined) return sessionValue;
    return pointer.fusion_render_first === true;
  }

  clearSession(): void {
    if (typeof sessionStorage !== 'undefined') {
      try { sessionStorage.removeItem(SESSION_KEY); } catch { /* ignore */ }
    }
  }

  unwrap<T>(envelope: FusionEnvelope<T>): T {
    if (!envelope || typeof envelope !== 'object') {
      throw new FusionDecodeError('Invalid envelope shape', envelope);
    }
    if (envelope.status < 200 || envelope.status >= 300) {
      throw new FusionDecodeError(
        `Non-success status ${envelope.status}: ${envelope.message}`, envelope);
    }
    return envelope.data;
  }

  decode(encoded: string): unknown {
    const parsed = this.parseCoded(encoded);
    return this.decodeB64(parsed);
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
        encoded.slice(0, 30));
    }
    return { encoded, version: match[1], b64: match[2] };
  }

  decodeB64(payload: CodedPayload | string): unknown {
    const b64 = typeof payload === 'string' ? payload : payload.b64;
    let jsonStr: string;
    try {
      jsonStr = Buffer.from(b64, 'base64').toString('utf-8');
    } catch {
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

  decodeFragmentPointer(
    body: FusionEnvelope | string | Record<string, unknown>,
  ): FragmentPointer {
    let pointer: FragmentPointer;
    if (typeof body === 'string') {
      pointer = this.decodeAs<FragmentPointer>(body);
    } else if ('data' in body && 'status' in body) {
      pointer = this.unwrap(body as FusionEnvelope) as unknown as FragmentPointer;
    } else {
      pointer = body as unknown as FragmentPointer;
    }
    if (!pointer.fragment_name || !pointer.fragment_url) {
      throw new FusionDecodeError(
        'Decoded pointer missing required fields', pointer);
    }
    return pointer;
  }
}

export const fusionDecoder = new FusionDecoder();
export type { CodedPayload, FragmentPointer, FusionEnvelope } from './fusion-types';
export default FusionDecoder;
