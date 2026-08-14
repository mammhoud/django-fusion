import { UnifiedFormHandler } from './formHandler.js';

// ==================== AUTH FORMS EXTENSION ====================

class AuthFormsHandler extends UnifiedFormHandler {
    constructor(formId, options = {}) {
        const authOptions = {
            isAuthForm: true,
            replaceOnSuccess: true,
            enableURLTracking: true,
            authOptions: {
                enablePasswordStrength: true,
                enablePasswordToggle: true,
                enableRememberMe: true,
                enableEmailUsername: true,
                enableProgressiveValidation: true
            },
            ...options
        };
        
        super(formId, authOptions);
        
        this.urlChangeHandler = null;
        this.currentURL = window.location.href;
        this.setupURLTracking();
    }

    setupURLTracking() {
        this.currentURL = window.location.href;
        
        // Listen for URL changes
        this.urlChangeHandler = () => this.handleURLChange();
        window.addEventListener('popstate', this.urlChangeHandler);
        
        // Monitor for SPA navigation
        this.setupSPAMonitoring();
        
        // Handle initial page type
        this.onPageTypeChange(this.isAuthPage());
    }

    setupSPAMonitoring() {
        // Observe DOM changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.target.nodeName === 'TITLE') {
                    this.handleURLChange();
                }
                
                if (mutation.type === 'attributes' && 
                    mutation.attributeName === 'data-page' && 
                    mutation.target === document.body) {
                    this.handleURLChange();
                }
            });
        });
        
        observer.observe(document.body, {
            attributes: true,
            attributeFilter: ['data-page'],
            childList: false,
            subtree: false
        });
        
        observer.observe(document.querySelector('title'), {
            childList: true,
            characterData: true,
            subtree: true
        });
    }

    handleURLChange() {
        const newURL = window.location.href;
        
        if (newURL !== this.currentURL) {
            const wasAuthPage = this.isAuthPage(this.currentURL);
            const isAuthPage = this.isAuthPage(newURL);
            this.currentURL = newURL;
            
            if (wasAuthPage !== isAuthPage) {
                this.onPageTypeChange(isAuthPage);
            }
        }
        
        // Update base handler URL
        this.updateUrl(newURL);
    }

    isAuthPage(url = window.location.href) {
        const path = new URL(url).pathname;
        const authPaths = [
            '/auth/', '/login/', '/register/', '/signin/', '/signup/',
            '/password-reset/', '/forgot-password/', '/reset-password/', '/verify-email/'
        ];
        
        return authPaths.some(authPath => path.startsWith(authPath));
    }

    onPageTypeChange(isAuthPage) {
        if (isAuthPage && this.form) {
            this.reinitialize();
        } else if (!isAuthPage && this.form) {
            this.cleanup();
        }
    }

    reinitialize() {
        this.cleanup();
        this.initialize();
        this.setupAuthFeatures();
    }

    cleanup() {
        // Remove JS-added elements
        this.removeJSElements();
        
        // Clone form to remove event listeners
        if (this.form) {
            const cleanClone = this.form.cloneNode(true);
            this.form.parentNode.replaceChild(cleanClone, this.form);
            this.form = document.getElementById(this.formId);
        }
    }

    removeJSElements() {
        if (!this.form) return;
        
        const elements = [
            '.password-toggle',
            '.password-strength',
            '.field-hint',
            '.character-counter',
            '.form-messages',
            '.validation-summary'
        ];
        
        elements.forEach(selector => {
            this.form.querySelectorAll(selector).forEach(el => el.remove());
        });
    }

    setupAuthFeatures() {
        super.setupAuthFeatures();
        
        if (this.options.authOptions.enableProgressiveValidation) {
            this.setupProgressiveValidation();
        }
    }

    setupProgressiveValidation() {
        const fields = Array.from(this.form.querySelectorAll('input, textarea, select'));
        const order = this.getValidationOrder(fields);
        
        order.forEach((field, index) => {
            field.dataset.validationOrder = index;
            
            field.addEventListener('blur', () => {
                if (this.validateField(field)) {
                    this.moveToNextField(field, order);
                }
            });
            
            field.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && field.type !== 'textarea') {
                    e.preventDefault();
                    if (this.validateField(field)) {
                        this.moveToNextField(field, order);
                    }
                }
            });
        });
    }

    getValidationOrder(fields) {
        const order = [];
        
        // Email/username first
        const emailUsername = fields.find(f => 
            f.type === 'email' || 
            f.name.includes('email') || 
            f.name.includes('username') ||
            f.name === 'email-username'
        );
        if (emailUsername) order.push(emailUsername);
        
        // Password fields
        const passwordFields = fields.filter(f => f.type === 'password');
        order.push(...passwordFields);
        
        // Other fields
        const otherFields = fields.filter(f => 
            !order.includes(f) && 
            f.type !== 'hidden' && 
            f.type !== 'submit' && 
            f.type !== 'button'
        );
        order.push(...otherFields);
        
        return order;
    }

    moveToNextField(currentField, order) {
        const currentIndex = order.indexOf(currentField);
        if (currentIndex === -1 || currentIndex >= order.length - 1) return;
        
        const nextField = order[currentIndex + 1];
        if (nextField) {
            nextField.focus();
            
            // Highlight fields
            currentField.classList.add('field-complete');
            nextField.classList.add('field-active');
            
            setTimeout(() => {
                nextField.classList.remove('field-active');
            }, 1000);
        }
    }

    destroy() {
        super.destroy();
        
        if (this.urlChangeHandler) {
            window.removeEventListener('popstate', this.urlChangeHandler);
        }
    }
}

export { AuthFormsHandler };