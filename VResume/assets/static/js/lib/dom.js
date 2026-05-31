/**
 * DOM Manager - Comprehensive DOM manipulation and querying helpers
 * Combines all DOM utilities with caching, event handling, and more
 */

// ============================================
// SELECTOR CACHE
// ============================================

const selectorCache = new Map();

class SelectorCache {
    /**
     * Get element from cache or query
     */
    static get(selector, context = document) {
        const cacheKey = `${selector}_${context === document ? 'doc' : context.id || 'ctx'}`;
        
        if (selectorCache.has(cacheKey)) {
            return selectorCache.get(cacheKey);
        }
        
        const element = context.querySelector(selector);
        if (element) {
            selectorCache.set(cacheKey, element);
        }
        
        return element;
    }
    
    /**
     * Get all elements from cache or query
     */
    static getAll(selector, context = document) {
        const cacheKey = `all_${selector}_${context === document ? 'doc' : context.id || 'ctx'}`;
        
        if (selectorCache.has(cacheKey)) {
            return selectorCache.get(cacheKey);
        }
        
        const elements = context.querySelectorAll(selector);
        selectorCache.set(cacheKey, elements);
        return elements;
    }
    
    /**
     * Clear selector cache
     */
    static clear() {
        selectorCache.clear();
    }
    
    /**
     * Invalidate cache entry for selector
     */
    static invalidate(selector, context = document) {
        const cacheKey = `${selector}_${context === document ? 'doc' : context.id || 'ctx'}`;
        const allCacheKey = `all_${selector}_${context === document ? 'doc' : context.id || 'ctx'}`;
        
        selectorCache.delete(cacheKey);
        selectorCache.delete(allCacheKey);
    }
}

// ============================================
// DOM UTILITIES
// ============================================

