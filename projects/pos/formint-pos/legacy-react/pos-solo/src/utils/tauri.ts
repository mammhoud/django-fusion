/**
 * Tauri environment detection — shared across the app.
 *
 * In browser dev mode (vite / `pnpm dev`) the Tauri runtime is absent.
 * Guards prevent `invoke()` crashes before the sidecar is available.
 */
export const isTauri = typeof (window as any).__TAURI__ !== 'undefined';
