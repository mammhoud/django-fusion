/**
 * Form Handling System
 * Unified form management across all sites
 * 
 * Features:
 * - Form validation display
 * - HTMX integration
 * - Loading states
 * - Error handling
 */

(function() {
    'use strict';

    window.app = window.app || {};

    /**
     * Validate form client-side
     */
    function validateForm(form) {
        if (!form.checkValidity() === false) {
            return true;
        }

        Array.from(form.querySelectorAll('input, select, textarea')).forEach(field => {
            if (!field.checkValidity()) {
                field.classList.add('is-invalid');
            } else {
                field.classList.remove('is-invalid');
            }
        });

        return form.checkValidity();
    }

    /**
     * Show form loading state
     */
    function setFormLoading(form, loading = true) {
        const submitBtn = form.querySelector('button[type="submit"]');
        const inputs = form.querySelectorAll('input, select, textarea, button');

        if (loading) {
            inputs.forEach(input => input.disabled = true);
            
            if (submitBtn) {
                const spinner = document.createElement('span');
                spinner.className = 'spinner-border spinner-border-sm me-2';
                spinner.setAttribute('role', 'status');
                spinner.setAttribute('data-original-content', submitBtn.innerHTML);
                
                submitBtn.innerHTML = '';
                submitBtn.appendChild(spinner);
                submitBtn.appendChild(document.createTextNode('Loading...'));
            }
        } else {
            inputs.forEach(input => input.disabled = false);
            
            if (submitBtn) {
                const originalContent = submitBtn.querySelector('[data-original-content]')?.getAttribute('data-original-content');
                if (originalContent) {
                    submitBtn.innerHTML = originalContent;
                }
            }
        }
    }

    /**
     * Display form errors
     */
    function displayFormErrors(form, errors) {
        // Clear previous errors
        form.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());

        // Display new errors
        for (const [field, messages] of Object.entries(errors)) {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                
                const feedback = document.createElement('div');
                feedback.className = 'invalid-feedback d-block small';
                feedback.textContent = Array.isArray(messages) ? messages.join(', ') : messages;
                
                input.parentElement.appendChild(feedback);
            }
        }

        // Show form-level errors
        if (errors.non_field_errors) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-danger alert-dismissible fade show';
            alert.setAttribute('role', 'alert');
            alert.innerHTML = `
                <strong>Error!</strong> ${Array.isArray(errors.non_field_errors) ? errors.non_field_errors.join(', ') : errors.non_field_errors}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            form.insertBefore(alert, form.firstChild);
        }
    }

    /**
     * Setup HTMX form submission
     */
    function setupHTMXForm(form, options = {}) {
        const {
            onSuccess = null,
            onError = null
        } = options;

        // Add CSRF token if not present
        const csrfToken = window.app?.getCookie?.('csrftoken');
        if (csrfToken && form.method.toUpperCase() !== 'GET') {
            let csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
            if (!csrfInput) {
                csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                form.appendChild(csrfInput);
            }
        }

        // Handle form submit with HTMX
        form.addEventListener('htmx:beforeRequest', (e) => {
            setFormLoading(form, true);
        });

        form.addEventListener('htmx:afterRequest', (e) => {
            setFormLoading(form, false);
            
            // Check for validation errors
            if (e.detail.xhr.status === 400) {
                try {
                    const errors = JSON.parse(e.detail.xhr.response);
                    displayFormErrors(form, errors);
                    
                    if (onError) {
                        onError(errors);
                    }
                } catch (err) {
                    console.error('Error parsing form errors:', err);
                }
            }
        });

        form.addEventListener('htmx:responseEnd', (e) => {
            if (e.detail.xhr.status === 200 || e.detail.xhr.status === 201) {
                if (onSuccess) {
                    onSuccess(e);
                } else {
                    // Show success notification
                    if (window.app?.showNotification) {
                        window.app.showNotification({
                            title: 'Success',
                            message: 'Form submitted successfully',
                            level: 'success'
                        });
                    }
                }
            }
        });
    }

    /**
     * Setup real-time form field validation
     */
    function setupFieldValidation(form) {
        const fields = form.querySelectorAll('input[required], select[required], textarea[required]');

        fields.forEach(field => {
            // Show validation on blur
            field.addEventListener('blur', () => {
                if (field.checkValidity()) {
                    field.classList.remove('is-invalid');
                    field.classList.add('is-valid');
                    
                    // Remove error message
                    const feedback = field.parentElement.querySelector('.invalid-feedback');
                    if (feedback) {
                        feedback.remove();
                    }
                } else {
                    field.classList.remove('is-valid');
                    field.classList.add('is-invalid');
                }
            });

            // Clear error on input
            field.addEventListener('input', () => {
                if (field.classList.contains('is-invalid')) {
                    field.classList.remove('is-invalid');
                }
            });
        });
    }

    /**
     * Get form data as object
     */
    function getFormData(form) {
        const formData = new FormData(form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            if (data[key] === undefined) {
                data[key] = value;
            } else if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        }

        return data;
    }

    /**
     * Reset form and clear validation classes
     */
    function resetForm(form) {
        form.reset();
        form.querySelectorAll('.is-invalid, .is-valid').forEach(el => {
            el.classList.remove('is-invalid', 'is-valid');
        });
        form.querySelectorAll('.invalid-feedback').forEach(el => {
            el.remove();
        });
    }

    // Export functions
    window.app.validateForm = validateForm;
    window.app.setFormLoading = setFormLoading;
    window.app.displayFormErrors = displayFormErrors;
    window.app.setupHTMXForm = setupHTMXForm;
    window.app.setupFieldValidation = setupFieldValidation;
    window.app.getFormData = getFormData;
    window.app.resetForm = resetForm;

    // Auto-setup forms with data attributes
    document.addEventListener('app:ready', () => {
        // Setup field validation on all forms
        document.querySelectorAll('form').forEach(form => {
            setupFieldValidation(form);

            // Setup HTMX forms
            if (form.getAttribute('hx-post') || form.getAttribute('hx-get') || form.getAttribute('hx-patch')) {
                setupHTMXForm(form);
            }
        });
    });

    // Re-setup after HTMX swap
    if (window.htmx) {
        document.body.addEventListener('htmx:afterSettle', () => {
            document.querySelectorAll('form:not([data-htmx-setup])').forEach(form => {
                form.setAttribute('data-htmx-setup', 'true');
                setupFieldValidation(form);

                if (form.getAttribute('hx-post') || form.getAttribute('hx-get') || form.getAttribute('hx-patch')) {
                    setupHTMXForm(form);
                }
            });
        });
    }

    console.log('✓ Form system loaded');

})();
