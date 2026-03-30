/**
 * Enhanced Preloader System with multiple types and progress tracking
 */

export class Preloader {
    constructor() {
        this.types = {
            1: this.createType1.bind(this),
            2: this.createType2.bind(this),
            3: this.createType3.bind(this)
        };

        this.loaded = false;
        this.progress = 0;
    }

    init() {
        this.checkPreloaderType();
        this.setupLoadEvents();
        this.setupProgressTracking();
    }

    checkPreloaderType() {
        if (document.querySelector('.preloader')) return;

        const body = document.body;
        const preloaderType = body.getAttribute("data-preloader");

        if (preloaderType && this.types[preloaderType]) {
            this.types[preloaderType]();
        }
    }

    createType1() {
        const preloader = document.createElement("div");
        preloader.className = "preloader preloader-1";
        preloader.innerHTML = `
            <div class="preloader-content">
                <svg class="loader-circular" viewBox="25 25 50 50">
                    <circle class="loader-path" cx="50" cy="50" r="20"></circle>
                </svg>
                <div class="preloader-progress"></div>
            </div>
        `;

        document.body.appendChild(preloader);

        // Add CSS for animation
        // this.addPreloaderStyles();
    }

    createType2() {
        const preloader = document.createElement("div");
        preloader.className = "preloader preloader-2";
        preloader.innerHTML = `
            <div class="preloader-content">
                <svg width="60" height="60" viewBox="0 0 50 50" class="loader-spinner">
                    <path fill="currentColor" d="M25,5A20,20,0,1,0,45,25h-5A15,15,0,1,1,25,10V5Z">
                        <animateTransform attributeName="transform" type="rotate" from="0 25 25" to="360 25 25" dur="1s" repeatCount="indefinite"/>
                    </path>
                </svg>
                <div class="preloader-progress"></div>
            </div>
        `;

        document.body.appendChild(preloader);
    }

    createType3() {
        const preloader = document.createElement("div");
        preloader.className = "preloader preloader-3";
        preloader.innerHTML = `
            <div class="preloader-content">
                <svg width="120" height="30" viewBox="0 0 120 30" xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="loader-dots">
                    <circle cx="15" cy="15" r="15">
                        <animate attributeName="r" from="15" to="15"
                                 begin="0s" dur="0.8s"
                                 values="15;9;15" calcMode="linear"
                                 repeatCount="indefinite" />
                        <animate attributeName="fill-opacity" from="1" to="1"
                                 begin="0s" dur="0.8s"
                                 values="1;.5;1" calcMode="linear"
                                 repeatCount="indefinite" />
                    </circle>
                    <circle cx="60" cy="15" r="9" fill-opacity="0.3">
                        <animate attributeName="r" from="9" to="9"
                                 begin="0s" dur="0.8s"
                                 values="9;15;9" calcMode="linear"
                                 repeatCount="indefinite" />
                        <animate attributeName="fill-opacity" from="0.5" to="0.5"
                                 begin="0s" dur="0.8s"
                                 values=".5;1;.5" calcMode="linear"
                                 repeatCount="indefinite" />
                    </circle>
                    <circle cx="105" cy="15" r="15">
                        <animate attributeName="r" from="15" to="15"
                                 begin="0s" dur="0.8s"
                                 values="15;9;15" calcMode="linear"
                                 repeatCount="indefinite" />
                        <animate attributeName="fill-opacity" from="1" to="1"
                                 begin="0s" dur="0.8s"
                                 values="1;.5;1" calcMode="linear"
                                 repeatCount="indefinite" />
                    </circle>
                </svg>
                <div class="preloader-progress"></div>
            </div>
        `;

        document.body.appendChild(preloader);
    }

    addPreloaderStyles() {
        const style = document.createElement('style');
        style.textContent = `
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
const preloader = new Preloader();
preloader.init();
