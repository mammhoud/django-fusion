// portfolio.js - Merged Portfolio Component
import { debounce, Utils, DOM } from '../../../utility/index.js';
import { ModalController } from '../modal.init.js';

/**
 * Portfolio Component (Masonry & Grid)
 * Handles portfolio grid layouts with filtering and interactive features
 */
export class Portfolio {
    constructor(options = {}) {
        this.initialized = false;
        this.masonryInstance = null;
        this.mixitupInstance = null;
        this.activeFilter = 'all';
        this.portfolioItems = [];
        this.modals = new Map();

        // Configuration with defaults
        this.options = {
            containerSelector: '.portfolio-grid',
            itemSelector: '.portfolio-item',
            filterSelector: '.portfolio-filter',
            masonryEnabled: true,
            gridEnabled: true,
            loadDependencies: true,
            apiUrl: null,
            updateUrl: false,
            ...options
        };
    }

    /**
     * Initialize portfolio
     */
    async init() {
        if (this.initialized) return;

        console.log('🔄 Initializing portfolio...');

        try {
            // Load external dependencies if needed
            if (this.options.loadDependencies) {
                await this.loadMixitup();
                await this.loadImagesLoaded();
            }

            // Initialize core functionality
            await this.loadPortfolioItems();
            this.initPortfolioMasonry();
            this.initPortfolioGrid();
            this.initFilters();
            this.initModals();
            this.initEvents();

            this.initialized = true;
            console.log('✅ Portfolio initialized successfully');
        } catch (error) {
            console.error('Failed to initialize portfolio:', error);
        }
    }

    /**
     * Load Mixitup library dynamically
     */
    async loadMixitup() {
        if (typeof mixitup === 'undefined') {
            try {
                const mixitupModule = await import('mixitup');
                window.mixitup = mixitupModule.default || mixitupModule;
            } catch (error) {
                console.warn('Mixitup not available:', error);
                this.options.gridEnabled = false;
            }
        }
    }

    /**
     * Load ImagesLoaded library dynamically
     */
    async loadImagesLoaded() {
        if (typeof imagesLoaded === 'undefined') {
            try {
                const imagesLoadedModule = await import('imagesloaded');
                window.imagesLoaded = imagesLoadedModule.default || imagesLoadedModule;
            } catch (error) {
                console.warn('ImagesLoaded not available:', error);
                this.options.masonryEnabled = false;
            }
        }
    }

    /**
     * Load portfolio items from server or static data
     */
    async loadPortfolioItems() {
        // Check if we need to fetch from an API
        if (this.options.apiUrl) {
            try {
                const response = await fetch(this.options.apiUrl);
                this.portfolioItems = await response.json();
                this.renderItems();
            } catch (error) {
                console.warn('Using static portfolio items:', error);
                this.collectStaticItems();
            }
        } else {
            this.collectStaticItems();
        }
    }

    /**
     * Collect static portfolio items from DOM
     */
    collectStaticItems() {
        const items = Utils.$$(this.options.itemSelector);
        this.portfolioItems = Array.from(items).map(item => ({
            id: item.dataset.id || Math.random().toString(36).substr(2, 9),
            element: item,
            category: item.dataset.category || 'all',
            tags: item.dataset.tags ? item.dataset.tags.split(' ') : [],
            title: item.dataset.title || '',
            description: item.dataset.description || '',
            data: item.dataset
        }));
    }

    /**
     * Render portfolio items (if using dynamic data)
     */
    renderItems() {
        if (!this.options.container || this.portfolioItems.length === 0) return;

        const container = Utils.$(this.options.containerSelector);
        if (!container) return;

        container.innerHTML = this.portfolioItems.map(item => `
            <div class="portfolio-item grid-item" 
                 data-id="${item.id}"
                 data-category="${item.category}"
                 data-tags="${item.tags.join(' ')}"
                 data-title="${item.title}">
                ${item.content || ''}
            </div>
        `).join('');
    }

    /**
     * Initialize portfolio masonry layout
     */
    initPortfolioMasonry() {
        if (!this.options.masonryEnabled) return;

        const portfolioMasonry = Utils.$(this.options.containerSelector);

        if (!portfolioMasonry) {
            console.log('ℹ️ Portfolio masonry container not found');
            return;
        }

        // Check for required libraries
        if (typeof $ === 'undefined' || typeof $.fn.isotope === 'undefined') {
            console.warn('⚠️ jQuery/Isotope not loaded, skipping masonry');
            return;
        }

        if (typeof imagesLoaded === 'undefined') {
            console.warn('⚠️ ImagesLoaded not available, skipping masonry');
            return;
        }

        // Initialize masonry with imagesLoaded
        window.imagesLoaded(portfolioMasonry, () => {
            try {
                this.masonryInstance = $(portfolioMasonry).isotope({
                    itemSelector: this.options.itemSelector,
                    layoutMode: 'masonry',
                    masonry: {
                        columnWidth: this.options.itemSelector,
                        gutter: 20
                    },
                    transitionDuration: '250ms',
                    filter: this.activeFilter === 'all' ? '*' : this.activeFilter,
                    stagger: 30
                });

                console.log('✅ Portfolio masonry initialized');
            } catch (error) {
                console.error('Failed to initialize portfolio masonry:', error);
            }
        });
    }

