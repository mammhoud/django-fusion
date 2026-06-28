// ================================================================
//   MAIN ENTRY - Import all modules
// ================================================================

// Import styles
import '../styles/main.scss';

// Import core
import { App } from './core/app';

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});

// Export for debugging
if (process.env.NODE_ENV === 'development') {
    window.__APP = App;
}