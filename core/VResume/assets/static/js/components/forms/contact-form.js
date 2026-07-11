

export class ContactFormComponent {
    constructor({ element } = {}) {
        this.element = element || document;
        this.form = this.element.matches('form') ? this.element : this.element.querySelector('form');
        this.formInputs = this.element.querySelectorAll('input, textarea, select');
        this.formBtn = this.element.querySelector('[type="submit"], button:not([type="button"])');
    }

    /**
     * Initialize contact form component
     */
    init() {
        if (!this.form || !this.formBtn) {
            console.debug('Contact form component: elements not found');
            return false;
        }

        this.bindValidation();
        this.updateButtonState();
        console.log('✅ Contact form component initialized');
        return true;
    }

    /**
     * Bind form validation events
     */
    bindValidation() {
        this.formInputs.forEach(input => {
            input.addEventListener('input', () => this.updateButtonState());
            input.addEventListener('change', () => this.updateButtonState());
        });
    }

    /**
     * Update submit button state based on form validity
     */
    updateButtonState() {
        const isValid = this.form.checkValidity();
        this.formBtn.disabled = !isValid;
    }

    /**
     * Check if form is valid
     */
    isValid() {
        return this.form.checkValidity();
    }

    /**
     * Reset form
     */
    reset() {
        this.form.reset();
        this.updateButtonState();
    }

    /**
     * Cleanup
     */
    destroy() {
        this.formInputs.forEach(input => {
            input.removeEventListener('input', () => this.updateButtonState());
            input.removeEventListener('change', () => this.updateButtonState());
        });
    }
}

export default ContactFormComponent;
