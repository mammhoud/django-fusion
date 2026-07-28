export class SidebarComponent {
    constructor() {
        this.sidebarHost = document.querySelector('[data-sidebar]');
        this.sidebar = this.sidebarHost?.querySelector('.sidebar') || this.sidebarHost;
        this.sidebarBtn = document.querySelector('[data-sidebar-btn]');
        this.isActive = false;
    }

    init() {
        if (!this.sidebarBtn || !this.sidebarHost || !this.sidebar) {
            console.debug('Sidebar component: elements not found');
            return false;
        }

        this.syncStateFromDOM();
        this.bindEvents();
        console.log('✅ Sidebar component initialized');
        return true;
    }

    syncStateFromDOM() {
        const more = this.sidebar.querySelector('.sidebar__more');
        const expanded = this.sidebarBtn.getAttribute('aria-expanded') === 'true' || more?.classList.contains('open');
        this.isActive = Boolean(expanded);
        this.sidebar.classList.toggle('sidebar--active', this.isActive);
    }

    bindEvents() {
        this._toggleHandler = this.toggle.bind(this);
        this.sidebarBtn.addEventListener('click', this._toggleHandler);
    }

    toggle() {
        this.isActive = !this.isActive;

        const more = this.sidebar.querySelector('.sidebar__more');
        if (more) {
            more.classList.toggle('open', this.isActive);
        }

        this.sidebar.classList.toggle('sidebar--active', this.isActive);

        if (this.sidebarBtn) {
            const textEl = this.sidebarBtn.querySelector('.sidebar__toggle-btn__text');
            const iconEl = this.sidebarBtn.querySelector('.sidebar__toggle-icon');
            if (textEl) textEl.textContent = this.isActive ? 'Hide Profile' : 'Show Profile';
            if (iconEl) iconEl.classList.toggle('ri-arrow-up-s-line', this.isActive);
            if (iconEl) iconEl.classList.toggle('ri-arrow-down-s-line', !this.isActive);
            this.sidebarBtn.setAttribute('aria-expanded', String(this.isActive));
        }
    }

    open() {
        if (!this.isActive) {
            this.toggle();
        }
    }

    close() {
        if (this.isActive) {
            this.toggle();
        }
    }

    destroy() {
        if (this.sidebarBtn && this._toggleHandler) {
            this.sidebarBtn.removeEventListener('click', this._toggleHandler);
            this._toggleHandler = null;
        }
    }
}

export default SidebarComponent;
