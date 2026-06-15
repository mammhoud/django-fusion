/**
 * Enhanced Sliders Component with Hero Support
 * Clean, maintainable version with all features
 */

import { DOM } from '../../../utility/dom.js';
import { debounce } from '../../../utility/index.js';

export class Sliders {
    constructor(options = {}) {
        this.options = {
            // Owl Carousel
            owlSelector: '.owl-carousel',
            heroCarouselSelector: '.hero-slider',

            // Dependencies with fallbacks
            dependencies: {
                jquery: [
                    'https://code.jquery.com/jquery-3.6.0.min.js',
                    'https://cdn.jsdelivr.net/npm/jquery@3.6.0/dist/jquery.min.js'
                ],
                owlCarouselJS: [
                    'https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/owl.carousel.min.js',
                    'https://cdn.jsdelivr.net/npm/owl.carousel@2.3.4/dist/owl.carousel.min.js'
                ],
                owlCarouselCSS: 'https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/assets/owl.carousel.min.css',
                owlThemeCSS: 'https://cdnjs.cloudflare.com/ajax/libs/OwlCarousel2/2.3.4/assets/owl.theme.default.min.css',
                animateCSS: 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css'
            },

            // Auto initialization
            autoInit: true,
            lazyLoad: true,
            fallbackEnabled: true,

            // Performance
            retryAttempts: 2,
            retryDelay: 1000,

            ...options
        };

        this.sliders = new Map();
        this.heroInstances = new Map();
        this.isInitialized = false;

        // Bind methods
        this.initHeroSlider = this.initHeroSlider.bind(this);

        // Auto-initialize
        if (this.options.autoInit && document.readyState !== 'loading') {
            this.init();
        } else if (this.options.autoInit) {
            document.addEventListener('DOMContentLoaded', () => this.init());
        }
    }

    /**
     * Initialize all sliders
     */
    async init() {
        if (this.isInitialized) return;

        try {
            console.log('🎬 Initializing Sliders...');

            // Initialize hero slider first
            const heroSlider = document.querySelector(this.options.heroCarouselSelector);
            if (heroSlider) {
                await this.initHeroSlider(heroSlider);
            }

            // Initialize other sliders
            await this.initOtherSliders();

            this.setupEventListeners();
            this.isInitialized = true;

            this.dispatchEvent('sliders:initialized');
            console.log('✅ Sliders initialized successfully');

        } catch (error) {
            console.error('Failed to initialize sliders:', error);
            this.showFallback();
        }
    }

    /**
     * Initialize hero slider
     */
    async initHeroSlider(element) {
        const sliderId = element.id || `hero-slider-${Date.now()}`;
        element.id = sliderId;

        // Load dependencies
        await this.loadDependencies();

        // Check if Owl Carousel is available
        if (!window.jQuery || !window.jQuery.fn.owlCarousel) {
            throw new Error('Owl Carousel not available');
        }

        // Initialize Owl Carousel
        const $ = window.jQuery;
        const config = this.getHeroConfig(element);

        const owlInstance = $(element).owlCarousel({
            ...config,
            onInitialized: (event) => this.handleHeroInitialized(event, $(element)),
            onTranslate: (event) => this.handleHeroTranslate(event, $(element)),
            onTranslated: (event) => this.handleHeroTranslated(event, $(element))
        });

        // Store instance
        this.heroInstances.set(sliderId, owlInstance);
        this.sliders.set(sliderId, {
            type: 'hero',
            instance: owlInstance,
            element: element
        });

        // Setup additional features
        this.setupHeroFeatures(element);

        console.log(`✅ Hero slider "${sliderId}" initialized`);
        return owlInstance;
    }

    /**
     * Load dependencies with fallback
     */
    async loadDependencies() {
        const deps = [];
        const dependencies = this.options.dependencies;

        // Load jQuery if needed
        if (!window.jQuery) {
            deps.push(this.loadResource(dependencies.jquery[0], 'script', dependencies.jquery[1]));
        }

        // Load Owl Carousel if needed
        if (!window.jQuery?.fn?.owlCarousel) {
            deps.push(
                this.loadResource(dependencies.owlCarouselCSS, 'stylesheet'),
                this.loadResource(dependencies.owlThemeCSS, 'stylesheet'),
                this.loadResource(dependencies.animateCSS, 'stylesheet'),
                this.loadResource(dependencies.owlCarouselJS[0], 'script', dependencies.owlCarouselJS[1])
            );
        }

        await Promise.all(deps.map(dep => dep.catch(e => console.warn('Dependency load warning:', e))));
    }

