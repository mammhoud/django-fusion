import bootbox from 'shared/js/utility/bootbox-shim.js';

/**
 * ModalService — unified API for site modals.
 * Uses `UnifiedModal` instances when available, falls back to Bootbox.
 */
export class ModalService {
    constructor() {
        this.unified = null;
        this._ensureUnified();
        this.currentModal = null;
    }

    _ensureUnified() {
        try {
            if (typeof window !== 'undefined' && window.uiManager) {
                const comps = window.uiManager.getComponent('unifiedModal');
                if (comps && comps.length) this.unified = comps[0];
            }
        } catch (err) {
            // ignore
        }
    }

    showUnified(htmlOrOptions = '', opts = {}) {
        // If we have a unified modal instance, use it
        if (!this.unified) this._ensureUnified();
        if (this.unified && typeof this.unified.openHTMXModal === 'function') {
            // If a URL is provided, treat as HTMX modal
            if (opts.url) return this.unified.openHTMXModal(opts.url, opts.title || '');
            // Otherwise inject HTML
            const container = document.getElementById('unified-modal-container');
            if (container) {
                container.innerHTML = typeof htmlOrOptions === 'string' ? htmlOrOptions : htmlOrOptions.html || '';
                this.unified._refreshModalComponents?.();
                this.unified.showUnifiedModal();
                return this.unified;
            }
        }

        // Fallback: Bootbox
        return bootbox.dialog({
            title: opts.title || '',
            message: typeof htmlOrOptions === 'string' ? htmlOrOptions : (htmlOrOptions.message || ''),
            className: opts.className || '',
            backdrop: opts.backdrop ?? true,
            closeButton: opts.closeButton ?? true,
            animate: opts.animate ?? true,
            size: opts.size || 'large',
            buttons: opts.buttons || { close: { label: 'Close', className: 'btn-secondary' } }
        });
    }

    alert(message, title = 'Alert', opts = {}) {
        const m = bootbox.alert({ title, message, callback: opts.callback });
        this.currentModal = m;
        return m;
    }

    confirm(message, title = 'Confirm', onConfirm = () => { }, onCancel = () => { }) {
        const m = bootbox.confirm({ title, message, callback: (r) => r ? onConfirm() : onCancel() });
        this.currentModal = m;
        return m;
    }

    prompt(title = 'Enter value', placeholder = '', onSubmit = () => { }, onCancel = () => { }) {
        const m = bootbox.prompt({ title, inputType: 'text', placeholder, callback: (r) => r !== null ? onSubmit(r) : onCancel() });
        this.currentModal = m;
        return m;
    }

    /**
     * Open a testimonial modal using Bootbox (moved from UnifiedModal)
     */
    openTestimonialModal(options = {}) {
        const { id, trigger } = options;
        let item = trigger;

        if (id) {
            item = document.querySelector(`[data-testimonials-item][data-id="${id}"]`);
        }
        if (!item) {
            console.warn('Testimonial item not found');
            return null;
        }

        const avatarSrc = item.querySelector('[data-testimonials-avatar]')?.src || '';
        const name = item.querySelector('[data-testimonials-title]')?.textContent.trim() || '';
        const title = item.querySelector('[data-testimonials-role]')?.textContent.trim() || '';
        const text = item.querySelector('[data-testimonials-text]')?.innerHTML || '';

        const message = `
            <div class="vresume-testimonial-modal-content">
                <div class="testimonial-header">
                    ${avatarSrc ? `<img src="${avatarSrc}" alt="${this._esc(name)}" class="testimonial-avatar" loading="lazy">` : ''}
                    <div class="testimonial-info">
                        <h4 class="testimonial-name">${this._esc(name)}</h4>
                        ${title ? `<p class="testimonial-title">${this._esc(title)}</p>` : ''}
                    </div>
                </div>
                <div class="testimonial-quote-icon"><i class="ri-double-quotes-l"></i></div>
                <div class="testimonial-body">${text}</div>
            </div>`;

        const dlg = bootbox.dialog({
            message,
            title: name,
            className: 'vresume-testimonial-modal modal-lg',
            backdrop: true,
            closeButton: true,
            animate: true,
            buttons: {
                close: {
                    label: 'Close',
                    className: 'btn-secondary',
                    callback: () => { return true; }
                }
            },
            onEscape: true,
        });
        this.currentModal = dlg;
        return dlg;
    }

    openCustomModal({ title = 'Modal', message = '', size = 'large', buttons = {}, onClose = () => { } } = {}) {
        const sizeClass = {
            small: 'modal-sm', medium: 'modal-md', large: 'modal-lg', 'extra-large': 'modal-xl'
        }[size] || 'modal-lg';

        const dlg = bootbox.dialog({
            title,
            message,
            className: sizeClass,
            backdrop: true,
            closeButton: true,
            animate: true,
            buttons: buttons || {
                close: {
                    label: 'Close',
                    className: 'btn-secondary',
                    callback: () => { onClose(); return true; }
                }
            },
            onEscape: true,
        });
        this.currentModal = dlg;
        return dlg;
    }

    closeAll() {
        // Remove any Bootbox modals and their backdrops
        document.querySelectorAll('.bootbox.modal').forEach(modal => {
            const backdrop = modal.nextElementSibling;
            if (backdrop?.classList.contains('modal-backdrop')) backdrop.remove();
            modal.remove();
        });
        this.currentModal = null;
    }

    _esc(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

export const modalService = new ModalService();
export default ModalService;
