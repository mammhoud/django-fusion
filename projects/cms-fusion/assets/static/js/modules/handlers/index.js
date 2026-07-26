/**
 * @file modules/handlers/index.js
 * Service Handlers Export
 */

export { EventManagerHandler } from './events.js';
export { CookieManagerHandler } from './cookies.js';
export { HTMXSSENotifications } from './htmxSSENotifications.js';
export { SSESecurityHandler } from './sseSecurity.js';

// Service name to handler mapping for dynamic loading
export const serviceHandlers = {
    events: () => import('./events.js').then(m => m.EventManagerHandler),
    cookies: () => import('./cookies.js').then(m => m.CookieManagerHandler),
    storage: () => import('./cookies.js').then(m => m.CookieManagerHandler), // Alias
    notifications: () => import('./htmxSSENotifications.js').then(m => m.HTMXSSENotifications),
    sse: () => import('./sseSecurity.js').then(m => m.SSESecurityHandler)
};

export default serviceHandlers;
