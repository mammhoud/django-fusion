/**
 * Listing Component
 * Handles grid/list view switcher, search, and filtering with data-tag extraction
 */

import { debounce, Utils, DOM } from '../../utility/index.js';

export class Listing {
    constructor(options = {}) {
        this.options = {
            containerSelector: '.listing-container',
            itemSelector: '.listing-item',
            searchInputSelector: '.listing-search',
            filterSelector: '.listing-filters',
            viewSwitcherSelector: '.view-switcher',
            gridViewClass: 'grid-view',
            listViewClass: 'list-view',
            activeFilterClass: 'active',
            debounceDelay: 300,
            ...options
        };

        this.currentView = 'grid';
        this.currentSearch = '';
        this.activeFilters = new Set();
        this.items = [];
        this.allTags = new Set();
        this.debounceTimer = null;

        this.init();
    }

    async init() {
        console.log('🔄 Initializing listing...');

        await this.collectItems();
        this.extractTags();
        this.initViewSwitcher();
        this.initSearch();
        this.initFilters();
        this.renderFilters();

        console.log(`✅ Listing initialized with ${this.items.length} items`);
    }

    /**
     * Collect listing items from DOM
     */
    collectItems() {
        const itemElements = DOM.$$(this.options.itemSelector);
        this.items = Array.from(itemElements).map((element, index) => ({
            id: element.dataset.id || `item-${index}`,
            element: element,
            title: element.dataset.title || element.querySelector('.title')?.textContent || '',
            description: element.dataset.description || element.querySelector('.description')?.textContent || '',
            category: element.dataset.category || '',
            tags: element.dataset.tags ? element.dataset.tags.split(' ').filter(tag => tag.trim()) : [],
            content: element.innerHTML,
            data: this.extractDataAttributes(element)
        }));
    }

    /**
     * Extract all data attributes from element
     */
    extractDataAttributes(element) {
        const data = {};
        Array.from(element.attributes).forEach(attr => {
            if (attr.name.startsWith('data-')) {
                const key = attr.name.replace('data-', '').replace(/-([a-z])/g, (g) => g[1].toUpperCase());
                data[key] = attr.value;
            }
        });
        return data;
    }

    /**
     * Extract unique tags from all items
     */
    extractTags() {
        this.allTags.clear();
        this.items.forEach(item => {
            item.tags.forEach(tag => this.allTags.add(tag));
        });
    }

    /**
     * Initialize view switcher (grid/list)
     */
    initViewSwitcher() {
        const switchers = DOM.$$(this.options.viewSwitcherSelector);

        switchers.forEach(switcher => {
            // Grid view button
            const gridBtn = switcher.querySelector('[data-view="grid"]');
            if (gridBtn) {
                DOM.on(gridBtn, 'click', () => this.switchView('grid'));
            }

            // List view button
            const listBtn = switcher.querySelector('[data-view="list"]');
            if (listBtn) {
                DOM.on(listBtn, 'click', () => this.switchView('list'));
            }
        });
    }

    /**
     * Initialize search functionality
     */
    initSearch() {
        const searchInputs = DOM.$$(this.options.searchInputSelector);

        searchInputs.forEach(input => {
            // Input event with debounce
            DOM.on(input, 'input', (e) => {
                this.debouncedSearch(e.target.value);
            });

            // Clear button if exists
            const clearBtn = input.parentNode.querySelector('.search-clear');
            if (clearBtn) {
                DOM.on(clearBtn, 'click', () => {
                    input.value = '';
                    this.search('');
                });
            }
        });
    }

    /**
     * Initialize filter functionality
     */
    initFilters() {
        const filterContainer = DOM.$(this.options.filterSelector);
        if (!filterContainer) return;

        // Event delegation for filter buttons
        DOM.on(filterContainer, 'click', (e) => {
            const filterBtn = e.target.closest('[data-filter]');
            if (!filterBtn) return;

            e.preventDefault();
            const filterValue = filterBtn.dataset.filter;
            this.toggleFilter(filterValue);

            // Update active state
            const allFilterBtns = filterContainer.querySelectorAll('[data-filter]');
            allFilterBtns.forEach(btn => {
                if (btn.dataset.filter === filterValue) {
                    DOM.toggleClass(btn, this.options.activeFilterClass);
                } else if (filterValue === 'all') {
                    DOM.removeClass(btn, this.options.activeFilterClass);
                }
            });
        });
    }

