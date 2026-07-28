/**
 * Unified Lightbox Component
 * Handles images, videos, and galleries with Plyr integration for videos
 * Supports GLightbox and MagnificPopup as optional fallbacks
 */

class Lightbox {
    constructor(options = {}) {
        // Default options with merged functionality
        this.options = {
            // General options
            autoInit: true,
            lazyLoad: true,

            // Selectors
            imageSelector: '.lightbox-image-link, .lightbox-image-box, [data-lightbox]',
            videoSelector: '.video-btn, [data-video-url], [data-video-src]',
            gallerySelector: '.gallery-wrapper, .carousel',
            modalSelector: '#previewModal',
            playerContainerSelector: '#plyrPlayerContainer',
            videoCarouselSelector: '#previewVideoCarousel',

            // Plyr video options
            plyrEnabled: true,
            plyrConfig: {
                autoplay: true,
                controls: ['play-large', 'play', 'progress', 'current-time', 'mute', 'volume', 'settings', 'pip', 'airplay', 'fullscreen'],
                settings: ['quality', 'speed'],
                quality: {
                    default: 720,
                    options: [4320, 2880, 2160, 1440, 1080, 720, 576, 480, 360, 240]
                },
                ratio: '16:9',
                fullscreen: { enabled: true, fallback: true, iosNative: true },
                vimeo: {
                    byline: false,
                    portrait: false,
                    title: false,
                    speed: true,
                    transparent: false
                },
                youtube: {
                    noCookie: true,
                    rel: 0,
                    showinfo: 0,
                    iv_load_policy: 3,
                    modestbranding: 1
                },
                html5: {
                    controls: ['play-large', 'play', 'progress', 'current-time', 'duration', 'mute', 'volume', 'settings', 'pip', 'airplay', 'fullscreen'],
                    settings: ['quality', 'speed', 'loop'],
                    storage: { enabled: true, key: 'plyr' }
                }
            },

            // GLightbox options (optional)
            glightboxEnabled: false,
            glightboxConfig: {
                selector: '.glightbox',
                touchNavigation: true,
                loop: true,
                autoplayVideos: true,
                plyr: {
                    css: 'https://cdn.plyr.io/3.7.8/plyr.css',
                    js: 'https://cdn.plyr.io/3.7.8/plyr.js'
                }
            },

            // Magnific Popup options (optional)
            magnificEnabled: false,

            // Carousel options
            carouselAutoInit: true,

            // Merge user options
            ...options
        };

        this.videoSrc = "";
        this.videoType = "html5";
        this.currentPlayer = null;
        this.carouselPlayers = new Map();
        this.glightboxInstance = null;
        this.magnificInstances = new Map();
        this.isInitialized = false;

        // If autoInit is true, initialize on creation
        if (this.options.autoInit) {
            this.init();
        }
    }

    /**
     * Initialize the lightbox component
     */
    async init() {
        if (this.isInitialized) {
            console.warn('Lightbox is already initialized');
            return;
        }

        console.log('🔄 Initializing Lightbox component...');

        try {
            // Initialize optional fallback libraries
            await this.initGLightbox();
            this.initMagnificPopup();

            // Initialize core functionality
            this.initVideoHandlers();
            this.initImageHandlers();
            this.initGalleryHandlers();
            this.initModalEvents();

            // Initialize carousel if present
            if (this.options.carouselAutoInit && document.querySelector(this.options.videoCarouselSelector)) {
                this.initCarousel();
            }

            // Setup lazy loading
            if (this.options.lazyLoad) {
                this.setupLazyLoading();
            }

            this.isInitialized = true;
            console.log('✅ Lightbox component initialized successfully');

            // Dispatch initialization event
            this.dispatchEvent('lightbox:initialized');
        } catch (error) {
            console.error('Failed to initialize lightbox component:', error);
            this.dispatchEvent('lightbox:error', { error });
        }
    }

