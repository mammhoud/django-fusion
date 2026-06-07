/**
 * Modal Management System
 * Unified modal handling across all sites
 * 
 * Features:
 * - Easy modal creation
 * - Form integration
 * - HTMX support
 * - Event handling
 */

(function() {
    'use strict';

    window.app = window.app || {};

    /**
     * Create and show a modal
     */
    function showModal(options = {}) {
        const {
            id = `modal-${Date.now()}`,
            title = '',
            content = '',
            size = 'modal-lg',
            centered = true,
            scrollable = false,
            footer = '',
            backdrop = 'static',
            keyboard = false
        } = options;

        // Create modal HTML
        const modal = document.createElement('div');
        modal.id = id;
        modal.className = 'modal fade';
        modal.setAttribute('tabindex', '-1');
        modal.setAttribute('data-bs-backdrop', backdrop);
        modal.setAttribute('data-bs-keyboard', keyboard);

        const dialogClass = ['modal-dialog', size];
        if (centered) dialogClass.push('modal-dialog-centered');
        if (scrollable) dialogClass.push('modal-dialog-scrollable');

        modal.innerHTML = `
            <div class="${dialogClass.join(' ')}">
                <div class="modal-content">
                    ${title ? `
                        <div class="modal-header">
                            <h5 class="modal-title">${escapeHtml(title)}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                    ` : ''}
                    <div class="modal-body">
                        ${content}
                    </div>
                    ${footer ? `
                        <div class="modal-footer">
                            ${footer}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        // Add to DOM
        document.body.appendChild(modal);

        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();

        // Clean up on hide
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });

        return bsModal;
    }

    /**
     * Close active modal
     */
    function closeModal(id = null) {
        let modal;
        if (id) {
            modal = document.getElementById(id);
        } else {
            modal = document.querySelector('.modal.show');
        }

        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }

    /**
     * Update modal content via HTMX
     */
    function loadModalContent(options = {}) {
        const {
            modalId,
            url,
            method = 'GET'
        } = options;

        const modal = document.getElementById(modalId);
        if (!modal) return;

        const body = modal.querySelector('.modal-body');
        if (!body) return;

        // Show loading spinner
        body.innerHTML = '<div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>';

        // Fetch content
        fetch(url, { method })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                return response.text();
            })
            .then(html => {
                body.innerHTML = html;

                // Re-initialize Bootstrap components
                if (window.app && window.app.reinitializeBootstrap) {
                    window.app.reinitializeBootstrap();
                }

                // Dispatch custom event
                document.dispatchEvent(new CustomEvent('modal:contentLoaded', { detail: { modalId } }));
            })
            .catch(error => {
                console.error('Error loading modal content:', error);
                body.innerHTML = `<div class="alert alert-danger">Error loading content. Please try again.</div>`;
            });
    }

    /**
     * Handle form submission in modal
     */
    function setupModalForm(options = {}) {
        const {
            modalId,
            formId,
            submitUrl,
            method = 'POST',
            onSuccess = null,
            onError = null
        } = options;

        const modal = document.getElementById(modalId);
        const form = modal?.querySelector(`#${formId}`) || modal?.querySelector('form');

        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn?.textContent;
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
            }

            try {
                const formData = new FormData(form);
                const response = await fetch(submitUrl || form.action, {
                    method: method || form.method,
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    // Close modal
                    closeModal(modalId);

                    // Call success callback
                    if (onSuccess) {
                        onSuccess(data);
                    } else {
                        // Show success notification
                        if (window.app?.showNotification) {
                            window.app.showNotification({
                                title: 'Success',
                                message: data.message || 'Operation completed successfully',
                                level: 'success'
                            });
                        }
                    }
                } else {
                    // Handle form errors
                    const errors = await response.json();
                    
                    if (onError) {
                        onError(errors);
                    } else {
                        // Display field errors
                        for (const [field, messages] of Object.entries(errors)) {
                            const input = form.querySelector(`[name="${field}"]`);
                            if (input) {
                                input.classList.add('is-invalid');
                                const feedback = document.createElement('div');
                                feedback.className = 'invalid-feedback d-block';
                                feedback.textContent = messages.join(', ');
                                input.parentElement.appendChild(feedback);
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Form submission error:', error);
                if (window.app?.showNotification) {
                    window.app.showNotification({
                        title: 'Error',
                        message: 'An error occurred. Please try again.',
                        level: 'danger'
                    });
                }
            } finally {
                // Restore button state
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            }
        });
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Export functions
    window.app.showModal = showModal;
    window.app.closeModal = closeModal;
    window.app.loadModalContent = loadModalContent;
    window.app.setupModalForm = setupModalForm;

    console.log('✓ Modal system loaded');

})();
