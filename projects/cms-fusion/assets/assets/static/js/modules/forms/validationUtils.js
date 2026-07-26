export class ValidationUtils {
    constructor() {
        this.rules = {
            email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            phone: /^[\+]?[1-9][\d]{0,15}$/,
            url: /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
            numeric: /^[0-9]+$/,
            alphabetic: /^[A-Za-z\s]+$/,
            alphanumeric: /^[a-zA-Z0-9\s]+$/,
            password: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$/,
            username: /^[a-zA-Z0-9_]{3,30}$/
        };
    }

    validateField(field, options = {}) {
        const value = field.value.trim();
        const type = field.type;
        const name = field.name || field.id;
        
        // Skip if optional and empty
        if (!field.required && !value) {
            return { valid: true, message: '' };
        }

        // Check required
        if (field.required && !value) {
            return { valid: false, message: 'This field is required' };
        }

        // Type-specific validation
        const validations = {
            email: () => this.rules.email.test(value) || 'Invalid email format',
            tel: () => this.rules.phone.test(value.replace(/\D/g, '')) || 'Invalid phone number',
            url: () => this.rules.url.test(value) || 'Invalid URL',
            password: () => value.length >= 8 || 'Password must be at least 8 characters',
            'email-username': () => this.validateEmailUsername(value)
        };

        const validator = validations[type] || validations[name];
        if (validator) {
            const result = validator();
            if (typeof result === 'string') {
                return { valid: false, message: result };
            }
        }

        // Custom validations
        if (field.dataset.validate) {
            const result = this.validateWithCustomRules(field, value, options);
            if (!result.valid) return result;
        }

        return { valid: true, message: '' };
    }

    validateEmailUsername(value) {
        if (this.rules.email.test(value)) return true;
        if (this.rules.username.test(value)) return true;
        return 'Enter a valid email or username (3-30 characters, letters, numbers, underscores)';
    }

    validateWithCustomRules(field, value, options) {
        const rules = field.dataset.validate.split(',');
        
        for (const rule of rules.map(r => r.trim())) {
            const [ruleName, param] = rule.split(':');
            
            switch(ruleName) {
                case 'match':
                    const matchField = field.form.querySelector(`[name="${param}"]`);
                    if (matchField && value !== matchField.value) {
                        return { valid: false, message: 'Values do not match' };
                    }
                    break;
                    
                case 'min':
                    if (value.length < parseInt(param)) {
                        return { valid: false, message: `Minimum ${param} characters required` };
                    }
                    break;
                    
                case 'max':
                    if (value.length > parseInt(param)) {
                        return { valid: false, message: `Maximum ${param} characters allowed` };
                    }
                    break;
                    
                case 'regex':
                    try {
                        const regex = new RegExp(param);
                        if (!regex.test(value)) {
                            return { valid: false, message: field.title || 'Invalid format' };
                        }
                    } catch(e) {
                        console.error('Invalid regex:', param);
                    }
                    break;
            }
        }
        
        return { valid: true, message: '' };
    }
}