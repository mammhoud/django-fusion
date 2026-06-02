/**
 * @file layouts/auth.layout.js
 * Authentication Layout with AuthFormsHandler
 */

import { BaseLayout } from './base.layout.js';
import { FormsManager } from '../../modules/forms/index.js';
import { AuthFormsHandler } from '../../modules/forms/authHandler.js';

export class AuthLayout extends BaseLayout {
    constructor(options = {}) {
        super({
            layoutId: 'auth',
            layoutType: 'auth',
            pageId: options.pageId || 'auth',
            debug: options.debug || false,
            ...options
        });

        // Initialize forms manager with AuthFormsHandler as default
        this.formsManager = new FormsManager({
            debug: this.options.debug,
            autoInitialize: true,
            trackURLChanges: true,
            analytics: true,
            formHandlers: {
                'default': AuthFormsHandler, // Use AuthFormsHandler as default
                'auth': AuthFormsHandler
            }
        });

        // Authentication states
        this.authStates = {
            LOGIN: 'login',
            REGISTER: 'register',
            FORGOT_PASSWORD: 'forgot-password',
            RESET_PASSWORD: 'reset-password',
            VERIFY_EMAIL: 'verify-email',
            TWO_FACTOR: 'two-factor'
        };

        this.currentAuthState = null;
        this.authStateHistory = [];
        this.isAuthenticated = false;
        this.authSession = null;

        // Auth features configuration
        this.authFeatures = {
            enableRememberMe: true,
            enablePasswordStrength: true,
            enableTwoFactor: false,
            enableSocialLogin: false,
            enableTermsConsent: true,
            autoRedirectOnSuccess: true,
            redirectDelay: 2000,
            ...options.authFeatures
        };
    }

    async initComponents() {
        this.log('🔐 Initializing authentication layout...');

        // Detect authentication state from URL
        this.detectAuthStateFromURL();

        // Initialize forms manager
        await this.formsManager.initialize();

        // Setup authentication state change tracking
        this.setupAuthStateTracking();

        // Setup authentication session management
        this.setupSessionManagement();

        // Setup social login if enabled
        if (this.authFeatures.enableSocialLogin) {
            this.setupSocialLogin();
        }

        // Setup two-factor authentication if enabled
        if (this.authFeatures.enableTwoFactor) {
            this.setupTwoFactor();
        }

        this.log('✅ Authentication layout initialized');
    }

    async applyContent() {
        this.log('Applying authentication layout content...');

        // Add auth layout classes
        document.body.classList.add('layout-auth');
        document.body.classList.add(`auth-${this.currentAuthState}`);

        // Apply auth state specific styling
        this.applyAuthStateStyles();

        // Update page metadata
        this.updatePageMetadata();

        // Apply auth-specific features to forms
        this.enhanceAuthForms();

        // Setup authentication event handlers
        this.setupAuthEventHandlers();

        this.dispatchEvent('auth:layout-ready', {
            authState: this.currentAuthState,
            timestamp: Date.now()
        });
    }

    /**
     * Detect authentication state from URL
     */
    detectAuthStateFromURL(url = window.location.pathname) {
        const path = url.toLowerCase();
        
        if (path.includes('/login') || path.includes('/signin')) {
            this.currentAuthState = this.authStates.LOGIN;
        } else if (path.includes('/register') || path.includes('/signup')) {
            this.currentAuthState = this.authStates.REGISTER;
        } else if (path.includes('/forgot-password') || path.includes('/reset-request')) {
            this.currentAuthState = this.authStates.FORGOT_PASSWORD;
        } else if (path.includes('/reset-password') || path.includes('/password-reset')) {
            this.currentAuthState = this.authStates.RESET_PASSWORD;
        } else if (path.includes('/verify-email') || path.includes('/email-verification')) {
            this.currentAuthState = this.authStates.VERIFY_EMAIL;
        } else if (path.includes('/two-factor') || path.includes('/2fa')) {
            this.currentAuthState = this.authStates.TWO_FACTOR;
        } else {
            this.currentAuthState = this.authStates.LOGIN; // Default
        }

        // Add to history
        this.authStateHistory.push({
            state: this.currentAuthState,
            url: window.location.href,
            timestamp: Date.now()
        });

        this.log(`Auth state detected: ${this.currentAuthState}`);
        return this.currentAuthState;
    }

