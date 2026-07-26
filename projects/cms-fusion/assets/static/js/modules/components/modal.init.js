/**
 * Modal Controller Component
 * Handles modal functionality with focus trap and animations
 */

import { debounce, Utils, DOM } from '../../utility/index.js';

export class ModalController {
    static activeModals = new Set();

    constructor(element, options = {}) {
        this.element = element;
        this.options = {
            backdrop: true,
            keyboard: true,
            focus: true,
            closeOnBackdropClick: true,
            animationDuration: 300,
            ...options
        };

        this.isOpen = false;
        this.previousActiveElement = null;
        this.focusableElements = [];

        this.init();
    }

    init() {
        this.setupModal();
        this.bindEvents();
    }

    setupModal() {
        // Create backdrop if needed
        if (this.options.backdrop && !this.element.querySelector('.modal-backdrop')) {
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop';
            this.element.prepend(backdrop);
        }

        // Add ARIA attributes
        this.element.setAttribute('role', 'dialog');
        this.element.setAttribute('aria-modal', 'true');
        this.element.setAttribute('aria-hidden', 'true');

        // Find focusable elements
        this.updateFocusableElements();
    }

    bindEvents() {
        // Close button
        const closeButtons = this.element.querySelectorAll('[data-modal-close]');
        closeButtons.forEach(btn => {
            DOM.on(btn, 'click', () => this.close());
        });

        // Keyboard events
        if (this.options.keyboard) {
            DOM.on(document, 'keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });
        }

        // Backdrop click
        if (this.options.closeOnBackdropClick) {
            DOM.on(this.element, 'click', (e) => {
                if (e.target === this.element || e.target.classList.contains('modal-backdrop')) {
                    this.close();
                }
            });
        }

        // Focus trap
        if (this.options.focus) {
            DOM.on(this.element, 'keydown', (e) => {
                if (e.key !== 'Tab' || !this.isOpen) return;

                if (this.focusableElements.length === 0) {
                    e.preventDefault();
                    return;
                }

                const firstElement = this.focusableElements[0];
                const lastElement = this.focusableElements[this.focusableElements.length - 1];

                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            });
        }
    }

    open() {
        if (this.isOpen) return;

        // Store current active element
        this.previousActiveElement = document.activeElement;

        // Show modal
        this.element.style.display = 'block';
        this.element.removeAttribute('aria-hidden');

        // Trigger animation
        setTimeout(() => {
            DOM.addClass(this.element, 'show');
            document.body.classList.add('modal-open');

            // Add to active modals
            ModalController.activeModals.add(this);
            this.isOpen = true;

            // Focus first focusable element
            if (this.options.focus && this.focusableElements.length > 0) {
                setTimeout(() => this.focusableElements[0].focus(), 10);
            }

            this.dispatchEvent('modal:opened');
        }, 10);
    }

    close() {
        if (!this.isOpen) return;

        // Hide modal
        DOM.removeClass(this.element, 'show');

        setTimeout(() => {
            this.element.style.display = 'none';
            this.element.setAttribute('aria-hidden', 'true');
            document.body.classList.remove('modal-open');

            // Remove from active modals
            ModalController.activeModals.delete(this);
            this.isOpen = false;

            // Restore focus
            if (this.previousActiveElement && this.previousActiveElement.focus) {
                this.previousActiveElement.focus();
            }

            this.dispatchEvent('modal:closed');
        }, this.options.animationDuration);
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    updateFocusableElements() {
        this.focusableElements = Array.from(
            this.element.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            )
        ).filter(el => !el.disabled && el.offsetParent !== null);
    }

    updateContent(content) {
        const contentElement = this.element.querySelector('.modal-content');
        if (contentElement) {
            contentElement.innerHTML = content;
            this.updateFocusableElements();
        }
    }

    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, modal: this },
            bubbles: true,
            cancelable: true
        });
        this.element.dispatchEvent(event);
    }

    destroy() {
        // Remove all event listeners
        const closeButtons = this.element.querySelectorAll('[data-modal-close]');
        closeButtons.forEach(btn => {
            DOM.off(btn, 'click');
        });

        DOM.off(document, 'keydown');
        DOM.off(this.element, 'click');
        DOM.off(this.element, 'keydown');

        // Close if open
        if (this.isOpen) {
            this.close();
        }

        ModalController.activeModals.delete(this);
    }
}

// Static method to close all modals
ModalController.closeAll = function () {
    ModalController.activeModals.forEach(modal => modal.close());
};

// Auto-initialize modals with data-modal attribute
document.addEventListener('DOMContentLoaded', () => {
    const modalElements = DOM.$$('[data-modal]');
    const modalInstances = new Map();

    // Initialize modal triggers
    DOM.$$('[data-modal-target]').forEach(trigger => {
        DOM.on(trigger, 'click', (e) => {
            e.preventDefault();
            const modalId = trigger.dataset.modalTarget;
            const modalElement = DOM.$(`#${modalId}`);

            if (!modalElement) return;

            if (!modalInstances.has(modalId)) {
                const modal = new ModalController(modalElement);
                modalInstances.set(modalId, modal);
            }

            modalInstances.get(modalId).open();
        });
    });
});

export default ModalController;