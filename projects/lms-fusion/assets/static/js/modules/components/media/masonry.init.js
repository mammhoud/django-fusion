/**
 * Masonry Layout Manager
 * Combines both implementations into a single class with enhanced functionality
 */

export class MasonryManager {
    constructor() {
        this.instances = new Map();
        this.initialized = false;
        this.$ = window.jQuery;
        this.isImagesLoadedAvailable = false;
        
        // Auto-initialize on DOMContentLoaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /**
     * Initialize Masonry Manager
     */
    async init() {
        if (this.initialized) return;
        
        try {
            await this.loadDependencies();
            await this.initializeAllMasonry();
            this.initialized = true;
            console.log('✅ Masonry Manager initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize Masonry Manager:', error);
        }
    }

    /**
     * Load required dependencies
     */
    async loadDependencies() {
        // Check if jQuery is available
        if (!this.$ || !this.$.fn || !this.$.fn.masonry) {
            console.warn('⚠️ jQuery Masonry plugin not available');
            throw new Error('Masonry plugin required');
        }

        // Load imagesLoaded if not available
        if (typeof imagesLoaded === 'undefined') {
            try {
                const imagesLoadedModule = await import('imagesloaded');
                window.imagesLoaded = imagesLoadedModule.default || imagesLoadedModule;
                this.isImagesLoadedAvailable = true;
            } catch (error) {
                console.warn('⚠️ imagesLoaded not available:', error);
                // Fallback: use native images loading
                window.imagesLoaded = this.fallbackImagesLoaded.bind(this);
            }
        } else {
            this.isImagesLoadedAvailable = true;
        }
    }

    /**
     * Fallback for imagesLoaded
     */
    fallbackImagesLoaded(elements, callback) {
        if (typeof elements === 'string') {
            elements = document.querySelectorAll(elements);
        } else if (elements instanceof Element) {
            elements = [elements];
        }

        const totalImages = elements.length;
        let loadedImages = 0;
        
        const checkAllLoaded = () => {
            loadedImages++;
            if (loadedImages === totalImages && callback) {
                callback();
            }
        };

        elements.forEach(element => {
            if (element.complete) {
                checkAllLoaded();
            } else {
                element.onload = checkAllLoaded;
                element.onerror = checkAllLoaded;
            }
        });

        // If no images, call callback immediately
        if (totalImages === 0 && callback) {
            callback();
        }
    }

    /**
     * Initialize all masonry layouts on page
     */
    async initializeAllMasonry() {
        await this.initMasonryGrids();
        await this.initBlogMasonry();
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('masonry:initialized'));
    }

    /**
     * Initialize masonry grids
     */
    async initMasonryGrids() {
        const masonryElements = document.querySelectorAll('.masonry');
        
        if (masonryElements.length === 0) {
            return;
        }

        console.log(`🔄 Initializing ${masonryElements.length} masonry grid(s)...`);

        for (const element of masonryElements) {
            await this.initMasonryElement(element, {
                itemSelector: '.masonry-item',
                percentPosition: true,
                columnWidth: element.dataset.columnWidth || '.masonry-item',
                gutter: element.dataset.gutter || 0,
                fitWidth: element.dataset.fitWidth === 'true'
            });
        }
    }

    /**
     * Initialize blog masonry
     */
    async initBlogMasonry() {
        const blogMasonry = document.querySelector('.blog-masonry');
        
        if (!blogMasonry) {
            return;
        }

        console.log('🔄 Initializing blog masonry...');
        
        await this.initMasonryElement(blogMasonry, {
            itemSelector: '.blog-post-box',
            percentPosition: true,
            columnWidth: blogMasonry.dataset.columnWidth || '.blog-post-box',
            gutter: blogMasonry.dataset.gutter || 0
        });
    }

