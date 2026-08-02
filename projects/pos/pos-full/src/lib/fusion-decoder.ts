/**
 * FusionDecoder — TypeScript counterpart of django-fusion's ``FusionCodec``
 * and ``FusionSessionChecker``.
 *
 * Responsibilities:
 *
 * 1. **Decode** the base64-encoded payload produced by
 *    ``django_fusion.routes.rendering.session.FusionCodec.encode()`` back into
 *    the original typed data.
 * 2. **Session health check** — cache the ``fusion_render_first``
 *    preference in ``sessionStorage`` so the frontend does not re-query
 *    the fragment pointer on every page navigation within the same
 *    browser tab.
 * 3. **Validate** the envelope shape ``{status, message, data}`` and
 *    extract ``data`` safely.
 *
 * This class is designed to be **reusable across all TypeScript projects**
 * (LMS Next.js, POS Tauri apps, dashboard, etc.).  Copy or vendor the file
 * into any TS project that consumes django-fusion data.
 *
 * Usage (POS example)::
 *
 *     import { FusionDecoder } from '@/lib/fusion-decoder';
 *
 *     const decoder = new FusionDecoder();
 *     const data = decoder.decode(encodedString);
 *     const pointer = decoder.decodeFragmentPointer(response.data);
 */

import type { CodedPayload, FragmentPointer, FusionEnvelope } from './fusion-types';

// ─── Errors ────────────────────────────────────────────────────────

export class FusionDecodeError extends Error {
  constructor(message: string, public readonly raw?: unknown) {
    super(`FusionDecodeError: ${message}`);
    this.name = 'FusionDecodeError';
  }
}

export class FusionSessionError extends Error {
  constructor(message: string) {
    super(`FusionSessionError: ${message}`);
    this.name = 'FusionSessionError';
  }
}

// ─── Constants ─────────────────────────────────────────────────────

const SESSION_KEY = 'fusion_render_first';
const CODEC_PREFIX_RE = /^fusion_v(\d+):(.+)$/;

// ─── Decoder class ─────────────────────────────────────────────────

export class FusionDecoder {
  // -------------------------------------------------------------------
  // Session health check — mirrors ``FusionSessionChecker`` on the
  // backend but uses browser ``sessionStorage`` instead of the Django
  // session so the preference survives soft navigations.
  // -------------------------------------------------------------------

  /**
   * Initialise the session preference from an explicit value.
   * Call this once after the first fragment-pointer response so the
   * frontend knows the backend's opinion without re-fetching.
   */
  initSession(value: boolean): void {
    if (typeof sessionStorage !== 'undefined') {
      try {
        sessionStorage.setItem(SESSION_KEY, String(value));
      } catch {
        // sessionStorage unavailable or full — ignore
      }
    }
  }

  /**
   * Return the session-cached ``fusion_render_first`` preference, or
   * ``undefined`` if it has not been initialised yet.
   */
  getSessionPreference(): boolean | undefined {
    if (typeof sessionStorage === 'undefined') return undefined;
    try {
      const raw = sessionStorage.getItem(SESSION_KEY);
      if (raw === null) return undefined;
      return raw === 'true';
    } catch {
      return undefined;
    }
  }

  /**
   * Convenience: given a ``FragmentPointer``, return whether the
   * frontend should render the server fragment first.
   *
   * Priority:
   * 1. Session-cached preference (if set) — the user or health-check
   *    has signalled a persistent preference.
   * 2. The pointer's own ``fusion_render_first`` — the component or
   *    backend setting decides.
   * 3. Default ``false`` — fall back to JSON/React rendering.
   */
  shouldRenderFragmentFirst(pointer: FragmentPointer): boolean {
    const sessionValue = this.getSessionPreference();
    if (sessionValue !== undefined) return sessionValue;
    return pointer.fusion_render_first === true;
  }

  /** Clear the session preference (e.g. when user logs out or toggles settings). */
  clearSession(): void {
    if (typeof sessionStorage !== 'undefined') {
      try {
        sessionStorage.removeItem(SESSION_KEY);
      } catch {
        // ignore
      }
    }
  }

  // -------------------------------------------------------------------
  // Envelope unwrapper — mirrors ``fusion_json_response`` backend
  // -------------------------------------------------------------------