    /**
     * Setup authentication state tracking
     */
    setupAuthStateTracking() {
        // Track URL changes for auth state transitions
        window.addEventListener('popstate', () => {
            setTimeout(() => {
                this.handleAuthStateChange();
            }, 0);
        });

        // Track hash changes (for OAuth callbacks, etc.)
        window.addEventListener('hashchange', () => {
            this.handleHashChange();
        });

        // Track form submissions for state transitions
        document.addEventListener('form:success', (event) => {
            if (event.detail.formId?.includes('auth')) {
                this.handleAuthSuccess(event.detail);
            }
        });

        // Track form errors for auth failures
        document.addEventListener('form:error', (event) => {
            if (event.detail.formId?.includes('auth')) {
                this.handleAuthError(event.detail);
            }
        });
    }

    /**
     * Setup session management
     */
    setupSessionManagement() {
        // Check for existing session
        const session = this.getSession();
        
        if (session) {
            this.authSession = session;
            this.isAuthenticated = true;
            this.log('Existing session found');
            
            // Check session expiration
            if (this.isSessionExpired(session)) {
                this.log('Session expired, clearing...');
                this.clearSession();
                this.redirectToLogin();
            }
        }

        // Setup session storage listener
        window.addEventListener('storage', (event) => {
            if (event.key === 'auth_session') {
                this.handleSessionStorageChange(event);
            }
        });
    }

    /**
     * Setup social login integration
     */
    setupSocialLogin() {
        this.log('Setting up social login...');

        // Listen for social login buttons
        document.addEventListener('click', (event) => {
            const socialBtn = event.target.closest('[data-social-login]');
            if (socialBtn) {
                event.preventDefault();
                this.initiateSocialLogin(socialBtn.dataset.socialLogin);
            }
        });

        // Handle OAuth callback
        if (window.location.hash.includes('access_token') || 
            window.location.search.includes('code')) {
            this.handleOAuthCallback();
        }
    }

    /**
     * Setup two-factor authentication
     */
    setupTwoFactor() {
        this.log('Setting up two-factor authentication...');

        // Auto-focus 2FA input
        const twoFactorInput = document.querySelector('[data-two-factor]');
        if (twoFactorInput) {
            twoFactorInput.focus();
            
            // Auto-submit on complete
            twoFactorInput.addEventListener('input', (event) => {
                if (event.target.value.length === 6) {
                    setTimeout(() => {
                        event.target.form?.submit();
                    }, 500);
                }
            });
        }
    }

    /**
     * Apply auth state specific styling
     */
    applyAuthStateStyles() {
        // Remove all auth state classes
        Object.values(this.authStates).forEach(state => {
            document.body.classList.remove(`auth-${state}`);
        });
        
        // Add current state class
        document.body.classList.add(`auth-${this.currentAuthState}`);

        // Apply theme based on auth state
        const themeColors = {
            [this.authStates.LOGIN]: { primary: '#8b5cf6', bg: '#f8fafc' },
            [this.authStates.REGISTER]: { primary: '#10b981', bg: '#ecfdf5' },
            [this.authStates.FORGOT_PASSWORD]: { primary: '#f59e0b', bg: '#fffbeb' },
            [this.authStates.RESET_PASSWORD]: { primary: '#ef4444', bg: '#fef2f2' },
            [this.authStates.VERIFY_EMAIL]: { primary: '#06b6d4', bg: '#f0f9ff' },
            [this.authStates.TWO_FACTOR]: { primary: '#6366f1', bg: '#f5f3ff' }
        };

        const theme = themeColors[this.currentAuthState] || themeColors[this.authStates.LOGIN];
        
        document.documentElement.style.setProperty('--auth-primary', theme.primary);
        document.documentElement.style.setProperty('--auth-bg', theme.bg);
    }

    /**
     * Enhance auth forms with additional features
     */
    enhanceAuthForms() {
        const authForms = document.querySelectorAll('form[data-auth-form]');
        
        authForms.forEach(form => {
            // Add remember me checkbox if not present
            if (this.authFeatures.enableRememberMe && 
                !form.querySelector('input[name="remember"]')) {
                this.addRememberMeCheckbox(form);
            }

            // Add terms consent if not present
            if (this.authFeatures.enableTermsConsent &&
                this.currentAuthState === this.authStates.REGISTER &&
                !form.querySelector('input[name="terms_consent"]')) {
                this.addTermsConsent(form);
            }

            // Add password strength meter
            if (this.authFeatures.enablePasswordStrength &&
                form.querySelector('input[type="password"]')) {
                this.addPasswordStrengthMeter(form);
            }
        });
    }

