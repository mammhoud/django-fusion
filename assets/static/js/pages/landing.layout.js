/**
 * @file layouts/landing.layout.js
 * Landing Pages Layout with Page Type Tracking
 */

import { BaseLayout } from './init.layout.js';

export class LandingLayout extends BaseLayout {
    constructor(options = {}) {
        super({
            layoutId: 'landing',
            layoutType: 'landing',
            pageId: options.pageId || 'landing',
            debug: options.debug || false,
            enableAnimations: options.enableAnimations !== false,
            enableScrollEffects: options.enableScrollEffects !== false,
            trackPageTypes: options.trackPageTypes !== false,
            ...options
        });

        // Landing specific state
        this.pageTypes = {
            HOME: 'home-page',
            CONTACT: 'contact-page',
            ABOUT: 'about-page',
            PRICING: 'pricing-page',
            FEATURES: 'features-page',
            BLOG: 'blog-page',
            FAQ: 'faq-page'
        };

        this.currentPageType = 'home-page';
        this.pageTypeHistory = [];
        this.sections = new Map();
        this.animations = [];
        this.scrollEffects = [];

        // Trackers
        this.sectionObserver = null;
        this.scrollTracker = null;

        // Performance
        this.animationPerformance = {
            totalAnimations: 0,
            activeAnimations: 0,
            fps: 60
        };
    }

    async initComponents() {
        this.log('🎯 Initializing landing components...');

        // Initialize sections
        await this.initSections();

        // Initialize page type tracking
        if (this.options.trackPageTypes) {
            await this.initPageTypeTracking();
        }

        // Initialize animations
        if (this.options.enableAnimations) {
            await this.initAnimations();
        }

        // Initialize scroll effects
        if (this.options.enableScrollEffects) {
            await this.initScrollEffects();
        }

        // Initialize hero section if exists
        await this.initHeroSection();

        // Initialize contact form if exists
        await this.initContactForm();

        // Initialize newsletter signup if exists
        await this.initNewsletterSignup();
    }

    async applyContent() {
        this.log('Applying landing layout content...');

        // Determine current page type from URL
        this.detectPageTypeFromURL();

        // Apply page type specific content
        await this.applyPageTypeContent();

        // Setup navigation tracking
        // await this.setupPageTypeNavigation();

        // Update page metadata
        this.updatePageMetadata();
    }

    // Page Type Tracking
    async initPageTypeTracking() {
        this.log('📊 Initializing page type tracking...');

        // Start with current page type
        this.detectPageTypeFromURL();

        // Listen for navigation events
        if (this.navigation) {
            this.onNavigationEvent('navigation:navigated', (data) => {
                this.handlePageTypeNavigation(data);
            });

            this.onNavigationEvent('navigation:url-changed', (data) => {
                this.handlePageTypeURLChange(data);
            });
        }

        // Track internal link clicks
        document.addEventListener('click', (e) => {
            this.trackPageTypeClick(e);
        });
    }

    detectPageTypeFromURL(url = window.location.pathname) {
        const pageTypeMap = {
            '/': this.pageTypes.HOME,
            '/home': this.pageTypes.HOME,
            '/index': this.pageTypes.HOME,
            '/contact': this.pageTypes.CONTACT,
            '/about': this.pageTypes.ABOUT,
            '/about-us': this.pageTypes.ABOUT,
            '/pricing': this.pageTypes.PRICING,
            '/features': this.pageTypes.FEATURES,
            '/blog': this.pageTypes.BLOG,
            '/faq': this.pageTypes.FAQ,
            '/help': this.pageTypes.FAQ
        };

        const previousPageType = this.currentPageType;

        // Check exact matches first
        if (pageTypeMap[url]) {
            this.currentPageType = pageTypeMap[url];
        } else {
            // Check partial matches
            for (const [path, pageType] of Object.entries(pageTypeMap)) {
                if (url.startsWith(path) && path !== '/') {
                    this.currentPageType = pageType;
                    break;
                }
            }
        }

        // If no match found, extract from URL
        if (!this.currentPageType) {
            const segments = url.split('/').filter(s => s);
            if (segments.length > 0) {
                this.currentPageType = `${segments[0]}-page`;
            } else {
                this.currentPageType = this.pageTypes.HOME;
            }
        }

        // Update options
        this.options.pageType = this.currentPageType;

        // Track history
        if (previousPageType !== this.currentPageType) {
            this.trackPageTypeChange(previousPageType, this.currentPageType);
        }

        this.log(`Page type detected: ${this.currentPageType}`);

        return this.currentPageType;
    }

