import { modalService } from '../../services/modal.js';

export class UnifiedModal {
    constructor({ element, manager } = {}) {
        this.element = element || document.body;
        this.currentModal = null;
        this.isOpen = false;
        this._listenersSetup = false;
        this.uiManager = manager || null;
    }

    async init() {
        if (!this.uiManager && typeof window !== 'undefined' && window.uiManager) {
            this.uiManager = window.uiManager;
        }

        console.log('✅ Unified Modal initialized (uiManager:', !!this.uiManager, ')');

        this.setupEventListeners();
        this.setupHTMXListeners();
        this.setupModalCloseHandlers();
        return true;
    }

    showUnifiedModal() {
        const overlay = this._getOverlay();
        if (!overlay) {
            console.error('❌ Unified modal overlay not found');
            return false;
        }

        try {
            const backdrops = Array.from(document.querySelectorAll('.modal-backdrop'));
            const topBackdrop = backdrops.length ? backdrops[backdrops.length - 1] : null;
            const backdropZ = topBackdrop ? parseInt(window.getComputedStyle(topBackdrop).zIndex) || 0 : 0;
            const desired = Math.max(11050, backdropZ + 10);
            overlay.style.zIndex = String(desired);
            console.log('🧭 Overlay z-index set to', overlay.style.zIndex, '(backdrop z-index:', backdropZ, ')');
        } catch (err) {}

        overlay.setAttribute('aria-hidden', 'false');
        overlay.classList.add('unified-modal__overlay--active');
        overlay.style.display = 'flex';
        overlay.style.visibility = 'visible';
        overlay.style.opacity = '1';
        document.body.style.overflow = 'hidden';
        this.isOpen = true;

        console.log('✨ Modal overlay shown');
        document.dispatchEvent(new CustomEvent('vresume:modal:shown', {
            detail: { overlay },
            bubbles: true, cancelable: false
        }));

        return true;
    }

    hideUnifiedModal() {
        const overlay = this._getOverlay();
        if (overlay) {
            overlay.setAttribute('aria-hidden', 'true');
            overlay.classList.remove('unified-modal__overlay--active');
            overlay.style.visibility = 'hidden';
            overlay.style.opacity = '0';
            overlay.style.display = 'none';
        }
        document.body.style.overflow = '';
        this.isOpen = false;

        const container = this._getContainer();
        if (container) {
            setTimeout(() => {
                container.innerHTML = '';
            }, 300);
        }

        console.log('🔒 Modal overlay hidden');
        document.dispatchEvent(new CustomEvent('vresume:modal:closed', {
            bubbles: true, cancelable: false
        }));
    }

    _getOverlay() {
        const el = document.getElementById('unified-modal-overlay');
        if (!el) console.warn('⚠️  #unified-modal-overlay missing in DOM');
        return el;
    }

    _getContainer() {
        const el = document.getElementById('unified-modal-container');
        if (!el) console.warn('⚠️  #unified-modal-container missing in DOM');
        return el;
    }

    _isUnifiedModalTarget(targetValue) {
        if (!targetValue) return false;
        return String(targetValue).trim() === '#unified-modal-container';
    }

    _isUnifiedModalRequest(detail = {}) {
        const directTarget = detail.target;
        if (directTarget?.id === 'unified-modal-container') return true;

        const sourceEl = detail.elt || detail.requestConfig?.elt || detail.requestConfig?.triggeringEvent?.target;
        const sourceTarget = sourceEl?.getAttribute?.('hx-target') || sourceEl?.dataset?.hxTarget;
        if (this._isUnifiedModalTarget(sourceTarget)) return true;

        const cfgTarget = detail.requestConfig?.target;
        if (this._isUnifiedModalTarget(cfgTarget)) return true;

        return false;
    }