    /**
     * Setup authentication event handlers
     */
    setupAuthEventHandlers() {
        // Handle state switching links
        document.addEventListener('click', (event) => {
            const switchLink = event.target.closest('[data-auth-switch]');
            if (switchLink) {
                event.preventDefault();
                this.switchAuthState(switchLink.dataset.authSwitch);
            }
        });

        // Handle logout
        document.addEventListener('click', (event) => {
            const logoutBtn = event.target.closest('[data-logout]');
            if (logoutBtn) {
                event.preventDefault();
                this.logout();
            }
        });
    }

    // ==================== AUTH STATE MANAGEMENT ====================

    handleAuthStateChange() {
        const previousState = this.currentAuthState;
        const newState = this.detectAuthStateFromURL();
        
        if (previousState !== newState) {
            this.log(`Auth state changed: ${previousState} -> ${newState}`);
            
            this.dispatchEvent('auth:state-changed', {
                previousState,
                newState,
                timestamp: Date.now()
            });

            // Update UI for new state
            this.applyAuthStateStyles();
            this.updatePageMetadata();
        }
    }

    switchAuthState(newState) {
        const stateMap = {
            'login': '/auth/login',
            'register': '/auth/register',
            'forgot-password': '/auth/forgot-password',
            'reset-password': '/auth/reset-password',
            'verify-email': '/auth/verify-email',
            'two-factor': '/auth/two-factor'
        };

        const path = stateMap[newState];
        if (path) {
            window.history.pushState({}, '', path);
            this.handleAuthStateChange();
        }
    }

    // ==================== SESSION MANAGEMENT ====================

    getSession() {
        try {
            const sessionData = localStorage.getItem('auth_session');
            return sessionData ? JSON.parse(sessionData) : null;
        } catch (error) {
            this.error('Failed to get session:', error);
            return null;
        }
    }

    setSession(sessionData) {
        try {
            const session = {
                ...sessionData,
                createdAt: Date.now(),
                expiresAt: Date.now() + (24 * 60 * 60 * 1000) // 24 hours
            };
            
            localStorage.setItem('auth_session', JSON.stringify(session));
            this.authSession = session;
            this.isAuthenticated = true;
            
            this.dispatchEvent('auth:session-created', { session });
            
            return session;
        } catch (error) {
            this.error('Failed to set session:', error);
            return null;
        }
    }

    clearSession() {
        localStorage.removeItem('auth_session');
        this.authSession = null;
        this.isAuthenticated = false;
        
        this.dispatchEvent('auth:session-cleared');
    }

    isSessionExpired(session) {
        return session.expiresAt < Date.now();
    }

    handleSessionStorageChange(event) {
        if (event.newValue === null) {
            // Session cleared
            this.authSession = null;
            this.isAuthenticated = false;
            this.dispatchEvent('auth:session-expired');
        } else {
            // Session updated
            try {
                this.authSession = JSON.parse(event.newValue);
                this.isAuthenticated = true;
                this.dispatchEvent('auth:session-updated');
            } catch (error) {
                this.error('Failed to parse updated session:', error);
            }
        }
    }

    // ==================== FORM HANDLING ====================

