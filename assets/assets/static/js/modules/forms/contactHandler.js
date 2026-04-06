import { UnifiedFormHandler } from './formHandler.js';

// ==================== CONTACT FORM EXTENSION ====================

class ContactFormHandler extends UnifiedFormHandler {
    constructor(formId, options = {}) {
        const contactOptions = {
            isContactForm: true,
            responseType: 'mixed',
            contactOptions: {
                minMessageLength: 20,
                maxMessageLength: 1000,
                requirePrivacyConsent: true,
                enableFileUpload: true,
                maxFileSize: 5 * 1024 * 1024 // 5MB
            },
            ...options
        };
        
        super(formId, contactOptions);
    }

    setupContactFeatures() {
        super.setupContactFeatures();
        
        // File upload validation
        if (this.options.contactOptions.enableFileUpload) {
            this.setupFileUpload();
        }
        
        // CAPTCHA if needed
        if (window.grecaptcha) {
            this.setupCaptcha();
        }
    }

    setupFileUpload() {
        const fileInput = this.form.querySelector('input[type="file"]');
        if (!fileInput) return;
        
        const maxSize = this.options.contactOptions.maxFileSize;
        
        fileInput.addEventListener('change', () => {
            const files = Array.from(fileInput.files);
            
            for (const file of files) {
                if (file.size > maxSize) {
                    this.showFieldError(fileInput, `File "${file.name}" exceeds maximum size of ${maxSize / (1024 * 1024)}MB`);
                    fileInput.value = '';
                    return;
                }
                
                // Validate file type
                const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'application/msword'];
                if (!validTypes.includes(file.type)) {
                    this.showFieldError(fileInput, `File type "${file.type}" is not supported`);
                    fileInput.value = '';
                    return;
                }
            }
            
            this.clearFieldError(fileInput);
        });
    }

    setupCaptcha() {
        const captchaContainer = this.form.querySelector('.g-recaptcha');
        if (!captchaContainer) return;
        
        this.form.addEventListener('submit', (e) => {
            const response = grecaptcha.getResponse();
            if (!response) {
                e.preventDefault();
                this.showError('Please complete the CAPTCHA');
                return false;
            }
        });
    }

    validateForm(showErrors = true) {
        const isValid = super.validateForm(showErrors);
        
        // Additional contact-specific validation
        if (isValid) {
            // Check message length
            const messageField = this.form.querySelector('textarea[name="message"]');
            if (messageField) {
                const length = messageField.value.trim().length;
                const min = this.options.contactOptions.minMessageLength;
                
                if (length < min) {
                    if (showErrors) {
                        this.showFieldError(messageField, `Message must be at least ${min} characters`);
                    }
                    return false;
                }
            }
            
            // Check privacy consent
            if (this.options.contactOptions.requirePrivacyConsent) {
                const consent = this.form.querySelector('input[name="privacy_consent"]');
                if (consent && !consent.checked) {
                    if (showErrors) {
                        this.showError('You must agree to the privacy policy');
                    }
                    return false;
                }
            }
        }
        
        return isValid;
    }
}

export { ContactFormHandler };