/**
 * Animations Initialization
 */
/**
 * Animations Component
 */

import { DOM } from '../utility/dom.js';

export const Animations = {
    counters: [],
    accordions: [],
    progressBars: [],
    initialized: false,
    
    /**
     * Initialize animations
     */
    init() {
        if (this.initialized) return Promise.resolve();
        
        console.log('🔄 Initializing animations...');
        
        this.initBackgroundImages();
        this.initCounters();
        this.initAccordions();
        this.initProgressBars();
        this.initScrollAnimations();
        
        this.initialized = true;
        return Promise.resolve();
    },
    
    /**
     * Initialize background images
     */
    initBackgroundImages() {
        const bgImages = DOM.$$('.bg-image[data-bg-src]');
        
        if (bgImages.length === 0) {
            console.log('ℹ️ No background images found');
            return;
        }
        
        bgImages.forEach(bgImage => {
            const bgSrc = bgImage.dataset.bgSrc;
            if (bgSrc) {
                // Lazy load background images
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            bgImage.style.backgroundImage = `url("${bgSrc}")`;
                            observer.unobserve(bgImage);
                        }
                    });
                });
                
                observer.observe(bgImage);
            }
        });
        
        console.log(`✅ ${bgImages.length} background images initialized`);
    },
    
    /**
     * Initialize counters
     */
    initCounters() {
        this.counters = DOM.$$('.counter');
        
        if (this.counters.length === 0) {
            console.log('ℹ️ No counters found');
            return;
        }
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        this.counters.forEach(counter => observer.observe(counter));
        
        console.log(`✅ ${this.counters.length} counters initialized`);
    },
    
    /**
     * Animate counter
     */
    animateCounter(counter) {
        const target = parseInt(counter.textContent) || parseInt(counter.dataset.count);
        const duration = 2000; // 2 seconds
        const frameDuration = 1000 / 60; // 60fps
        const totalFrames = Math.round(duration / frameDuration);
        let frame = 0;
        
        const easeOutQuad = (t) => t * (2 - t);
        
        const updateCounter = () => {
            frame++;
            const progress = frame / totalFrames;
            const easedProgress = easeOutQuad(progress);
            
            const current = Math.round(target * easedProgress);
            counter.textContent = current.toLocaleString();
            
            if (frame < totalFrames) {
                requestAnimationFrame(updateCounter);
            } else {
                counter.textContent = target.toLocaleString();
            }
        };
        
        updateCounter();
    },
    
    /**
     * Initialize accordions
     */
    initAccordions() {
        this.accordions = DOM.$$('.accordion');
        
        if (this.accordions.length === 0) {
            console.log('ℹ️ No accordions found');
            return;
        }
        
        this.accordions.forEach(accordion => {
            const items = accordion.querySelectorAll('.accordion-item');
            const isSingleOpen = DOM.hasClass(accordion, 'single-open');
            
            items.forEach(item => {
                const title = item.querySelector('.accordion-title');
                const content = item.querySelector('.accordion-content');
                
                if (!title || !content) return;
                
                // Add aria attributes
                title.setAttribute('aria-expanded', 'false');
                content.setAttribute('aria-hidden', 'true');
                
                DOM.on(title, 'click', () => {
                    this.toggleAccordion(item, isSingleOpen, accordion);
                });
                
                // Set initial state
                if (DOM.hasClass(item, 'active')) {
                    this.openAccordion(item);
                }
            });
        });
        
        console.log(`✅ ${this.accordions.length} accordions initialized`);
    },
    
    /**
     * Toggle accordion item
     */
    toggleAccordion(item, isSingleOpen, accordion) {
        const isActive = DOM.hasClass(item, 'active');
        
        if (isSingleOpen) {
            // Close all other items
            const otherItems = accordion.querySelectorAll('.accordion-item.active');
            otherItems.forEach(otherItem => {
                if (otherItem !== item) {
                    this.closeAccordion(otherItem);
                }
            });
        }
        
        if (isActive) {
            this.closeAccordion(item);
        } else {
            this.openAccordion(item);
        }
    },
    
    /**
     * Open accordion item
     */
    openAccordion(item) {
        const content = item.querySelector('.accordion-content');
        const title = item.querySelector('.accordion-title');
        
        DOM.addClass(item, 'active');
        title.setAttribute('aria-expanded', 'true');
        content.setAttribute('aria-hidden', 'false');
        content.style.maxHeight = content.scrollHeight + 'px';
    },
    
    /**
     * Close accordion item
     */
    closeAccordion(item) {
        const content = item.querySelector('.accordion-content');
        const title = item.querySelector('.accordion-title');
        
        DOM.removeClass(item, 'active');
        title.setAttribute('aria-expanded', 'false');
        content.setAttribute('aria-hidden', 'true');
        content.style.maxHeight = null;
    },
    
    /**
     * Initialize progress bars
     */
    initProgressBars() {
        this.progressBars = DOM.$$('.animated-progress div');
        
        if (this.progressBars.length === 0) {
            console.log('ℹ️ No progress bars found');
            return;
        }
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const bar = entry.target;
                    const progress = bar.dataset.progress || '100';
                    
                    bar.style.width = `${progress}%`;
                    observer.unobserve(bar);
                }
            });
        }, { threshold: 0.5 });
        
        this.progressBars.forEach(bar => observer.observe(bar));
        
        console.log(`✅ ${this.progressBars.length} progress bars initialized`);
    },
    
    /**
     * Initialize scroll animations
     */
    initScrollAnimations() {
        const animatedElements = DOM.$$('[data-animate]');
        
        if (animatedElements.length === 0) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const element = entry.target;
                    const animation = element.dataset.animate || 'fadeIn';
                    const delay = element.dataset.animateDelay || '0';
                    
                    DOM.addClass(element, `animate-${animation}`);
                    element.style.animationDelay = `${delay}ms`;
                    
                    observer.unobserve(element);
                }
            });
        }, { threshold: 0.1 });
        
        animatedElements.forEach(element => observer.observe(element));
        
        console.log(`✅ ${animatedElements.length} scroll animations initialized`);
    },
    
    /**
     * Initialize in specific element
     */
    initInElement(element) {
        // Counters
        const counters = element.querySelectorAll('.counter');
        counters.forEach(counter => {
            if (!this.counters.includes(counter)) {
                this.counters.push(counter);
                this.animateCounter(counter);
            }
        });
        
        // Accordions
        const accordions = element.querySelectorAll('.accordion');
        accordions.forEach(accordion => {
            if (!this.accordions.includes(accordion)) {
                this.initAccordion(accordion);
                this.accordions.push(accordion);
            }
        });
        
        // Progress bars
        const progressBars = element.querySelectorAll('.animated-progress div');
        progressBars.forEach(bar => {
            if (!this.progressBars.includes(bar)) {
                this.progressBars.push(bar);
                const progress = bar.dataset.progress || '100';
                bar.style.width = `${progress}%`;
            }
        });
    },
    
    /**
     * Initialize single accordion
     */
    initAccordion(accordion) {
        const items = accordion.querySelectorAll('.accordion-item');
        const isSingleOpen = DOM.hasClass(accordion, 'single-open');
        
        items.forEach(item => {
            const title = item.querySelector('.accordion-title');
            const content = item.querySelector('.accordion-content');
            
            if (title && content) {
                DOM.on(title, 'click', () => {
                    this.toggleAccordion(item, isSingleOpen, accordion);
                });
            }
        });
    }
};

export default Animations;
