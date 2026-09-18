/**
 * Unified Form Handler Core
 * Supports: Validation, HTMX, SSE, Form Replacement, Auth Features
 */
import { ValidationUtils } from './validationUtils.js';
import { HTMXSSENotifications } from '../handlers/htmxSSENotifications.js';

export class UnifiedFormHandler {
    constructor(formId, options = {}) {
        this.formId = formId;
        this.form = document.getElementById(formId);
        this.currentUrl = options.url || window.location.href; // Store current URL
        
        if (!this.form) {
            console.warn(`Form with ID "${formId}" not found`);
            return;
        }

        this.options = {
            // Validation
            validateOnBlur: true,
            validateOnSubmit: true,
            showLiveValidation: true,
            scrollToError: true,
            
            // Response handling
            responseType: 'sse', // 'html', 'json', 'sse', 'mixed'
            sseEndpoint: '/notifications/',
            
            // Form replacement
            replaceOnSuccess: false,
            replaceSelector: null, // Selector for element to replace
            successTemplate: null, // Template ID for success state
            
            // Error handling
            showFieldErrors: true,
            showFormErrors: true,
            errorTimeout: 8000,
            
            // HTMX integration
            useHTMX: true,
            htmxTarget: null,
            htmxSwap: 'innerHTML',
            
            // Auth specific
            isAuthForm: false,
            authOptions: {
                enablePasswordStrength: true,
                enablePasswordToggle: true,
                enableRememberMe: true,
                enableEmailUsername: false
            },
            
            // Contact form specific
            isContactForm: false,
            contactOptions: {
                minMessageLength: 10,
                maxMessageLength: 2000,
                requirePrivacyConsent: true
            },
            
            // Callbacks
            onSuccess: null,
            onError: null,
            onValidation: null,
            onReplace: null,
            
            ...options
        };

        this.validator = new ValidationUtils();
        // this.sseHandler = this.options.sseEndpoint ? new SSEHandler(this.options.sseEndpoint) : null;
        this.eventListeners = new Map();
        this.isSubmitting = false;
        this.isConnected = false;
        this.validationState = new Map();

        this.initialize();
    }

    // ==================== INITIALIZATION ====================

    initialize() {
        if (!this.form) return;

        try {
            // Setup form structure
            this.setupFormStructure();
            
            // Setup validation
            this.setupValidation();
            
            // // Setup response handling
            // this.setupResponseHandling();
            
            // Setup HTMX if enabled
            if (this.options.useHTMX && typeof htmx !== 'undefined') {
                this.setupHTMX();
            }
            
            // Setup auth features if needed
            if (this.options.isAuthForm) {
                this.setupAuthFeatures();
            }
            
            // Setup contact features if needed
            if (this.options.isContactForm) {
                this.setupContactFeatures();
            }
            
            // // Setup SSE if configured
            // if (this.sseHandler) {
            //     this.setupSSE();
            // }
            
            // Mark as initialized
            this.form.dataset.handlerInitialized = 'true';
            this.form.dataset.handlerType = 'unified';
            this.form.dataset.url = this.currentUrl; // Store URL on form
            
            this.dispatchEvent('initialized', { formId: this.formId, url: this.currentUrl });
            
            console.log(`✅ UnifiedFormHandler initialized: ${this.formId}`);
            
        } catch(error) {
            console.error(`Failed to initialize handler for ${this.formId}:`, error);
            this.showError('Failed to initialize form handler. Please refresh the page.');
        }
    }

