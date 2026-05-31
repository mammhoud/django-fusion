// sliders.js
class SlidersComponent {
    constructor(options = {}) {
        if (SlidersComponent._instance) {
            if (SlidersComponent._instance.isInitialized) {
                SlidersComponent._instance.refreshAll();
            }
            return SlidersComponent._instance;
        }
        SlidersComponent._instance = this;

        this.options = {
            swiperSelector: '.swiper',
            homeSliderSelector: '.slider__container',
            teamSliderSelector: '.team__list',
            dependencies: {
                swiperCSS: 'https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.css',
                swiperJS: 'https://cdn.jsdelivr.net/npm/swiper@12/swiper-bundle.min.js'
            },
            autoCreateNavigation: true,
            autoInit: true,
            htmxEnabled: true,
            fallbackEnabled: true,
            ...options
        };

        this.sliders = new Map();     // Map<id, { type, instance, element }>
        this.isInitialized = false;
        this.depsLoaded = false;
        this._refreshTimer = null;
        this._listeners = {};

        this.init = this.init.bind(this);
        this.debouncedRefresh = this._debounce(() => this.updateAll(), 250);

        if (this.options.autoInit) {
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
            } else {
                this.init();
            }
        }
    }

    /* ---------- PUBLIC API ---------- */
    async init() {
        if (this.isInitialized) { await this.refreshAll(); return; }

        console.log('🎬 SlidersManager initializing');
        try {
            await this._loadDependencies();
            await this._initAllSliders();
            this._setupEventListeners();
            this.isInitialized = true;
            this._dispatch('sliders:initialized');
            console.log('✅ SlidersManager ready');
        } catch (err) {
            console.error('SlidersManager init failed:', err);
            this._showFallback();
        }
    }

    /** Refresh all sliders on the page. */
    async refreshAll() {
        if (!this.isInitialized) return;
        this._destroyAllSliders();
        await this._initAllSliders();
        this._dispatch('sliders:refreshed');
    }

    /**
     * Refresh **only** sliders inside a specific container (e.g., after a modal HTMX swap).
     * @param {HTMLElement} container
     */
    refreshContainer(container) {
        if (!container || !this.isInitialized) return;

        // Destroy Swipers whose elements live inside the container
        for (const [id, { instance, element }] of this.sliders) {
            if (!element) continue;
            if (container.contains(element) || element.closest('#unified-modal-container')) {
                if (instance?.destroy) {
                    try { instance.destroy(true, true); } catch (_) { /* ignore */ }
                }
                this.sliders.delete(id);
            }
        }

        // Re‑init sliders inside that container
        const selectors = [
            this.options.homeSliderSelector,
            this.options.teamSliderSelector,
            `${this.options.swiperSelector}:not(.home-slider):not(.team-slider)`
        ];

        for (const sel of selectors) {
            try {
                const els = container.querySelectorAll(sel);
                for (const el of els) {
                    if (el.matches(this.options.homeSliderSelector)) {
                        await this._initHomeSlider(el);
                    } else if (el.matches(this.options.teamSliderSelector)) {
                        await this._initTeamSlider(el);
                    } else {
                        await this._initGenericSwiper(el);
                    }
                }
            } catch (_) { /* skip broken selectors */ }
        }

        this._dispatch('sliders:containerRefreshed', { container });
    }

    updateAll() {
        for (const { instance } of this.sliders.values()) {
            if (instance?.update) instance.update();
        }
    }

    pauseAll() {
        for (const { instance } of this.sliders.values()) {
            if (instance?.autoplay?.stop) instance.autoplay.stop();
        }
    }

    playAll() {
        for (const { instance } of this.sliders.values()) {
            if (instance?.autoplay?.start) instance.autoplay.start();
        }
    }

    destroy() {
        this._destroyAllSliders();
        this.isInitialized = false;
        window.removeEventListener('resize', this.debouncedRefresh);
        document.removeEventListener('visibilitychange', this._listeners.visibility);
        if (this.options.htmxEnabled && window.htmx) {
            document.body.removeEventListener('htmx:afterSwap', this._listeners.htmx);
        }
        console.log('🧹 SlidersManager destroyed');
    }

    getStatus() {
        return {
            isInitialized: this.isInitialized,
            total: this.sliders.size,
            types: Object.fromEntries(
                [...this.sliders.values()].reduce((acc, s) => {
                    acc.set(s.type, (acc.get(s.type) || 0) + 1);
                    return acc;
                }, new Map())
            )
        };
    }

    /* ---------- INTERNAL ---------- */
    async _loadDependencies() {
        if (this.depsLoaded) return;
        if (window.Swiper) { this.depsLoaded = true; return; }

        const { swiperCSS, swiperJS } = this.options.dependencies;
        const tasks = [];
        if (!document.querySelector(`link[href="${swiperCSS}"]`))
            tasks.push(this._loadResource(swiperCSS, 'stylesheet'));
        if (!window.Swiper)
            tasks.push(this._loadResource(swiperJS, 'script'));
        await Promise.all(tasks);
        this.depsLoaded = true;
    }

    _loadResource(url, type) {
        return new Promise((resolve, reject) => {
            if (type === 'stylesheet' && document.querySelector(`link[href="${url}"]`)) return resolve();
            if (type === 'script' && document.querySelector(`script[src="${url}"]`)) return resolve();

            const el = type === 'stylesheet'
                ? Object.assign(document.createElement('link'), { rel: 'stylesheet', href: url })
                : Object.assign(document.createElement('script'), { src: url });

            el.onload = resolve;
            el.onerror = () => reject(new Error(`Failed to load ${url}`));
            (type === 'stylesheet' ? document.head : document.body).appendChild(el);
        });
    }

    async _initAllSliders() {
        const homeSliders = document.querySelectorAll(this.options.homeSliderSelector);
        const teamSliders = document.querySelectorAll(this.options.teamSliderSelector);
        const otherSliders = document.querySelectorAll(
            `${this.options.swiperSelector}:not(.home-slider):not(.team-slider)`
        );

        for (const el of homeSliders) await this._initHomeSlider(el);
        for (const el of teamSliders) await this._initTeamSlider(el);
        for (const el of otherSliders) await this._initGenericSwiper(el);
    }

    _destroyAllSliders() {
        for (const { instance } of this.sliders.values()) {
            if (instance?.destroy) instance.destroy(true, true);
        }
        this.sliders.clear();
    }

    /* ---------- Slider type initializers ---------- */
    async _initHomeSlider(element) {
        if (!window.Swiper) return;
        if (!element.classList.contains('swiper')) this._wrapSwiperStructure(element, 'home-slider');
        if (this.options.autoCreateNavigation) this._ensureNavigation(element);

        const sliderId = element.id || `home-${Date.now()}`;
        element.id = sliderId;

        const pagination = element.querySelector('.swiper-pagination');
        const next = element.querySelector('.swiper-button-next');
        const prev = element.querySelector('.swiper-button-prev');

        // Ensure slider images fill properly
        element.querySelectorAll('.slider__image, .swiper-slide img').forEach(img => {
            if (!img.complete) {
                img.addEventListener('load', () => { if (swiper) swiper.update(); });
            }
        });

        const swiper = new window.Swiper(element, {
            spaceBetween: 30,
            effect: 'fade',
            loop: true,
            autoplay: { delay: 5000, disableOnInteraction: false },
            pagination: { el: pagination, clickable: true, type: 'bullets' },
            navigation: { nextEl: next, prevEl: prev },
            keyboard: { enabled: true },
            observer: true,
            observeParents: true,
            on: {
                init: function() { this.update(); }
            }
        });

        this.sliders.set(sliderId, { type: 'home', instance: swiper, element });
        console.log(`🏠 Home slider "${sliderId}" ready`);
    }

    async _initTeamSlider(element) {
        if (!window.Swiper) return;
        if (!element.classList.contains('swiper')) this._wrapSwiperStructure(element, 'team-slider');

        const sliderId = element.id || `team-${Date.now()}`;
        element.id = sliderId;

        const pagination = element.querySelector('.swiper-pagination');
        const swiper = new window.Swiper(element, {
            slidesPerView: 1,
            spaceBetween: 20,
            loop: false,
            pagination: { el: pagination, clickable: true },
            breakpoints: {
                640: { slidesPerView: 2, spaceBetween: 20 },
                768: { slidesPerView: 3, spaceBetween: 30 },
                1024: { slidesPerView: 4, spaceBetween: 30 }
            },
            observer: true,
            observeParents: true
        });

        this.sliders.set(sliderId, { type: 'team', instance: swiper, element });
        console.log(`👥 Team slider "${sliderId}" ready`);
    }

    async _initGenericSwiper(element) {
        if (!window.Swiper) return;
        const sliderId = element.id || `swiper-${Date.now()}`;
        element.id = sliderId;
        const swiper = new window.Swiper(element, {
            spaceBetween: 30,
            pagination: { el: '.swiper-pagination', clickable: true }
        });
        this.sliders.set(sliderId, { type: 'generic', instance: swiper, element });
    }

    /* ---------- DOM helpers ---------- */
    _wrapSwiperStructure(element, className) {
        element.classList.add('swiper', className);
        const children = Array.from(element.children);
        const wrapper = document.createElement('div');
        wrapper.className = 'swiper-wrapper';
        children.forEach(child => {
            child.classList.add('swiper-slide');
            // Ensure images inside slides display properly
            child.querySelectorAll('img').forEach(img => {
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'cover';
            });
            wrapper.appendChild(child);
        });
        element.innerHTML = '';
        element.appendChild(wrapper);
        element.appendChild(Object.assign(document.createElement('div'), { className: 'swiper-pagination' }));
    }

    _ensureNavigation(container) {
        if (!container.querySelector('.swiper-pagination')) {
            const el = document.createElement('div');
            el.className = 'swiper-pagination';
            container.appendChild(el);
        }
        ['swiper-button-prev', 'swiper-button-next'].forEach(cls => {
            if (!container.querySelector(`.${cls}`)) {
                const btn = document.createElement('div');
                btn.className = cls;
                container.appendChild(btn);
            }
        });
    }

    /* ---------- Event listeners ---------- */
    _setupEventListeners() {
        window.addEventListener('resize', this.debouncedRefresh);
        this._listeners.visibility = () => document.hidden ? this.pauseAll() : this.playAll();
        document.addEventListener('visibilitychange', this._listeners.visibility);

        if (this.options.htmxEnabled && window.htmx) {
            this._listeners.htmx = async (event) => {
                // Debounce to avoid reacting to every rapid swap
                if (this._refreshTimer) clearTimeout(this._refreshTimer);
                this._refreshTimer = setTimeout(async () => {
                    console.log('🔄 HTMX swap – refreshing sliders');
                    await new Promise(r => requestAnimationFrame(r));
                    await this.refreshAll();
                }, 100);
            };
            document.body.addEventListener('htmx:afterSwap', this._listeners.htmx);
        }
    }

    _showFallback() {
        if (!this.options.fallbackEnabled) return;
        console.warn('⚠️ Using static fallback (no Swiper)');
        for (const { element } of this.sliders.values()) {
            const slides = element.querySelectorAll('.swiper-slide, .slider__item, .team__item');
            slides.forEach((s, i) => s.style.display = i === 0 ? 'block' : 'none');
        }
    }

    _debounce(fn, delay) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => fn.apply(this, args), delay);
        };
    }

    _dispatch(name, detail = {}) {
        document.dispatchEvent(new CustomEvent(name, { detail: { ...detail, manager: this }, bubbles: true }));
    }
}

// Auto‑instantiate when sliders are present
if (typeof window !== 'undefined') {
    window.SlidersManager = SlidersComponent;
    if (!SlidersComponent._instance && document.querySelector('.slider__container, .team__list, .swiper')) {
        window.appSliders = new SlidersComponent();
    }
}

export default SlidersComponent;