    trackPageTypeChange(from, to) {
        const change = {
            from,
            to,
            timestamp: Date.now(),
            url: window.location.href
        };

        this.pageTypeHistory.unshift(change);

        // Keep history manageable
        if (this.pageTypeHistory.length > 20) {
            this.pageTypeHistory.pop();
        }

        // Dispatch event
        this.dispatchEvent('landing:page-type-changed', change);

    }

    handlePageTypeNavigation(data) {
        const url = data.detail?.url || data.detail?.currentUrl;
        if (url) {
            const pageType = this.detectPageTypeFromURL(new URL(url).pathname);

            // Update layout if page type changed
            if (pageType !== this.currentPageType) {
                this.applyPageTypeContent();
            }
        }
    }

    handlePageTypeURLChange(data) {
        const url = data.detail?.currentUrl;
        if (url) {
            this.detectPageTypeFromURL(new URL(url).pathname);
        }
    }

    trackPageTypeClick(event) {
        const link = event.target.closest('a[href]');
        if (!link) return;

        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;

        try {
            const url = new URL(href, window.location.origin);
            if (url.origin === window.location.origin) {
                const pageType = this.detectPageTypeFromURL(url.pathname);

                // Track in analytics if available
                if (window.ga || window.gtag) {
                    this.trackPageView(pageType, url.pathname);
                }
            }
        } catch (error) {
            // Ignore invalid URLs
        }
    }

    trackPageView(pageType, path) {
        // Track page view in analytics
        const analyticsData = {
            page_type: pageType,
            page_path: path,
            page_title: document.title,
            timestamp: Date.now()
        };

        this.dispatchEvent('landing:page-view', analyticsData);

        // Send to analytics services
        if (window.ga) {
            window.ga('send', 'pageview', {
                page: path,
                title: `${document.title} (${pageType})`
            });
        }

        if (window.gtag) {
            window.gtag('config', 'GA_MEASUREMENT_ID', {
                page_path: path,
                page_title: `${document.title} (${pageType})`
            });
        }
    }

    // Page Type Content
    async applyPageTypeContent() {
        this.log(`Applying content for page type: ${this.currentPageType}`);

        // Remove previous page type classes
        Object.values(this.pageTypes).forEach(pageType => {
            document.body.classList.remove(`page-${pageType}`);
        });

        // Add current page type class
        document.body.classList.add(`page-${this.currentPageType}`);

        // // Apply page type specific transformations
        // switch (this.currentPageType) {
        //     case this.pageTypes.HOME:
        //         await this.applyHomePageContent();
        //         break;
        //     case this.pageTypes.CONTACT:
        //         await this.applyContactPageContent();
        //         break;
        //     case this.pageTypes.ABOUT:
        //         await this.applyAboutPageContent();
        //         break;
        //     case this.pageTypes.PRICING:
        //         await this.applyPricingPageContent();
        //         break;
        //     case this.pageTypes.FEATURES:
        //         await this.applyFeaturesPageContent();
        //         break;
        //     case this.pageTypes.BLOG:
        //         await this.applyBlogPageContent();
        //         break;
        //     case this.pageTypes.FAQ:
        //         await this.applyFAQPageContent();
        //         break;
        // }

        // Update navigation highlighting
        this.updatePageTypeNavigation();

        this.dispatchEvent('landing:page-type-content-applied', {
            pageType: this.currentPageType,
            timestamp: Date.now()
        });
    }

