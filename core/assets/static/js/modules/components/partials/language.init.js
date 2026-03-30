/**
 * Enhanced Language Switcher for Django/Wagtail
 * Simple enhancement of the working version
 */

class LanguageSwitcher {
    constructor(options = {}) {
        this.options = {
            // Selectors
            itemSelector: '.dropdown-item-language',
            formSelector: '#languageForm',
            languageInputSelector: '#selectedLanguage',
            nextInputSelector: 'input[name="next"]',
            
            // Behavior
            updateNextField: true,
            showLoading: true,
            cookieSupport: true,
            cookieName: 'django_language',
            
            // Events
            dispatchEvents: false, // Keep simple, disable by default
            
            // Debug
            debug: false,
            
            ...options
        };
        
        this.elements = {
            items: [],
            form: null,
            languageInput: null,
            nextInput: null
        };
        
        this.state = {
            initialized: false,
            isChanging: false
        };
        
        this.log('Enhanced Language Switcher created');
    }
    
    /**
     * Initialize
     */
    init() {
        if (this.state.initialized) return this;
        
        try {
            this.log('Initializing...');
            
            // Find elements
            this.findElements();
            
            // Validate required elements
            if (!this.elements.form || !this.elements.languageInput) {
                throw new Error('Required form elements not found');
            }
            
            // Setup event listeners
            this.setupEventListeners();
            
            // Update next field if enabled
            if (this.options.updateNextField && this.elements.nextInput) {
                this.updateNextField();
            }
            
            this.state.initialized = true;
            this.log('Initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize language switcher:', error);
        }
        
        return this;
    }
    
    /**
     * Find elements
     */
    findElements() {
        this.elements.items = document.querySelectorAll(this.options.itemSelector);
        this.elements.form = document.getElementById(this.options.formSelector);
        
        if (this.elements.form) {
            this.elements.languageInput = document.getElementById(this.options.languageInputSelector);
            this.elements.nextInput = this.elements.form.querySelector(this.options.nextInputSelector);
        }
        
        this.log('Elements found:', {
            items: this.elements.items.length,
            form: !!this.elements.form,
            languageInput: !!this.elements.languageInput,
            nextInput: !!this.elements.nextInput
        });
    }
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        this.elements.items.forEach(item => {
            // Store original onclick for cleanup
            item._originalOnClick = item.onclick;
            
            item.addEventListener('click', (e) => {
                this.handleItemClick(e, item);
            });
            
            this.log('Added listener for:', item.getAttribute('data-lang-code'));
        });
    }
    
    /**
     * Handle item click
     */
    handleItemClick(e, item) {
        e.preventDefault();
        e.stopPropagation();
        
        // Check if already changing
        if (this.state.isChanging) {
            this.log('Already processing language change');
            return;
        }
        
        const langCode = item.getAttribute('data-lang-code');
        if (!langCode) {
            this.log('No language code found');
            return;
        }
        
        this.log('Changing to language:', langCode);
        
        // Dispatch before event if enabled
        if (this.options.dispatchEvents) {
            this.dispatchEvent('language-switcher:before-change', { langCode });
        }
        
        // Change language
        this.changeLanguage(langCode, item);
    }
    
    /**
     * Change language
     */
    changeLanguage(langCode, clickedElement) {
        this.state.isChanging = true;
        
        // Update form value
        this.elements.languageInput.value = langCode;
        
        // Update next field
        if (this.options.updateNextField && this.elements.nextInput) {
            this.updateNextField();
        }
        
        // Set cookie if enabled
        if (this.options.cookieSupport) {
            this.setCookie(langCode);
        }
        
        // Show loading state
        if (this.options.showLoading) {
            this.showLoadingState(clickedElement);
        }
        
        // Submit form with delay to allow UI updates
        setTimeout(() => {
            this.elements.form.submit();
        }, 100);
    }
    
    /**
     * Update next field
     */
    updateNextField() {
        if (this.elements.nextInput) {
            const currentPath = window.location.pathname + window.location.search;
            this.elements.nextInput.value = currentPath;
            this.log('Next field updated:', currentPath);
        }
    }
    
    /**
     * Set language cookie
     */
    setCookie(langCode) {
        try {
            const cookie = `${this.options.cookieName}=${langCode}; path=/; max-age=31536000`; // 1 year
            document.cookie = cookie;
            this.log('Cookie set:', langCode);
        } catch (error) {
            console.warn('Failed to set cookie:', error);
        }
    }
    
    /**
     * Show loading state
     */
    showLoadingState(clickedElement) {
        // Add loading class to clicked element
        clickedElement.classList.add('changing');
        
        // Add loading text
        const originalHTML = clickedElement.innerHTML;
        clickedElement.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status"></span>
            <span>Changing...</span>
        `;
        clickedElement.style.pointerEvents = 'none';
        
        // Restore after timeout (in case submission fails)
        setTimeout(() => {
            if (clickedElement.classList.contains('changing')) {
                clickedElement.innerHTML = originalHTML;
                clickedElement.classList.remove('changing');
                clickedElement.style.pointerEvents = '';
                this.state.isChanging = false;
                this.log('Loading state reset');
            }
        }, 3000);
    }
    
    /**
     * Dispatch event
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, switcher: this },
            bubbles: true
        });
        document.dispatchEvent(event);
    }
    
    /**
     * Log messages
     */
    log(...args) {
        if (this.options.debug) {
            console.log('[LanguageSwitcher]', ...args);
        }
    }
    
    /**
     * Get current state
     */
    getState() {
        return {
            initialized: this.state.initialized,
            isChanging: this.state.isChanging,
            elements: {
                items: this.elements.items.length,
                form: !!this.elements.form
            }
        };
    }
    
    /**
     * Cleanup
     */
    destroy() {
        // Remove event listeners
        this.elements.items.forEach(item => {
            // We can't easily remove anonymous event listeners
            // This is a limitation of the simple approach
        });
        
        this.state.initialized = false;
        this.log('Destroyed');
    }
}

// ==================== AUTO-INITIALIZATION ====================

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if we should use enhanced version
    const useEnhanced = document.querySelector('[data-language-enhanced]');
    
    if (useEnhanced) {
        // Use enhanced version
        const config = useEnhanced.dataset.languageEnhanced 
            ? JSON.parse(useEnhanced.dataset.languageEnhanced)
            : {};
        
        LanguageSwitcher(config);
        
    } else if (document.querySelector('.dropdown-item-language')) {
        // Use original working code as fallback
        const languageItems = document.querySelectorAll('.dropdown-item-language');
        const languageForm = document.getElementById('languageForm');
        const selectedLanguageInput = document.getElementById('selectedLanguage');
        
        if (languageItems.length && languageForm && selectedLanguageInput) {
            languageItems.forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    const langCode = this.getAttribute('data-lang-code');
                    selectedLanguageInput.value = langCode;
                    languageForm.submit();
                });
            });
            
            console.log('Basic language switcher initialized');
        }
    }
});

// Export for module usage
export default LanguageSwitcher;
export { LanguageSwitcher };