  /**
   * Extract ``data`` from a ``FusionEnvelope``, throwing on non-2xx
   * status codes.
   */
  unwrap<T>(envelope: FusionEnvelope<T>): T {
    if (!envelope || typeof envelope !== 'object') {
      throw new FusionDecodeError('Invalid envelope shape', envelope);
    }
    if (envelope.status < 200 || envelope.status >= 300) {
      throw new FusionDecodeError(
        `Non-success status ${envelope.status}: ${envelope.message}`,
        envelope,
      );
    }
    return envelope.data;
  }

  // -------------------------------------------------------------------
  // Codec decoder — mirrors ``FusionCodec.decode()`` on the backend
  // -------------------------------------------------------------------

  /**
   * Parse a codec-encoded string ``fusion_v<version>:<base64>`` and
   * return the decoded object.
   *
   * Example::
   *
   *     const decoder = new FusionDecoder();
   *     const data = decoder.decode('fusion_v1:eyJrZXkiOiAidmFsdWUifQ==');
   *     // -> { key: "value" }
   */
  decode(encoded: string): unknown {
    const parsed = this.parseCoded(encoded);
    return this.decodeB64(parsed);
  }

  /**
   * Typed variant of ``decode()`` that casts the result.
   *
   * Example::
   *
   *     const pointer = decoder.decodeAs<FragmentPointer>(encodedStr);
   *     console.log(pointer.fragment_name);
   */
  decodeAs<T>(encoded: string): T {
    return this.decode(encoded) as T;
  }

  /**
   * Parse the ``fusion_v<version>:<base64>`` format and return
   * structured parts.  Throws ``FusionDecodeError`` on invalid input.
   */
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
    return {
      encoded,
      version: match[1],
      b64: match[2],
    };
  }

  /**
   * Base64-decode a ``CodedPayload`` (or its ``b64`` string) and parse
   * the JSON payload.
   */
  decodeB64(payload: CodedPayload | string): unknown {
    const b64 = typeof payload === 'string' ? payload : payload.b64;

    let jsonStr: string;
    try {
      // Node.js Buffer-compatible
      jsonStr = Buffer.from(b64, 'base64').toString('utf-8');
    } catch {
      try {
        // Browser fallback — urlsafe base64 uses - and _ instead of + and /
        jsonStr = atob(b64.replace(/-/g, '+').replace(/_/g, '/'));
      } catch {
        throw new FusionDecodeError('Failed to base64-decode payload', b64);
      }
    }

    try {
      return JSON.parse(jsonStr);
    } catch (cause) {
      throw new FusionDecodeError('Failed to JSON-parse decoded payload', jsonStr);
    }
  }

  // -------------------------------------------------------------------
  // Fragment-pointer convenience
  // -------------------------------------------------------------------

  /**
   * High-level convenience: given the raw body of a fragment-pointer
   * response (either a ``FusionEnvelope`` or a codec-encoded string),
   * return the decoded ``FragmentPointer``.
   */
  decodeFragmentPointer(
    body: FusionEnvelope | string | Record<string, unknown>,
  ): FragmentPointer {
    let pointer: FragmentPointer;

    if (typeof body === 'string') {
      // Codec-encoded string — decode then cast
      pointer = this.decodeAs<FragmentPointer>(body);
    } else if ('data' in body && 'status' in body) {
      // Envelope — unwrap
      pointer = this.unwrap(body as FusionEnvelope) as unknown as FragmentPointer;
    } else {
      // Assume it's already a flat FragmentPointer (backward compat)
      pointer = body as unknown as FragmentPointer;
    }

    // Validate required fields
    if (!pointer.fragment_name || !pointer.fragment_url) {
      throw new FusionDecodeError(
        'Decoded pointer is missing required fields (fragment_name, fragment_url)',
        pointer,
      );
    }

    return pointer;
  }
}

// --- Singleton export for convenience ---

/** Global singleton ``FusionDecoder`` instance. */
export const fusionDecoder = new FusionDecoder();

// Re-export types for backward compatibility
export type { CodedPayload, FragmentPointer, FusionEnvelope } from './fusion-types';

export default FusionDecoder;
