/**
 * Testimonials Component
 * Uses UnifiedModal for bootbox integration
 */

import UnifiedModal from '../modals/unified-modal.js';

export class TestimonialsComponent {
    constructor({ element } = {}) {
        this.element = element || document;
        this.testimonialsItems = this.element.querySelectorAll('[data-testimonials-item]');
        this.unifiedModal = new UnifiedModal({ element: this.element });
    }

    /**
     * Initialize testimonials component
     */
    async init() {
        if (this.testimonialsItems.length === 0) {
            console.debug('Testimonials component: elements not found');
            return false;
        }

        await this.unifiedModal.init();
        this.bindEvents();
        console.log('✅ Testimonials component initialized');
        return true;
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Testimonial item click
        this.testimonialsItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.openModal(item);
            });
            // Make it keyboard accessible
            item.setAttribute('role', 'button');
            item.setAttribute('tabindex', '0');
            item.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.openModal(item);
                }
            });
        });
    }

    /**
     * Open testimonials modal using UnifiedModal
     */
    openModal(item) {
        this.unifiedModal.openTestimonialModal({ trigger: item });
    }

    /**
     * Cleanup
     */
    destroy() {
        this.testimonialsItems.forEach(item => {
            // Remove event listeners
            const clone = item.cloneNode(true);
            if(item.parentNode) item.parentNode.replaceChild(clone, item);
        });
        this.unifiedModal.destroy();
    }
}

export default TestimonialsComponent;
