/**
 * @file FormValidator.js
 * Form validation system for auth pages
 * 
 * Features:
 * - Real-time validation on blur and input
 * - Touched field tracking
 * - Error/success state styling
 * - Submit button state management
 * - Password strength indicator
 */

export class FormValidator {
    constructor(form, options = {}) {
        this.form = typeof form === 'string' ? document.querySelector(form) : form;
        
        if (!this.form) {
            console.error('FormValidator: Form not found');
            return;
        }

        this.options = {
            validateOnBlur: options.validateOnBlur ?? true,
            validateOnInput: options.validateOnInput ?? true,
            showSuccessState: options.showSuccessState ?? true,
            disableSubmitUntilValid: options.disableSubmitUntilValid ?? true,
            focusFirstInvalid: options.focusFirstInvalid ?? true,
            errorClass: options.errorClass || 'is-invalid',
            successClass: options.successClass || 'is-valid',
            errorColor: options.errorColor || '#EF4444',
            successColor: options.successColor || '#10B981',
            ...options
        };

        this.touchedFields = new Set();
        this.fieldErrors = new Map();
        this.validators = new Map();
        this.submitButton = null;

        this._init();
    }

    /**
     * Initialize validator
     */
    _init() {
        // Find submit button
        this.submitButton = this.form.querySelector('button[type="submit"], input[type="submit"]');

        // Setup field listeners
        this._setupFieldListeners();

        // Setup form submit handler
        this.form.addEventListener('submit', (e) => this._handleSubmit(e));

        // Initial button state
        if (this.options.disableSubmitUntilValid) {
            this._updateSubmitButtonState();
        }

        // Inject styles
        this._injectStyles();
    }


    /**
     * Setup event listeners for form fields
     */
    _setupFieldListeners() {
        const fields = this.form.querySelectorAll('input, select, textarea');
        
        fields.forEach(field => {
            if (field.type === 'hidden' || field.type === 'submit') return;

            // Blur validation
            if (this.options.validateOnBlur) {
                field.addEventListener('blur', () => {
                    this.touchedFields.add(field.name);
                    this.validateField(field);
                });
            }

            // Input validation (debounced)
            if (this.options.validateOnInput) {
                let timeout;
                field.addEventListener('input', () => {
                    clearTimeout(timeout);
                    timeout = setTimeout(() => {
                        if (this.touchedFields.has(field.name)) {
                            this.validateField(field);
                        }
                    }, 300);
                });
            }

            // Password strength for password fields
            if (field.type === 'password' && field.name.includes('password') && !field.name.includes('confirm')) {
                this._setupPasswordStrength(field);
            }
        });
    }

    /**
     * Validate a single field
     * @param {HTMLElement} field - Field to validate
     * @returns {boolean} Whether field is valid
     */
    validateField(field) {
        const errors = [];
        const value = field.value.trim();
        const fieldName = field.name;

        // Required validation
        if (field.required && !value) {
            errors.push(this._getFieldLabel(field) + ' is required');
        }

        // Type-specific validation
        if (value) {
            switch (field.type) {
                case 'email':
                    if (!this._isValidEmail(value)) {
                        errors.push('Please enter a valid email address');
                    }
                    break;
                case 'tel':
                    if (!this._isValidPhone(value)) {
                        errors.push('Please enter a valid phone number');
                    }
                    break;
                case 'url':
                    if (!this._isValidUrl(value)) {
                        errors.push('Please enter a valid URL');
                    }
                    break;
            }

            // Min/max length
            if (field.minLength > 0 && value.length < field.minLength) {
                errors.push(`Must be at least ${field.minLength} characters`);
            }
            if (field.maxLength > 0 && value.length > field.maxLength) {
                errors.push(`Must be no more than ${field.maxLength} characters`);
            }

            // Pattern validation
            if (field.pattern) {
                const regex = new RegExp(field.pattern);
                if (!regex.test(value)) {
                    errors.push(field.title || 'Please match the requested format');
                }
            }

            // Password confirmation
            if (fieldName === 'password_confirm' || fieldName === 'confirm_password') {
                const passwordField = this.form.querySelector('input[name="password"]');
                if (passwordField && value !== passwordField.value) {
                    errors.push('Passwords do not match');
                }
            }
        }

        // Custom validators
        if (this.validators.has(fieldName)) {
            const customErrors = this.validators.get(fieldName)(value, field);
            if (customErrors) {
                errors.push(...(Array.isArray(customErrors) ? customErrors : [customErrors]));
            }
        }

        // Update field state
        this._updateFieldState(field, errors);
        
        // Update submit button
        if (this.options.disableSubmitUntilValid) {
            this._updateSubmitButtonState();
        }

        return errors.length === 0;
    }