    /**
     * Render filter buttons based on extracted tags
     */
    renderFilters() {
        const filterContainer = DOM.$(this.options.filterSelector);
        if (!filterContainer) return;

        // Clear existing filters
        filterContainer.innerHTML = '';

        // Add "All" filter
        const allFilter = document.createElement('button');
        allFilter.type = 'button';
        allFilter.className = `filter-btn ${this.options.activeFilterClass}`;
        allFilter.dataset.filter = 'all';
        allFilter.textContent = 'All';
        filterContainer.appendChild(allFilter);

        // Add tag filters
        Array.from(this.allTags).sort().forEach(tag => {
            const filterBtn = document.createElement('button');
            filterBtn.type = 'button';
            filterBtn.className = 'filter-btn';
            filterBtn.dataset.filter = tag;
            filterBtn.textContent = tag;
            filterContainer.appendChild(filterBtn);
        });

        // Re-bind events
        this.initFilters();
    }

    /**
     * Switch between grid and list view
     */
    switchView(viewType) {
        if (this.currentView === viewType) return;

        this.currentView = viewType;
        const container = DOM.$(this.options.containerSelector);

        if (!container) return;

        // Update container classes
        DOM.removeClass(container, this.options.gridViewClass);
        DOM.removeClass(container, this.options.listViewClass);
        DOM.addClass(container, `${viewType}-view`);

        // Update switcher buttons
        const switchers = DOM.$$(this.options.viewSwitcherSelector);
        switchers.forEach(switcher => {
            switcher.querySelectorAll('[data-view]').forEach(btn => {
                if (btn.dataset.view === viewType) {
                    DOM.addClass(btn, 'active');
                } else {
                    DOM.removeClass(btn, 'active');
                }
            });
        });

        // Dispatch event
        DOM.trigger(container, 'listing:viewChanged', { view: viewType });

        console.log(`🔀 Switched to ${viewType} view`);
    }