    /**
     * Initialize video handlers
     */
    initVideoHandlers() {
        const videoElements = document.querySelectorAll(this.options.videoSelector);

        videoElements.forEach(element => {
            // Remove any existing listeners to prevent duplicates
            element.removeEventListener('click', this.handleVideoClick);

            // Add click listener
            element.addEventListener('click', (e) => this.handleVideoClick(e, element));

            // Mark as processed
            element.dataset.lightboxProcessed = 'true';
        });

        console.log(`✅ ${videoElements.length} video triggers initialized`);
    }

    /**
     * Handle video click event
     */
    handleVideoClick(e, element) {
        e.preventDefault();

        // Get video source and type
        this.videoSrc = element.dataset.videoUrl ||
            element.dataset.src ||
            element.dataset.videoSrc ||
            element.getAttribute('href');

        this.videoType = element.dataset.videoType ||
            this.detectVideoType(this.videoSrc);

        console.log('Selected video:', this.videoSrc, 'Type:', this.videoType);

        // Store video type for later use
        const modal = document.querySelector(this.options.modalSelector);
        if (modal) {
            modal.dataset.videoType = this.videoType;

            // Show modal
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            } else {
                // Fallback: show modal directly
                modal.style.display = 'block';
                modal.classList.add('show');
                document.body.classList.add('modal-open');
            }
        } else {
            // If no modal, create a temporary one
            this.createTempModal();
        }
    }

    /**
     * Detect video type from URL
     */
    detectVideoType(url) {
        if (!url) return 'html5';

        if (url.includes('youtube.com') || url.includes('youtu.be')) {
            return 'youtube';
        } else if (url.includes('vimeo.com')) {
            return 'vimeo';
        } else if (url.includes('.mp4') || url.includes('.webm') || url.includes('.ogg')) {
            return 'html5';
        } else {
            return 'iframe';
        }
    }

    /**
     * Initialize Plyr video player
     */
    initializePlyrPlayer() {
        const videoType = this.videoType;
        const videoContainer = document.querySelector(this.options.playerContainerSelector);

        if (!videoContainer) {
            console.error('Video container not found:', this.options.playerContainerSelector);
            return;
        }

        // Destroy existing player
        this.destroyPlayer();

        // Clear container
        videoContainer.innerHTML = '';

        let playerElement;

        if (videoType === 'youtube' || videoType === 'vimeo') {
            // Create embed URL
            let embedUrl = this.videoSrc;

            if (this.videoSrc.includes('youtube.com/watch?v=')) {
                embedUrl = this.videoSrc.replace('watch?v=', 'embed/');
            } else if (this.videoSrc.includes('youtu.be/')) {
                embedUrl = this.videoSrc.replace('youtu.be/', 'youtube.com/embed/');
            } else if (this.videoSrc.includes('vimeo.com/')) {
                const videoId = this.videoSrc.split('vimeo.com/')[1];
                embedUrl = `https://player.vimeo.com/video/${videoId}`;
            }

            // Add Plyr-compatible parameters
            let finalUrl = embedUrl;
            if (videoType === 'youtube') {
                finalUrl += (embedUrl.includes('?') ? '&' : '?') + 'origin=' + window.location.origin + '&enablejsapi=1&widgetid=1';
            }

            // Create iframe
            playerElement = document.createElement('iframe');
            playerElement.src = finalUrl;
            playerElement.setAttribute('allowfullscreen', '');
            playerElement.setAttribute('allow', 'autoplay; encrypted-media; picture-in-picture');

        } else {
            // Create HTML5 video element
            playerElement = document.createElement('video');
            playerElement.setAttribute('playsinline', '');
            playerElement.setAttribute('controls', '');

            const source = document.createElement('source');
            source.src = this.videoSrc;

            // Detect MIME type
            if (this.videoSrc.includes('.mp4')) {
                source.type = 'video/mp4';
            } else if (this.videoSrc.includes('.webm')) {
                source.type = 'video/webm';
            } else if (this.videoSrc.includes('.ogg')) {
                source.type = 'video/ogg';
            }

            playerElement.appendChild(source);
            playerElement.appendChild(document.createTextNode('Your browser does not support the video tag.'));
        }

        videoContainer.appendChild(playerElement);

        // Initialize Plyr with appropriate config
        const config = { ...this.options.plyrConfig };

        if (videoType === 'youtube' || videoType === 'vimeo') {
            config.selector = 'iframe';
        } else {
            config.selector = 'video';
            Object.assign(config, config.html5);
            delete config.html5;
        }

        this.currentPlayer = new Plyr(playerElement, config);

        // Add event listeners
        this.setupPlayerEvents();
    }

    /**
     * Setup player event listeners
     */
    setupPlayerEvents() {
        if (!this.currentPlayer) return;

        this.currentPlayer.on('ready', () => {
            console.log('Plyr player ready');
            this.dispatchEvent('lightbox:videoReady', { player: this.currentPlayer });

            // Autoplay
            this.currentPlayer.play().catch(error => {
                console.warn('Autoplay failed:', error);
            });
        });

        this.currentPlayer.on('play', () => {
            console.log('Video playing');
            this.dispatchEvent('lightbox:videoPlay', { player: this.currentPlayer });
            this.pauseOtherVideos();
        });

        this.currentPlayer.on('pause', () => {
            this.dispatchEvent('lightbox:videoPause', { player: this.currentPlayer });
        });

        this.currentPlayer.on('ended', () => {
            this.dispatchEvent('lightbox:videoEnded', { player: this.currentPlayer });
        });

        this.currentPlayer.on('error', (event) => {
            console.error('Plyr player error:', event.detail);
            this.dispatchEvent('lightbox:videoError', { error: event.detail, player: this.currentPlayer });
            this.fallbackToOriginalMethod();
        });

        this.currentPlayer.on('qualitychange', (event) => {
            this.dispatchEvent('lightbox:qualityChanged', { quality: event.detail.quality });
        });

        this.currentPlayer.on('fullscreenchange', (event) => {
            this.dispatchEvent('lightbox:fullscreenChanged', { isFullscreen: this.currentPlayer.fullscreen.active });
        });
    }

    /**
     * Initialize image handlers
     */
    initImageHandlers() {
        const imageElements = document.querySelectorAll(this.options.imageSelector);

        imageElements.forEach(element => {
            // Skip if already processed or if it's a video
            if (element.dataset.lightboxProcessed ||
                element.dataset.videoUrl ||
                element.dataset.videoSrc) {
                return;
            }

            element.addEventListener('click', (e) => this.handleImageClick(e, element));
            element.dataset.lightboxProcessed = 'true';
        });

        console.log(`✅ ${imageElements.length} image triggers initialized`);
    }

    /**
     * Handle image click event
     */
    handleImageClick(e, element) {
        e.preventDefault();

        const imageSrc = element.href ||
            element.dataset.imageSrc ||
            element.dataset.src ||
            element.querySelector('img')?.src;

        const imageTitle = element.dataset.imageTitle ||
            element.getAttribute('title') ||
            element.querySelector('img')?.alt || '';

        if (this.options.glightboxEnabled && typeof GLightbox !== 'undefined') {
            // Use GLightbox if available
            this.openWithGLightbox([{ href: imageSrc, title: imageTitle }]);
        } else if (this.options.magnificEnabled && typeof $.fn.magnificPopup !== 'undefined') {
            // Use Magnific Popup if available
            this.openWithMagnificPopup(imageSrc, 'image', imageTitle);
        } else {
            // Fallback to simple modal
            this.openSimpleImageModal(imageSrc, imageTitle);
        }
    }

    /**
     * Initialize gallery handlers
     */
    initGalleryHandlers() {
        const galleryElements = document.querySelectorAll(this.options.gallerySelector);

        galleryElements.forEach(gallery => {
            const items = gallery.querySelectorAll('a, [data-lightbox-item]');

            items.forEach((item, index) => {
                if (!item.dataset.lightboxProcessed) {
                    item.addEventListener('click', (e) => this.handleGalleryItemClick(e, item, gallery, index));
                    item.dataset.lightboxProcessed = 'true';
                }
            });
        });

        console.log(`✅ ${galleryElements.length} galleries initialized`);
    }

    /**
     * Handle gallery item click
     */
    handleGalleryItemClick(e, item, gallery, index) {
        e.preventDefault();

        // Collect all gallery items
        const items = Array.from(gallery.querySelectorAll('a, [data-lightbox-item]')).map(el => ({
            href: el.href || el.dataset.imageSrc || el.dataset.src,
            title: el.dataset.imageTitle || el.getAttribute('title') || '',
            type: el.dataset.videoUrl ? 'video' : 'image'
        }));

        if (this.options.glightboxEnabled && typeof GLightbox !== 'undefined') {
            this.openWithGLightbox(items, index);
        } else if (this.options.magnificEnabled && typeof $.fn.magnificPopup !== 'undefined') {
            this.openWithMagnificPopup(items, 'gallery', null, index);
        } else {
            // Fallback to simple gallery
            this.openSimpleGallery(items, index);
        }
    }

    /**
     * Initialize modal events
     */
    initModalEvents() {
        const modal = document.querySelector(this.options.modalSelector);
        if (!modal) return;

        // Handle modal shown event
        modal.addEventListener('shown.bs.modal', () => {
            if (this.videoSrc) {
                this.initializePlyrPlayer();
            }
        });

        // Handle modal hidden event
        modal.addEventListener('hide.bs.modal', () => {
            this.destroyPlayer();
            this.videoSrc = "";
            this.videoType = "html5";
        });

        // Handle backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });

        // Handle Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && modal.classList.contains('show')) {
                this.closeModal();
            }
        });
    }

    /**
     * Initialize carousel
     */
    initCarousel() {
        const carousel = document.querySelector(this.options.videoCarouselSelector);
        if (!carousel) return;

        // Initialize Plyr for each video in carousel
        carousel.querySelectorAll('.carousel-item video').forEach((videoElement, index) => {
            if (!videoElement.plyr) {
                const player = new Plyr(videoElement, {
                    controls: ['play', 'progress', 'current-time', 'mute', 'volume', 'fullscreen'],
                    ratio: '16:9',
                    fullscreen: { enabled: true }
                });

                this.carouselPlayers.set(videoElement, player);

                player.on('play', () => {
                    this.pauseOtherCarouselVideos(videoElement);
                });
            }
        });

        // Handle carousel slide events
        carousel.addEventListener('slide.bs.carousel', (event) => {
            const activeVideo = event.relatedTarget.querySelector('video');
            if (activeVideo && activeVideo.plyr) {
                activeVideo.plyr.pause();
            }
        });

        carousel.addEventListener('slid.bs.carousel', (event) => {
            const activeVideo = event.relatedTarget.querySelector('video');
            if (activeVideo && activeVideo.plyr) {
                activeVideo.plyr.play();
            }

            // Update counter if exists
            const activeIndex = event.to;
            const totalVideos = carousel.querySelectorAll('.carousel-item').length;

            const currentCounter = document.getElementById('currentVideo');
            const totalCounter = document.getElementById('totalVideos');

            if (currentCounter) currentCounter.textContent = activeIndex + 1;
            if (totalCounter) totalCounter.textContent = totalVideos;
        });

        console.log('✅ Carousel initialized');
    }

    /**
     * Pause other videos
     */
    pauseOtherVideos() {
        // Pause other Plyr players
        this.carouselPlayers.forEach(player => {
            if (player !== this.currentPlayer) {
                player.pause();
            }
        });

        // Pause native video elements
        document.querySelectorAll('video:not([plyr])').forEach(video => {
            if (video !== this.currentPlayer?.media) {
                video.pause();
            }
        });

        // Pause iframes
        document.querySelectorAll('iframe').forEach(iframe => {
            if (iframe !== this.currentPlayer?.media) {
                const src = iframe.src;
                if (src.includes('autoplay=1')) {
                    iframe.src = src.replace('autoplay=1', 'autoplay=0');
                }
            }
        });
    }

    /**
     * Pause other carousel videos
     */
    pauseOtherCarouselVideos(currentVideo) {
        this.carouselPlayers.forEach((player, videoElement) => {
            if (videoElement !== currentVideo) {
                player.pause();
            }
        });
    }

    /**
     * Fallback method if Plyr fails
     */
    fallbackToOriginalMethod() {
        console.log('Falling back to original video player');

        if (!this.videoSrc) return;

        let embedUrl = this.videoSrc;

        if (this.videoSrc.includes('youtube.com/watch?v=')) {
            embedUrl = this.videoSrc.replace('watch?v=', 'embed/');
        } else if (this.videoSrc.includes('youtu.be/')) {
            embedUrl = this.videoSrc.replace('youtu.be/', 'youtube.com/embed/');
        } else if (this.videoSrc.includes('vimeo.com/')) {
            const videoId = this.videoSrc.split('vimeo.com/')[1];
            embedUrl = `https://player.vimeo.com/video/${videoId}`;
        }

        const separator = embedUrl.includes('?') ? '&' : '?';
        const finalUrl = embedUrl + separator + 'autoplay=1&rel=0&controls=1&modestbranding=1';

        const videoFrame = document.querySelector('#videoFrame');
        if (videoFrame) {
            videoFrame.src = finalUrl;
            videoFrame.style.display = 'block';
        }
    }

    /**
     * Initialize GLightbox (optional)
     */
    async initGLightbox() {
        if (!this.options.glightboxEnabled) return;

        if (typeof GLightbox !== 'undefined') {
            this.glightboxInstance = GLightbox(this.options.glightboxConfig);
            console.log('✅ GLightbox initialized');
        } else {
            try {
                const GLightboxModule = await import('glightbox');
                const GLightbox = GLightboxModule.default || GLightboxModule;
                this.glightboxInstance = GLightbox(this.options.glightboxConfig);
                console.log('✅ GLightbox initialized (dynamic import)');
            } catch (error) {
                console.warn('GLightbox not available:', error);
            }
        }
    }

    /**
     * Initialize Magnific Popup (optional)
     */
    initMagnificPopup() {
        if (!this.options.magnificEnabled || typeof $ === 'undefined' || typeof $.fn.magnificPopup === 'undefined') {
            return;
        }

        // Initialize Magnific Popup for non-video elements
        console.log('✅ Magnific Popup initialized');
    }

    /**
     * Setup lazy loading
     */
    setupLazyLoading() {
        const lazyImages = document.querySelectorAll('[data-lightbox-src], [data-src][data-lightbox-lazy]');

        if (typeof IntersectionObserver === 'undefined') {
            // Fallback: Load all images
            lazyImages.forEach(img => this.loadLazyImage(img));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    this.loadLazyImage(img);
                    observer.unobserve(img);
                }
            });
        }, {
            rootMargin: '50px',
            threshold: 0.1
        });

        lazyImages.forEach(img => observer.observe(img));
    }

    /**
     * Load lazy image
     */
    loadLazyImage(img) {
        const src = img.dataset.lightboxSrc || img.dataset.src;
        if (!src) return;

        const tempImg = new Image();
        tempImg.onload = () => {
            if (img.tagName === 'IMG') {
                img.src = src;
            } else {
                img.style.backgroundImage = `url('${src}')`;
            }
            img.classList.add('loaded');
        };
        tempImg.src = src;
    }

    /**
     * Open with GLightbox
     */
    openWithGLightbox(items, startAt = 0) {
        if (!this.glightboxInstance) return false;

        this.glightboxInstance.setElements(items);
        this.glightboxInstance.openAt(startAt);
        return true;
    }

    /**
     * Open with Magnific Popup
     */
    openWithMagnificPopup(items, type, title, index = 0) {
        if (typeof $.magnificPopup === 'undefined') return false;

        if (type === 'gallery') {
            $.magnificPopup.open({
                items: items,
                type: 'image',
                gallery: { enabled: true },
                index: index
            });
        } else {
            $.magnificPopup.open({
                items: [{
                    src: items,
                    title: title
                }],
                type: type
            });
        }
        return true;
    }

    /**
     * Open simple image modal
     */
    openSimpleImageModal(src, title) {
        // Create and show a simple modal
        const modal = document.createElement('div');
        modal.className = 'simple-lightbox-modal';
        modal.innerHTML = `
            <div class="modal-backdrop"></div>
            <div class="modal-content">
                <button class="modal-close">&times;</button>
                <img src="${src}" alt="${title}">
                ${title ? `<div class="modal-title">${title}</div>` : ''}
            </div>
        `;

        document.body.appendChild(modal);

        // Add close handlers
        modal.querySelector('.modal-backdrop').addEventListener('click', () => this.closeSimpleModal(modal));
        modal.querySelector('.modal-close').addEventListener('click', () => this.closeSimpleModal(modal));
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeSimpleModal(modal);
        });
    }

    /**
     * Open simple gallery
     */
    openSimpleGallery(items, startIndex = 0) {
        const gallery = document.createElement('div');
        gallery.className = 'simple-lightbox-gallery';

        let currentIndex = startIndex;

        const showItem = (index) => {
            gallery.innerHTML = `
                <div class="gallery-backdrop"></div>
                <div class="gallery-content">
                    <button class="gallery-close">&times;</button>
                    <button class="gallery-prev">&larr;</button>
                    <button class="gallery-next">&rarr;</button>
                    <img src="${items[index].href}" alt="${items[index].title}">
                    ${items[index].title ? `<div class="gallery-title">${items[index].title}</div>` : ''}
                    <div class="gallery-counter">${index + 1} / ${items.length}</div>
                </div>
            `;
        };

        showItem(currentIndex);
        document.body.appendChild(gallery);

        // Add event listeners
        const updateListeners = () => {
            gallery.querySelector('.gallery-backdrop').addEventListener('click', () => this.closeSimpleModal(gallery));
            gallery.querySelector('.gallery-close').addEventListener('click', () => this.closeSimpleModal(gallery));
            gallery.querySelector('.gallery-prev').addEventListener('click', () => {
                currentIndex = (currentIndex - 1 + items.length) % items.length;
                showItem(currentIndex);
                updateListeners();
            });
            gallery.querySelector('.gallery-next').addEventListener('click', () => {
                currentIndex = (currentIndex + 1) % items.length;
                showItem(currentIndex);
                updateListeners();
            });
        };

        updateListeners();
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeSimpleModal(gallery);
            if (e.key === 'ArrowLeft') {
                currentIndex = (currentIndex - 1 + items.length) % items.length;
                showItem(currentIndex);
                updateListeners();
            }
            if (e.key === 'ArrowRight') {
                currentIndex = (currentIndex + 1) % items.length;
                showItem(currentIndex);
                updateListeners();
            }
        });
    }

    /**
     * Create temporary modal
     */
    createTempModal() {
        const modal = document.createElement('div');
        modal.id = 'tempPreviewModal';
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Video Preview</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div id="tempPlyrPlayerContainer"></div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Store original selectors
        const originalModalSelector = this.options.modalSelector;
        const originalPlayerSelector = this.options.playerContainerSelector;

        // Update selectors
        this.options.modalSelector = '#tempPreviewModal';
        this.options.playerContainerSelector = '#tempPlyrPlayerContainer';

        // Show modal
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();

            // Restore selectors after modal is hidden
            modal.addEventListener('hidden.bs.modal', () => {
                this.options.modalSelector = originalModalSelector;
                this.options.playerContainerSelector = originalPlayerSelector;
                modal.remove();
            });
        }
    }

    /**
     * Close modal
     */
    closeModal() {
        const modal = document.querySelector(this.options.modalSelector);
        if (!modal) return;

        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        } else {
            modal.style.display = 'none';
            modal.classList.remove('show');
            document.body.classList.remove('modal-open');
        }
    }

    /**
     * Close simple modal
     */
    closeSimpleModal(modal) {
        if (modal && modal.parentNode) {
            modal.parentNode.removeChild(modal);
        }
    }

    /**
     * Destroy player
     */
    destroyPlayer() {
        if (this.currentPlayer) {
            this.currentPlayer.destroy();
            this.currentPlayer = null;
        }

        const videoContainer = document.querySelector(this.options.playerContainerSelector);
        if (videoContainer) {
            videoContainer.innerHTML = '';
        }
    }

    /**
     * Open video programmatically
     */
    openVideo(src, type = null) {
        this.videoSrc = src;
        this.videoType = type || this.detectVideoType(src);

        const modal = document.querySelector(this.options.modalSelector);
        if (modal) {
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            } else {
                modal.style.display = 'block';
                modal.classList.add('show');
                document.body.classList.add('modal-open');
                this.initializePlyrPlayer();
            }
            return true;
        }
        return false;
    }

    /**
     * Open image programmatically
     */
    openImage(src, title = '') {
        return this.openWithGLightbox([{ href: src, title }]) ||
            this.openWithMagnificPopup(src, 'image', title) ||
            (() => { this.openSimpleImageModal(src, title); return true; })();
    }

    /**
     * Open gallery programmatically
     */
    openGallery(items, startAt = 0) {
        return this.openWithGLightbox(items, startAt) ||
            this.openWithMagnificPopup(items, 'gallery', null, startAt) ||
            (() => { this.openSimpleGallery(items, startAt); return true; })();
    }

    /**
     * Close active lightbox
     */
    close() {
        if (this.glightboxInstance && this.glightboxInstance.close) {
            this.glightboxInstance.close();
            return true;
        }

        if (typeof $.magnificPopup !== 'undefined' && $.magnificPopup.instance) {
            $.magnificPopup.close();
            return true;
        }

        this.closeModal();

        // Close any simple modals
        document.querySelectorAll('.simple-lightbox-modal, .simple-lightbox-gallery').forEach(modal => {
            this.closeSimpleModal(modal);
        });

        return true;
    }

    /**
     * Check if lightbox is open
     */
    isOpen() {
        if (this.glightboxInstance && this.glightboxInstance.activeSlide !== -1) {
            return true;
        }

        if (typeof $.magnificPopup !== 'undefined' && $.magnificPopup.instance) {
            return $.magnificPopup.instance.isOpen;
        }

        const modal = document.querySelector(this.options.modalSelector);
        return modal && modal.classList.contains('show');
    }

    /**
     * Dispatch custom event
     */
    dispatchEvent(eventName, detail = {}) {
        const event = new CustomEvent(eventName, {
            detail: { ...detail, lightbox: this },
            bubbles: true,
            cancelable: true
        });
        document.dispatchEvent(event);
    }

    /**
     * Get statistics
     */
    getStats() {
        return {
            isInitialized: this.isInitialized,
            plyrEnabled: this.options.plyrEnabled,
            glightboxEnabled: !!this.glightboxInstance,
            magnificEnabled: this.options.magnificEnabled,
            carouselPlayers: this.carouselPlayers.size,
            currentPlayer: !!this.currentPlayer,
            isOpen: this.isOpen()
        };
    }

    /**
     * Update configuration
     */
    updateConfig(newConfig) {
        this.options = { ...this.options, ...newConfig };

        // Reinitialize if needed
        if (this.isInitialized) {
            this.destroy();
            this.init();
        }
    }

    /**
     * Destroy all instances
     */
    destroy() {
        // Destroy Plyr players
        this.destroyPlayer();

        // Destroy carousel players
        this.carouselPlayers.forEach(player => {
            if (player && player.destroy) {
                player.destroy();
            }
        });
        this.carouselPlayers.clear();

        // Destroy GLightbox
        if (this.glightboxInstance && this.glightboxInstance.destroy) {
            this.glightboxInstance.destroy();
            this.glightboxInstance = null;
        }

        // Close Magnific Popup
        if (typeof $.magnificPopup !== 'undefined' && $.magnificPopup.instance && $.magnificPopup.instance.isOpen) {
            $.magnificPopup.close();
        }

        // Remove event listeners
        document.querySelectorAll('[data-lightbox-processed="true"]').forEach(element => {
            delete element.dataset.lightboxProcessed;
        });

        this.isInitialized = false;
        console.log('🛑 Lightbox destroyed');
    }
}

// Auto-initialize if data-lightbox attribute is present
document.addEventListener('DOMContentLoaded', () => {
    const lightboxElements = document.querySelectorAll('[data-lightbox-auto]');

    lightboxElements.forEach(element => {
        try {
            const options = JSON.parse(element.dataset.lightboxAuto || '{}');
            const lightbox = new Lightbox(options);

            // Store instance on element
            element.lightboxInstance = lightbox;
        } catch (error) {
            console.error('Failed to auto-initialize lightbox:', error);
        }
    });
});

export default Lightbox;