    /**
     * Validate entire form
     * @returns {boolean} Whether form is valid
     */
    validate() {
        const fields = this.form.querySelectorAll('input, select, textarea');
        let isValid = true;
        let firstInvalidField = null;

        fields.forEach(field => {
            if (field.type === 'hidden' || field.type === 'submit') return;
            
            this.touchedFields.add(field.name);
            const fieldValid = this.validateField(field);
            
            if (!fieldValid && !firstInvalidField) {
                firstInvalidField = field;
            }
            
            isValid = isValid && fieldValid;
        });

        // Focus first invalid field
        if (!isValid && this.options.focusFirstInvalid && firstInvalidField) {
            firstInvalidField.focus();
        }

        return isValid;
    }

    /**
     * Add custom validator for a field
     * @param {string} fieldName - Field name
     * @param {Function} validator - Validator function (value, field) => error string or null
     */
    addValidator(fieldName, validator) {
        this.validators.set(fieldName, validator);
    }

    /**
     * Update field visual state
     */
    _updateFieldState(field, errors) {
        const container = field.closest('.form-group') || field.parentElement;
        const existingMessage = container.querySelector('.validation-message');
        
        // Remove existing classes
        field.classList.remove(this.options.errorClass, this.options.successClass);
        
        if (errors.length > 0) {
            // Error state
            field.classList.add(this.options.errorClass);
            field.style.borderColor = this.options.errorColor;
            this.fieldErrors.set(field.name, errors);
            
            // Show error message
            if (existingMessage) {
                existingMessage.textContent = errors[0];
                existingMessage.className = 'validation-message validation-error';
            } else {
                const message = document.createElement('div');
                message.className = 'validation-message validation-error';
                message.textContent = errors[0];
                container.appendChild(message);
            }
        } else if (this.touchedFields.has(field.name) && this.options.showSuccessState) {
            // Success state
            field.classList.add(this.options.successClass);
            field.style.borderColor = this.options.successColor;
            this.fieldErrors.delete(field.name);
            
            // Remove error message
            if (existingMessage) {
                existingMessage.remove();
            }
        } else {
            // Neutral state
            field.style.borderColor = '';
            this.fieldErrors.delete(field.name);
            
            if (existingMessage) {
                existingMessage.remove();
            }
        }
    }

