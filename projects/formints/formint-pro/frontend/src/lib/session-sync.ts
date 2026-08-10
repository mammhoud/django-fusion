/**
 * FusionSessionSync — cross-tab sync for the session-mode preference.
 *
 * The fusion render-mode preference (``fusion_render_first``) is cached
 * per-tab in ``sessionStorage`` by ``FusionDecoder``. When an operator
 * toggles it on the ``/fusion/`` page in one tab, the other tabs of the
 * same origin would otherwise stay stale. This module broadcasts local
 * changes to every other tab and applies remote ones, so all tabs agree
 * on the effective strategy without a reload.
 *
 * Transport (dual, with timestamp dedupe):
 *
 * 1. **BroadcastChannel** — primary, typed, instant (modern browsers).
 * 2. **localStorage mirror + ``storage`` events** — fallback for browsers
 *    without ``BroadcastChannel``; ``storage`` events fire in *other*
 *    tabs whenever the shared mirror key is written.
 *
 * Both transports carry the same monotonically-increasing timestamp, so a
 * change delivered by both paths is applied exactly once (last-writer-wins).
 * The module only transports the preference — callers update the
 * ``FusionDecoder`` (and the server, via ``/fusion/session-mode/``)
 * themselves; see ``src/pages/fusion.astro``.
 */

export interface SessionSyncMessage {
  type: 'fusion-render-mode';
  /** ``true``/``false`` preference, or ``null`` for "cleared → default". */
  value: boolean | null;
  /** Monotonic timestamp used for dedupe / last-writer-wins. */
  at: number;
}

/** Shared channel name for all tabs of this origin. */
export const SESSION_SYNC_CHANNEL = 'formint:fusion-session';
/** localStorage mirror key (fallback transport + cross-tab catch-up). */
export const SESSION_SYNC_MIRROR_KEY = 'formint:fusion-render-mode:sync';

type OnChange = (value: boolean | null) => void;

function parseMirror(raw: string): { at: number; value: boolean | null } | null {
  const sep = raw.indexOf(':');
  if (sep === -1) return null;
  const at = Number(raw.slice(0, sep));
  if (!Number.isFinite(at)) return null;
  const token = raw.slice(sep + 1);
  if (token === 'null') return { at, value: null };
  if (token === 'true' || token === 'false') return { at, value: token === 'true' };
  return null;
}

export class FusionSessionSync {
  private channel: BroadcastChannel | null = null;
  private storageHandler: ((event: StorageEvent) => void) | null = null;
  private onChange: OnChange | null = null;
  /** Highest timestamp applied (from either transport). */
  private lastAppliedAt = 0;
  /** Last timestamp sent, kept monotonic across rapid toggles. */
  private lastSentAt = 0;
  /** True after dispose() — publish/subscribe become no-ops. */
  private disposed = false;

  constructor(
    private readonly channelName: string = SESSION_SYNC_CHANNEL,
  ) {}

  /** Start listening for preference changes made in other tabs. */
  subscribe(onChange: OnChange): void {
    if (this.disposed) return;
    this.onChange = onChange;
    this.ensureChannel();

    if (typeof window !== 'undefined') {
      this.storageHandler = (event: StorageEvent) => {
        if (event.key !== SESSION_SYNC_MIRROR_KEY) return;
        if (typeof event.newValue !== 'string') return;
        const parsed = parseMirror(event.newValue);
        if (parsed) this.apply(parsed.value, parsed.at);
      };
      window.addEventListener('storage', this.storageHandler);
    }
  }

  /** Broadcast a local preference change to every other tab. */
  publish(value: boolean | null): void {
    if (this.disposed) return;
    this.ensureChannel();
    const at = this.nextAt();
    const message: SessionSyncMessage = {
      type: 'fusion-render-mode',
      value,
      at,
    };
    if (this.channel) {
      try {
        this.channel.postMessage(message);
      } catch {
        /* channel closed mid-flight — mirror still covers other tabs */
      }
    }
    // Mirror write fires ``storage`` events in other tabs (the fallback
    // transport). Late-loading tabs catch up from the server instead
    // (seedSessionFromServer in fusion.astro) — the mirror is transport
    // only, not a read-back source.
    if (typeof localStorage !== 'undefined') {
      try {
        localStorage.setItem(
          SESSION_SYNC_MIRROR_KEY,
          `${at}:${value === null ? 'null' : String(value)}`,
        );
      } catch {
        /* private-mode storage — ignore */
      }
    }
  }

  /** Lazily create the BroadcastChannel (safe when not yet subscribed). */
  private ensureChannel(): void {
    if (this.channel || typeof BroadcastChannel === 'undefined') return;
    try {
      this.channel = new BroadcastChannel(this.channelName);
      this.channel.addEventListener('message', (event: MessageEvent) => {
        this.applyMessage(event.data);
      });
    } catch {
      this.channel = null; // fall back to storage events
    }
  }

  /** Remove listeners and close the channel (page teardown / tests). */
  dispose(): void {
    this.disposed = true;
    if (this.channel) {
      try { this.channel.close(); } catch { /* ignore */ }
      this.channel = null;
    }
    if (this.storageHandler && typeof window !== 'undefined') {
      window.removeEventListener('storage', this.storageHandler);
      this.storageHandler = null;
    }
    this.onChange = null;
    // Reset so a reused instance starts from a clean slate.
    this.lastAppliedAt = 0;
    this.lastSentAt = 0;
  }

  private applyMessage(data: unknown): void {
    if (!data || typeof data !== 'object') return;
    const msg = data as SessionSyncMessage;
    if (msg.type !== 'fusion-render-mode') return;
    const valueOk = msg.value === null || typeof msg.value === 'boolean';
    if (typeof msg.at !== 'number' || !valueOk) {
      return;
    }
    this.apply(msg.value, msg.at);
  }

  private apply(value: boolean | null, at: number): void {
    // Stale or already-applied (both transports deliver the same change).
    if (at <= this.lastAppliedAt) return;
    this.lastAppliedAt = at;
    this.onChange?.(value);
  }

  private nextAt(): number {
    // Monotonic even when Date.now() collides across rapid toggles.
    this.lastSentAt = Math.max(Date.now(), this.lastSentAt + 1);
    return this.lastSentAt;
  }
}

/** Global singleton (one channel per page instance). */
export const fusionSessionSync = new FusionSessionSync();