export const DOM = {
    // ============================================
    // QUERY METHODS WITH CACHING
    // ============================================
    
    /**
     * Query selector with caching
     */
    $: (selector, context = document) => {
        return SelectorCache.get(selector, context);
    },
    
    /**
     * Query selector all with caching
     */
    $$: (selector, context = document) => {
        return SelectorCache.getAll(selector, context);
    },
    
    /**
     * Find element by selector (alias for $)
     */
    find: (selector, context = document) => DOM.$(selector, context),
    
    /**
     * Find all elements by selector (alias for $$)
     */
    findAll: (selector, context = document) => DOM.$$(selector, context),
    
    /**
     * Get closest parent matching selector
     */
    closest: (element, selector) => {
        return element?.closest(selector) || null;
    },
    
    /**
     * Check if element matches selector
     */
    matches: (element, selector) => {
        return element?.matches(selector) || false;
    },
    
    /**
     * Get element's parent
     */
    parent: (element, selector = null) => {
        let parent = element?.parentElement;
        while (parent && parent !== document.body) {
            if (!selector || parent.matches(selector)) {
                return parent;
            }
            parent = parent.parentElement;
        }
        return null;
    },
    
    // ============================================
    // ELEMENT CREATION
    // ============================================
    
    /**
     * Create element with attributes and content
     */
    create: (tag, attributes = {}, children = []) => {
        const element = document.createElement(tag);
        
        // Set attributes
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className' || key === 'class') {
                element.className = value;
            } else if (key === 'style' && typeof value === 'object') {
                Object.assign(element.style, value);
            } else if (key === 'dataset' && typeof value === 'object') {
                Object.assign(element.dataset, value);
            } else if (key === 'data' && typeof value === 'object') {
                Object.entries(value).forEach(([dataKey, dataValue]) => {
                    element.dataset[dataKey] = dataValue;
                });
            } else if (value === true) {
                element.setAttribute(key, '');
            } else if (value === false || value === null || value === undefined) {
                element.removeAttribute(key);
            } else {
                element.setAttribute(key, value);
            }
        });
        
        // Add children
        children.forEach(child => {
            if (typeof child === 'string') {
                element.appendChild(document.createTextNode(child));
            } else if (child) {
                element.appendChild(child);
            }
        });
        
        return element;
    },
    
    /**
     * Create HTML element from string
     */
    fromHTML: (html) => {
        const template = document.createElement('template');
        template.innerHTML = html.trim();
        return template.content.firstChild;
    },
    
    /**
     * Create document fragment
     */
    fragment: (children = []) => {
        const fragment = document.createDocumentFragment();
        children.forEach(child => {
            if (child) fragment.appendChild(child);
        });
        return fragment;
    },
    
    // ============================================
    // CLASS MANIPULATION
    // ============================================
    
    /**
     * Add class to element
     */
    addClass: (element, className) => {
        if (!element || !className) return element;
        
        if (Array.isArray(className)) {
            element.classList.add(...className.filter(c => c));
        } else {
            element.classList.add(className);
        }
        
        return element;
    },
    
    /**
     * Remove class from element
     */
    removeClass: (element, className) => {
        if (!element || !className) return element;
        
        if (Array.isArray(className)) {
            element.classList.remove(...className.filter(c => c));
        } else {
            element.classList.remove(className);
        }
        
        return element;
    },
    
    /**
     * Toggle class on element
     */
    toggleClass: (element, className, force) => {
        if (!element || !className) return element;
        element.classList.toggle(className, force);
        return element;
    },
    
    /**
     * Check if element has class
     */
    hasClass: (element, className) => {
        return element?.classList.contains(className) || false;
    },
    
    /**
     * Add class to body
     */
    addBodyClass: (className) => {
        if (className) document.body.classList.add(className);
        return document.body;
    },
    
    /**
     * Remove class from body
     */
    removeBodyClass: (className) => {
        if (className) document.body.classList.remove(className);
        return document.body;
    },
    
    /**
     * Toggle class on body
     */
    toggleBodyClass: (className, force) => {
        if (className) document.body.classList.toggle(className, force);
        return document.body;
    },
    
    // ============================================
    // ATTRIBUTE MANIPULATION
    // ============================================
    
    /**
     * Get or set attribute
     */
    attr: (element, name, value) => {
        if (value === undefined) {
            return element?.getAttribute(name) || null;
        }
        
        if (element) {
            if (value === null || value === undefined) {
                element.removeAttribute(name);
            } else if (value === true) {
                element.setAttribute(name, '');
            } else if (value === false) {
                element.removeAttribute(name);
            } else {
                element.setAttribute(name, value);
            }
        }
        
        return element;
    },
    
    /**
     * Remove attribute
     */
    removeAttr: (element, name) => {
        element?.removeAttribute(name);
        return element;
    },
    
    /**
     * Get or set dataset
     */
    dataset: (element, key, value) => {
        if (!element || !element.dataset) {
            return value === undefined ? {} : element;
        }
        
        if (value === undefined) {
            return key ? element.dataset[key] : { ...element.dataset };
        }
        
        element.dataset[key] = value;
        return element;
    },
    
    // ============================================
    // DOM MANIPULATION
    // ============================================
    
    /**
     * Append element(s) to parent
     */
    append: (parent, children) => {
        if (!parent) return parent;
        
        const appendChild = (child) => {
            if (child instanceof Node) {
                parent.appendChild(child);
            } else if (typeof child === 'string') {
                parent.appendChild(document.createTextNode(child));
            }
        };
        
        if (Array.isArray(children)) {
            children.forEach(appendChild);
        } else {
            appendChild(children);
        }
        
        // Invalidate cache
        SelectorCache.invalidate(':scope > *', parent);
        
        return parent;
    },
    
    /**
     * Prepend element(s) to parent
     */
    prepend: (parent, children) => {
        if (!parent) return parent;
        
        const prependChild = (child) => {
            if (child instanceof Node) {
                parent.insertBefore(child, parent.firstChild);
            } else if (typeof child === 'string') {
                parent.insertBefore(document.createTextNode(child), parent.firstChild);
            }
        };
        
        if (Array.isArray(children)) {
            children.slice().reverse().forEach(prependChild);
        } else {
            prependChild(children);
        }
        
        // Invalidate cache
        SelectorCache.invalidate(':scope > *', parent);
        
        return parent;
    },
    
    /**
     * Insert element after reference
     */
    insertAfter: (reference, element) => {
        if (!reference || !element) return null;
        
        reference.parentNode.insertBefore(element, reference.nextSibling);
        SelectorCache.invalidate(':scope > *', reference.parentNode);
        
        return element;
    },
    
    /**
     * Insert element before reference
     */
    insertBefore: (reference, element) => {
        if (!reference || !element) return null;
        
        reference.parentNode.insertBefore(element, reference);
        SelectorCache.invalidate(':scope > *', reference.parentNode);
        
        return element;
    },
    
    /**
     * Remove element from DOM
     */
    remove: (element) => {
        if (element?.parentNode) {
            SelectorCache.invalidate(':scope > *', element.parentNode);
            element.parentNode.removeChild(element);
            return true;
        }
        return false;
    },
    
    /**
     * Remove all children from element
     */
    empty: (element) => {
        if (!element) return element;
        
        SelectorCache.invalidate(':scope > *', element);
        
        while (element.firstChild) {
            element.removeChild(element.firstChild);
        }
        
        return element;
    },
    
    /**
     * Replace element with new element
     */
    replace: (oldElement, newElement) => {
        if (!oldElement || !newElement || !oldElement.parentNode) return false;
        
        SelectorCache.invalidate(':scope > *', oldElement.parentNode);
        oldElement.parentNode.replaceChild(newElement, oldElement);
        
        return true;
    },
    
    // ============================================
    // TEXT & CONTENT
    // ============================================
    
    /**
     * Get or set text content
     */
    text: (element, content) => {
        if (content === undefined) {
            return element?.textContent || '';
        }
        
        if (element) {
            element.textContent = content;
        }
        
        return element;
    },
    
    /**
     * Get or set inner HTML (use with caution)
     */
    html: (element, content) => {
        if (content === undefined) {
            return element?.innerHTML || '';
        }
        
        if (element) {
            element.innerHTML = content;
        }
        
        return element;
    },
    
    /**
     * Get or set value
     */
    val: (element, value) => {
        if (value === undefined) {
            return element?.value || '';
        }
        
        if (element) {
            element.value = value;
        }
        
        return element;
    },
    
    // ============================================
    // STYLE MANIPULATION
    // ============================================
    
    /**
     * Set style properties
     */
    style: (element, styles) => {
        if (element && styles) {
            Object.assign(element.style, styles);
        }
        return element;
    },
    
    /**
     * Get computed style
     */
    getStyle: (element, property) => {
        if (!element) return null;
        
        const computed = window.getComputedStyle(element);
        return property ? computed.getPropertyValue(property) : computed;
    },
    
    /**
     * Show element
     */
    show: (element, display = '') => {
        if (!element) return element;
        
        if (display) {
            element.style.display = display;
        } else {
            element.style.removeProperty('display');
        }
        
        return element;
    },
    
    /**
     * Hide element
     */
    hide: (element) => {
        if (element) {
            element.style.display = 'none';
        }
        return element;
    },
    
    /**
     * Toggle element visibility
     */
    toggleVisibility: (element, show, display = '') => {
        if (show === undefined) {
            show = DOM.getStyle(element, 'display') === 'none';
        }
        
        return show ? DOM.show(element, display) : DOM.hide(element);
    },
    
    // ============================================
    // EVENT HANDLING
    // ============================================
    
    /**
     * Add event listener with delegation support
     */
    on: (target, event, selector, handler, options = {}) => {
        if (!target || !event) return () => {};
        
        let cleanup;
        
        if (typeof selector === 'function') {
            // Direct event listener
            handler = selector;
            target.addEventListener(event, handler, options);
            cleanup = () => target.removeEventListener(event, handler, options);
        } else {
            // Delegated event listener
            const wrappedHandler = (e) => {
                if (e.target.matches(selector)) {
                    handler.call(e.target, e);
                } else if (e.target.closest(selector)) {
                    const closest = e.target.closest(selector);
                    handler.call(closest, e);
                }
            };
            
            target.addEventListener(event, wrappedHandler, options);
            cleanup = () => target.removeEventListener(event, wrappedHandler, options);
        }
        
        return cleanup;
    },
    
    /**
     * Remove event listener
     */
    off: (target, event, handler, options = {}) => {
        if (target && event && handler) {
            target.removeEventListener(event, handler, options);
        }
        return target;
    },
    
    /**
     * Trigger custom event
     */
    trigger: (target, eventName, detail = {}, options = {}) => {
        if (!target) return null;
        
        const event = new CustomEvent(eventName, {
            bubbles: options.bubbles !== false,
            cancelable: options.cancelable !== false,
            detail,
            ...options
        });
        
        target.dispatchEvent(event);
        return { event, result: true };
    },
    
    // ============================================
    // POSITION & VISIBILITY
    // ============================================
    
    /**
     * Get element's bounding rect
     */
    rect: (element) => {
        return element?.getBoundingClientRect() || null;
    },
    
    /**
     * Check if element is in viewport
     */
    isInViewport: (element, threshold = 0) => {
        if (!element) return false;
        
        const rect = element.getBoundingClientRect();
        const windowHeight = window.innerHeight || document.documentElement.clientHeight;
        const windowWidth = window.innerWidth || document.documentElement.clientWidth;
        
        return (
            rect.top >= -threshold &&
            rect.left >= -threshold &&
            rect.bottom <= windowHeight + threshold &&
            rect.right <= windowWidth + threshold
        );
    },
    
    /**
     * Check if element is visible
     */
    isVisible: (element) => {
        if (!element) return false;
        
        const style = window.getComputedStyle(element);
        return style.display !== 'none' &&
               style.visibility !== 'hidden' &&
               style.opacity !== '0' &&
               element.offsetWidth > 0 &&
               element.offsetHeight > 0;
    },
    
    /**
     * Check if element is hidden
     */
    isHidden: (element) => {
        return !DOM.isVisible(element);
    },
    
    // ============================================
    // SCROLLING
    // ============================================
    
    /**
     * Scroll element into view
     */
    scrollTo: (element, options = {}) => {
        if (!element) return;
        
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
            inline: 'nearest',
            ...options
        });
    },
    
    /**
     * Scroll to top
     */
    scrollToTop: (options = {}) => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth',
            ...options
        });
    },
    
    // ============================================
    // OBSERVERS
    // ============================================
    
    /**
     * Wait for DOM element to exist
     */
    waitForElement: (selector, timeout = 10000) => {
        return new Promise((resolve, reject) => {
            // Check immediately
            const element = DOM.$(selector);
            if (element) {
                resolve(element);
                return;
            }
            
            // Set up mutation observer
            const observer = new MutationObserver(() => {
                const element = DOM.$(selector);
                if (element) {
                    observer.disconnect();
                    resolve(element);
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            // Timeout
            setTimeout(() => {
                observer.disconnect();
                reject(new Error(`Element "${selector}" not found within ${timeout}ms`));
            }, timeout);
        });
    },
    
    /**
     * Observe element for mutations
     */
    observe: (element, callback, options = { childList: true, subtree: true }) => {
        if (!element || !callback) return null;
        
        const observer = new MutationObserver(callback);
        observer.observe(element, options);
        
        return observer;
    },
    
    /**
     * Observe element with IntersectionObserver
     */
    observeIntersection: (element, callback, options = {}) => {
        if (!element || !callback) return null;
        
        const defaultOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => callback(entry));
        }, mergedOptions);
        
        observer.observe(element);
        return observer;
    },
    
    // ============================================
    // FORM HANDLING
    // ============================================
    
    /**
     * Get form data as object
     */
    getFormData: (form) => {
        if (!form) return {};
        
        const formData = new FormData(form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
        
        return data;
    },
    
    /**
     * Clear form
     */
    clearForm: (form) => {
        if (!form) return;
        
        form.reset();
        
        // Clear validation states
        DOM.removeClass(form, 'was-validated');
        
        DOM.findAll('.is-invalid, .is-valid', form).forEach(el => {
            DOM.removeClass(el, 'is-invalid');
            DOM.removeClass(el, 'is-valid');
        });
    },
    
    /**
     * Validate form
     */
    validateForm: (form) => {
        if (!form) return { valid: false, errors: [] };
        
        const errors = [];
        let isValid = true;
        
        // Required fields
        DOM.findAll('[required]', form).forEach(field => {
            const value = field.value.trim();
            const fieldName = field.getAttribute('data-label') || field.name || field.placeholder || 'This field';
            
            if (!value) {
                errors.push({
                    field: field.name,
                    message: `${fieldName} is required`
                });
                isValid = false;
                DOM.addClass(field, 'is-invalid');
                DOM.removeClass(field, 'is-valid');
            } else {
                DOM.removeClass(field, 'is-invalid');
                DOM.addClass(field, 'is-valid');
            }
        });
        
        // Email validation
        DOM.findAll('input[type="email"]', form).forEach(field => {
            const value = field.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (value && !emailRegex.test(value)) {
                errors.push({
                    field: field.name,
                    message: 'Please enter a valid email address'
                });
                isValid = false;
                DOM.addClass(field, 'is-invalid');
                DOM.removeClass(field, 'is-valid');
            } else if (value) {
                DOM.removeClass(field, 'is-invalid');
                DOM.addClass(field, 'is-valid');
            }
        });
        
        // Add was-validated class for Bootstrap forms
        if (isValid) {
            DOM.addClass(form, 'was-validated');
        }
        
        return { valid: isValid, errors };
    },
    
    // ============================================
    // UTILITIES
    // ============================================
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml: (text) => {
        if (!text) return '';
        
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        
        return text.replace(/[&<>"']/g, m => map[m]);
    },
    
    /**
     * Copy text to clipboard
     */
    copyToClipboard: (text) => {
        return new Promise((resolve, reject) => {
            if (!text) {
                reject(new Error('No text provided'));
                return;
            }
            
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(text).then(resolve).catch(reject);
            } else {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                try {
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    resolve();
                } catch (err) {
                    document.body.removeChild(textArea);
                    reject(err);
                }
            }
        });
    },
    
    // ============================================
    // CACHE MANAGEMENT
    // ============================================
    
    /**
     * Clear selector cache (used after HTMX swaps)
     */
    clearCache: () => {
        SelectorCache.clear();
    },
    
    /**
     * Invalidate cache for specific selector
     */
    invalidateCache: (selector, context = document) => {
        SelectorCache.invalidate(selector, context);
    },

    // ============================================
    // PERFORMANCE UTILITIES
    // ============================================
    
    /**
     * Measure function performance
     */
    measure: (label, callback) => {
        const start = performance.now();
        const result = callback();
        const end = performance.now();
        console.log(`${label}: ${(end - start).toFixed(2)}ms`);
        return result;
    },
};

// Make available globally for caching and component access
if (typeof window !== 'undefined') {
    window.DOM = DOM;
}

export default DOM;