    /**
     * Perform search with debouncing
     */
    debouncedSearch(searchTerm) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.search(searchTerm);
        }, this.options.debounceDelay);
    }

    /**
     * Search items by title, description, and tags
     */
    search(searchTerm) {
        this.currentSearch = searchTerm.toLowerCase().trim();
        this.updateDisplay();

        // Dispatch event
        DOM.trigger(document, 'listing:searched', {
            searchTerm: searchTerm,
            results: this.getVisibleItems()
        });
    }

    /**
     * Toggle filter on/off
     */
    toggleFilter(filterValue) {
        if (filterValue === 'all') {
            this.activeFilters.clear();
        } else {
            if (this.activeFilters.has(filterValue)) {
                this.activeFilters.delete(filterValue);
            } else {
                this.activeFilters.add(filterValue);
            }
        }

        this.updateDisplay();

        // Dispatch event
        DOM.trigger(document, 'listing:filtered', {
            filters: Array.from(this.activeFilters),
            items: this.getVisibleItems()
        });
    }

    /**
     * Update item display based on current filters and search
     */
    updateDisplay() {
        this.items.forEach(item => {
            const isVisible = this.isItemVisible(item);
            item.element.style.display = isVisible ? '' : 'none';

            // Add/remove visibility class
            if (isVisible) {
                DOM.removeClass(item.element, 'hidden');
            } else {
                DOM.addClass(item.element, 'hidden');
            }
        });

        // Update counter if exists
        this.updateCounter();
    }

    /**
     * Check if item should be visible
     */
    isItemVisible(item) {
        // Check search term
        if (this.currentSearch) {
            const inTitle = item.title.toLowerCase().includes(this.currentSearch);
            const inDescription = item.description.toLowerCase().includes(this.currentSearch);
            const inTags = item.tags.some(tag => tag.toLowerCase().includes(this.currentSearch));

            if (!inTitle && !inDescription && !inTags) {
                return false;
            }
        }

        // Check filters
        if (this.activeFilters.size > 0) {
            const hasMatchingFilter = item.tags.some(tag => this.activeFilters.has(tag));
            if (!hasMatchingFilter) return false;
        }

        return true;
    }

    /**
     * Update results counter
     */
    updateCounter() {
        const counter = DOM.$('.listing-counter');
        if (!counter) return;

        const visibleCount = this.getVisibleItems().length;
        counter.textContent = `Showing ${visibleCount} of ${this.items.length} items`;
    }

    /**
     * Get currently visible items
     */
    getVisibleItems() {
        return this.items.filter(item => this.isItemVisible(item));
    }

    /**
     * Add new item to listing
     */
    addItem(itemData) {
        const container = DOM.$(this.options.containerSelector);
        if (!container) return;

        const newItem = document.createElement('div');
        newItem.className = 'listing-item';
        newItem.dataset.id = itemData.id;
        newItem.dataset.title = itemData.title;
        newItem.dataset.description = itemData.description;
        newItem.dataset.tags = itemData.tags.join(' ');
        newItem.innerHTML = itemData.content;

        container.appendChild(newItem);

        // Re-initialize to update collection
        this.collectItems();
        this.extractTags();
        this.renderFilters();
        this.updateDisplay();
    }

    /**
     * Remove item from listing
     */
    removeItem(itemId) {
        const itemElement = DOM.$(`[data-id="${itemId}"]`);
        if (itemElement) {
            itemElement.remove();
            this.collectItems();
            this.extractTags();
            this.renderFilters();
            this.updateDisplay();
        }
    }

    /**
     * Get all unique tags
     */
    getTags() {
        return Array.from(this.allTags);
    }

    /**
     * Get filtered items by tag
     */
    getItemsByTag(tag) {
        return this.items.filter(item => item.tags.includes(tag));
    }

    /**
     * Export listing data
     */
    exportData(format = 'json') {
        const data = {
            items: this.items.map(item => ({
                id: item.id,
                title: item.title,
                description: item.description,
                tags: item.tags,
                category: item.category,
                data: item.data
            })),
            tags: this.getTags(),
            currentView: this.currentView,
            activeFilters: Array.from(this.activeFilters),
            searchTerm: this.currentSearch,
            visibleItems: this.getVisibleItems().length,
            totalItems: this.items.length
        };

        if (format === 'csv') {
            return this.convertToCSV(data);
        }

        return JSON.stringify(data, null, 2);
    }

    /**
     * Convert data to CSV format
     */
    convertToCSV(data) {
        const items = data.items;
        if (items.length === 0) return '';

        const headers = ['ID', 'Title', 'Description', 'Tags', 'Category'];
        const rows = items.map(item => [
            item.id,
            `"${item.title.replace(/"/g, '""')}"`,
            `"${item.description.replace(/"/g, '""')}"`,
            `"${item.tags.join(', ')}"`,
            item.category
        ]);

        return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    }

    /**
     * Destroy listing instance
     */
    destroy() {
        // Remove all event listeners
        const searchInputs = DOM.$$(this.options.searchInputSelector);
        searchInputs.forEach(input => {
            DOM.off(input, 'input');
        });

        const filterContainer = DOM.$(this.options.filterSelector);
        if (filterContainer) {
            DOM.off(filterContainer, 'click');
        }

        console.log('🛑 Listing destroyed');
    }
}

// Auto-initialize listing components
document.addEventListener('DOMContentLoaded', () => {
    const listingElements = DOM.$$('[data-listing]');

    listingElements.forEach(element => {
        const options = JSON.parse(element.dataset.listing || '{}');
        const listing = new Listing(options);

        // Store instance on element
        element.listingInstance = listing;
    });
});

export default Listing;