/**
 * Client version — single source of truth for the desktop app's version.
 *
 * Why it used to be empty: nothing in the client ever read or exposed a
 * version — the value exists in `package.json` / `src-tauri/tauri.conf.json`
 * but no code fetched it. Here we pull the live Tauri app version at runtime
 * (from the compiled binary) and fall back to the static package version
 * when running in a plain browser (Vite dev).
 */
import pkg from '../../package.json';
import { getVersion } from '@tauri-apps/api/app';

/** Read straight from package.json — no manual sync needed. */
export const CLIENT_VERSION: string = pkg.version;

/**
 * Resolve the running client version.
 * - Tauri runtime → the version baked into the binary (tauri.conf.json).
 * - Browser (Vite dev / preview) → the package.json version constant.
 */
export async function getClientVersion(): Promise<string> {
    try {
        return await getVersion();
    } catch {
        return CLIENT_VERSION;
    }
}