    async applyHomePageContent() {
        // Home page specific content
        this.log('Applying home page content...');

        // Initialize hero slider if exists
        const heroSlider = document.querySelector('.hero-slider');
        if (heroSlider) {
            await this.initHeroSlider(heroSlider);
        }

        // Initialize featured sections
        const featuredSections = document.querySelectorAll('[data-featured-section]');
        featuredSections.forEach(section => {
            this.initFeaturedSection(section);
        });

        // Initialize call-to-action buttons
        const ctaButtons = document.querySelectorAll('.cta-button, [data-cta]');
        ctaButtons.forEach(button => {
            this.initCTAButton(button);
        });
    }

    async applyContactPageContent() {
        // Contact page specific content
        this.log('Applying contact page content...');

        // Initialize contact form
        const contactForm = document.querySelector('#contactForm, .contact-form');
        if (contactForm) {
            await this.initContactForm(contactForm);
        }

        // Initialize map if exists
        const mapElement = document.querySelector('#contactMap, .contact-map');
        if (mapElement) {
            await this.initContactMap(mapElement);
        }

        // Initialize contact info cards
        const infoCards = document.querySelectorAll('.contact-info-card');
        infoCards.forEach(card => {
            this.initContactInfoCard(card);
        });
    }

    async applyAboutPageContent() {
        // About page specific content
        this.log('Applying about page content...');

        // Initialize team members
        const teamMembers = document.querySelectorAll('.team-member');
        teamMembers.forEach(member => {
            this.initTeamMember(member);
        });

        // Initialize timeline if exists
        const timeline = document.querySelector('.timeline, [data-timeline]');
        if (timeline) {
            await this.initTimeline(timeline);
        }

        // Initialize values/culture sections
        const valueSections = document.querySelectorAll('.value-section, .culture-section');
        valueSections.forEach(section => {
            this.initValueSection(section);
        });
    }

    async applyPricingPageContent() {
        // Pricing page specific content
        this.log('Applying pricing page content...');

        // Initialize pricing tables
        const pricingTables = document.querySelectorAll('.pricing-table, .price-card');
        pricingTables.forEach(table => {
            this.initPricingTable(table);
        });

        // Initialize toggle switches
        const toggles = document.querySelectorAll('.pricing-toggle, [data-pricing-toggle]');
        toggles.forEach(toggle => {
            this.initPricingToggle(toggle);
        });

        // Initialize feature comparisons
        const comparisons = document.querySelectorAll('.feature-comparison, [data-comparison]');
        comparisons.forEach(comparison => {
            this.initFeatureComparison(comparison);
        });
    }

    async applyFeaturesPageContent() {
        // Features page specific content
        this.log('Applying features page content...');

        // Initialize feature cards
        const featureCards = document.querySelectorAll('.feature-card, [data-feature]');
        featureCards.forEach(card => {
            this.initFeatureCard(card);
        });

        // Initialize feature tabs
        const featureTabs = document.querySelectorAll('.feature-tabs, [data-feature-tabs]');
        featureTabs.forEach(tabs => {
            this.initFeatureTabs(tabs);
        });

        // Initialize demo videos
        const demoVideos = document.querySelectorAll('.feature-demo, [data-demo]');
        demoVideos.forEach(video => {
            this.initDemoVideo(video);
        });
    }

    async applyBlogPageContent() {
        // Blog page specific content
        this.log('Applying blog page content...');

        // Initialize blog posts
        const blogPosts = document.querySelectorAll('.blog-post, .article-card');
        blogPosts.forEach(post => {
            this.initBlogPost(post);
        });

        // Initialize categories filter
        const categoryFilter = document.querySelector('.category-filter, [data-categories]');
        if (categoryFilter) {
            await this.initCategoryFilter(categoryFilter);
        }

        // Initialize search
        const searchInput = document.querySelector('.blog-search, [data-blog-search]');
        if (searchInput) {
            await this.initBlogSearch(searchInput);
        }
    }

