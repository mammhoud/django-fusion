import { Utils } from '../../utility/index.js';

export class EventManagerHandler {
    constructor() {
        this.eventListeners = new Map();
        console.log('🎯 Event manager handler created');
    }

    setup() {
        // Window resize
        const resizeHandler = Utils.debounce(() => {
            // Will be updated by AppState
            console.log('Window resized');
        }, 250);

        // Window scroll
        const scrollHandler = Utils.throttle(() => {
            // Will be updated by AppState
            console.log('Window scrolled');
        }, 100);

        this.eventListeners.set('resize', resizeHandler);
        this.eventListeners.set('scroll', scrollHandler);

        window.addEventListener('resize', resizeHandler);
        window.addEventListener('scroll', scrollHandler);

        console.log('✅ Event listeners initialized');
    }

    cleanup() {
        this.eventListeners.forEach((handler, event) => {
            window.removeEventListener(event, handler);
        });
        this.eventListeners.clear();
    }
}