    /**
     * Initialize masonry on a single element
     */
    async initMasonryElement(element, options = {}) {
        if (!element || this.instances.has(element)) {
            return;
        }

        const instanceId = `masonry_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        return new Promise((resolve, reject) => {
            const onImagesLoaded = () => {
                try {
                    const $element = this.$(element);
                    const masonryInstance = $element.masonry(options);
                    
                    // Store the instance
                    this.instances.set(element, {
                        id: instanceId,
                        element: element,
                        instance: masonryInstance,
                        options: options
                    });

                    // Add resize observer
                    this.addResizeObserver(element);
                    
                    console.log(`✅ Masonry initialized: ${instanceId}`);
                    resolve(masonryInstance);
                } catch (error) {
                    console.error(`❌ Failed to initialize masonry:`, error);
                    reject(error);
                }
            };

            // Wait for images to load
            if (this.isImagesLoadedAvailable) {
                imagesLoaded(element, onImagesLoaded);
            } else {
                // Use fallback
                this.fallbackImagesLoaded(element.querySelectorAll('img'), onImagesLoaded);
            }
        });
    }

    /**
     * Initialize masonry within a container element
     */
    async initInContainer(container) {
        if (!container) {
            return;
        }

        const masonryElements = container.querySelectorAll('.masonry, .blog-masonry');
        
        if (masonryElements.length === 0) {
            return;
        }

        console.log(`🔄 Initializing masonry in container (${masonryElements.length} elements)...`);

        for (const element of masonryElements) {
            if (!this.instances.has(element)) {
                await this.initMasonryElement(element, this.getDefaultOptions(element));
            }
        }
    }

    /**
     * Get default options based on element class
     */
    getDefaultOptions(element) {
        const isBlogMasonry = element.classList.contains('blog-masonry');
        
        return {
            itemSelector: isBlogMasonry ? '.blog-post-box' : '.masonry-item',
            percentPosition: true,
            columnWidth: element.dataset.columnWidth || (isBlogMasonry ? '.blog-post-box' : '.masonry-item'),
            gutter: element.dataset.gutter || 0,
            fitWidth: element.dataset.fitWidth === 'true',
            transitionDuration: '0.4s'
        };
    }

    /**
     * Add resize observer for responsive layouts
     */
    addResizeObserver(element) {
        if (!window.ResizeObserver) {
            return;
        }

        const resizeObserver = new ResizeObserver(() => {
            setTimeout(() => this.refresh(element), 100);
        });

        resizeObserver.observe(element);
        
        // Store observer for cleanup
        if (this.instances.has(element)) {
            const instanceData = this.instances.get(element);
            instanceData.resizeObserver = resizeObserver;
        }
    }

    /**
     * Refresh masonry layout
     */
    refresh(target = null) {
        if (target) {
            // Refresh specific instance
            if (target instanceof Element && this.instances.has(target)) {
                const instanceData = this.instances.get(target);
                if (instanceData && instanceData.instance && instanceData.instance.masonry) {
                    instanceData.instance.masonry('layout');
                    console.log(`♻️ Refreshed masonry: ${instanceData.id}`);
                    return true;
                }
            } else if (typeof target === 'string') {
                // Find by instance ID
                for (const [element, instanceData] of this.instances.entries()) {
                    if (instanceData.id === target) {
                        if (instanceData.instance && instanceData.instance.masonry) {
                            instanceData.instance.masonry('layout');
                            return true;
                        }
                    }
                }
            }
        } else {
            // Refresh all instances
            let refreshedCount = 0;
            this.instances.forEach((instanceData, element) => {
                if (instanceData.instance && instanceData.instance.masonry) {
                    instanceData.instance.masonry('layout');
                    refreshedCount++;
                }
            });
            console.log(`♻️ Refreshed ${refreshedCount} masonry layout(s)`);
            return refreshedCount > 0;
        }
        
        return false;
    }

    /**
     * Add item to masonry
     */
    addItem(target, item) {
        if (!target || !item) {
            return false;
        }

        let element;
        let instanceData;

        if (target instanceof Element) {
            element = target;
        } else if (typeof target === 'string') {
            // Find by instance ID
            for (const [el, data] of this.instances.entries()) {
                if (data.id === target) {
                    element = el;
                    instanceData = data;
                    break;
                }
            }
        }

        if (!element && this.instances.has(target)) {
            element = target;
        }

        if (!element) {
            return false;
        }

        if (!instanceData) {
            instanceData = this.instances.get(element);
        }

        if (instanceData && instanceData.instance && instanceData.instance.masonry) {
            const $item = this.$(item);
            instanceData.instance.masonry('appended', $item);
            
            // Re-layout after images load
            if (this.isImagesLoadedAvailable) {
                imagesLoaded(item, () => {
                    instanceData.instance.masonry('layout');
                });
            } else {
                setTimeout(() => instanceData.instance.masonry('layout'), 100);
            }
            
            console.log(`➕ Added item to masonry: ${instanceData.id}`);
            return true;
        }

        return false;
    }

    /**
     * Remove item from masonry
     */
    removeItem(target, item) {
        if (!target || !item) {
            return false;
        }

        let element;
        let instanceData;

        if (target instanceof Element) {
            element = target;
        } else if (typeof target === 'string') {
            // Find by instance ID
            for (const [el, data] of this.instances.entries()) {
                if (data.id === target) {
                    element = el;
                    instanceData = data;
                    break;
                }
            }
        }

        if (!element && this.instances.has(target)) {
            element = target;
        }

        if (!element) {
            return false;
        }

        if (!instanceData) {
            instanceData = this.instances.get(element);
        }

        if (instanceData && instanceData.instance && instanceData.instance.masonry) {
            const $item = this.$(item);
            instanceData.instance.masonry('remove', $item);
            instanceData.instance.masonry('layout');
            
            console.log(`➖ Removed item from masonry: ${instanceData.id}`);
            return true;
        }

        return false;
    }

    /**
     * Destroy masonry instance
     */
    destroy(target = null) {
        if (target) {
            // Destroy specific instance
            let element;
            
            if (target instanceof Element) {
                element = target;
            } else if (typeof target === 'string') {
                // Find by instance ID
                for (const [el, data] of this.instances.entries()) {
                    if (data.id === target) {
                        element = el;
                        break;
                    }
                }
            }

            if (element && this.instances.has(element)) {
                const instanceData = this.instances.get(element);
                
                // Cleanup resize observer
                if (instanceData.resizeObserver) {
                    instanceData.resizeObserver.disconnect();
                }
                
                // Destroy masonry
                if (instanceData.instance && instanceData.instance.masonry) {
                    instanceData.instance.masonry('destroy');
                }
                
                this.instances.delete(element);
                console.log(`🗑️ Destroyed masonry: ${instanceData.id}`);
                return true;
            }
        } else {
            // Destroy all instances
            let destroyedCount = 0;
            
            this.instances.forEach((instanceData, element) => {
                // Cleanup resize observer
                if (instanceData.resizeObserver) {
                    instanceData.resizeObserver.disconnect();
                }
                
                // Destroy masonry
                if (instanceData.instance && instanceData.instance.masonry) {
                    instanceData.instance.masonry('destroy');
                }
                
                destroyedCount++;
            });
            
            this.instances.clear();
            this.initialized = false;
            
            console.log(`🗑️ Destroyed ${destroyedCount} masonry layout(s)`);
            return destroyedCount > 0;
        }
        
        return false;
    }

    /**
     * Get masonry instance by element or ID
     */
    getInstance(target) {
        if (target instanceof Element && this.instances.has(target)) {
            return this.instances.get(target).instance;
        } else if (typeof target === 'string') {
            for (const [element, instanceData] of this.instances.entries()) {
                if (instanceData.id === target) {
                    return instanceData.instance;
                }
            }
        }
        return null;
    }

    /**
     * Get all masonry instances
     */
    getAllInstances() {
        const instances = {};
        this.instances.forEach((instanceData, element) => {
            instances[instanceData.id] = {
                element: element,
                instance: instanceData.instance,
                options: instanceData.options
            };
        });
        return instances;
    }

    /**
     * Check if masonry is initialized
     */
    isInitialized() {
        return this.initialized;
    }

    /**
     * Reinitialize all masonry layouts (useful after AJAX/DOM updates)
     */
    async reinitialize() {
        console.log('🔄 Reinitializing all masonry layouts...');
        
        // Destroy existing instances
        this.destroy();
        
        // Reinitialize
        await this.initializeAllMasonry();
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('masonry:reinitialized'));
    }

    /**
     * Static method for quick initialization
     */
    static async initialize() {
        if (!window.MasonryManagerInstance) {
            window.MasonryManagerInstance = new MasonryManager();
        }
        return window.MasonryManagerInstance;
    }

    /**
     * Quick refresh static method
     */
    static refresh(target = null) {
        if (window.MasonryManagerInstance) {
            return window.MasonryManagerInstance.refresh(target);
        }
        return false;
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MasonryManager;
}

// Auto-initialize global instance
if (typeof window !== 'undefined') {
    window.MasonryManager = MasonryManager;
    
    // Create global instance for easy access
    document.addEventListener('DOMContentLoaded', () => {
        window.MasonryManagerInstance = new MasonryManager();
    });
}
