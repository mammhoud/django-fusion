import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath, URL } from "node:url";
import { readFileSync, existsSync } from "node:fs";

// ── Dependency-free .env loader ─────────────────────────────────────────────
// Shell env wins, then .env.local, then .env (see .env.example).
const __env: Record<string, string> = {};
for (const __f of [".env.local", ".env"]) {
    if (!existsSync(__f)) {
        continue;
    }
    for (const __line of readFileSync(__f, "utf8").split("\n")) {
        const __m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$/.exec(__line);
        if (__m && !(__m[1] in __env)) {
            __env[__m[1]] = __m[2].replace(/^['"]|['"]$/g, "");
        }
    }
}
// @ts-expect-error process is a nodejs global
const envVal = (key: string, fallback: string) => process.env[key] ?? __env[key] ?? fallback;

// @ts-expect-error process is a nodejs global
const host = process.env.TAURI_DEV_HOST;

/** Dev server port — keep 1420 for Tauri (tauri.conf.json devUrl is fixed). */
const PORT = Number(envVal("PORT", "1420"));
/** HMR WebSocket port (Tauri uses 1421 when exposed on a network host). */
const HMR_PORT = Number(envVal("HMR_PORT", "1421"));
const SHARED_ASSETS = fileURLToPath(new URL("../assets/shared", import.meta.url));

// https://vitejs.dev/config/
export default defineConfig(async () => ({
    plugins: [vue(), tailwindcss()],

    // Path alias — shadcn-vue components import via @/…
    resolve: {
        alias: {
            "@": fileURLToPath(new URL("./src", import.meta.url)),
            "@formints-assets": SHARED_ASSETS,
        },
    },

    // Vite options tailored for Tauri development and only applied in `tauri dev` or `tauri build`
    //
    // 1. prevent vite from obscuring rust errors
    clearScreen: false,
    // 2. tauri expects a fixed port, fail if that port is not available
    server: {
        fs: { allow: [SHARED_ASSETS] },
        port: PORT,
        strictPort: true,
        host: host || false,
        hmr: host
            ? {
                  protocol: "ws",
                  host,
                  port: HMR_PORT,
              }
            : undefined,
        watch: {
            // 3. tell vite to ignore watching `src-tauri`
            ignored: ["**/src-tauri/**"],
        },
    },
}));
