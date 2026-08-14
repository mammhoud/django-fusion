/**
 * Enhanced Accordion Manager
 * Combines original Accordion class with BEM styling for FAQ section
 */

class Accordion {
    constructor(options = {}) {
        this.options = {
            titleSelector: '.accordion__button',
            contentSelector: '.accordion__content',
            itemSelector: '.accordion__item',
            containerSelector: '.faq-accordion, .accordion',
            activeClass: 'active',
            singleOpenClass: 'single-open',
            autoInitialize: true,
            ...options
        };
        
        this.initialized = false;
        this.instances = new Map();
        
        if (this.options.autoInitialize) {
            this.init();
        }
    }

    /**
     * Initialize all accordions on the page
     */
    init() {
        if (this.initialized) return;
        
        this.attachEventListeners();
        this.setupInitialState();
        
        this.initialized = true;
        console.log('✅ Enhanced Accordions initialized');
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('accordions:initialized'));
    }

    /**
     * Attach event listeners to accordion titles/buttons
     */
    attachEventListeners() {
        const titles = document.querySelectorAll(this.options.titleSelector);
        
        if (!titles.length) {
            console.warn('⚠️ No accordion elements found');
            return;
        }

        titles.forEach(title => {
            // Remove existing listeners to prevent duplicates
            title.removeEventListener('click', this.handleTitleClick);
            
            // Add new listener
            title.addEventListener('click', (e) => this.handleTitleClick(e));
            
            // Store instance reference
            const accordionContainer = this.findAccordionContainer(title);
            if (accordionContainer) {
                this.instances.set(accordionContainer, {
                    container: accordionContainer,
                    items: accordionContainer.querySelectorAll(this.options.itemSelector)
                });
            }
        });
    }

    /**
     * Handle accordion title click
     */
    handleTitleClick(event) {
        const title = event.currentTarget;
        const accordionItem = title.closest(this.options.itemSelector);
        const content = accordionItem.querySelector(this.options.contentSelector);
        const accordionContainer = this.findAccordionContainer(title);

        if (!accordionItem || !content) return;

        // Check if accordion is already active
        const isActive = accordionItem.classList.contains(this.options.activeClass);

        if (isActive) {
            this.closeAccordionItem(accordionItem, content);
        } else {
            this.openAccordionItem(accordionItem, content, accordionContainer);
        }

        // Dispatch custom event
        const eventName = isActive ? 'accordion:closed' : 'accordion:opened';
        title.dispatchEvent(new CustomEvent(eventName, {
            detail: { accordionItem, content }
        }));
    }

    /**
     * Open an accordion item
     */
    openAccordionItem(item, content, container) {
        // Handle single-open accordions
        if (container && container.classList.contains(this.options.singleOpenClass)) {
            this.closeAllInContainer(container, item);
        }

        // Open the clicked item
        item.classList.add(this.options.activeClass);
        
        // Use modern approach with CSS transitions
        content.style.maxHeight = content.scrollHeight + 'px';
        
        // For smooth animation
        requestAnimationFrame(() => {
            content.style.transition = 'max-height 0.3s ease';
        });

        // Dispatch opening event
        item.dispatchEvent(new CustomEvent('accordion:opening', { bubbles: true }));
    }

    /**
     * Close an accordion item
     */
    closeAccordionItem(item, content) {
        item.classList.remove(this.options.activeClass);
        
        // Animate closing
        content.style.maxHeight = '0';
        
        // Dispatch closing event
        item.dispatchEvent(new CustomEvent('accordion:closing', { bubbles: true }));
    }

    /**
     * Close all accordion items in a container (except specified one)
     */
    closeAllInContainer(container, exceptItem = null) {
        const items = container.querySelectorAll(this.options.itemSelector);
        
        items.forEach(item => {
            if (exceptItem && item === exceptItem) return;
            
            const content = item.querySelector(this.options.contentSelector);
            if (item.classList.contains(this.options.activeClass) && content) {
                this.closeAccordionItem(item, content);
            }
        });
    }

    /**
     * Find the accordion container for an item
     */
    findAccordionContainer(element) {
        return element.closest(this.options.containerSelector);
    }

    /**
     * Set up initial state for accordions
     */
    setupInitialState() {
        const containers = document.querySelectorAll(this.options.containerSelector);
        
        containers.forEach(container => {
            const activeItems = container.querySelectorAll(`${this.options.itemSelector}.${this.options.activeClass}`);
            
            activeItems.forEach(item => {
                const content = item.querySelector(this.options.contentSelector);
                if (content) {
                    content.style.maxHeight = content.scrollHeight + 'px';
                }
            });
        });
    }

    /**
     * Open a specific accordion item
     */
    openItem(itemOrSelector) {
        let item;
        
        if (typeof itemOrSelector === 'string') {
            item = document.querySelector(itemOrSelector);
        } else if (itemOrSelector instanceof Element) {
            item = itemOrSelector;
        }
        
        if (!item || !item.matches(this.options.itemSelector)) {
            console.warn('Invalid accordion item');
            return false;
        }
        
        const content = item.querySelector(this.options.contentSelector);
        const container = this.findAccordionContainer(item);
        
        if (content) {
            this.openAccordionItem(item, content, container);
            return true;
        }
        
        return false;
    }

    /**
     * Close a specific accordion item
     */
    closeItem(itemOrSelector) {
        let item;
        
        if (typeof itemOrSelector === 'string') {
            item = document.querySelector(itemOrSelector);
        } else if (itemOrSelector instanceof Element) {
            item = itemOrSelector;
        }
        
        if (!item || !item.matches(this.options.itemSelector)) {
            console.warn('Invalid accordion item');
            return false;
        }
        
        const content = item.querySelector(this.options.contentSelector);
        
        if (content && item.classList.contains(this.options.activeClass)) {
            this.closeAccordionItem(item, content);
            return true;
        }
        
        return false;
    }

    /**
     * Open all accordion items in a container
     */
    openAll(containerOrSelector) {
        let container;
        
        if (typeof containerOrSelector === 'string') {
            container = document.querySelector(containerOrSelector);
        } else if (containerOrSelector instanceof Element) {
            container = containerOrSelector;
        }
        
        if (!container) return false;
        
        const items = container.querySelectorAll(this.options.itemSelector);
        let openedCount = 0;
        
        items.forEach(item => {
            if (!item.classList.contains(this.options.activeClass)) {
                const content = item.querySelector(this.options.contentSelector);
                if (content) {
                    this.openAccordionItem(item, content, container);
                    openedCount++;
                }
            }
        });
        
        return openedCount > 0;
    }

    /**
     * Close all accordion items in a container
     */
    closeAll(containerOrSelector) {
        let container;
        
        if (typeof containerOrSelector === 'string') {
            container = document.querySelector(containerOrSelector);
        } else if (containerOrSelector instanceof Element) {
            container = containerOrSelector;
        }
        
        if (!container) return false;
        
        const items = container.querySelectorAll(this.options.itemSelector);
        let closedCount = 0;
        
        items.forEach(item => {
            if (item.classList.contains(this.options.activeClass)) {
                const content = item.querySelector(this.options.contentSelector);
                if (content) {
                    this.closeAccordionItem(item, content);
                    closedCount++;
                }
            }
        });
        
        return closedCount > 0;
    }

    /**
     * Toggle all accordion items in a container
     */
    toggleAll(containerOrSelector) {
        let container;
        
        if (typeof containerOrSelector === 'string') {
            container = document.querySelector(containerOrSelector);
        } else if (containerOrSelector instanceof Element) {
            container = containerOrSelector;
        }
        
        if (!container) return false;
        
        const items = container.querySelectorAll(this.options.itemSelector);
        const allOpen = Array.from(items).every(item => 
            item.classList.contains(this.options.activeClass)
        );
        
        if (allOpen) {
            return this.closeAll(container);
        } else {
            return this.openAll(container);
        }
    }

    /**
     * Refresh accordion content heights
     */
    refresh() {
        const containers = document.querySelectorAll(this.options.containerSelector);
        
        containers.forEach(container => {
            const items = container.querySelectorAll(this.options.itemSelector);
            
            items.forEach(item => {
                const content = item.querySelector(this.options.contentSelector);
                if (item.classList.contains(this.options.activeClass) && content) {
                    content.style.maxHeight = content.scrollHeight + 'px';
                }
            });
        });
        
        return true;
    }

    /**
     * Reinitialize accordions (useful after dynamic content updates)
     */
    reinitialize() {
        this.instances.clear();
        this.attachEventListeners();
        this.setupInitialState();
        
        document.dispatchEvent(new CustomEvent('accordions:reinitialized'));
        return true;
    }

    /**
     * Destroy accordion instances and remove event listeners
     */
    destroy() {
        const titles = document.querySelectorAll(this.options.titleSelector);
        
        titles.forEach(title => {
            title.removeEventListener('click', this.handleTitleClick);
        });
        
        this.instances.clear();
        this.initialized = false;
        
        document.dispatchEvent(new CustomEvent('accordions:destroyed'));
        return true;
    }

    /**
     * Static method for quick initialization
     */
    static initialize(options = {}) {
        if (!window.EnhancedAccordionInstance) {
            window.EnhancedAccordionInstance = new Accordion(options);
        }
        return window.EnhancedAccordionInstance;
    }
}

// Auto-initialize when DOM is ready
if (typeof document !== 'undefined') {
    // Create global instance for easy access
    window.Accordion = Accordion;
    
    // Auto-initialize with default options
    document.addEventListener('DOMContentLoaded', () => {
        window.Accordion = new Accordion();
    });
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Accordion;
}

export default Accordion;