    setupFormStructure() {
        // Ensure form has proper attributes
        if (!this.form.hasAttribute('novalidate')) {
            this.form.setAttribute('novalidate', '');
        }
        
        // Add data attributes
        this.form.dataset.handlerFormId = this.formId;
        this.form.dataset.responseType = this.options.responseType;
        this.form.dataset.url = this.currentUrl; // Store URL
        
        // Create message container if not exists
        if (!this.form.querySelector('.form-messages')) {
            const msgContainer = document.createElement('div');
            msgContainer.className = 'form-messages';
            this.form.prepend(msgContainer);
        }
        
        // Create progress indicator if not exists
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.querySelector('.submit-progress')) {
            const progress = document.createElement('span');
            progress.className = 'submit-progress';
            progress.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            progress.style.display = 'none';
            submitBtn.appendChild(progress);
        }
    }

    setupValidation() {
        const fields = this.form.querySelectorAll('input, textarea, select');
        
        fields.forEach(field => {
            // Store initial state
            this.validationState.set(field, {
                valid: true,
                message: '',
                touched: false
            });
            
            // Live validation on input
            if (this.options.showLiveValidation) {
                field.addEventListener('input', () => {
                    if (field.value.trim()) {
                        this.validateField(field, false);
                    } else {
                        this.clearFieldError(field);
                    }
                });
            }
            
            // Validation on blur
            if (this.options.validateOnBlur) {
                field.addEventListener('blur', () => {
                    if (field.value.trim() || field.required) {
                        this.validateField(field, true);
                        this.validationState.get(field).touched = true;
                    }
                });
            }
            
            // Clear error on focus
            field.addEventListener('focus', () => {
                this.clearFieldError(field);
            });
        });
        
        // Form submission validation
        this.form.addEventListener('submit', (e) => {
            if (this.options.validateOnSubmit) {
                if (!this.validateForm()) {
                    e.preventDefault();
                    e.stopImmediatePropagation();
                    return false;
                }
            }
            
            if (this.isSubmitting) {
                e.preventDefault();
                return false;
            }
            
            this.handleSubmit(e);
        });
    }

    setupResponseHandling() {
        // Setup response type specific handling
        switch(this.options.responseType) {
            case 'sse':
                this.setupSSEResponse();
                break;
                
            case 'json':
                this.setupJSONResponse();
                break;
                
            case 'mixed':
                this.setupMixedResponse();
                break;
                
            default: // html
                this.setupHTMLResponse();
        }
    }

    setupHTMX() {
        if (!this.form.hasAttribute('hx-post')) {
            this.form.setAttribute('hx-post', this.form.action || window.location.href);
        }
        
        if (this.options.htmxTarget) {
            this.form.setAttribute('hx-target', this.options.htmxTarget);
        }
        
        if (this.options.htmxSwap) {
            this.form.setAttribute('hx-swap', this.options.htmxSwap);
        }
        
        // Add HTMX indicator
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn && !submitBtn.querySelector('.htmx-indicator')) {
            const indicator = document.createElement('span');
            indicator.className = 'htmx-indicator ms-2';
            indicator.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
            submitBtn.appendChild(indicator);
        }
        
        // Handle HTMX events
        this.onHTMXEvent('htmx:beforeRequest', () => this.showLoading());
        this.onHTMXEvent('htmx:afterRequest', (e) => this.handleHTMXResponse(e));
        this.onHTMXEvent('htmx:responseError', (e) => this.handleHTMXError(e));
    }

    setupAuthFeatures() {
        const opts = this.options.authOptions;
        
        if (opts.enablePasswordStrength) {
            this.setupPasswordStrength();
        }
        
        if (opts.enablePasswordToggle) {
            this.setupPasswordToggle();
        }
        
        if (opts.enableRememberMe) {
            this.setupRememberMe();
        }
        
        if (opts.enableEmailUsername) {
            this.setupEmailUsernameField();
        }
    }

    setupContactFeatures() {
        const opts = this.options.contactOptions;
        
        // Message length validation
        const messageField = this.form.querySelector('textarea[name="message"]');
        if (messageField) {
            messageField.minLength = opts.minMessageLength;
            messageField.maxLength = opts.maxMessageLength;
            this.setupCharacterCounter(messageField);
        }
        
        // Privacy consent
        if (opts.requirePrivacyConsent) {
            this.setupPrivacyConsent();
        }
    }

    setupSSE() {
        if (!this.sseHandler) return;
        
        // Connect to SSE
        this.sseHandler.connect();
        
        // Listen for SSE events
        const unsubscribe = this.sseHandler.on('*', (data) => {
            this.handleSSEMessage(data);
        });
        
        // Store unsubscribe function
        this.eventListeners.set('sse', unsubscribe);
        
        // Handle form submission with SSE
        this.form.addEventListener('submit', (e) => {
            if (this.options.responseType === 'sse' || this.options.responseType === 'mixed') {
                e.preventDefault();
                this.submitWithSSE();
            }
        });
    }

    // ==================== VALIDATION ====================

    validate(target, showErrors = true) {
        if (target instanceof HTMLFormElement) {
            return this.validateForm(showErrors);
        } else if (target instanceof HTMLElement) {
            return this.validateField(target, showErrors);
        }
        return false;
    }

    validateForm(showErrors = true) {
        let isValid = true;
        const invalidFields = [];
        
        const fields = this.form.querySelectorAll('input, textarea, select');
        
        fields.forEach(field => {
            const result = this.validator.validateField(field);
            const state = this.validationState.get(field);
            
            if (state) {
                state.valid = result.valid;
                state.message = result.message;
            }
            
            if (!result.valid) {
                isValid = false;
                invalidFields.push({ field, message: result.message });
                
                if (showErrors) {
                    this.showFieldError(field, result.message);
                }
            } else {
                if (showErrors) {
                    this.clearFieldError(field);
                    field.classList.add('is-valid');
                }
            }
        });
        
        // Show form-level errors
        if (!isValid && showErrors) {
            this.showValidationSummary(invalidFields);
            
            // Scroll to first error
            if (this.options.scrollToError && invalidFields.length > 0) {
                this.scrollToField(invalidFields[0].field);
            }
        }
        
        // Dispatch validation event
        this.dispatchEvent('validated', { 
            isValid, 
            invalidFields,
            form: this.form 
        });
        
        // Call custom validation callback
        if (this.options.onValidation) {
            this.options.onValidation({ isValid, invalidFields, form: this.form });
        }
        
        return isValid;
    }

    validateField(field, showError = true) {
        const result = this.validator.validateField(field);
        const state = this.validationState.get(field);
        
        if (state) {
            state.valid = result.valid;
            state.message = result.message;
        }
        
        if (showError) {
            if (!result.valid) {
                this.showFieldError(field, result.message);
            } else {
                this.clearFieldError(field);
                field.classList.add('is-valid');
            }
        }
        
        this.dispatchEvent('fieldValidated', { 
            field, 
            valid: result.valid,
            message: result.message 
        });
        
        return result.valid;
    }

    // ==================== SUBMISSION HANDLING ====================

    async handleSubmit(e) {
        this.isSubmitting = true;
        this.showLoading();
        
        try {
            // If using HTMX, let it handle
            if (this.options.useHTMX && typeof htmx !== 'undefined' && 
                this.form.hasAttribute('hx-post')) {
                return;
            }
            
            // Handle based on response type
            switch(this.options.responseType) {
                case 'json':
                    await this.submitJSON();
                    break;
                    
                case 'sse':
                    e.preventDefault();
                    await this.submitWithSSE();
                    break;
                    
                case 'mixed':
                    e.preventDefault();
                    await this.submitMixed();
                    break;
                    
                default:
                    // Regular form submission
                    // (form will submit normally)
                    break;
            }
            
        } catch(error) {
            console.error('Form submission error:', error);
            this.handleError(error);
            this.isSubmitting = false;
            this.hideLoading();
        }
    }

    async submitJSON() {
        const formData = new FormData(this.form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Include URL in submission
        data._submissionUrl = this.currentUrl;
        
        const response = await fetch(this.form.action || window.location.href, {
            method: this.form.method || 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken(),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            await this.handleSuccess(result);
        } else {
            this.handleError(result);
        }
    }

    async submitWithSSE() {
        if (!this.sseHandler) {
            throw new Error('SSE handler not initialized');
        }
        
        const formData = new FormData(this.form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Include URL in submission
        data._submissionUrl = this.currentUrl;
        
        // Send form data via POST
        const response = await fetch(this.form.action || window.location.href, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({ 
                ...data, 
                _sse: true,
                _formId: this.formId 
            })
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            this.handleError(error);
        }
        
        // SSE will handle updates via event stream
    }

    async submitMixed() {
        // First submit normally
        await this.submitJSON();
        
        // Then connect SSE for real-time updates
        if (this.sseHandler && !this.isConnected) {
            this.sseHandler.connect();
            this.isConnected = true;
        }
    }

    // ==================== RESPONSE HANDLING ====================

    handleHTMXResponse(event) {
        this.hideLoading();
        this.isSubmitting = false;
        
        if (event.detail.successful) {
            try {
                const response = JSON.parse(event.detail.xhr.responseText);
                this.handleSuccess(response);
            } catch(e) {
                // HTML response
                this.handleHTMLElementResponse(event.detail.xhr.responseText);
            }
        } else {
            this.handleHTMXError(event.detail);
        }
    }

    handleHTMLElementResponse(html) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        // Check for success messages
        const successMsg = doc.querySelector('.alert-success, .success-message');
        if (successMsg) {
            this.showSuccess(successMsg.textContent);
            
            if (this.options.replaceOnSuccess) {
                this.replaceFormWithSuccess();
            }
        }
        
        // Check for error messages
        const errorMsg = doc.querySelector('.alert-danger, .error-message');
        if (errorMsg) {
            this.showError(errorMsg.textContent);
        }
    }

    handleSuccess(result) {
        this.clearErrors();
        this.showSuccess(result.message || 'Form submitted successfully!');
        
        // Call custom success callback
        if (this.options.onSuccess) {
            this.options.onSuccess(result, this.form);
        }
        
        // Handle form replacement
        if (this.options.replaceOnSuccess) {
            setTimeout(() => {
                this.replaceFormWithSuccess();
            }, 1500);
        }
        
        // Reset form if needed
        if (result.reset !== false) {
            setTimeout(() => {
                this.reset();
            }, 2000);
        }
        
        this.dispatchEvent('success', { result, form: this.form, url: this.currentUrl });
    }

    handleError(error) {
        console.error('Form error:', error);
        
        if (error && typeof error === 'object') {
            // Server validation errors
            if (error.errors) {
                this.processServerErrors(error.errors);
            } else if (error.message) {
                this.showError(error.message);
            }
        } else if (typeof error === 'string') {
            this.showError(error);
        } else {
            this.showError('An error occurred. Please try again.');
        }
        
        // Call custom error callback
        if (this.options.onError) {
            this.options.onError(error, this.form);
        }
        
        this.dispatchEvent('error', { error, form: this.form, url: this.currentUrl });
    }

    processServerErrors(errors) {
        this.clearErrors();
        
        // Field errors
        Object.entries(errors).forEach(([fieldName, messages]) => {
            if (fieldName !== 'non_field_errors') {
                const field = this.form.querySelector(`[name="${fieldName}"]`);
                if (field) {
                    const message = Array.isArray(messages) ? messages.join(', ') : messages;
                    this.showFieldError(field, message);
                }
            }
        });
        
        // Non-field errors
        if (errors.non_field_errors) {
            const message = Array.isArray(errors.non_field_errors) 
                ? errors.non_field_errors.join(', ') 
                : errors.non_field_errors;
            this.showError(message);
        }
    }

    handleSSEMessage(data) {
        console.log('SSE Message:', data);
        
        switch(data.type) {
            case 'validation':
                this.handleSSEValidation(data);
                break;
                
            case 'progress':
                this.handleSSEProgress(data);
                break;
                
            case 'success':
                this.handleSSESuccess(data);
                break;
                
            case 'error':
                this.handleSSEError(data);
                break;
                
            case 'update':
                this.handleSSEUpdate(data);
                break;
                
            default:
                this.dispatchEvent('sse', data);
        }
    }

    handleSSEValidation(data) {
        if (data.field) {
            const field = this.form.querySelector(`[name="${data.field}"]`);
            if (field) {
                if (data.valid) {
                    this.clearFieldError(field);
                    field.classList.add('is-valid');
                } else {
                    this.showFieldError(field, data.message);
                }
            }
        }
    }

    handleSSEProgress(data) {
        const progressEl = this.form.querySelector('.submit-progress');
        if (progressEl) {
            progressEl.textContent = data.message || `${data.percent || 0}%`;
        }
    }

    handleSSESuccess(data) {
        this.showSuccess(data.message || 'Success!');
        this.hideLoading();
        this.isSubmitting = false;
        
        if (this.options.replaceOnSuccess) {
            this.replaceFormWithSuccess(data);
        }
    }

    handleSSEError(data) {
        this.showError(data.message || 'An error occurred');
        this.hideLoading();
        this.isSubmitting = false;
    }

    handleSSEUpdate(data) {
        // Update form fields with real-time data
        if (data.updates) {
            Object.entries(data.updates).forEach(([field, value]) => {
                const fieldEl = this.form.querySelector(`[name="${field}"]`);
                if (fieldEl) {
                    fieldEl.value = value;
                }
            });
        }
    }

    // ==================== FORM REPLACEMENT ====================

    replaceFormWithSuccess(data = {}) {
        let replacementContent = '';
        
        // Use custom template if provided
        if (this.options.successTemplate) {
            const template = document.getElementById(this.options.successTemplate);
            if (template) {
                replacementContent = this.renderTemplate(template.innerHTML, data);
            }
        } else {
            // Default success template
            replacementContent = `
                <div class="success-message alert alert-success">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-check-circle fa-2x me-3"></i>
                        <div>
                            <h4 class="alert-heading mb-2">Success!</h4>
                            <p class="mb-0">${data.message || 'Your form has been submitted successfully.'}</p>
                        </div>
                    </div>
                    <div class="mt-3">
                        <button class="btn btn-outline-primary reset-form" data-form-id="${this.formId}">
                            <i class="fas fa-redo me-2"></i>
                            Submit Another
                        </button>
                    </div>
                </div>
            `;
        }
        
        // Determine what to replace
        let targetElement = this.form;
        if (this.options.replaceSelector) {
            targetElement = document.querySelector(this.options.replaceSelector) || this.form;
        }
        
        // Create wrapper and replace
        const wrapper = document.createElement('div');
        wrapper.className = 'form-replacement';
        wrapper.innerHTML = replacementContent;
        
        targetElement.parentNode.replaceChild(wrapper, targetElement);
        
        // Add event listener to reset button
        const resetBtn = wrapper.querySelector('.reset-form');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetForm(wrapper);
            });
        }
        
        // Call custom replace callback
        if (this.options.onReplace) {
            this.options.onReplace(wrapper, data);
        }
        
        this.dispatchEvent('replaced', { 
            element: wrapper, 
            data,
            originalForm: this.form,
            url: this.currentUrl
        });
    }

    resetForm(wrapper) {
        const originalForm = this.form;
        
        // If we have the original form stored
        if (originalForm) {
            wrapper.parentNode.replaceChild(originalForm, wrapper);
            
            // Re-initialize the form
            this.initialize();
            
            this.dispatchEvent('reset', { form: originalForm, url: this.currentUrl });
        } else {
            // Reload the page to get fresh form
            window.location.reload();
        }
    }

    // ==================== UI METHODS ====================

    showLoading() {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            
            const progress = submitBtn.querySelector('.submit-progress');
            if (progress) {
                progress.style.display = 'inline-block';
            }
        }
    }

    hideLoading() {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            
            const progress = submitBtn.querySelector('.submit-progress');
            if (progress) {
                progress.style.display = 'none';
            }
        }
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showAlert(message, type) {
        const container = this.form.querySelector('.form-messages') || this.form;
        
        // Remove existing alerts
        const existingAlerts = container.querySelectorAll('.alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create new alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.prepend(alert);
        
        // Auto-dismiss
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, this.options.errorTimeout);
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        // Remove existing error
        this.clearFieldError(field);
        
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid', 'is-valid');
        
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    clearErrors() {
        this.form.querySelectorAll('.is-invalid').forEach(field => {
            this.clearFieldError(field);
        });
        
        const alerts = this.form.querySelectorAll('.alert');
        alerts.forEach(alert => alert.remove());
    }

    showValidationSummary(invalidFields) {
        if (!this.options.showFormErrors || invalidFields.length === 0) return;
        
        let summary = this.form.querySelector('.validation-summary');
        
        if (!summary) {
            summary = document.createElement('div');
            summary.className = 'validation-summary alert alert-danger mt-3';
            this.form.prepend(summary);
        }
        
        let message = '<strong>Please fix the following errors:</strong><ul class="mb-0 mt-2">';
        
        invalidFields.slice(0, 3).forEach(({ field, message }) => {
            const fieldName = field.labels?.[0]?.textContent || field.name || 'Field';
            message += `<li><strong>${fieldName}:</strong> ${message}</li>`;
        });
        
        if (invalidFields.length > 3) {
            message += `<li>...and ${invalidFields.length - 3} more errors</li>`;
        }
        
        message += '</ul>';
        summary.innerHTML = message;
    }

    scrollToField(field) {
        field.scrollIntoView({
            behavior: 'smooth',
            block: 'center'
        });
        
        field.focus();
        field.classList.add('field-highlight');
        
        setTimeout(() => {
            field.classList.remove('field-highlight');
        }, 2000);
    }

    // ==================== AUTH FEATURES ====================

    setupPasswordStrength() {
        const passwordFields = this.form.querySelectorAll('input[type="password"]');
        
        passwordFields.forEach(field => {
            // Skip confirmation fields
            if (field.name.includes('confirm') || field.name.includes('Confirm')) {
                return;
            }
            
            // Create strength meter
            const meter = document.createElement('div');
            meter.className = 'password-strength mt-2';
            meter.innerHTML = `
                <div class="password-strength-meter">
                    <div class="strength-bar"></div>
                </div>
                <small class="strength-label form-text"></small>
            `;
            
            field.parentNode.appendChild(meter);
            
            field.addEventListener('input', () => {
                const strength = this.calculatePasswordStrength(field.value);
                this.updatePasswordStrength(meter, strength);
            });
        });
    }

    calculatePasswordStrength(password) {
        if (!password) return 0;
        
        let score = 0;
        
        // Length
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        
        // Complexity
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;
        
        return Math.min(score, 4);
    }

    updatePasswordStrength(meter, strength) {
        const bar = meter.querySelector('.strength-bar');
        const label = meter.querySelector('.strength-label');
        
        const classes = ['weak', 'fair', 'good', 'strong'];
        const labels = ['Very weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const colors = ['#dc3545', '#ffc107', '#0dcaf0', '#198754'];
        
        // Update bar
        if (bar) {
            bar.style.width = `${(strength / 4) * 100}%`;
            bar.style.backgroundColor = colors[strength] || '#6c757d';
        }
        
        // Update label
        if (label) {
            label.textContent = `Strength: ${labels[strength]}`;
            label.style.color = colors[strength] || '#6c757d';
        }
    }

    setupPasswordToggle() {
        const passwordFields = this.form.querySelectorAll('input[type="password"]');
        
        passwordFields.forEach(field => {
            const toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'password-toggle btn btn-sm btn-outline-secondary';
            toggleBtn.innerHTML = '<i class="fas fa-eye"></i>';
            toggleBtn.setAttribute('aria-label', 'Show password');
            
            field.parentNode.appendChild(toggleBtn);
            
            toggleBtn.addEventListener('click', () => {
                const type = field.type === 'password' ? 'text' : 'password';
                field.type = type;
                
                const icon = toggleBtn.querySelector('i');
                icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
                toggleBtn.setAttribute('aria-label', 
                    type === 'password' ? 'Show password' : 'Hide password'
                );
            });
        });
    }

    setupRememberMe() {
        const rememberCheckbox = this.form.querySelector('input[name="remember"]');
        if (!rememberCheckbox) return;
        
        // Load saved preference
        const saved = localStorage.getItem('auth_remember');
        if (saved !== null) {
            rememberCheckbox.checked = saved === 'true';
        }
        
        // Save on change
        rememberCheckbox.addEventListener('change', () => {
            localStorage.setItem('auth_remember', rememberCheckbox.checked);
        });
    }

    setupEmailUsernameField() {
        const field = this.form.querySelector('input[name="email-username"]');
        if (!field) return;
        
        field.addEventListener('input', () => {
            const value = field.value.trim();
            const hint = this.getEmailUsernameHint(value);
            
            this.updateFieldHint(field, hint);
        });
    }

    getEmailUsernameHint(value) {
        if (!value) {
            return { text: 'Enter email or username', valid: false };
        }
        
        if (this.validator.rules.email.test(value)) {
            return { text: '✓ Valid email', valid: true };
        }
        
        if (this.validator.rules.username.test(value)) {
            return { text: '✓ Valid username', valid: true };
        }
        
        return { text: 'Invalid format', valid: false };
    }

    updateFieldHint(field, hint) {
        let hintElement = field.parentNode.querySelector('.field-hint');
        
        if (!hintElement) {
            hintElement = document.createElement('small');
            hintElement.className = 'field-hint form-text';
            field.parentNode.appendChild(hintElement);
        }
        
        hintElement.textContent = hint.text;
        hintElement.className = `field-hint form-text ${hint.valid ? 'text-success' : 'text-muted'}`;
    }

    setupCharacterCounter(textarea) {
        const counter = document.createElement('div');
        counter.className = 'character-counter form-text text-end mt-1';
        counter.innerHTML = `<span class="current-count">0</span>/<span class="max-count">${textarea.maxLength}</span>`;
        
        textarea.parentNode.appendChild(counter);
        
        textarea.addEventListener('input', () => {
            const count = textarea.value.length;
            counter.querySelector('.current-count').textContent = count;
            
            if (count > textarea.maxLength * 0.9) {
                counter.classList.add('text-warning');
                counter.classList.remove('text-muted');
            } else if (count > textarea.maxLength) {
                counter.classList.add('text-danger');
                counter.classList.remove('text-warning', 'text-muted');
            } else {
                counter.classList.remove('text-danger', 'text-warning');
                counter.classList.add('text-muted');
            }
        });
    }

    setupPrivacyConsent() {
        // Implementation for privacy consent
    }

    // ==================== UTILITY METHODS ====================

    updateUrl(url) {
        this.currentUrl = url;
        if (this.form) {
            this.form.dataset.url = url;
        }
        this.dispatchEvent('url:updated', { url, formId: this.formId });
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    renderTemplate(template, data) {
        return template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return data[key] !== undefined ? data[key] : match;
        });
    }

    onHTMXEvent(event, callback) {
        if (typeof htmx !== 'undefined') {
            this.form.addEventListener(event, callback);
        }
    }

    on(event, callback) {
        const fullEvent = `form:${event}`;
        this.form.addEventListener(fullEvent, (e) => callback(e.detail));
        return () => this.form.removeEventListener(fullEvent, callback);
    }

    dispatchEvent(event, detail = {}) {
        const fullEvent = `form:${event}`;
        const customEvent = new CustomEvent(fullEvent, {
            detail: { 
                ...detail, 
                formId: this.formId, 
                form: this.form,
                url: this.currentUrl // Include URL in all events
            }
        });
        this.form.dispatchEvent(customEvent);
    }

    getData() {
        const formData = new FormData(this.form);
        const data = {};
        
        for (const [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        // Include URL in data
        data._url = this.currentUrl;
        
        return data;
    }

    setData(data) {
        Object.entries(data).forEach(([key, value]) => {
            const field = this.form.querySelector(`[name="${key}"]`);
            if (field) {
                field.value = value;
            }
        });
    }

    reset() {
        this.form.reset();
        this.clearErrors();
        this.validationState.clear();
        
        // Reset field states
        this.form.querySelectorAll('input, textarea, select').forEach(field => {
            field.classList.remove('is-valid', 'is-invalid');
        });
        
        this.dispatchEvent('reset', { url: this.currentUrl });
    }

    destroy() {
        // Remove event listeners
        this.eventListeners.forEach(unsubscribe => {
            if (typeof unsubscribe === 'function') {
                unsubscribe();
            }
        });
        
        // Disconnect SSE
        if (this.sseHandler) {
            this.sseHandler.disconnect();
        }
        
        // Remove data attributes
        if (this.form) {
            this.form.removeAttribute('data-handler-initialized');
            this.form.removeAttribute('data-handler-type');
            this.form.removeAttribute('data-url');
        }
        
        console.log(`🗑️ UnifiedFormHandler destroyed: ${this.formId}`);
    }
}

export default { UnifiedFormHandler };