    /**
     * Initialize portfolio grid with Mixitup
     */
    initPortfolioGrid() {
        if (!this.options.gridEnabled) return;

        const portfolioGrid = Utils.$(this.options.containerSelector);

        if (!portfolioGrid) {
            console.log('ℹ️ Portfolio grid container not found');
            return;
        }

        if (typeof mixitup === 'undefined') {
            console.warn('⚠️ Mixitup not available, skipping grid');
            return;
        }

        try {
            this.mixitupInstance = mixitup(portfolioGrid, {
                selectors: {
                    target: this.options.itemSelector
                },
                animation: {
                    duration: 250,
                    effects: 'fade scale(0.4)'
                },
                load: {
                    filter: this.activeFilter === 'all' ? 'all' : this.activeFilter
                },
                classNames: {
                    block: 'portfolio-grid',
                    elementFilter: 'portfolio-filter__item',
                    modifierActive: 'portfolio-filter__item--active'
                }
            });

            console.log('✅ Portfolio grid initialized');
        } catch (error) {
            console.error('Failed to initialize portfolio grid:', error);
        }
    }

    /**
     * Initialize portfolio filters
     */
    initFilters() {
        const filterButtons = Utils.$$(`${this.options.filterSelector} [data-filter]`);

        if (filterButtons.length === 0) {
            console.log('ℹ️ No filter buttons found');
            return;
        }

        filterButtons.forEach(button => {
            Utils.on(button, 'click', (e) => {
                e.preventDefault();

                const filterValue = button.dataset.filter || 'all';
                this.filterPortfolio(filterValue);

                // Update active state
                filterButtons.forEach(btn => {
                    btn.classList.remove('active', 'portfolio-filter__item--active');
                });
                button.classList.add('active', 'portfolio-filter__item--active');

                // Update active filter
                this.activeFilter = filterValue;

                // Dispatch custom event
                this.dispatchFilterEvent(filterValue);
            });
        });

        console.log(`✅ ${filterButtons.length} filter buttons initialized`);
    }

