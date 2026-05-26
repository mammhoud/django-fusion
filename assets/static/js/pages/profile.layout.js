/**
 * @file layouts/profile.layout.js
 * Profile Layout with Navigation and Dynamic State Management
 */

import { BaseLayout } from './init.layout.js';

export class ProfileLayout extends BaseLayout {
    constructor(options = {}) {
        super({
            layoutId: 'profile',
            layoutType: 'profile',
            pageId: options.pageId || 'profile',
            debug: options.debug || false,
            enableNavigation: options.enableNavigation !== false,
            enableHeader: options.enableHeader !== false,
            enableModals: options.enableModals !== false,
            ...options
        });

        // Profile specific state
        this.subTypes = {
            PROFILE: 'profile',
            SETTINGS: 'settings',
            DASHBOARD: 'dashboard',
            ACTIVITY: 'activity',
            SECURITY: 'security'
        };

        this.currentSubType = null;
        this.currentPath = window.location.pathname;
        this.navLinks = null;
        this.offcanvas = null;
    }

    async initComponents() {
        this.log('🚀 Initializing profile components...');

        // Initialize navigation
        if (this.options.enableNavigation) {
            await this.initProfileNavigation();
        }

        // Initialize header
        if (this.options.enableHeader) {
            await this.initProfileHeader();
        }

        // Initialize modals
        if (this.options.enableModals) {
            await this.initModals();
        }

        // Initialize content areas
        await this.initContentAreas();
    }

    async applyContent() {
        this.log('Applying profile layout content...');

        // Detect sub-type from URL
        this.detectSubTypeFromURL();

        // Apply sub-type specific content
        await this.applySubTypeContent();

        // Update navigation state
        this.updateActiveState(window.location.pathname);

        // Update profile UI
        this.updateProfileUI();
    }

    // Sub-Type Detection
    detectSubTypeFromURL(url = window.location.pathname) {
        const subTypeMap = {
            '/profile': this.subTypes.PROFILE,
            '/profile/profile': this.subTypes.PROFILE,
            '/user/profile': this.subTypes.PROFILE,
            '/profile/settings': this.subTypes.SETTINGS,
            '/user/settings': this.subTypes.SETTINGS,
            '/profile/dashboard': this.subTypes.DASHBOARD,
            '/profile/activity': this.subTypes.ACTIVITY,
            '/profile/security': this.subTypes.SECURITY
        };

        // Check exact matches
        if (subTypeMap[url]) {
            this.currentSubType = subTypeMap[url];
        } else {
            // Check partial matches
            for (const [path, subType] of Object.entries(subTypeMap)) {
                if (url.startsWith(path)) {
                    this.currentSubType = subType;
                    break;
                }
            }
        }

        // Fallback to profile
        if (!this.currentSubType) {
            this.currentSubType = this.subTypes.PROFILE;
        }

        // Update options
        this.options.subType = this.currentSubType;
        this.options.pageType = this.currentSubType;

        this.log(`Profile sub-type detected: ${this.currentSubType}`);

        return this.currentSubType;
    }

    // Sub-Type Content
    async applySubTypeContent() {
        this.log(`Applying content for sub-type: ${this.currentSubType}`);

        // Remove previous sub-type classes
        Object.values(this.subTypes).forEach(subType => {
            document.body.classList.remove(`profile-${subType}`);
        });

        // Add current sub-type class
        document.body.classList.add(`profile-${this.currentSubType}`);

        // Apply sub-type specific transformations
        switch (this.currentSubType) {
            case this.subTypes.PROFILE:
                await this.applyProfileContent();
                break;
            case this.subTypes.SETTINGS:
                await this.applySettingsContent();
                break;
            case this.subTypes.DASHBOARD:
                await this.applyDashboardContent();
                break;
            case this.subTypes.ACTIVITY:
                await this.applyActivityContent();
                break;
            case this.subTypes.SECURITY:
                await this.applySecurityContent();
                break;
        }

        this.dispatchEvent('profile:sub-type-content-applied', {
            subType: this.currentSubType,
            timestamp: Date.now()
        });
    }

