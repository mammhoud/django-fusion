/**
 * Tag Filter Component
 * Provides tabbed interface for filtering content by tags
 * Supports both portfolio and blog pages
 */

export class TagFilterComponent {
    constructor({ element, manager } = {}) {
        this.element = element;
        this.manager = manager;
        this.filterContainer = null;
        this.contentItems = [];
        this.tags = [];
        this.activeTag = 'all';
    }

    /**
     * Initialize tag filter component
     */
    init() {
        if (!this.element) return false;

        try {
            this.setupFilterUI();
            this.bindEvents();
            console.log('✅ Tag filter component initialized');
            return true;
        } catch (error) {
            console.error('Failed to initialize tag filter:', error);
            return false;
        }
    }

    /**
     * Setup filter UI with tabs
     */
    setupFilterUI() {
        // Find content items
        this.contentItems = this.element.querySelectorAll('[data-tags]');
        if (this.contentItems.length === 0) {
            console.debug('No tagged content items found');
            return;
        }

        // Extract unique tags
        const tagSet = new Set();
        this.contentItems.forEach(item => {
            const tags = item.getAttribute('data-tags');
            if (tags) {
                tags.split(',').forEach(tag => {
                    tagSet.add(tag.trim());
                });
            }
        });

        this.tags = Array.from(tagSet).sort();

        // Create filter UI
        this.createFilterUI();
    }

    /**
     * Create filter tabs UI
     */
    createFilterUI() {
        // Check if filter UI already exists
        let filterUI = this.element.querySelector('[data-tag-filter-ui]');
        if (filterUI) {
            return; // Already created
        }

        // Create filter container
        filterUI = document.createElement('div');
        filterUI.className = 'tag-filter-ui';
        filterUI.setAttribute('data-tag-filter-ui', '');

        // Create tabs container
        const tabsContainer = document.createElement('div');
        tabsContainer.className = 'tag-filter-tabs';

        // Add "All" tab
        const allTab = this.createTab('all', 'All', true);
        tabsContainer.appendChild(allTab);

        // Add tag tabs
        this.tags.forEach(tag => {
            const tab = this.createTab(tag, tag, false);
            tabsContainer.appendChild(tab);
        });

        filterUI.appendChild(tabsContainer);

        // Insert before content
        this.element.insertBefore(filterUI, this.element.firstChild);
    }

    /**
     * Create individual tab element
     */
    createTab(value, label, isActive = false) {
        const tab = document.createElement('button');
        tab.className = `tag-filter-tab ${isActive ? 'active' : ''}`;
        tab.setAttribute('data-tag-value', value);
        tab.textContent = label;
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-selected', isActive);

        return tab;
    }

    /**
     * Bind event listeners using stored handler references for proper cleanup
     */
    bindEvents() {
        this._boundHandleTabClick = (e) => this.handleTabClick(e);
        this._boundHandleKeypress = (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.handleTabClick(e);
            }
        };

        const tabs = this.element.querySelectorAll('[data-tag-filter-ui] .tag-filter-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', this._boundHandleTabClick);
            tab.addEventListener('keypress', this._boundHandleKeypress);
        });
    }

    /**
     * Handle tab click
     */
    handleTabClick(event) {
        const tab = event.currentTarget;
        const tagValue = tab.getAttribute('data-tag-value');

        // Update active tab
        const tabs = this.element.querySelectorAll('[data-tag-filter-ui] .tag-filter-tab');
        tabs.forEach(t => {
            t.classList.remove('active');
            t.setAttribute('aria-selected', 'false');
        });
        tab.classList.add('active');
        tab.setAttribute('aria-selected', 'true');

        // Filter content
        this.filterContent(tagValue);
        this.activeTag = tagValue;
    }

    /**
     * Filter content items by tag
     */
    filterContent(tagValue) {
        this.contentItems.forEach(item => {
            if (tagValue === 'all') {
                item.style.display = '';
                item.classList.add('fade-in');
            } else {
                const tags = item.getAttribute('data-tags');
                const hasTag = tags && tags.split(',').map(t => t.trim()).includes(tagValue);
                item.style.display = hasTag ? '' : 'none';
                if (hasTag) {
                    item.classList.add('fade-in');
                }
            }
        });
    }

    /**
     * Get active tag
     */
    getActiveTag() {
        return this.activeTag;
    }

    /**
     * Set active tag programmatically
     */
    setActiveTag(tagValue) {
        const tab = this.element.querySelector(`[data-tag-filter-ui] [data-tag-value="${tagValue}"]`);
        if (tab) {
            tab.click();
        }
    }

    /**
     * Cleanup
     */
    destroy() {
        const tabs = this.element.querySelectorAll('[data-tag-filter-ui] .tag-filter-tab');
        tabs.forEach(tab => {
            tab.removeEventListener('click', this._boundHandleTabClick);
            tab.removeEventListener('keypress', this._boundHandleKeypress);
        });
    }
}

export default TagFilterComponent;