    setupEventListeners() {
        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('[data-modal-trigger]');
            if (trigger) {
                e.preventDefault();
                const modalType = trigger.dataset.modalTrigger;
                const modalId = trigger.dataset.modalId;
                this.openModal(modalType, { id: modalId, trigger });
            }
        });

        document.addEventListener('click', (e) => {
            const trigger = e.target.closest('[data-htmx-modal]');
            if (trigger) {
                e.preventDefault();
                const url = trigger.dataset.htmxModal;
                const title = trigger.dataset.modalTitle || 'Modal';
                this.openHTMXModal(url, title);
            }
        });

        document.addEventListener('click', (e) => {
            const el = e.target.closest('[hx-get][hx-target]');
            if (!el) return;
            const target = el.getAttribute('hx-target') || '';
            if (this._isUnifiedModalTarget(target)) {
                this.showUnifiedModal();
            }
        });
    }

    setupModalCloseHandlers() {
        document.addEventListener('click', (e) => {
            const closeBtn = e.target.closest('[data-modal-close]');
            if (closeBtn) {
                e.preventDefault();
                e.stopPropagation();
                console.log('🔒 Close button clicked');
                this.hideUnifiedModal();
            }
        });

        const overlay = this._getOverlay();
        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    console.log('🔒 Overlay clicked - closing modal');
                    this.hideUnifiedModal();
                }
            });
        }

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                console.log('🔒 Escape key pressed - closing modal');
                this.hideUnifiedModal();
            }
        });
    }

    setupHTMXListeners() {
        if (this._listenersSetup) return;
        this._listenersSetup = true;

        this._htmxHandlers = {
            beforeRequest: (e) => {
                const target = e.detail.target;
                if (this._isUnifiedModalRequest(e.detail) || target?.hasAttribute?.('data-htmx-modal-content')) {
                    console.log('📡 HTMX request started for modal');
                    this.showUnifiedModal();
                    const container = this._getContainer();
                    if (container) {
                        container.innerHTML = `<div class="text-center p-4"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div><p class="mt-2">Loading...</p></div>`;
                    }
                }
            },

            responseError: (e) => {
                console.error('❌ HTMX response error:', e.detail);
                if (e.detail.target?.hasAttribute?.('data-htmx-modal-content') || e.detail.target?.id === 'unified-modal-container') {
                    const container = this._getContainer();
                    if (container) {
                        const errorMsg = e.detail.error?.message || 'Error loading content. Please try again.';
                        container.innerHTML = `<div class="alert alert-danger m-3"><strong>Error</strong><p>${this._esc(errorMsg)}</p></div>`;
                        if (!this.isOpen) {
                            this.showUnifiedModal();
                        }
                    }
                }
            },

            afterSwapContainer: (e) => {
                const target = e.detail.target;
                if (!target) return;

                const container = this._getContainer();
                if (!container) return;

                if (target === container || target.id === 'unified-modal-container' || container.contains(target)) {
                    console.log('✅ HTMX swap completed for modal container');
                    setTimeout(async () => {
                        if (container.innerHTML.trim()) {
                            console.log('🔄 Refreshing components after content swap...');
                            await this._refreshModalComponents();

                            if (!this.isOpen) {
                                this.showUnifiedModal();
                            }

                            console.log('📢 Dispatching modal:shown event');
                            document.dispatchEvent(new CustomEvent('vresume:modal:shown', {
                                detail: { container },
                                bubbles: true,
                                cancelable: false,
                            }));
                        } else {
                            console.warn('⚠️  HTMX swap but container empty — hiding overlay');
                            this.hideUnifiedModal();
                        }
                    }, 50);
                }
            },
        };

        document.addEventListener('htmx:beforeRequest', this._htmxHandlers.beforeRequest);
        document.addEventListener('htmx:afterSwap', this._htmxHandlers.afterSwapContainer);
        document.addEventListener('htmx:responseError', this._htmxHandlers.responseError);

        document.addEventListener('htmx:afterSettle', (e) => {
            const target = e.detail.target;
            const container = this._getContainer();
            if (container && (target === container || target.id === 'unified-modal-container' || container.contains(target))) {
                console.log('🎯 HTMX settled for modal - final check');
                if (!this.isOpen && container.innerHTML.trim()) {
                    console.log('🚀 Modal not open but content exists - showing now');
                    this._refreshModalComponents();
                    this.showUnifiedModal();
                }
            }
        });

        console.log('📡 Unified Modal HTMX listeners registered');
    }

    async _refreshModalComponents() {
        const container = this._getContainer();
        if (!container) {
            console.warn('⚠️  Container not found during component refresh');
            return;
        }

        console.log('🔄 Starting component refresh in modal...');

        console.log('⏱️ Waiting 150ms for DOM settle before refreshing components');
        await new Promise(r => setTimeout(r, 150));

        let refreshCount = 0;

        if (this.uiManager && typeof this.uiManager.refreshComponent === 'function') {
            try {
                console.log('🎬 Refreshing sliders...');
                const sliderCount = await this.uiManager.refreshComponent('sliders');
                if (sliderCount) {
                    console.log(`✅ Refreshed ${sliderCount} slider instances`);
                    refreshCount += sliderCount;
                }
            } catch (error) {
                console.warn('⚠️  Error refreshing sliders:', error);
            }

            try {
                console.log('🖼️  Refreshing background images...');
                const imageCount = await this.uiManager.refreshComponent('images');
                if (imageCount) {
                    console.log(`✅ Refreshed ${imageCount} image instances`);
                    refreshCount += imageCount;
                }
            } catch (error) {
                console.warn('⚠️  Error refreshing images:', error);
            }

            const refreshIds = ['animations', 'lightbox', 'contentFilter', 'tagFilter', 'accordion'];
            for (const id of refreshIds) {
                try {
                    const instances = this.uiManager.getComponent(id);
                    if (instances && instances.length > 0) {
                        const result = await this.uiManager.refreshComponent(id);
                        if (result) {
                            console.log(`✅ Refreshed ${id}`);
                            refreshCount += instances.length;
                        }
                    }
                } catch (error) {
                    console.warn(`⚠️  Error refreshing ${id}:`, error);
                }
            }
        }

        if (!refreshCount && window.SlidersManager?._instance) {
            try {
                console.log('🎬 Using fallback SlidersManager...');
                window.SlidersManager._instance.refreshContainer(container);
                console.log('✅ SlidersManager refresh completed');
                refreshCount++;
            } catch (error) {
                console.warn('⚠️  Error with SlidersManager:', error);
            }
        }

        if (window.htmx) {
            try {
                console.log('📡 Processing HTMX elements...');
                window.htmx.process(container);
                console.log('✅ HTMX processing completed');
            } catch (error) {
                console.warn('⚠️  Error processing HTMX:', error);
            }
        }

        console.log(`🎉 Component refresh completed (${refreshCount} components refreshed)`);
    }

    openHTMXModal(url) {
        const container = this._getContainer();
        if (!container) {
            console.error('❌ Unified modal container not found');
            return null;
        }

        console.log(`🚀 Opening HTMX modal from URL: ${url}`);

        this.showUnifiedModal();
        container.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading...</p>
            </div>`;

        fetch(url, {
            headers: { 'HX-Request': 'true' }
        })
            .then(r => {
                if (!r.ok) {
                    console.error(`❌ HTTP Error: ${r.status}`);
                    throw new Error(`HTTP ${r.status}`);
                }
                return r.text();
            })
            .then(async html => {
                console.log('📄 Content received, injecting into modal');
                container.innerHTML = html;

                console.log('🔄 Refreshing components after content load');
                await this._refreshModalComponents();

                if (!this.isOpen) {
                    console.log('🚀 Ensuring modal is visible');
                    this.showUnifiedModal();
                }

                console.log('📢 Dispatching modal:shown event');
                document.dispatchEvent(new CustomEvent('vresume:modal:shown', {
                    detail: { container },
                    bubbles: true, cancelable: false,
                }));
            })
            .catch(err => {
                console.error('❌ Modal load error:', err);
                container.innerHTML = `<div class="alert alert-danger m-3"><strong>Error</strong><p>${this._esc(err.message || 'Error loading content.')}</p></div>`;
                if (!this.isOpen) {
                    this.showUnifiedModal();
                }
            });

        return this;
    }

    openModal(type, options = {}) {
        switch (type) {
            case 'testimonial':
                return modalService.openTestimonialModal(options);
            case 'confirm':
                return modalService.confirm(options.message || options, options.title, options.onConfirm, options.onCancel);
            case 'alert':
                return modalService.alert(options.message || options, options.title, { callback: options.onClose });
            case 'prompt':
                return modalService.prompt(options.title, options.placeholder, options.onSubmit, options.onCancel);
            case 'custom':
                return modalService.openCustomModal(options);
            default:
                console.warn(`Unknown modal type: ${type}`);
                return null;
        }
    }

    close() {
        try {
            if (modalService && typeof modalService.closeAll === 'function') {
                modalService.closeAll();
            }
        } catch (error) {
            console.warn('⚠️  Failed to close modal service:', error);
        }
        this.isOpen = false;
    }

    closeAll() {
        try {
            if (modalService && typeof modalService.closeAll === 'function') modalService.closeAll();
        } catch (error) {
            console.warn('⚠️  Failed to close all modal service dialogs:', error);
        }
        this.isOpen = false;
    }

    destroy() {
        this.closeAll();
        this.currentModal = null;
    }

    _esc(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

export default UnifiedModal;