    /**
     * Load resource with fallback
     */
    loadResource(url, type, fallbackUrl = null) {
        return new Promise((resolve, reject) => {
            // Check if already loaded
            if (type === 'stylesheet' && document.querySelector(`link[href="${url}"]`)) {
                resolve();
                return;
            }
            if (type === 'script' && document.querySelector(`script[src="${url}"]`)) {
                resolve();
                return;
            }

            let element;

            if (type === 'stylesheet') {
                element = document.createElement('link');
                element.rel = 'stylesheet';
                element.href = url;
                document.head.appendChild(element);
            } else {
                element = document.createElement('script');
                element.src = url;
                document.body.appendChild(element);
            }

            element.onload = resolve;
            element.onerror = () => {
                if (fallbackUrl) {
                    console.log(`Trying fallback for ${url}`);
                    this.loadResource(fallbackUrl, type).then(resolve).catch(reject);
                } else {
                    reject(new Error(`Failed to load ${url}`));
                }
            };
        });
    }

    /**
     * Get hero slider configuration
     */
    getHeroConfig(element) {
        const data = element.dataset;

        return {
            items: parseInt(data.owlItems) || 1,
            loop: data.owlLoop !== 'false',
            nav: data.owlNav === 'true',
            dots: data.owlDots !== 'false',
            autoplay: data.owlAutoplay !== 'false',
            autoplayTimeout: parseInt(data.owlAutoplayTimeout) || 5000,
            autoplayHoverPause: true,
            smartSpeed: parseInt(data.owlSmartSpeed) || 800,
            animateOut: data.owlAnimateOut || 'fadeOut',
            animateIn: data.owlAnimateIn || 'fadeIn',
            touchDrag: data.owlTouchDrag !== 'false',
            mouseDrag: data.owlMouseDrag === 'true',
            lazyLoad: data.owlLazyLoad !== 'false',
            autoHeight: data.owlAutoHeight === 'true',
            responsiveClass: true,
            responsiveRefreshRate: 200
        };
    }

    /**
     * Handle hero initialized event
     */
    handleHeroInitialized(event, $slider) {
        const currentIndex = event.item.index;
        const currentSlide = $slider.find('.owl-item').eq(currentIndex);

        // Activate first slide
        currentSlide.addClass('active');

        // Trigger animations
        this.triggerHeroAnimations(currentSlide);

        // Show notification
        // this.showNotification('Hero slider ready', 'success'); #

        // Dispatch event
        this.dispatchEvent('hero:initialized', {
            index: currentIndex,
            slider: $slider[0]
        });
    }

    /**
     * Handle hero translate event
     */
    handleHeroTranslate(event, $slider) {
        const currentIndex = event.item.index;

        // Update active class
        $slider.find('.owl-item').removeClass('active');
        $slider.find('.owl-item').eq(currentIndex).addClass('active');
    }

    /**
     * Handle hero translated event
     */
    handleHeroTranslated(event, $slider) {
        const currentIndex = event.item.index;
        const currentSlide = $slider.find('.owl-item').eq(currentIndex);

        // Trigger animations for new slide
        this.triggerHeroAnimations(currentSlide);

        this.dispatchEvent('hero:slideChanged', {
            index: currentIndex,
            slider: $slider[0]
        });
    }

    /**
     * Trigger hero animations
     */
    triggerHeroAnimations(slide) {
        const $ = window.jQuery;
        if (!$) return;

        // Reset animations
        slide.find('[data-animation]').removeClass(function () {
            const animation = $(this).data('animation');
            return `animate__animated animate__${animation}`;
        });

        // Trigger animations with delays
        slide.find('[data-animation]').each(function () {
            const $element = $(this);
            const animation = $element.data('animation');
            const delay = $element.data('delay') || 0;

            setTimeout(() => {
                $element.addClass(`animate__animated animate__${animation}`);
            }, parseFloat(delay) * 1000);
        });
    }

    /**
     * Setup hero slider features
     */
    setupHeroFeatures(element) {
        // Keyboard navigation
        this.setupKeyboardNavigation(element);

        // Touch indicators
        this.setupTouchIndicators(element);

        // Progress indicator
        // this.setupProgressIndicator(element);
    }

    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation(element) {
        document.addEventListener('keydown', (e) => {
            if (!element.contains(document.activeElement)) return;

            const $ = window.jQuery;
            if (!$) return;

            switch (e.key) {
                case 'ArrowLeft':
                    $(element).trigger('prev.owl.carousel');
                    e.preventDefault();
                    this.showNavigationIndicator('←');
                    break;

                case 'ArrowRight':
                    $(element).trigger('next.owl.carousel');
                    e.preventDefault();
                    this.showNavigationIndicator('→');
                    break;

                case ' ':
                    e.preventDefault();
                    this.toggleAutoplay(element);
                    break;
            }
        });
    }

