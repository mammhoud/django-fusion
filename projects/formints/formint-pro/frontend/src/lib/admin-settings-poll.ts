/**
 * AdminSettingsWatcher — propagate Unfold admin preference saves to open tabs.
 *
 * The session-mode preference has three writers: the operator toggle on
 * `/fusion/` (per-session), the Unfold admin settings page
 * (`UserSettings.fusion_render_mode` — per-operator, persisted), and the
 * `FormintSessionModeMiddleware` that seeds each session from the admin row.
 *
 * Client-side cross-tab transports (`BroadcastChannel` / `storage` events,
 * see `session-sync.ts`) are origin-scoped, so an admin save made on the
 * server origin (`:8767`) can never reach tabs on the Astro origin
 * (`:4321`) directly. Propagation must go through the server: this watcher
 * polls `GET /fusion/session-mode/`, which reports the **DB-truth** admin
 * preference (``admin_preference``) plus a per-row version
 * (``admin_version``) independent of the session cache, and fires
 * ``onChange`` whenever that preference actually changes. The page then
 * applies it (persist to the session, update the FusionDecoder, publish via
 * `FusionSessionSync`) so every open tab converges.
 *
 * Why the DB truth and not the session value: the middleware seeds a session
 * once (`_fusion_settings_synced`), so if another admin edits an operator's
 * row after their session was seeded, the session cache is stale while the
 * row holds the new value. The watcher compares the row value against the
 * session cache on first sight and applies the row (source of truth).
 *
 * The watcher is transport- and page-agnostic — callers decide what
 * "applying" means (see `src/pages/fusion.astro`).
 */

export interface AdminSettingsState {
  /** Session cache of the preference (null when unset / no explicit value). */
  session_preference: boolean | null;
  /**
   * DB-truth preference mapped from `UserSettings.fusion_render_mode`:
   * `fusion` → `true`, `data` → `false`, `default` → `null`.
   * `null` when the authenticated user has no settings row.
   */
  admin_preference: boolean | null;
  /**
   * Monotonic per-row version (derived from `updated_at`).
   * `null` when no settings row exists — lets callers distinguish
   * "row says default" (`admin_version` non-null, preference null) from
   * "no admin source at all" (both null).
   */
  admin_version: number | null;
}

export interface AdminSettingsWatcherOptions {
  /** Fetch the current state. Defaults to `GET /fusion/session-mode/`. */
  fetchState?: () => Promise<AdminSettingsState | null>;
  /** Called when the admin preference changed and must be applied. */
  onChange?: (preference: boolean | null) => void;
  /** Poll interval in ms (default 25000). */
  intervalMs?: number;
  /** Re-check on `visibilitychange` (tab becomes visible) and `focus`. */
  visibilityAware?: boolean;
}

export class AdminSettingsWatcher {
  private readonly intervalMs: number;
  private readonly fetchState: () => Promise<AdminSettingsState | null>;
  private readonly onChange?: (preference: boolean | null) => void;
  private readonly visibilityAware: boolean;

  private timer: ReturnType<typeof setInterval> | null = null;
  private visibilityHandler: (() => void) | null = null;
  private focusHandler: (() => void) | null = null;

  /** true once a settings row has been seen (baseline recorded). */
  private baseline = false;
  /** Last observed admin preference (used for change detection). */
  private lastPref: boolean | null = null;
  /** Last observed row version. */
  private lastVersion: number | null = null;
  /** Guards against overlapping in-flight checks (focus + interval). */
  private checking = false;
  private disposed = false;

  constructor(options: AdminSettingsWatcherOptions = {}) {
    this.intervalMs = options.intervalMs ?? 25_000;
    this.visibilityAware = options.visibilityAware ?? true;
    this.onChange = options.onChange;
    this.fetchState =
      options.fetchState ??
      (async () => {
        const res = await fetch('/fusion/session-mode/', {
          headers: { 'Accept': 'application/json' },
        });
        if (!res.ok) return null;
        return (await res.json()) as AdminSettingsState;
      });
  }

  /** Start polling + visibility/focus re-checks, with an immediate check. */
  start(): void {
    if (this.disposed) return;
    this.attachEventHandlers();
    void this.checkNow();
    this.timer = setInterval(() => void this.checkNow(), this.intervalMs);
  }

  /** Stop polling and remove event listeners (page teardown / tests). */
  stop(): void {
    if (this.timer !== null) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.detachEventHandlers();
  }

  /** Permanently stop; further start()/checkNow() calls are no-ops. */
  dispose(): void {
    this.disposed = true;
    this.stop();
  }

  /** Fetch the current state and fire onChange when the admin preference changed. */
  async checkNow(): Promise<void> {
    if (this.disposed || this.checking) return;
    this.checking = true;
    let state: AdminSettingsState | null = null;
    try {
      state = await this.fetchState();
    } catch {
      /* network blip — keep the last observed baseline */
    } finally {
      this.checking = false;
    }
    if (!state) return;

    const { admin_preference: pref, admin_version: version } = state;

    // No settings row — nothing to propagate; a manual toggle stays the
    // operator's own choice until the admin row exists.
    if (version === null) {
      this.baseline = true;
      this.lastVersion = null;
      this.lastPref = null;
      return;
    }

    if (!this.baseline) {
      // First sight of a settings row: the session cache may predate the
      // row (stale) — apply the DB truth when they disagree.
      this.baseline = true;
      this.lastVersion = version;
      this.lastPref = pref;
      if (pref !== state.session_preference) {
        this.onChange?.(pref);
      }
      return;
    }

    // Row saved again AND the mapped preference changed (a same-mode save
    // — e.g. an unrelated settings edit — bumps the version but not the
    // preference, so no propagation is needed).
    if (version !== this.lastVersion && pref !== this.lastPref) {
      this.lastVersion = version;
      this.lastPref = pref;
      this.onChange?.(pref);
      return;
    }
    this.lastVersion = version;
    this.lastPref = pref;
  }

  private attachEventHandlers(): void {
    if (!this.visibilityAware || typeof window === 'undefined') return;
    this.visibilityHandler = () => {
      if (document.visibilityState === 'visible') void this.checkNow();
    };
    document.addEventListener('visibilitychange', this.visibilityHandler);
    this.focusHandler = () => void this.checkNow();
    window.addEventListener('focus', this.focusHandler);
  }

  private detachEventHandlers(): void {
    if (this.visibilityHandler) {
      document.removeEventListener('visibilitychange', this.visibilityHandler);
      this.visibilityHandler = null;
    }
    if (this.focusHandler) {
      window.removeEventListener('focus', this.focusHandler);
      this.focusHandler = null;
    }
  }
}

/** Convenience singleton (one watcher per page instance). */
export const adminSettingsWatcher = new AdminSettingsWatcher();
