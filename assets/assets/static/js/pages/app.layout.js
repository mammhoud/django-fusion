/**
 * @file layouts/app.layout.js
 * Main Application Layout with Dashboard, Profile, Settings
 */

import { BaseLayout } from './init.layout.js';

export class AppLayout extends BaseLayout {
    constructor(options = {}) {
        super({
            layoutId: 'app',
            layoutType: 'app',
            pageId: options.pageId || 'app',
            debug: options.debug || false,
            enableSidebar: options.enableSidebar !== false,
            enableHeader: options.enableHeader !== false,
            enableTabs: options.enableTabs !== false,
            enableModals: options.enableModals !== false,
            ...options
        });

        // App specific state
        this.subTypes = {
            DASHBOARD: 'dashboard',
            PROFILE: 'profile',
            PROFILE_SETTINGS: 'profile-settings',
            PROFILE_DASHBOARD: 'profile-dashboard',
            SETTINGS: 'settings',
            REPORTS: 'reports',
            ANALYTICS: 'analytics'
        };
        
        this.currentSubType = null;
        this.panels = new Map();
        this.modals = new Map();
        this.tabs = new Map();
        this.widgets = new Map();
        
        // UI State
        this.sidebarOpen = true;
        this.headerVisible = true;
        this.panelStates = new Map();
        
        // Performance
        this.widgetPerformance = new Map();
    }

    async initComponents() {
        this.log('🚀 Initializing app components...');
        
        // Initialize sidebar
        if (this.options.enableSidebar) {
            await this.initSidebar();
        }
        
        // Initialize header
        if (this.options.enableHeader) {
            await this.initAppHeader();
        }
        
        // Initialize panels
        await this.initPanels();
        
        // Initialize modals
        if (this.options.enableModals) {
            await this.initModals();
        }
        
        // Initialize tabs
        if (this.options.enableTabs) {
            await this.initTabs();
        }
        
        // Initialize widgets
        await this.initWidgets();
        
        // Initialize navigation
        await this.initAppNavigation();
    }

    async applyContent() {
        this.log('Applying app layout content...');
        
        // Detect sub-type from URL
        this.detectSubTypeFromURL();
        
        // Apply sub-type specific content
        await this.applySubTypeContent();
        
        // Setup app navigation
        await this.setupAppNavigation();
        
        // Initialize user state
        await this.initUserState();
        
        // Update app UI
        this.updateAppUI();
    }