    addRememberMeCheckbox(form) {
        const checkboxContainer = document.createElement('div');
        checkboxContainer.className = 'form-check mb-3';
        checkboxContainer.innerHTML = `
            <input class="form-check-input" type="checkbox" name="remember" id="remember_me">
            <label class="form-check-label" for="remember_me">
                Remember me
            </label>
        `;
        
        // Insert before submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.parentNode.insertBefore(checkboxContainer, submitBtn);
        } else {
            form.appendChild(checkboxContainer);
        }
    }

    addTermsConsent(form) {
        const termsContainer = document.createElement('div');
        termsContainer.className = 'form-check mb-3';
        termsContainer.innerHTML = `
            <input class="form-check-input" type="checkbox" name="terms_consent" id="terms_consent" required>
            <label class="form-check-label" for="terms_consent">
                I agree to the <a href="/terms" target="_blank">Terms of Service</a> and <a href="/privacy" target="_blank">Privacy Policy</a>
            </label>
            <div class="invalid-feedback">
                You must agree to the terms and conditions
            </div>
        `;
        
        // Insert before submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.parentNode.insertBefore(termsContainer, submitBtn);
        } else {
            form.appendChild(termsContainer);
        }
    }

    addPasswordStrengthMeter(form) {
        const passwordInput = form.querySelector('input[type="password"]');
        if (!passwordInput) return;

        const meterContainer = document.createElement('div');
        meterContainer.className = 'password-strength-meter mt-2';
        meterContainer.innerHTML = `
            <div class="strength-bar-container">
                <div class="strength-bar"></div>
            </div>
            <small class="strength-text form-text"></small>
        `;

        passwordInput.parentNode.appendChild(meterContainer);

        passwordInput.addEventListener('input', (event) => {
            const strength = this.calculatePasswordStrength(event.target.value);
            this.updatePasswordStrengthMeter(meterContainer, strength);
        });
    }

    calculatePasswordStrength(password) {
        if (!password) return 0;
        
        let score = 0;
        
        // Length
        if (password.length >= 8) score++;
        if (password.length >= 12) score++;
        
        // Complexity
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/[0-9]/.test(password)) score++;
        if (/[^A-Za-z0-9]/.test(password)) score++;
        
        return Math.min(score, 4);
    }

    updatePasswordStrengthMeter(meter, strength) {
        const bar = meter.querySelector('.strength-bar');
        const text = meter.querySelector('.strength-text');
        
        const labels = ['Very weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const colors = ['#dc3545', '#ffc107', '#0dcaf0', '#198754', '#198754'];
        
        if (bar) {
            bar.style.width = `${(strength / 4) * 100}%`;
            bar.style.backgroundColor = colors[strength] || '#6c757d';
        }
        
        if (text) {
            text.textContent = `Password strength: ${labels[strength]}`;
            text.style.color = colors[strength] || '#6c757d';
        }
    }

    // ==================== EVENT HANDLERS ====================

    handleAuthSuccess(detail) {
        this.log('Auth form succeeded:', detail.formId);
        
        // If it's a login/register form, create session
        if (detail.formId.includes('login') || detail.formId.includes('register')) {
            const sessionData = {
                userId: detail.result?.user?.id || 'anonymous',
                userEmail: detail.result?.user?.email || '',
                userName: detail.result?.user?.name || '',
                accessToken: detail.result?.accessToken,
                refreshToken: detail.result?.refreshToken,
                roles: detail.result?.user?.roles || ['user']
            };
            
            const session = this.setSession(sessionData);
            
            // Auto-redirect if enabled
            if (this.authFeatures.autoRedirectOnSuccess && session) {
                setTimeout(() => {
                    this.redirectAfterAuth();
                }, this.authFeatures.redirectDelay);
            }
        }
    }

    handleAuthError(detail) {
        this.error('Auth form failed:', detail.formId, detail.error);
        
        // Handle specific auth errors
        if (detail.error?.includes('invalid credentials') || 
            detail.error?.includes('wrong password')) {
            this.showAuthError('Invalid email or password. Please try again.');
        } else if (detail.error?.includes('user not found')) {
            this.showAuthError('No account found with this email.');
        } else if (detail.error?.includes('email already exists')) {
            this.showAuthError('An account with this email already exists.');
        } else if (detail.error?.includes('weak password')) {
            this.showAuthError('Password is too weak. Please use a stronger password.');
        }
    }

    handleHashChange() {
        // Handle OAuth callback in hash
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);
        
        if (params.has('access_token') || params.has('id_token')) {
            this.handleOAuthCallback();
        }
    }

    initiateSocialLogin(provider) {
        this.log(`Initiating social login with ${provider}...`);
        
        const oauthUrls = {
            google: '/auth/google',
            facebook: '/auth/facebook',
            github: '/auth/github',
            twitter: '/auth/twitter'
        };
        
        const url = oauthUrls[provider];
        if (url) {
            const redirectUri = window.location.origin + '/auth/callback';
            const state = this.generateState();
            
            const authUrl = `${url}?redirect_uri=${encodeURIComponent(redirectUri)}&state=${state}`;
            window.location.href = authUrl;
        }
    }

    handleOAuthCallback() {
        this.log('Handling OAuth callback...');
        
        // Extract tokens from URL
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);
        
        const accessToken = params.get('access_token');
        const idToken = params.get('id_token');
        const state = params.get('state');
        
        if (accessToken || idToken) {
            // Store tokens and redirect
            const sessionData = {
                accessToken,
                idToken,
                provider: 'oauth',
                timestamp: Date.now()
            };
            
            this.setSession(sessionData);
            this.redirectAfterAuth();
        }
    }

    // ==================== REDIRECTS ====================

    redirectAfterAuth() {
        // Get redirect URL from session storage or default
        const redirectTo = sessionStorage.getItem('auth_redirect') || '/dashboard';
        sessionStorage.removeItem('auth_redirect');
        
        this.log(`Redirecting to: ${redirectTo}`);
        window.location.href = redirectTo;
    }

    redirectToLogin() {
        // Store current URL for post-login redirect
        sessionStorage.setItem('auth_redirect', window.location.pathname + window.location.search);
        window.location.href = '/auth/login';
    }

    // ==================== UTILITIES ====================

    generateState() {
        return Math.random().toString(36).substring(2) + Date.now().toString(36);
    }

    showAuthError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-auth';
        errorDiv.textContent = message;
        
        // Remove existing auth errors
        document.querySelectorAll('.alert-auth').forEach(el => el.remove());
        
        // Insert at top of auth container or form
        const authContainer = document.querySelector('.auth-container') || 
                             document.querySelector('form[data-auth-form]') ||
                             document.body;
        
        authContainer.prepend(errorDiv);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 10000);
    }

    updatePageMetadata() {
        const stateLabels = {
            [this.authStates.LOGIN]: 'Sign In',
            [this.authStates.REGISTER]: 'Create Account',
            [this.authStates.FORGOT_PASSWORD]: 'Reset Password',
            [this.authStates.RESET_PASSWORD]: 'Set New Password',
            [this.authStates.VERIFY_EMAIL]: 'Verify Email',
            [this.authStates.TWO_FACTOR]: 'Two-Factor Authentication'
        };

        const label = stateLabels[this.currentAuthState] || 'Authentication';
        
        // Update title
        document.title = `${label} | ${document.title.split('|').pop() || 'Authentication'}`;
        
        // Update meta description
        let metaDescription = document.querySelector('meta[name="description"]');
        if (!metaDescription) {
            metaDescription = document.createElement('meta');
            metaDescription.name = 'description';
            document.head.appendChild(metaDescription);
        }
        
        const descriptions = {
            [this.authStates.LOGIN]: 'Sign in to your account to access your dashboard and manage your settings.',
            [this.authStates.REGISTER]: 'Create a new account to get started with our platform.',
            [this.authStates.FORGOT_PASSWORD]: 'Reset your password to regain access to your account.',
            [this.authStates.RESET_PASSWORD]: 'Set a new password for your account.',
            [this.authStates.VERIFY_EMAIL]: 'Verify your email address to complete your registration.',
            [this.authStates.TWO_FACTOR]: 'Enter your two-factor authentication code to continue.'
        };
        
        metaDescription.content = descriptions[this.currentAuthState] || 
                                 'Authentication page for accessing your account.';
    }

    logout() {
        this.clearSession();
        this.redirectToLogin();
    }

    // ==================== PUBLIC API ====================

    isLoggedIn() {
        return this.isAuthenticated;
    }

    getCurrentUser() {
        return this.authSession?.user || null;
    }

    getAccessToken() {
        return this.authSession?.accessToken || null;
    }

    requireAuth(redirectUrl = '/auth/login') {
        if (!this.isAuthenticated) {
            sessionStorage.setItem('auth_redirect', window.location.pathname);
            window.location.href = redirectUrl;
            return false;
        }
        return true;
    }

    // ==================== CLEANUP ====================

    async destroy() {
        this.log('Destroying authentication layout...');

        // Clear any auth-specific event listeners
        if (this.urlChangeHandler) {
            window.removeEventListener('popstate', this.urlChangeHandler);
        }
        
        window.removeEventListener('hashchange', this.handleHashChange);
        window.removeEventListener('storage', this.handleSessionStorageChange);

        // Destroy forms manager
        await this.formsManager.destroy();

        // Remove all auth classes
        Object.values(this.authStates).forEach(state => {
            document.body.classList.remove(`auth-${state}`);
        });

        // Remove auth layout class
        document.body.classList.remove('layout-auth');

        // Call parent destroy
        await super.destroy();
    }
}

export default AuthLayout;