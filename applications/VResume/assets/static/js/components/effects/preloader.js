/**
 * Enhanced Preloader System with HTMX support
 * - Initial page load preloader (full screen)
 * - HTMX request preloader (target component only)
 */

export class Preloader {
    constructor({ element } = {}) {
        this.element = element || document.body;
        this.loaded = false;
        this.progress = 0;
        this.htmxPreloaders = new Map();
        this.mainPreloader = null;
    }

    async init() {
        this.addPreloaderStyles();
        this.checkPreloaderType();
        this.setupLoadEvents();
        this.setupProgressTracking();
        this.setupHTMXPreloaders();
        console.log('✅ Preloader initialized');
    }

    checkPreloaderType() {
        if (document.querySelector('.preloader')) return;
        this.mainPreloader = this.createType1();
    }

    createType1() {
        const preloader = document.createElement("div");
        preloader.className = "preloader preloader-1";
        preloader.innerHTML = `
            <div class="preloader-content">
                <svg class="loader-circular" viewBox="25 25 50 50">
                    <circle class="loader-path" cx="50" cy="50" r="20"></circle>
                </svg>
                <div class="preloader-progress">0%</div>
            </div>
        `;

        document.body.appendChild(preloader);
        return preloader;
    }


    /**
     * Create target-specific preloader for HTMX requests
     */
    createHTMXPreloader(targetId) {
        const target = document.getElementById(targetId);
        if (!target) return null;

        const preloader = document.createElement('div');
        preloader.className = 'htmx-preloader';
        preloader.innerHTML = `
            <div class="htmx-preloader-spinner">
                <svg width="40" height="40" viewBox="0 0 50 50" class="loader-spinner-htmx">
                    <path fill="currentColor" d="M25,5A20,20,0,1,0,45,25h-5A15,15,0,1,1,25,10V5Z">
                        <animateTransform attributeName="transform" type="rotate" from="0 25 25" to="360 25 25" dur="1s" repeatCount="indefinite"/>
                    </path>
                </svg>
            </div>
        `;

        // Position relative to target
        target.style.position = 'relative';
        target.appendChild(preloader);

        return preloader;
    }

    /**
     * Show preloader for specific HTMX target
     */
    showHTMXPreloader(targetId) {
        // Remove stale entry if one already exists for this target
        if (this.htmxPreloaders.has(targetId)) {
            const existing = this.htmxPreloaders.get(targetId);
            if (existing && existing.parentNode) {
                existing.remove();
            }
            this.htmxPreloaders.delete(targetId);
        }

        const preloader = this.createHTMXPreloader(targetId);
        if (preloader) {
            this.htmxPreloaders.set(targetId, preloader);
            // Force layout so the 'show' class transition works
            requestAnimationFrame(() => {
                preloader.classList.add('show');
            });
        }
    }

    /**
     * Hide preloader for specific HTMX target
     */
    hideHTMXPreloader(targetId) {
        const preloader = this.htmxPreloaders.get(targetId);
        if (preloader) {
            preloader.classList.remove('show');
            // Remove after animation
            setTimeout(() => {
                if (preloader.parentNode) {
                    preloader.remove();
                }
                this.htmxPreloaders.delete(targetId);
            }, 300);
        }
    }

    /**
     * Setup HTMX event listeners for target-specific preloaders
     */
    setupHTMXPreloaders() {
        if (typeof window === 'undefined' || !window.htmx) return;

        // Listen for HTMX requests on elements with data-htmx-preloader
        document.addEventListener('htmx:beforeRequest', (event) => {
            const target = event.detail.target;
            if (target && target.hasAttribute('data-htmx-preloader')) {
                const targetId = target.id || `htmx-target-${Date.now()}`;
                if (!target.id) target.id = targetId;
                this.showHTMXPreloader(targetId);
            }
        });

        // Hide preloader when response received and swap completes
        document.addEventListener('htmx:afterSettle', (event) => {
            const target = event.detail.target;
            if (target && target.hasAttribute('data-htmx-preloader')) {
                this.hideHTMXPreloader(target.id);
            }
        });

        // Also hide on error
        document.addEventListener('htmx:responseError', (event) => {
            const target = event.detail.target;
            if (target && target.hasAttribute('data-htmx-preloader')) {
                this.hideHTMXPreloader(target.id);
            }
        });

        // Hide on timeout
        document.addEventListener('htmx:timeout', (event) => {
            const target = event.detail.target;
            if (target && target.hasAttribute('data-htmx-preloader')) {
                this.hideHTMXPreloader(target.id);
            }
        });
    }

    addPreloaderStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .preloader {
                position: fixed;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgb(var(--bg-canvas-rgb, 12, 12, 14), 0.92);
                z-index: 99999;
                opacity: 1;
                visibility: visible;
                transition: opacity .35s ease, visibility .35s ease;
            }
            body.loaded .preloader {
                opacity: 0;
                visibility: hidden;
                pointer-events: none;
            }
            .preloader-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: .8rem;
                color: var(--text-primary, #fff);
            }
            .preloader-progress {
                font-size: 0.8rem;
                opacity: .9;
                min-height: 1rem;
                color: var(--color-accent, #fff);
            }

            /* SVG loader path — uses accent color for the animated circle */
            .preloader-1 .loader-path {
                fill: none;
                stroke: var(--color-accent, #fff);
                stroke-width: 3;
                stroke-dasharray: 150 200;
                stroke-linecap: round;
                animation: loader-dash 1.5s ease-in-out infinite;
            }
            @keyframes loader-dash {
                0%   { stroke-dasharray: 1, 200; stroke-dashoffset: 0; }
                50%  { stroke-dasharray: 90, 150; stroke-dashoffset: -35; }
                100% { stroke-dasharray: 90, 150; stroke-dashoffset: -124; }
            }

            
            /* HTMX Target Preloaders */
            .htmx-preloader {
                position: absolute;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgb(var(--bg-canvas-rgb, 255, 255, 255), 0.6);
                z-index: 9999;
                opacity: 0;
                visibility: hidden;
                transition: opacity .3s ease, visibility .3s ease;
                border-radius: inherit;
            }
            .htmx-preloader.show {
                opacity: 1;
                visibility: visible;
            }
            .htmx-preloader-spinner {
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--color-accent, currentColor);
            }
            .loader-spinner-htmx {
                color: var(--color-accent, currentColor);
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        `;

        document.head.appendChild(style);
    }

    setupLoadEvents() {
        const handleLoad = () => {
            if (this.loaded) return;
            this.loaded = true;
            document.body.classList.add('loaded');

            // Remove preloader after animation
            setTimeout(() => {
                const preloaders = document.querySelectorAll('.preloader');
                preloaders.forEach(preloader => {
                    preloader.remove();
                });
            }, 500);
        };

        if (document.readyState === 'complete') {
            handleLoad();
        } else {
            window.addEventListener('load', handleLoad);
        }

        // Fallback in case load event doesn't fire
        setTimeout(() => {
            if (!this.loaded) {
                handleLoad();
            }
        }, 3000);
    }

    setupProgressTracking() {
        if (!window.performance || !window.performance.getEntriesByType) return;

        const resources = window.performance.getEntriesByType('resource');
        let loaded = 0;

        const updateProgress = () => {
            loaded++;
            this.progress = Math.min(100, Math.round((loaded / resources.length) * 100));

            const progressEl = document.querySelector('.preloader-progress');
            if (progressEl) {
                progressEl.textContent = `${this.progress}%`;
            }
        };

        // Track individual resource loads
        resources.forEach(resource => {
            const img = new Image();
            img.src = resource.name;
            img.onload = updateProgress;
            img.onerror = updateProgress;
        });
    }

    show() {
        document.body.classList.remove('loaded');
    }

    hide() {
        document.body.classList.add('loaded');
    }
}

// UIManager initializes Preloader via the [data-preloader] selector on <body>.
export default Preloader;