    async applyFAQPageContent() {
        // FAQ page specific content
        this.log('Applying FAQ page content...');

        // Initialize FAQ accordions
        const faqItems = document.querySelectorAll('.faq-item, .accordion-item');
        faqItems.forEach(item => {
            this.initFAQItem(item);
        });

        // Initialize search
        const searchInput = document.querySelector('.faq-search, [data-faq-search]');
        if (searchInput) {
            await this.initFAQSearch(searchInput);
        }

        // Initialize category tabs
        const categoryTabs = document.querySelector('.faq-categories, [data-faq-categories]');
        if (categoryTabs) {
            await this.initFAQCategories(categoryTabs);
        }
    }

    // Section Management
    async initSections() {
        this.log('Initializing landing sections...');

        // Find all sections with data-section attribute
        const sectionElements = document.querySelectorAll('[data-section]');

        sectionElements.forEach(element => {
            const sectionName = element.getAttribute('data-section');
            const sectionId = element.id || `section-${sectionName}`;

            this.sections.set(sectionName, {
                element,
                id: sectionId,
                name: sectionName,
                visible: false,
                initialized: false,
                data: {}
            });
        });

        // Setup intersection observer for sections
        this.setupSectionObserver();

        this.log(`Found ${this.sections.size} sections`);
    }