    /**
     * Update submit button disabled state
     */
    _updateSubmitButtonState() {
        if (!this.submitButton) return;

        const requiredFields = this.form.querySelectorAll('[required]');
        let allValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                allValid = false;
            }
        });

        // Also check for any errors
        if (this.fieldErrors.size > 0) {
            allValid = false;
        }

        this.submitButton.disabled = !allValid;
    }

    /**
     * Handle form submission
     */
    _handleSubmit(event) {
        if (!this.validate()) {
            event.preventDefault();
            return false;
        }
        return true;
    }

    /**
     * Setup password strength indicator
     */
    _setupPasswordStrength(field) {
        const container = field.closest('.form-group') || field.parentElement;
        
        // Create strength indicator
        const indicator = document.createElement('div');
        indicator.className = 'password-strength';
        indicator.innerHTML = `
            <div class="strength-bars">
                <div class="strength-bar"></div>
                <div class="strength-bar"></div>
                <div class="strength-bar"></div>
                <div class="strength-bar"></div>
            </div>
            <span class="strength-label"></span>
        `;
        container.appendChild(indicator);

        // Update on input
        field.addEventListener('input', () => {
            const strength = this._calculatePasswordStrength(field.value);
            this._updatePasswordStrengthUI(indicator, strength);
        });
    }

    /**
     * Calculate password strength
     * @returns {Object} { score: 0-4, label: string }
     */
    _calculatePasswordStrength(password) {
        if (!password) return { score: 0, label: '' };

        let score = 0;
        const checks = {
            length: password.length >= 8,
            longLength: password.length >= 12,
            lowercase: /[a-z]/.test(password),
            uppercase: /[A-Z]/.test(password),
            numbers: /\d/.test(password),
            special: /[^A-Za-z0-9]/.test(password)
        };

        // Common passwords check
        const commonPasswords = ['password', '123456', 'qwerty', 'admin', 'letmein'];
        const isCommon = commonPasswords.some(p => password.toLowerCase().includes(p));

        if (isCommon) return { score: 0, label: 'Very weak' };

        if (checks.length) score++;
        if (checks.longLength) score++;
        if (checks.lowercase && checks.uppercase) score++;
        if (checks.numbers) score++;
        if (checks.special) score++;

        const labels = ['Very weak', 'Weak', 'Fair', 'Good', 'Strong'];
        return { score: Math.min(score, 4), label: labels[Math.min(score, 4)] };
    }

    /**
     * Update password strength UI
     */
    _updatePasswordStrengthUI(indicator, strength) {
        const bars = indicator.querySelectorAll('.strength-bar');
        const label = indicator.querySelector('.strength-label');
        const colors = ['#EF4444', '#F59E0B', '#FBBF24', '#10B981', '#059669'];

        bars.forEach((bar, index) => {
            if (index < strength.score) {
                bar.style.backgroundColor = colors[strength.score];
            } else {
                bar.style.backgroundColor = '#e5e7eb';
            }
        });

        label.textContent = strength.label;
        label.style.color = colors[strength.score] || '#6b7280';
    }

    // Validation helpers
    _isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    _isValidPhone(phone) {
        return /^[\d\s\-\+\(\)]{7,}$/.test(phone);
    }

    _isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    _getFieldLabel(field) {
        const label = this.form.querySelector(`label[for="${field.id}"]`);
        return label?.textContent?.trim() || field.placeholder || field.name;
    }

    /**
     * Inject validation styles
     */
    _injectStyles() {
        if (document.getElementById('form-validator-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'form-validator-styles';
        styles.textContent = `
            .validation-message {
                font-size: 0.75rem;
                margin-top: 0.25rem;
                transition: all 0.2s ease;
            }
            .validation-error {
                color: #EF4444;
            }
            .validation-success {
                color: #10B981;
            }
            .password-strength {
                margin-top: 0.5rem;
            }
            .strength-bars {
                display: flex;
                gap: 4px;
                margin-bottom: 0.25rem;
            }
            .strength-bar {
                height: 4px;
                flex: 1;
                background: #e5e7eb;
                border-radius: 2px;
                transition: background-color 0.2s;
            }
            .strength-label {
                font-size: 0.75rem;
                color: #6b7280;
            }
        `;
        document.head.appendChild(styles);
    }

    /**
     * Reset form validation state
     */
    reset() {
        this.touchedFields.clear();
        this.fieldErrors.clear();
        
        const fields = this.form.querySelectorAll('input, select, textarea');
        fields.forEach(field => {
            field.classList.remove(this.options.errorClass, this.options.successClass);
            field.style.borderColor = '';
        });

        this.form.querySelectorAll('.validation-message').forEach(el => el.remove());
        this._updateSubmitButtonState();
    }

    /**
     * Destroy validator
     */
    destroy() {
        this.reset();
        this.validators.clear();
    }
}

export default FormValidator;