    async applyProfileContent() {
        this.log('Applying profile content...');
        // Profile-specific initialization
    }

    async applySettingsContent() {
        this.log('Applying settings content...');
        // Settings-specific initialization
    }

    async applyDashboardContent() {
        this.log('Applying dashboard content...');
        // Dashboard-specific initialization
    }

    async applyActivityContent() {
        this.log('Applying activity content...');
        // Activity-specific initialization
    }

    async applySecurityContent() {
        this.log('Applying security content...');
        // Security-specific initialization
    }

    // Component Initialization
    async initProfileNavigation() {
        this.log('Initializing profile navigation...');

        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            await new Promise(resolve => {
                document.addEventListener('DOMContentLoaded', resolve);
            });
        }

        this.navLinks = document.querySelectorAll('.profile__nav-link');

        if (!this.navLinks.length) {
            console.warn('ProfileLayout: No navigation links found');
            return;
        }

        this.attachNavigationListeners();

        // Store offcanvas reference
        this.offcanvas = document.getElementById('offcanvasNavigator');

        // Register component
        this.registerComponent('navigation', {
            element: this.navLinks,
            links: Array.from(this.navLinks),
            destroy: () => {
                // Cleanup handled by cleanup functions
            }
        });
    }

    attachNavigationListeners() {
        // Listen for HTMX after swap events
        const htmxAfterSwapHandler = (event) => {
            // Check if it's a profile navigation swap
            if (event.detail.target && event.detail.target.id === 'panel-content') {
                this.handleNavigation(event);
            }
        };

        document.body.addEventListener('htmx:afterSwap', htmxAfterSwapHandler);
        this.cleanupFunctions.push(() => {
            document.body.removeEventListener('htmx:afterSwap', htmxAfterSwapHandler);
        });

        // Listen for popstate (browser back/forward)
        const popstateHandler = () => {
            this.updateActiveState(window.location.pathname);
        };

        window.addEventListener('popstate', popstateHandler);
        this.cleanupFunctions.push(() => {
            window.removeEventListener('popstate', popstateHandler);
        });

        // Click handler for manual tracking
        this.navLinks.forEach(link => {
            const clickHandler = (e) => {
                const href = link.getAttribute('href');
                if (href) {
                    // Pre-emptively update active state for better UX
                    this.updateActiveState(href);
                }
            };

            link.addEventListener('click', clickHandler);
            this.cleanupFunctions.push(() => {
                link.removeEventListener('click', clickHandler);
            });
        });
    }

    handleNavigation(event) {
        // Get the new URL from the request
        const newPath = event.detail.pathInfo?.requestPath || window.location.pathname;
        this.updateActiveState(newPath);

        // Close mobile offcanvas if open
        this.closeMobileNav();

        // Dispatch event
        this.dispatchEvent('profile:navigated', {
            path: newPath,
            timestamp: Date.now()
        });
    }

    updateActiveState(path) {
        if (!this.navLinks) return;

        // Remove active class from all links
        this.navLinks.forEach(link => {
            link.classList.remove('active');
        });

        // Find and activate the matching link
        let matchedLink = null;

        // First try exact match
        this.navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href === path) {
                matchedLink = link;
            }
        });

        // If no exact match, try to match by URL pattern
        if (!matchedLink) {
            this.navLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href && path.startsWith(href)) {
                    matchedLink = link;
                }
            });
        }

        // Add active class to matched link
        if (matchedLink) {
            matchedLink.classList.add('active');
            this.currentPath = path;

            // Update sub-type if path changed
            const newSubType = this.detectSubTypeFromURL(path);
            if (newSubType !== this.currentSubType) {
                this.applySubTypeContent();
            }
        } else {
            console.warn('ProfileLayout: No matching link found for path:', path);
        }

        // Dispatch event
        this.dispatchEvent('profile:active-state-updated', {
            path,
            matchedLink: matchedLink ? matchedLink.getAttribute('href') : null,
            timestamp: Date.now()
        });
    }

    closeMobileNav() {
        if (this.offcanvas) {
            // Use Bootstrap's offcanvas API if available
            const bsOffcanvas = bootstrap?.Offcanvas?.getInstance(this.offcanvas);
            if (bsOffcanvas) {
                bsOffcanvas.hide();
            }
        }
    }

    async initProfileHeader() {
        const header = document.querySelector('.profile-header, [data-profile-header]');
        if (!header) return;

        this.log('Initializing profile header...');

        // Register component
        this.registerComponent('header', {
            element: header,
            destroy: () => {
                // Cleanup handled by cleanup functions
            }
        });
    }

    async initModals() {
        const modals = document.querySelectorAll('.profile-modal, [data-profile-modal]');

        modals.forEach(modal => {
            const modalId = modal.id || `modal-${modals.length}`;

            // Initialize modal controls
            this.initModalControls(modal, modalId);

            // Register component
            this.registerComponent(`modal-${modalId}`, {
                element: modal,
                id: modalId,
                destroy: () => {
                    // Cleanup handled by cleanup functions
                }
            });
        });
    }

    initModalControls(modal, modalId) {
        // Close buttons
        const closeButtons = modal.querySelectorAll('.modal-close, [data-close-modal]');
        closeButtons.forEach(btn => {
            const closeHandler = () => {
                this.closeModal(modalId);
            };

            btn.addEventListener('click', closeHandler);
            this.cleanupFunctions.push(() => {
                btn.removeEventListener('click', closeHandler);
            });
        });

        // Close on backdrop click
        const backdropClickHandler = (e) => {
            if (e.target === modal) {
                this.closeModal(modalId);
            }
        };

        modal.addEventListener('click', backdropClickHandler);
        this.cleanupFunctions.push(() => {
            modal.removeEventListener('click', backdropClickHandler);
        });

        // Close on escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                this.closeModal(modalId);
            }
        };

        document.addEventListener('keydown', escapeHandler);
        this.cleanupFunctions.push(() => {
            document.removeEventListener('keydown', escapeHandler);
        });
    }

    async initContentAreas() {
        const contentArea = document.getElementById('panel-content');
        if (!contentArea) return;

        this.log('Initializing content areas...');

        // Register component
        this.registerComponent('content', {
            element: contentArea,
            destroy: () => {
                // Cleanup handled by cleanup functions
            }
        });
    }

    // Modal Controls
    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('show');

        // Set focus to first input if exists
        const firstInput = modal.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }

        this.dispatchEvent('profile:modal-opened', {
            modal: modalId,
            timestamp: Date.now()
        });
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.remove('show');

        this.dispatchEvent('profile:modal-closed', {
            modal: modalId,
            timestamp: Date.now()
        });
    }

    // UI Updates
    updateProfileUI() {
        // Update page title
        this.updatePageTitle();
    }

    updatePageTitle() {
        const titleMap = {
            [this.subTypes.PROFILE]: 'Profile',
            [this.subTypes.SETTINGS]: 'Settings',
            [this.subTypes.DASHBOARD]: 'Dashboard',
            [this.subTypes.ACTIVITY]: 'Activity',
            [this.subTypes.SECURITY]: 'Security'
        };

        const baseTitle = document.title.split('|')[0]?.trim() || 'Profile';
        const subTypeTitle = titleMap[this.currentSubType] || this.currentSubType;

        document.title = `${subTypeTitle} | ${baseTitle}`;
    }

    // Public API
    refresh() {
        this.updateActiveState(window.location.pathname);
    }

    setActive(path) {
        this.updateActiveState(path);
    }

    getCurrentSubType() {
        return this.currentSubType;
    }

    getCurrentPath() {
        return this.currentPath;
    }

    // Cleanup
    async destroy() {
        this.log('Destroying profile layout...');

        // Clear references
        this.navLinks = null;
        this.offcanvas = null;

        await super.destroy();
    }
}

export default ProfileLayout;