    /**
     * Initialize event listeners
     */
    initEvents() {
        // Handle window resize with debounce
        const handleResize = debounce(() => {
            if (this.masonryInstance) {
                this.masonryInstance.isotope('layout');
            }
        }, 250);

        window.addEventListener('resize', handleResize);

        // Handle lazy loaded images
        const lazyImages = Utils.$$(`${this.options.itemSelector} img[data-src]`);
        if (lazyImages.length > 0 && 'IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);

                        // Refresh layout after image loads
                        img.onload = () => {
                            if (this.masonryInstance) {
                                this.masonryInstance.isotope('layout');
                            }
                        };
                    }
                });
            });

            lazyImages.forEach(img => imageObserver.observe(img));
        }
    }

    /**
     * Initialize portfolio item modals
     */
    initModals() {
        const modalTriggers = Utils.$$(`${this.options.itemSelector} [data-modal]`);

        modalTriggers.forEach(trigger => {
            Utils.on(trigger, 'click', (e) => {
                e.preventDefault();
                const modalId = trigger.dataset.modal;
                this.openPortfolioModal(modalId);
            });
        });
    }

    /**
     * Filter portfolio items
     */
    filterPortfolio(filterValue) {
        // Filter masonry
        if (this.masonryInstance && this.masonryInstance.isotope) {
            this.masonryInstance.isotope({
                filter: filterValue === 'all' ? '*' : filterValue
            });
        }

        // Filter mixitup
        if (this.mixitupInstance && this.mixitupInstance.filter) {
            this.mixitupInstance.filter(filterValue);
        }

        // Update URL hash
        if (this.options.updateUrl) {
            const url = new URL(window.location);
            url.hash = `filter=${filterValue}`;
            window.history.replaceState(null, null, url.toString());
        }

        console.log(`🔍 Filter applied: ${filterValue}`);
    }

    /**
     * Dispatch filter event
     */
    dispatchFilterEvent(filterValue) {
        const event = new CustomEvent('portfolio:filter', {
            detail: {
                filter: filterValue,
                items: this.getFilteredItems(filterValue),
                timestamp: Date.now()
            },
            bubbles: true
        });

        document.dispatchEvent(event);
    }

    /**
     * Open portfolio modal
     */
    openPortfolioModal(modalId) {
        const modalElement = Utils.$(`#${modalId}`);
        if (!modalElement) {
            console.warn(`Modal #${modalId} not found`);
            return;
        }

        // Check if modal already exists
        if (!this.modals.has(modalId)) {
            const modal = new ModalController(modalElement);
            this.modals.set(modalId, modal);
        }

        // Trigger modal open
        this.modals.get(modalId).open();
    }

    /**
     * Refresh portfolio layout
     */
    refresh() {
        if (this.masonryInstance && this.masonryInstance.isotope) {
            this.masonryInstance.isotope('layout');
            return true;
        }
        return false;
    }

    /**
     * Sort portfolio items
     */
    sortBy(attribute, order = 'asc') {
        if (this.masonryInstance && this.masonryInstance.isotope) {
            this.masonryInstance.isotope({
                sortBy: attribute,
                sortAscending: order === 'asc'
            });
            return true;
        }
        return false;
    }

    /**
     * Get filtered items
     */
    getFilteredItems(filterValue = null) {
        const filter = filterValue || this.activeFilter;

        if (filter === 'all') return this.portfolioItems;

        return this.portfolioItems.filter(item => {
            if (item.category === filter) return true;
            if (item.tags && item.tags.includes(filter)) return true;
            return false;
        });
    }

    /**
     * Get unique categories
     */
    getCategories() {
        const categories = new Set(['all']);
        this.portfolioItems.forEach(item => {
            categories.add(item.category);
            item.tags?.forEach(tag => categories.add(tag));
        });
        return Array.from(categories);
    }

    /**
     * Update filter buttons based on available categories
     */
    updateFilterButtons() {
        const categories = this.getCategories();
        const filterContainer = Utils.$(this.options.filterSelector);

        if (!filterContainer) return;

        filterContainer.innerHTML = categories.map(category => `
            <button class="portfolio-filter__item ${category === 'all' ? 'portfolio-filter__item--active' : ''}" 
                    data-filter="${category === 'all' ? 'all' : `.${category}`}">
                ${this.formatCategoryName(category)}
                <span class="portfolio-filter__count" data-category="${category}"></span>
            </button>
        `).join('');

        // Re-initialize filters
        this.initFilters();
        this.updateFilterCounts();
    }

    /**
     * Update count badges on filter buttons
     */
    updateFilterCounts() {
        const counts = {};

        // Count items per category
        this.portfolioItems.forEach(item => {
            counts[item.category] = (counts[item.category] || 0) + 1;
            item.tags?.forEach(tag => {
                counts[tag] = (counts[tag] || 0) + 1;
            });
        });

        // Update count elements
        Object.entries(counts).forEach(([category, count]) => {
            const countElement = Utils.$(`[data-category="${category}"]`);
            if (countElement) {
                countElement.textContent = `(${count})`;
            }
        });

        // Update 'all' count
        const allCountElement = Utils.$('[data-category="all"]');
        if (allCountElement) {
            allCountElement.textContent = `(${this.portfolioItems.length})`;
        }
    }

    /**
     * Format category name for display
     */
    formatCategoryName(category) {
        return category.split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }

    /**
     * Destroy portfolio instances
     */
    destroy() {
        if (this.masonryInstance && this.masonryInstance.isotope) {
            this.masonryInstance.isotope('destroy');
            this.masonryInstance = null;
        }

        if (this.mixitupInstance && this.mixitupInstance.destroy) {
            this.mixitupInstance.destroy();
            this.mixitupInstance = null;
        }

        // Destroy modals
        this.modals.forEach(modal => modal.destroy());
        this.modals.clear();

        // Remove event listeners
        const filterButtons = Utils.$$(`${this.options.filterSelector} [data-filter]`);
        filterButtons.forEach(button => {
            button.replaceWith(button.cloneNode(true));
        });

        this.initialized = false;
        console.log('🛑 Portfolio destroyed');
    }
}

// Export singleton instance for convenience
export const portfolio = new Portfolio();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const portfolioElements = document.querySelectorAll('[data-portfolio]');

    portfolioElements.forEach(element => {
        try {
            const options = JSON.parse(element.dataset.portfolio || '{}');
            const instance = new Portfolio(options);
            instance.init();
        } catch (error) {
            console.error('Failed to parse portfolio options:', error);
        }
    });
});

// Global access for debugging
window.Portfolio = Portfolio;