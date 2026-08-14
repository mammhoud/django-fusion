/**
 * Background Images Handler with Lazy Loading
 * Uses IntersectionObserver for performance optimization
 */

export class BackgroundImages {
    constructor(options = {}) {
        this.options = {
            selector: '.bg-image[data-bg-src]',
            rootMargin: '50px 0px',
            threshold: 0.01,
            lazyLoad: true,
            ...options
        };

        this.observer = null;
        this.initialized = false;
    }

    init() {
        if (this.initialized) return;
        const bgImages = document.querySelectorAll(this.options.selector);
        if (bgImages.length === 0) {
            this.initialized = true;
            return;
        }
        if (this.options.lazyLoad && 'IntersectionObserver' in window) {
            this.initLazyLoading(bgImages);
        } else {
            this.loadAllImages(bgImages);
        }

        this.initialized = true;
        console.log(`✅ ${bgImages.length} background images initialized`);
    }

    initLazyLoading(images) {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadImage(entry.target);
                    this.observer.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: this.options.rootMargin,
            threshold: this.options.threshold
        });

        images.forEach(image => {
            this.observer.observe(image);
        });
    }

    loadAllImages(images) {
        images.forEach(image => this.loadImage(image));
    }

    loadImage(element) {
        const bgSrc = element.getAttribute('data-bg-src');
        if (!bgSrc) return;

        // Preload image before applying
        const img = new Image();
        img.onload = () => {
            element.style.backgroundImage = `url("${bgSrc}")`;
            element.classList.add('bg-loaded');
            element.classList.remove('bg-image');
        };
        img.onerror = () => {
            console.warn(`Failed to load background image: ${bgSrc}`);
            element.classList.add('bg-error');
        };
        img.src = bgSrc;
    }

    refresh() {
        if (this.observer) {
            this.observer.disconnect();
        }
        this.initialized = false;
        this.init();
    }

    destroy() {
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
        this.initialized = false;
    }
}

// Backward compatibility alias
export const BackgroundImagesHandler = BackgroundImages;
export default BackgroundImages;