    // Sub-Type Detection
    detectSubTypeFromURL(url = window.location.pathname) {
        const subTypeMap = {
            '/dashboard': this.subTypes.DASHBOARD,
            '/app/dashboard': this.subTypes.DASHBOARD,
            '/profile': this.subTypes.PROFILE,
            '/profile/profile': this.subTypes.PROFILE,
            '/user/profile': this.subTypes.PROFILE,
            '/profile/settings': this.subTypes.PROFILE_SETTINGS,
            '/user/settings': this.subTypes.PROFILE_SETTINGS,
            '/profile/dashboard': this.subTypes.PROFILE_DASHBOARD,
            '/settings': this.subTypes.SETTINGS,
            '/app/settings': this.subTypes.SETTINGS,
            '/reports': this.subTypes.REPORTS,
            '/analytics': this.subTypes.ANALYTICS
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
        
        // Fallback to dashboard
        if (!this.currentSubType) {
            this.currentSubType = this.subTypes.DASHBOARD;
        }
        
        // Update options
        this.options.subType = this.currentSubType;
        this.options.pageType = this.currentSubType;
        
        this.log(`App sub-type detected: ${this.currentSubType}`);
        
        return this.currentSubType;
    }

    // Sub-Type Content
    async applySubTypeContent() {
        this.log(`Applying content for sub-type: ${this.currentSubType}`);
        
        // Remove previous sub-type classes
        Object.values(this.subTypes).forEach(subType => {
            document.body.classList.remove(`app-${subType}`);
        });
        
        // Add current sub-type class
        document.body.classList.add(`app-${this.currentSubType}`);
        
        // Apply sub-type specific transformations
        switch (this.currentSubType) {
            case this.subTypes.DASHBOARD:
                await this.applyDashboardContent();
                break;
            case this.subTypes.PROFILE:
                await this.applyProfileContent();
                break;
            case this.subTypes.PROFILE_SETTINGS:
                await this.applyProfileSettingsContent();
                break;
            case this.subTypes.PROFILE_DASHBOARD:
                await this.applyProfileDashboardContent();
                break;
            case this.subTypes.SETTINGS:
                await this.applySettingsContent();
                break;
            case this.subTypes.REPORTS:
                await this.applyReportsContent();
                break;
            case this.subTypes.ANALYTICS:
                await this.applyAnalyticsContent();
                break;
        }
        
        // Update navigation highlighting
        this.updateAppNavigation();
        
        this.dispatchEvent('app:sub-type-content-applied', {
            subType: this.currentSubType,
            timestamp: Date.now()
        });
    }

    async applyDashboardContent() {
        // this.log('Applying dashboard content...');
        
        // Initialize dashboard widgets
        // await this.initDashboardWidgets();
        
        // Initialize charts
        // await this.initCharts();
        
        // Initialize quick stats
        // await this.initQuickStats();
        
        // Initialize recent activity
        // await this.initRecentActivity();
    }

    async applyProfileContent() {
        this.log('Applying profile content...');
        
        // Initialize profile header
        await this.initProfileHeader();
        
        // Initialize profile tabs
        await this.initProfileTabs();
        
        // Initialize profile form
        await this.initProfileForm();
    }

    async applyProfileSettingsContent() {
        this.log('Applying profile settings content...');
        
        // Initialize settings tabs
        await this.initSettingsTabs();
        
        // Initialize settings forms
        await this.initSettingsForms();
        
        // Initialize security settings
        await this.initSecuritySettings();
    }

    async applyProfileDashboardContent() {
        this.log('Applying profile dashboard content...');
        
        // Initialize user stats
        await this.initUserStats();
        
        // Initialize user activity
        await this.initUserActivity();
        
        // Initialize connections
        await this.initConnections();
    }

    async applySettingsContent() {
        this.log('Applying settings content...');
        
        // Initialize account settings
        await this.initAccountSettings();
        
        // Initialize notification settings
        await this.initNotificationSettings();
        
        // Initialize privacy settings
        await this.initPrivacySettings();
    }

    async applyReportsContent() {
        this.log('Applying reports content...');
        
        // Initialize report filters
        await this.initReportFilters();
        
        // Initialize report tables
        await this.initReportTables();
        
        // Initialize export functionality
        await this.initExportFunctionality();
    }

    async applyAnalyticsContent() {
        this.log('Applying analytics content...');
        
        // Initialize analytics charts
        await this.initAnalyticsCharts();
        
        // Initialize metrics
        await this.initAnalyticsMetrics();
        
        // Initialize filters
        await this.initAnalyticsFilters();
    }

    // Component Initialization
    async initSidebar() {
        const sidebar = document.querySelector('.app-sidebar, [data-sidebar]');
        if (!sidebar) return;
        
        this.log('Initializing sidebar...');
        
        // Toggle button
        const toggleBtn = document.querySelector('.sidebar-toggle, [data-toggle-sidebar]');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleSidebar();
            });
        }
        
        // Collapse/expand sections
        const collapseButtons = sidebar.querySelectorAll('.sidebar-collapse, [data-collapse]');
        collapseButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = button.getAttribute('data-target');
                const target = document.getElementById(targetId);
                if (target) {
                    target.classList.toggle('collapsed');
                }
            });
        });
        
        // Store sidebar state
        this.sidebarOpen = !sidebar.classList.contains('collapsed');
        
        // Add to components
        this.registerComponent('sidebar', {
            element: sidebar,
            open: this.sidebarOpen,
            destroy: () => {
                // Cleanup event listeners
            }
        });
    }

    async initAppHeader() {
        const header = document.querySelector('.app-header, [data-app-header]');
        if (!header) return;
        
        this.log('Initializing app header...');
        
        // Search functionality
        const searchInput = header.querySelector('.app-search, [data-app-search]');
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce((e) => {
                this.handleAppSearch(e.target.value);
            }, 300));
        }
        
        // Notifications dropdown
        const notificationsBtn = header.querySelector('.notifications-btn, [data-notifications]');
        if (notificationsBtn) {
            notificationsBtn.addEventListener('click', () => {
                this.toggleNotifications();
            });
        }
        
        // User menu
        const userMenuBtn = header.querySelector('.user-menu-btn, [data-user-menu]');
        if (userMenuBtn) {
            userMenuBtn.addEventListener('click', () => {
                this.toggleUserMenu();
            });
        }
        
        // Add to components
        this.registerComponent('header', {
            element: header,
            visible: this.headerVisible,
            destroy: () => {
                // Cleanup event listeners
            }
        });
    }

    async initPanels() {
        const panels = document.querySelectorAll('.app-panel, [data-panel]');
        
        panels.forEach(panel => {
            const panelId = panel.id || `panel-${panels.length}`;
            const panelName = panel.getAttribute('data-panel') || panelId;
            
            // Initialize panel controls
            this.initPanelControls(panel, panelName);
            
            // Store panel state
            this.panelStates.set(panelName, {
                element: panel,
                open: !panel.classList.contains('collapsed'),
                pinned: panel.classList.contains('pinned')
            });
        });
    }

    initPanelControls(panel, panelName) {
        // Close button
        const closeBtn = panel.querySelector('.panel-close, [data-close-panel]');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closePanel(panelName);
            });
        }
        
        // Collapse button
        const collapseBtn = panel.querySelector('.panel-collapse, [data-collapse-panel]');
        if (collapseBtn) {
            collapseBtn.addEventListener('click', () => {
                this.togglePanel(panelName);
            });
        }
        
        // Pin button
        const pinBtn = panel.querySelector('.panel-pin, [data-pin-panel]');
        if (pinBtn) {
            pinBtn.addEventListener('click', () => {
                this.togglePanelPin(panelName);
            });
        }
    }

    async initModals() {
        const modals = document.querySelectorAll('.app-modal, [data-modal]');
        
        modals.forEach(modal => {
            const modalId = modal.id || `modal-${modals.length}`;
            
            // Store modal
            this.modals.set(modalId, {
                element: modal,
                open: modal.classList.contains('show')
            });
            
            // Initialize modal controls
            this.initModalControls(modal, modalId);
        });
    }

    initModalControls(modal, modalId) {
        // Close buttons
        const closeButtons = modal.querySelectorAll('.modal-close, [data-close-modal]');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.closeModal(modalId);
            });
        });
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal(modalId);
            }
        });
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                this.closeModal(modalId);
            }
        });
    }

    async initTabs() {
        const tabContainers = document.querySelectorAll('.app-tabs, [data-tabs]');
        
        tabContainers.forEach(container => {
            const tabs = container.querySelectorAll('.nav-tabs .nav-link, [data-tab]');
            const tabContents = container.querySelectorAll('.tab-content, [data-tab-content]');
            
            tabs.forEach(tab => {
                tab.addEventListener('click', (e) => {
                    e.preventDefault();
                    const tabId = tab.getAttribute('data-tab') || tab.getAttribute('href')?.substring(1);
                    if (tabId) {
                        this.switchTab(container, tabId);
                    }
                });
            });
            
            // Store tabs
            this.tabs.set(container.id || `tabs-${this.tabs.size}`, {
                container,
                tabs: Array.from(tabs),
                contents: Array.from(tabContents),
                active: this.getActiveTab(container)
            });
        });
    }

    async initWidgets() {
        const widgetElements = document.querySelectorAll('.app-widget, [data-widget]');
        
        widgetElements.forEach(widget => {
            const widgetId = widget.id || `widget-${widgetElements.length}`;
            const widgetType = widget.getAttribute('data-widget');
            
            // Initialize based on widget type
            this.initWidgetByType(widget, widgetType, widgetId);
            
            // Store widget
            this.widgets.set(widgetId, {
                element: widget,
                type: widgetType,
                performance: {
                    loadTime: 0,
                    refreshCount: 0
                }
            });
        });
    }

    initWidgetByType(widget, type, id) {
        switch (type) {
            case 'stats':
                this.initStatsWidget(widget, id);
                break;
            case 'chart':
                this.initChartWidget(widget, id);
                break;
            case 'table':
                this.initTableWidget(widget, id);
                break;
            case 'list':
                this.initListWidget(widget, id);
                break;
            case 'calendar':
                this.initCalendarWidget(widget, id);
                break;
            default:
                this.initGenericWidget(widget, id);
        }
    }

    // Widget Initialization Methods
    async initStatsWidget(widget, id) {
        const valueElements = widget.querySelectorAll('.stat-value');
        const loading = widget.querySelector('.widget-loading');
        
        if (loading) {
            // Simulate loading
            setTimeout(() => {
                loading.style.display = 'none';
                valueElements.forEach(el => {
                    el.textContent = this.formatNumber(Math.random() * 1000);
                });
            }, 1000);
        }
        
        // Refresh button
        const refreshBtn = widget.querySelector('.widget-refresh');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshWidget(id);
            });
        }
    }

    async initChartWidget(widget, id) {
        const canvas = widget.querySelector('canvas');
        if (!canvas || typeof Chart === 'undefined') return;
        
        const ctx = canvas.getContext('2d');
        const chartType = widget.getAttribute('data-chart-type') || 'line';
        const chartData = JSON.parse(widget.getAttribute('data-chart-data') || '{}');
        
        const chart = new Chart(ctx, {
            type: chartType,
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
        
        // Store chart instance
        this.widgets.get(id).chart = chart;
        
        // Resize handler
        const resizeHandler = () => {
            chart.resize();
        };
        
        window.addEventListener('resize', resizeHandler);
        this.cleanupFunctions.push(() => {
            window.removeEventListener('resize', resizeHandler);
            chart.destroy();
        });
    }

    async initTableWidget(widget, id) {
        const table = widget.querySelector('table');
        if (!table) return;
        
        // Initialize sorting if DataTables is available
        if (typeof $.fn.DataTable !== 'undefined') {
            $(table).DataTable({
                pageLength: 10,
                responsive: true
            });
        }
        
        // Initialize filtering
        const searchInput = widget.querySelector('.table-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterTable(table, e.target.value);
            });
        }
    }

    // Navigation
    async initAppNavigation() {
        this.log('Initializing app navigation...');
        
        // Listen for navigation events
        if (this.navigation) {
            this.onNavigationEvent('navigation:navigated', (data) => {
                this.handleAppNavigation(data);
            });
        }
        
        // Setup app-specific navigation
        this.setupAppNavLinks();
    }

    handleAppNavigation(data) {
        const url = data.detail?.url || data.detail?.currentUrl;
        if (url) {
            const subType = this.detectSubTypeFromURL(new URL(url).pathname);
            
            // Update content if sub-type changed
            if (subType !== this.currentSubType) {
                this.applySubTypeContent();
            }
        }
    }

    setupAppNavLinks() {
        const navLinks = document.querySelectorAll('.app-nav-link, [data-app-nav]');
        
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                if (href && href.startsWith('/')) {
                    // Track app navigation
                    this.trackAppNavigation(href);
                }
            });
        });
    }

    trackAppNavigation(path) {
        const analyticsData = {
            path,
            subType: this.currentSubType,
            timestamp: Date.now()
        };
        
        this.dispatchEvent('app:navigation', analyticsData);
        
        // Send to analytics if available
        if (window.gtag) {
            window.gtag('event', 'app_navigation', {
                app_sub_type: this.currentSubType,
                navigation_path: path
            });
        }
    }

    // UI Controls
    toggleSidebar() {
        const sidebar = document.querySelector('.app-sidebar, [data-sidebar]');
        if (!sidebar) return;
        
        sidebar.classList.toggle('collapsed');
        this.sidebarOpen = !sidebar.classList.contains('collapsed');
        
        // Dispatch event
        this.dispatchEvent('app:sidebar-toggled', {
            open: this.sidebarOpen,
            timestamp: Date.now()
        });
        
        // Update other UI elements
        this.updateLayoutForSidebar();
    }

    updateLayoutForSidebar() {
        const mainContent = document.querySelector('.app-main, .main-content');
        if (mainContent) {
            if (this.sidebarOpen) {
                mainContent.classList.remove('sidebar-collapsed');
            } else {
                mainContent.classList.add('sidebar-collapsed');
            }
        }
    }

    toggleHeader() {
        const header = document.querySelector('.app-header, [data-app-header]');
        if (!header) return;
        
        header.classList.toggle('hidden');
        this.headerVisible = !header.classList.contains('hidden');
        
        this.dispatchEvent('app:header-toggled', {
            visible: this.headerVisible,
            timestamp: Date.now()
        });
    }

    // Panel Controls
    openPanel(panelName) {
        const panelState = this.panelStates.get(panelName);
        if (!panelState) return;
        
        panelState.element.classList.add('open');
        panelState.open = true;
        
        this.dispatchEvent('app:panel-opened', {
            panel: panelName,
            timestamp: Date.now()
        });
    }

    closePanel(panelName) {
        const panelState = this.panelStates.get(panelName);
        if (!panelState) return;
        
        panelState.element.classList.remove('open');
        panelState.open = false;
        
        this.dispatchEvent('app:panel-closed', {
            panel: panelName,
            timestamp: Date.now()
        });
    }

    togglePanel(panelName) {
        const panelState = this.panelStates.get(panelName);
        if (!panelState) return;
        
        if (panelState.open) {
            this.closePanel(panelName);
        } else {
            this.openPanel(panelName);
        }
    }

    togglePanelPin(panelName) {
        const panelState = this.panelStates.get(panelName);
        if (!panelState) return;
        
        panelState.element.classList.toggle('pinned');
        panelState.pinned = !panelState.pinned;
        
        this.dispatchEvent('app:panel-pinned', {
            panel: panelName,
            pinned: panelState.pinned,
            timestamp: Date.now()
        });
    }

    // Modal Controls
    openModal(modalId, options = {}) {
        const modal = this.modals.get(modalId);
        if (!modal) return;
        
        modal.element.classList.add('show');
        modal.open = true;
        
        // Set focus to first input if exists
        const firstInput = modal.element.querySelector('input, textarea, select');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
        
        this.dispatchEvent('app:modal-opened', {
            modal: modalId,
            options,
            timestamp: Date.now()
        });
    }

    closeModal(modalId) {
        const modal = this.modals.get(modalId);
        if (!modal) return;
        
        modal.element.classList.remove('show');
        modal.open = false;
        
        this.dispatchEvent('app:modal-closed', {
            modal: modalId,
            timestamp: Date.now()
        });
    }

    // Tab Controls
    switchTab(container, tabId) {
        // Deactivate all tabs in container
        const tabs = container.querySelectorAll('.nav-tabs .nav-link, [data-tab]');
        const contents = container.querySelectorAll('.tab-content, [data-tab-content]');
        
        tabs.forEach(tab => {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        });
        
        contents.forEach(content => {
            content.classList.remove('active');
            content.classList.remove('show');
        });
        
        // Activate selected tab
        const activeTab = container.querySelector(`[data-tab="${tabId}"], [href="#${tabId}"]`);
        const activeContent = document.getElementById(tabId);
        
        if (activeTab && activeContent) {
            activeTab.classList.add('active');
            activeTab.setAttribute('aria-selected', 'true');
            activeContent.classList.add('active', 'show');
            
            this.dispatchEvent('app:tab-switched', {
                container: container.id,
                tab: tabId,
                timestamp: Date.now()
            });
        }
    }

    getActiveTab(container) {
        const activeTab = container.querySelector('.nav-tabs .nav-link.active, [data-tab].active');
        if (activeTab) {
            return activeTab.getAttribute('data-tab') || 
                   activeTab.getAttribute('href')?.substring(1);
        }
        return null;
    }

    // Widget Controls
    refreshWidget(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        widget.performance.refreshCount++;
        
        // Show loading state
        const loading = widget.element.querySelector('.widget-loading');
        if (loading) {
            loading.style.display = 'block';
        }
        
        // Simulate refresh
        setTimeout(() => {
            if (loading) {
                loading.style.display = 'none';
            }
            
            // Refresh widget content
            this.refreshWidgetContent(widgetId);
            
            this.dispatchEvent('app:widget-refreshed', {
                widget: widgetId,
                type: widget.type,
                refreshCount: widget.performance.refreshCount,
                timestamp: Date.now()
            });
        }, 1000);
    }

    refreshWidgetContent(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget) return;
        
        switch (widget.type) {
            case 'stats':
                this.refreshStatsWidget(widgetId);
                break;
            case 'chart':
                this.refreshChartWidget(widgetId);
                break;
            case 'table':
                this.refreshTableWidget(widgetId);
                break;
        }
    }

    refreshStatsWidget(widgetId) {
        const widget = this.widgets.get(widgetId);
        const valueElements = widget.element.querySelectorAll('.stat-value');
        
        valueElements.forEach(el => {
            const currentValue = parseInt(el.textContent.replace(/,/g, '')) || 0;
            const newValue = currentValue + Math.floor(Math.random() * 100);
            el.textContent = this.formatNumber(newValue);
        });
    }

    refreshChartWidget(widgetId) {
        const widget = this.widgets.get(widgetId);
        if (!widget.chart) return;
        
        // Update chart data with random values
        widget.chart.data.datasets.forEach(dataset => {
            dataset.data = dataset.data.map(() => Math.random() * 100);
        });
        
        widget.chart.update();
    }

    // User State
    async initUserState() {
        // Load user preferences
        const preferences = this.loadUserPreferences();
        
        // Apply preferences
        if (preferences.sidebarCollapsed !== undefined) {
            this.sidebarOpen = !preferences.sidebarCollapsed;
            if (preferences.sidebarCollapsed) {
                document.querySelector('.app-sidebar')?.classList.add('collapsed');
            }
        }
        
        // Load user data
        await this.loadUserData();
    }

    loadUserPreferences() {
        try {
            const saved = localStorage.getItem('app_preferences');
            return saved ? JSON.parse(saved) : {};
        } catch (error) {
            console.error('Failed to load user preferences:', error);
            return {};
        }
    }

    saveUserPreferences() {
        const preferences = {
            sidebarCollapsed: !this.sidebarOpen,
            // Add other preferences here
        };
        
        try {
            localStorage.setItem('app_preferences', JSON.stringify(preferences));
        } catch (error) {
            console.error('Failed to save user preferences:', error);
        }
    }

    async loadUserData() {
        // Load user data from API
        try {
            if (window.App && typeof window.App.fetchAPI === 'function') {
                const userData = await window.App.fetchAPI('/api/user/current');
                this.userData = userData;
                
                // Update UI with user data
                this.updateUserUI(userData);
            }
        } catch (error) {
            console.error('Failed to load user data:', error);
        }
    }

    updateUserUI(userData) {
        // Update user name in header
        const userNameElements = document.querySelectorAll('.user-name, [data-user-name]');
        userNameElements.forEach(el => {
            if (userData.name) {
                el.textContent = userData.name;
            }
        });
        
        // Update user avatar
        const avatarElements = document.querySelectorAll('.user-avatar, [data-user-avatar]');
        avatarElements.forEach(el => {
            if (userData.avatar) {
                el.src = userData.avatar;
            }
        });
        
        // Update user role
        const roleElements = document.querySelectorAll('.user-role, [data-user-role]');
        roleElements.forEach(el => {
            if (userData.role) {
                el.textContent = userData.role;
            }
        });
    }

    // Update App UI
    updateAppUI() {
        // Update navigation based on current sub-type
        this.updateAppNavigation();
        
        // Update breadcrumbs
        this.updateBreadcrumbs();
        
        // Update page title
        this.updatePageTitle();
    }

    updateAppNavigation() {
        const navLinks = document.querySelectorAll('.app-nav-link, [data-app-nav]');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (!href) return;
            
            const isActive = this.isLinkForCurrentSubType(href);
            
            if (isActive) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            } else {
                link.classList.remove('active');
                link.removeAttribute('aria-current');
            }
        });
    }

    isLinkForCurrentSubType(href) {
        try {
            const url = new URL(href, window.location.origin);
            const path = url.pathname;
            
            const subTypeFromHref = this.detectSubTypeFromURL(path);
            return subTypeFromHref === this.currentSubType;
        } catch (error) {
            return false;
        }
    }

    updateBreadcrumbs() {
        const breadcrumbContainer = document.querySelector('.breadcrumb, [data-breadcrumbs]');
        if (!breadcrumbContainer) return;
        
        // Generate breadcrumbs based on current path
        const path = window.location.pathname;
        const segments = path.split('/').filter(s => s);
        
        let breadcrumbHTML = '<li class="breadcrumb-item"><a href="/">Home</a></li>';
        
        let currentPath = '';
        segments.forEach((segment, index) => {
            currentPath += `/${segment}`;
            const isLast = index === segments.length - 1;
            const segmentName = segment.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            
            if (isLast) {
                breadcrumbHTML += `<li class="breadcrumb-item active" aria-current="page">${segmentName}</li>`;
            } else {
                breadcrumbHTML += `<li class="breadcrumb-item"><a href="${currentPath}">${segmentName}</a></li>`;
            }
        });
        
        breadcrumbContainer.innerHTML = breadcrumbHTML;
    }

    updatePageTitle() {
        const titleMap = {
            [this.subTypes.DASHBOARD]: 'Dashboard',
            [this.subTypes.PROFILE]: 'Profile',
            [this.subTypes.PROFILE_SETTINGS]: 'Settings',
            [this.subTypes.PROFILE_DASHBOARD]: 'Profile Dashboard',
            [this.subTypes.SETTINGS]: 'Settings',
            [this.subTypes.REPORTS]: 'Reports',
            [this.subTypes.ANALYTICS]: 'Analytics'
        };
        
        const baseTitle = document.title.split('|')[0]?.trim() || 'App';
        const subTypeTitle = titleMap[this.currentSubType] || this.currentSubType;
        
        document.title = `${subTypeTitle} | ${baseTitle}`;
    }

    // Utility Methods
    formatNumber(num) {
        return num.toLocaleString();
    }

    filterTable(table, searchText) {
        const rows = table.querySelectorAll('tbody tr');
        const searchLower = searchText.toLowerCase();
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchLower) ? '' : 'none';
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    handleAppSearch(query) {
        this.dispatchEvent('app:search', {
            query,
            timestamp: Date.now()
        });
        
        // Implement search functionality here
        console.log('App search:', query);
    }

    toggleNotifications() {
        const notificationsPanel = document.querySelector('.notifications-panel');
        if (notificationsPanel) {
            notificationsPanel.classList.toggle('show');
        }
    }

    toggleUserMenu() {
        const userMenu = document.querySelector('.user-menu');
        if (userMenu) {
            userMenu.classList.toggle('show');
        }
    }

    // Cleanup
    async destroy() {
        // Save user preferences
        this.saveUserPreferences();
        
        // Destroy widgets
        this.widgets.forEach(widget => {
            if (widget.chart) {
                widget.chart.destroy();
            }
        });
        this.widgets.clear();
        
        // Destroy modals
        this.modals.clear();
        
        // Destroy tabs
        this.tabs.clear();
        
        // Clear panels
        this.panels.clear();
        this.panelStates.clear();
        
        await super.destroy();
    }

    // Public API
    getCurrentSubType() {
        return this.currentSubType;
    }

    getWidgetPerformance(widgetId) {
        const widget = this.widgets.get(widgetId);
        return widget ? widget.performance : null;
    }

    getAllWidgets() {
        return Array.from(this.widgets.values());
    }

    getPanelState(panelName) {
        return this.panelStates.get(panelName);
    }

    getAllPanels() {
        return Array.from(this.panelStates.values());
    }

    showNotification(message, type = 'info') {
        // Create notification
        const notification = document.createElement('div');
        notification.className = `app-notification notification-${type}`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            border-radius: 4px;
            color: white;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        
        // Set color based on type
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#17a2b8'
        };
        
        notification.style.backgroundColor = colors[type] || colors.info;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    refreshAllWidgets() {
        this.widgets.forEach((widget, id) => {
            this.refreshWidget(id);
        });
    }

    collapseAllPanels() {
        this.panelStates.forEach((state, name) => {
            if (state.open && !state.pinned) {
                this.closePanel(name);
            }
        });
    }

    expandAllPanels() {
        this.panelStates.forEach((state, name) => {
            if (!state.open) {
                this.openPanel(name);
            }
        });
    }
}

export default AppLayout;