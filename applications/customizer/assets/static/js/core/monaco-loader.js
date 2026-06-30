// ================================================================
//   MONACO LOADER
// ================================================================

export class MonacoLoader {
    constructor() {
        this.isLoaded = false;
        this.loadingPromise = null;
    }

    load() {
        if (this.isLoaded) {
            return Promise.resolve(window.monaco);
        }

        if (this.loadingPromise) {
            return this.loadingPromise;
        }

        this.loadingPromise = new Promise((resolve, reject) => {
            if (window.monaco) {
                this.isLoaded = true;
                resolve(window.monaco);
                return;
            }

            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/monaco-editor@0.39.0/min/vs/loader.js';
            script.onload = () => {
                // Use window.require (Monaco's AMD loader attaches itself to the global scope)
                // instead of bare require() so webpack's static analysis doesn't try to
                // resolve Monaco's internal module paths during bundling.
                const mr = /** @type {any} */ (window).require;
                mr.config({
                    paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.39.0/min/vs' },
                });
                mr(['vs/editor/editor.main'], () => {
                    this.isLoaded = true;
                    resolve(window.monaco);
                });
            };
            script.onerror = reject;
            document.head.appendChild(script);
        });

        return this.loadingPromise;
    }

    createEditor(container, options) {
        if (!this.isLoaded) {
            console.warn('Monaco not loaded yet');
            return null;
        }
        return monaco.editor.create(container, options);
    }
}