    setupSectionObserver() {
        const options = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        this.sectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const sectionName = entry.target.getAttribute('data-section');
                const section = this.sections.get(sectionName);

                if (section) {
                    const wasVisible = section.visible;
                    section.visible = entry.isIntersecting;

                    // Trigger events
                    if (section.visible && !wasVisible) {
                        this.handleSectionVisible(section);
                    } else if (!section.visible && wasVisible) {
                        this.handleSectionHidden(section);
                    }
                }
            });
        }, options);

        // Observe all sections
        this.sections.forEach(section => {
            this.sectionObserver.observe(section.element);
        });
    }

    handleSectionVisible(section) {
        this.log(`Section visible: ${section.name}`);

        // Initialize section if not already initialized
        if (!section.initialized) {
            this.initializeSection(section);
        }

        // Trigger animations
        this.triggerSectionAnimations(section);

        // Dispatch event
        this.dispatchEvent('landing:section-visible', {
            section: section.name,
            element: section.element,
            timestamp: Date.now()
        });
    }

    handleSectionHidden(section) {
        this.log(`Section hidden: ${section.name}`);

        this.dispatchEvent('landing:section-hidden', {
            section: section.name,
            element: section.element,
            timestamp: Date.now()
        });
    }

    initializeSection(section) {
        this.log(`Initializing section: ${section.name}`);

        // Add initialized class
        section.element.classList.add('section-initialized');

        // Mark as initialized
        section.initialized = true;

        // Section-specific initialization
        switch (section.name) {
            case 'hero':
                this.initHeroSection(section.element);
                break;
            case 'features':
                this.initFeaturesSection(section.element);
                break;
            case 'testimonials':
                this.initTestimonialsSection(section.element);
                break;
            case 'cta':
                this.initCTASection(section.element);
                break;
            case 'contact':
                this.initContactSection(section.element);
                break;
        }
    }

    triggerSectionAnimations(section) {
        // Trigger stagger animations for elements in section
        const animatableElements = section.element.querySelectorAll(
            '[data-animate], .animate-on-scroll'
        );

        animatableElements.forEach((element, index) => {
            setTimeout(() => {
                element.classList.add('animate-in');
            }, index * 100);
        });
    }

    // Animation System
    async initAnimations() {
        if (!this.options.enableAnimations) return;

        this.log('🎬 Initializing animations...');

        // Check for AOS library
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-out-cubic',
                once: true,
                mirror: false,
                offset: 50
            });
            this.log('AOS animations initialized');
        }

        // Initialize custom animations
        this.initCustomAnimations();

        // Setup animation performance monitor
        this.setupAnimationPerformanceMonitor();
    }

    initCustomAnimations() {
        // Find elements with animation attributes
        const animatedElements = document.querySelectorAll('[data-animation]');

        animatedElements.forEach(element => {
            const animationType = element.getAttribute('data-animation');
            const animationConfig = {
                element,
                type: animationType,
                duration: element.getAttribute('data-animation-duration') || 1000,
                delay: element.getAttribute('data-animation-delay') || 0,
                running: false,
                completed: false
            };

            this.animations.push(animationConfig);

            // Setup intersection observer for each animation
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !animationConfig.completed) {
                        this.playAnimation(animationConfig);
                    }
                });
            }, { threshold: 0.1 });

            observer.observe(element);
        });

        this.animationPerformance.totalAnimations = this.animations.length;
    }

    playAnimation(config) {
        config.running = true;
        this.animationPerformance.activeAnimations++;

        setTimeout(() => {
            config.element.classList.add(`animate-${config.type}`);

            // Mark as completed
            setTimeout(() => {
                config.running = false;
                config.completed = true;
                this.animationPerformance.activeAnimations--;
            }, config.duration);
        }, config.delay);
    }

    setupAnimationPerformanceMonitor() {
        let frameCount = 0;
        let lastTime = performance.now();

        const checkFPS = () => {
            frameCount++;
            const currentTime = performance.now();

            if (currentTime - lastTime >= 1000) {
                this.animationPerformance.fps = Math.round(
                    (frameCount * 1000) / (currentTime - lastTime)
                );

                // Log warning if FPS is low
                if (this.animationPerformance.fps < 30) {
                    console.warn(`Low animation FPS: ${this.animationPerformance.fps}`);
                }

                frameCount = 0;
                lastTime = currentTime;
            }

            requestAnimationFrame(checkFPS);
        };

        checkFPS();
    }

    // Scroll Effects
    async initScrollEffects() {
        if (!this.options.enableScrollEffects) return;

        this.log('📜 Initializing scroll effects...');

        // Initialize parallax effects
        this.initParallaxEffects();

        // Initialize sticky elements
        this.initStickyElements();

        // Initialize progress indicators
        this.initProgressIndicators();

        // Initialize smooth scroll
        this.initSmoothScroll();

        // Setup scroll tracking
        this.setupScrollTracking();
    }

    initParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');

        parallaxElements.forEach(element => {
            const speed = parseFloat(element.getAttribute('data-parallax-speed')) || 0.5;

            const updateParallax = () => {
                const scrollTop = window.pageYOffset;
                const offset = scrollTop * speed;
                element.style.transform = `translateY(${offset}px)`;
            };

            // Throttle updates for performance
            const throttledUpdate = this.throttle(updateParallax, 16);

            window.addEventListener('scroll', throttledUpdate);
            this.cleanupFunctions.push(() => {
                window.removeEventListener('scroll', throttledUpdate);
            });

            // Initial update
            updateParallax();
        });
    }

    initStickyElements() {
        const stickyElements = document.querySelectorAll('[data-sticky]');

        stickyElements.forEach(element => {
            const offset = parseInt(element.getAttribute('data-sticky-offset')) || 0;
            const originalTop = element.offsetTop;

            const updateSticky = () => {
                const scrollTop = window.pageYOffset;

                if (scrollTop >= originalTop - offset) {
                    element.classList.add('sticky-active');
                    element.style.top = `${offset}px`;
                } else {
                    element.classList.remove('sticky-active');
                    element.style.top = '';
                }
            };

            window.addEventListener('scroll', updateSticky);
            this.cleanupFunctions.push(() => {
                window.removeEventListener('scroll', updateSticky);
            });

            // Initial update
            updateSticky();
        });
    }

    initProgressIndicators() {
        const progressElements = document.querySelectorAll('[data-progress]');

        progressElements.forEach(element => {
            const updateProgress = () => {
                const scrollTop = window.pageYOffset;
                const documentHeight = document.documentElement.scrollHeight;
                const windowHeight = window.innerHeight;
                const progress = (scrollTop / (documentHeight - windowHeight)) * 100;

                element.style.width = `${progress}%`;
            };

            window.addEventListener('scroll', updateProgress);
            this.cleanupFunctions.push(() => {
                window.removeEventListener('scroll', updateProgress);
            });

            // Initial update
            updateProgress();
        });
    }

    initSmoothScroll() {
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();

                const targetId = anchor.getAttribute('href');
                if (targetId === '#') return;

                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });

                    // Update URL hash
                    history.pushState(null, null, targetId);
                }
            });
        });
    }

    setupScrollTracking() {
        let lastScrollPosition = 0;
        let scrollDirection = 'down';

        const trackScroll = () => {
            const currentScroll = window.pageYOffset;
            scrollDirection = currentScroll > lastScrollPosition ? 'down' : 'up';
            lastScrollPosition = currentScroll;

            // Dispatch scroll events
            this.dispatchEvent('landing:scroll', {
                position: currentScroll,
                direction: scrollDirection,
                percent: this.getScrollPercentage(),
                timestamp: Date.now()
            });
        };

        // Throttle scroll events for performance
        const throttledTrackScroll = this.throttle(trackScroll, 100);

        window.addEventListener('scroll', throttledTrackScroll);
        this.cleanupFunctions.push(() => {
            window.removeEventListener('scroll', throttledTrackScroll);
        });
    }

    // Component Initialization
    async initHeroSection(element) {
        if (!element) return;

        this.log('Initializing hero section...');

        // Animate hero elements
        const headline = element.querySelector('.hero-headline');
        const subhead = element.querySelector('.hero-subhead');
        const cta = element.querySelector('.hero-cta');

        if (headline) {
            setTimeout(() => {
                headline.classList.add('animate-in');
            }, 100);
        }

        if (subhead) {
            setTimeout(() => {
                subhead.classList.add('animate-in');
            }, 300);
        }

        if (cta) {
            setTimeout(() => {
                cta.classList.add('animate-in');
            }, 500);
        }

        // Initialize hero slider if exists
        const slider = element.querySelector('.hero-slider');
        if (slider && typeof Swiper !== 'undefined') {
            new Swiper(slider, {
                loop: true,
                autoplay: {
                    delay: 5000,
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true
                },
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev'
                }
            });
        }
    }

    async initContactForm(element) {
        if (!element) return;

        this.log('Initializing contact form...');

        element.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(element);
            const submitButton = element.querySelector('[type="submit"]');
            const originalText = submitButton.textContent;

            // Show loading state
            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';

            try {
                const response = await fetch(element.action || '/api/contact', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    // Show success message
                    this.showNotification('Message sent successfully!', 'success');
                    element.reset();
                } else {
                    throw new Error('Failed to send message');
                }
            } catch (error) {
                console.error('Contact form error:', error);
                this.showNotification('Failed to send message. Please try again.', 'error');
            } finally {
                // Reset button
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }

    async initNewsletterSignup() {
        const newsletterForm = document.querySelector('.newsletter-form');
        if (!newsletterForm) return;

        newsletterForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const emailInput = newsletterForm.querySelector('input[type="email"]');
            const email = emailInput.value.trim();

            if (!this.validateEmail(email)) {
                this.showNotification('Please enter a valid email address', 'error');
                return;
            }

            try {
                const response = await fetch('/api/newsletter/subscribe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email })
                });

                if (response.ok) {
                    this.showNotification('Successfully subscribed to newsletter!', 'success');
                    emailInput.value = '';
                } else {
                    throw new Error('Subscription failed');
                }
            } catch (error) {
                console.error('Newsletter subscription error:', error);
                this.showNotification('Failed to subscribe. Please try again.', 'error');
            }
        });
    }

    // Utility Methods
    validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `landing-notification notification-${type}`;
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

        // Set background color based on type
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

    getScrollPercentage() {
        const winHeight = window.innerHeight;
        const docHeight = document.documentElement.scrollHeight;
        const scrollTop = window.pageYOffset;

        return (scrollTop / (docHeight - winHeight)) * 100;
    }

    throttle(func, limit) {
        let inThrottle;
        return function (...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // // Navigation Integration
    // async setupPageTypeNavigation() {
    //     if (!this.navigation) return;
    //     try {
    //         // Update navigation for current page type
    //         this.navigation.updateCurrentPage({
    //             layout: 'landing',
    //             pageType: this.currentPageType,
    //             title: document.title
    //         });
    //     }
    //     catch { }


    // }

    updatePageTypeNavigation() {
        // Update navigation links based on current page type
        const navLinks = document.querySelectorAll('.nav-link, [data-nav]');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (!href) return;

            const isCurrentPage = this.isLinkForCurrentPageType(href);

            if (isCurrentPage) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            } else {
                link.classList.remove('active');
                link.removeAttribute('aria-current');
            }
        });
    }

    isLinkForCurrentPageType(href) {
        try {
            const url = new URL(href, window.location.origin);
            const path = url.pathname;

            // Check if this link leads to current page type
            const pageTypeFromHref = this.detectPageTypeFromURL(path);
            return pageTypeFromHref === this.currentPageType;
        } catch (error) {
            return false;
        }
    }

    updatePageMetadata() {
        // Update meta tags based on page type
        const metaDescription = document.querySelector('meta[name="description"]');
        if (metaDescription) {
            // Update description based on page type
            const descriptions = {
                [this.pageTypes.HOME]: 'Welcome to our website - Discover amazing features',
                [this.pageTypes.CONTACT]: 'Get in touch with us - Contact information and form',
                [this.pageTypes.ABOUT]: 'Learn more about our company and team',
                [this.pageTypes.PRICING]: 'View our pricing plans and packages',
                [this.pageTypes.FEATURES]: 'Explore our amazing features and capabilities',
                [this.pageTypes.BLOG]: 'Read our latest articles and updates',
                [this.pageTypes.FAQ]: 'Frequently asked questions and answers'
            };

            if (descriptions[this.currentPageType]) {
                metaDescription.setAttribute('content', descriptions[this.currentPageType]);
            }
        }

        // Update Open Graph tags
        const ogTitle = document.querySelector('meta[property="og:title"]');
        if (ogTitle) {
            ogTitle.setAttribute('content', `${document.title} | ${this.currentPageType}`);
        }
    }

    // Cleanup
    async destroy() {
        // Cleanup animations
        this.animations = [];

        // Cleanup scroll effects
        this.scrollEffects = [];

        // Disconnect observers
        if (this.sectionObserver) {
            this.sectionObserver.disconnect();
            this.sectionObserver = null;
        }

        // Clear sections
        this.sections.clear();

        // Clear page type history
        this.pageTypeHistory = [];

        await super.destroy();
    }

    // Public API
    getPageTypeHistory(limit = 10) {
        return this.pageTypeHistory.slice(0, limit);
    }

    getCurrentPageType() {
        return this.currentPageType;
    }

    getSectionState(sectionName) {
        return this.sections.get(sectionName);
    }

    getAllSections() {
        return Array.from(this.sections.values());
    }

    scrollToSection(sectionName) {
        const section = this.sections.get(sectionName);
        if (section && section.element) {
            section.element.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
            return true;
        }
        return false;
    }

    refreshAnimations() {
        // Reset and replay animations
        this.animations.forEach(animation => {
            animation.completed = false;
            animation.element.classList.remove(`animate-${animation.type}`);
        });
    }
}

export default LandingLayout;