    /**
     * Show navigation indicator
     */
    showNavigationIndicator(direction) {
        const indicator = document.createElement('div');
        indicator.className = 'nav-indicator';
        indicator.textContent = direction;
        indicator.style.cssText = `
            position: fixed;
            top: 50%;
            ${direction === '←' ? 'left: 20px' : 'right: 20px'};
            transform: translateY(-50%);
            background: rgba(0,0,0,0.7);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            z-index: 1000;
            animation: fadeInOut 1s ease;
        `;

        document.body.appendChild(indicator);
        setTimeout(() => indicator.remove(), 1000);
    }

    /**
     * Toggle autoplay
     */
    toggleAutoplay(element) {
        const $ = window.jQuery;
        if (!$) return;

        const instance = $(element).data('owl.carousel');
        if (!instance) return;

        const isPlaying = instance.settings.autoplay;

        if (isPlaying) {
            $(element).trigger('stop.owl.autoplay');
            this.showNotification('Autoplay paused', 'info');
        } else {
            $(element).trigger('play.owl.autoplay');
            this.showNotification('Autoplay resumed', 'info');
        }
    }

    /**
     * Setup touch indicators
     */
    setupTouchIndicators(element) {
        let startX = 0;

        element.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        }, { passive: true });

        element.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const diff = startX - endX;

            if (Math.abs(diff) > 50) {
                const $ = window.jQuery;
                if (!$) return;

                if (diff > 0) {
                    $(element).trigger('next.owl.carousel');
                } else {
                    $(element).trigger('prev.owl.carousel');
                }
            }
        }, { passive: true });
    }

    /**
     * Setup progress indicator
     */
    setupProgressIndicator(element) {
        const progress = document.createElement('div');
        progress.className = 'slider-progress';
        progress.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: rgba(255,255,255,0.2);
            z-index: 10;
        `;

        const bar = document.createElement('div');
        bar.className = 'slider-progress-bar';
        bar.style.cssText = `
            height: 100%;
            background: var(--bs-primary);
            width: 0%;
            transition: width 0.1s linear;
        `;

        progress.appendChild(bar);
        element.appendChild(progress);

        // Update progress
        setInterval(() => {
            const $ = window.jQuery;
            if (!$) return;

            const instance = $(element).data('owl.carousel');
            if (instance && instance.settings.autoplay && instance.autoplay) {
                const progress = (instance.autoplay.timeout / instance.settings.autoplayTimeout) * 100;
                bar.style.width = `${progress}%`;
            }
        }, 100);
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `slider-notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 12px 24px;
            border-radius: 30px;
            font-size: 14px;
            z-index: 1000;
            transition: transform 0.3s ease;
            pointer-events: none;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.transform = 'translateX(-50%) translateY(0)';
        }, 10);

        setTimeout(() => {
            notification.style.transform = 'translateX(-50%) translateY(100px)';
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }

    /**
     * Initialize other sliders
     */
    async initOtherSliders() {
        const owlSliders = document.querySelectorAll(`${this.options.owlSelector}:not(${this.options.heroCarouselSelector})`);

        for (const slider of owlSliders) {
            try {
                await this.initOwlSlider(slider);
            } catch (error) {
                console.warn('Failed to initialize slider:', error);
            }
        }
    }

    /**
     * Initialize Owl slider
     */
    async initOwlSlider(element) {
        if (!window.jQuery || !window.jQuery.fn.owlCarousel) {
            throw new Error('Owl Carousel not available');
        }

        const $ = window.jQuery;
        const config = this.getOwlConfig(element);
        const sliderId = element.id || `owl-slider-${Date.now()}`;

        element.id = sliderId;
        const instance = $(element).owlCarousel(config);

        this.sliders.set(sliderId, {
            type: 'owl',
            instance: instance,
            element: element
        });

        return instance;
    }

    /**
     * Get Owl slider configuration
     */
    getOwlConfig(element) {
        const data = element.dataset;

        return {
            items: parseInt(data.owlItems) || 1,
            margin: parseInt(data.owlMargin) || 0,
            loop: data.owlLoop === 'true',
            nav: data.owlNav === 'true',
            dots: data.owlDots === 'true',
            autoplay: data.owlAutoplay === 'true',
            autoplayTimeout: parseInt(data.owlAutoplayTimeout) || 4000,
            smartSpeed: parseInt(data.owlSmartSpeed) || 450,
            responsive: {
                0: { items: parseInt(data.owlXs) || 1 },
                576: { items: parseInt(data.owlSm) || 2 },
                768: { items: parseInt(data.owlMd) || 3 },
                992: { items: parseInt(data.owlLg) || 4 },
                1200: { items: parseInt(data.owlXl) || 5 }
            }
        };
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Resize handling
        window.addEventListener('resize', debounce(() => {
            this.refresh();
        }, 250));

        // Visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAll();
            } else {
                this.playAll();
            }
        });
    }

    /**
     * Pause all sliders
     */
    pauseAll() {
        this.sliders.forEach(({ instance, type }) => {
            if (type === 'hero' || type === 'owl') {
                const $ = window.jQuery;
                if ($ && instance && instance.$element) {
                    instance.$element.trigger('stop.owl.autoplay');
                }
            }
        });
    }

    /**
     * Play all sliders
     */
    playAll() {
        this.sliders.forEach(({ instance, type }) => {
            if (type === 'hero' || type === 'owl') {
                const $ = window.jQuery;
                if ($ && instance && instance.$element) {
                    instance.$element.trigger('play.owl.autoplay');
                }
            }
        });
    }

    /**
     * Refresh all sliders
     */
    refresh() {
        this.sliders.forEach(({ instance }) => {
            const $ = window.jQuery;
            if ($ && instance && instance.$element) {
                instance.$element.trigger('refresh.owl.carousel');
            }
        });
    }

    /**
     * Show fallback if initialization fails
     */
    showFallback() {
        if (!this.options.fallbackEnabled) return;

        const heroSlider = document.querySelector(this.options.heroCarouselSelector);
        if (!heroSlider) return;

        console.log('Using static fallback for hero slider');

        const slides = heroSlider.querySelectorAll('.hero-slide');
        if (slides.length === 0) return;

        // Show first slide only
        slides.forEach((slide, index) => {
            slide.style.display = index === 0 ? 'block' : 'none';
        });

        // Add manual navigation
        const template = document.getElementById('hero-fallback-template');
        if (template) {
            const nav = template.content.cloneNode(true);
            const container = nav.querySelector('.static-fallback-nav');

            // Set initial counter
            const counter = container.querySelector('.slide-counter');
            counter.textContent = `1 / ${slides.length}`;

            heroSlider.parentNode.appendChild(container);

            let currentIndex = 0;

            // Navigation handlers
            container.querySelector('.prev-btn').addEventListener('click', () => {
                if (currentIndex > 0) {
                    slides[currentIndex].style.display = 'none';
                    currentIndex--;
                    slides[currentIndex].style.display = 'block';
                    counter.textContent = `${currentIndex + 1} / ${slides.length}`;
                }
            });

            container.querySelector('.next-btn').addEventListener('click', () => {
                if (currentIndex < slides.length - 1) {
                    slides[currentIndex].style.display = 'none';
                    currentIndex++;
                    slides[currentIndex].style.display = 'block';
                    counter.textContent = `${currentIndex + 1} / ${slides.length}`;
                }
            });

            heroSlider.classList.add('static-fallback-active');
        }

        this.showNotification('Using static fallback navigation', 'warning');
    }

    /**
     * Dispatch custom event
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, component: this },
            bubbles: true
        });
        document.dispatchEvent(event);
    }

    /**
     * Get slider by ID
     */
    getSlider(id) {
        return this.sliders.get(id);
    }

    /**
     * Go to specific slide
     */
    goToSlide(sliderId, slideIndex) {
        const slider = this.sliders.get(sliderId);
        if (!slider) return false;

        const $ = window.jQuery;
        if (!$ || !slider.instance || !slider.instance.$element) return false;

        slider.instance.$element.trigger('to.owl.carousel', [slideIndex, 300]);
        return true;
    }

    /**
     * Destroy all sliders
     */
    destroy() {
        this.sliders.forEach(({ instance }) => {
            if (instance && instance.destroy) {
                try {
                    instance.destroy();
                } catch (error) {
                    console.warn('Error destroying slider:', error);
                }
            }
        });

        this.sliders.clear();
        this.heroInstances.clear();
        this.isInitialized = false;

        console.log('✅ Sliders destroyed');
    }

    /**
     * Get status
     */
    getStatus() {
        return {
            isInitialized: this.isInitialized,
            totalSliders: this.sliders.size,
            heroSliders: Array.from(this.sliders.values()).filter(s => s.type === 'hero').length
        };
    }
}

// Auto-initialize if sliders are found
document.addEventListener('DOMContentLoaded', () => {
    const hasSliders = document.querySelector('.owl-carousel, .hero-slider');

    if (hasSliders && !window.appSliders) {
        window.appSliders = new Sliders();
    }
});

// Export for module usage
export default Sliders;
