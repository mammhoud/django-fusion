/**
 * Core Utilities - Essential utility functions
 * Comprehensive collection of debounce, throttle, type checking, string manipulation, etc.
 */

// ============================================
// LOGGER
// ============================================

export const createLogger = (name, enabled = true) => ({
    log: (...args) => enabled && console.log(`[${name}]`, ...args),
    info: (...args) => enabled && console.info(`[${name}]`, ...args),
    warn: (...args) => enabled && console.warn(`[${name}]`, ...args),
    error: (...args) => enabled && console.error(`[${name}]`, ...args),
    debug: (...args) => enabled && console.debug(`[${name}]`, ...args)
});

// ============================================
// TIMING & EXECUTION
// ============================================

export const debounce = (func, wait, immediate = false) => {
    let timeout;
    return function executedFunction(...args) {
        const context = this;
        const later = () => {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
};

export const throttle = (func, limit) => {
    let inThrottle;
    return function(...args) {
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

export const batchUpdates = (callback) => {
    if (typeof requestAnimationFrame !== 'undefined') {
        requestAnimationFrame(callback);
    } else {
        setTimeout(callback, 0);
    }
};

export const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// ============================================
// TYPE CHECKING
// ============================================

export const isString = (value) => typeof value === 'string';
export const isNumber = (value) => typeof value === 'number';
export const isBoolean = (value) => typeof value === 'boolean';
export const isFunction = (value) => typeof value === 'function';
export const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
export const isArray = (value) => Array.isArray(value);
export const isElement = (value) => value instanceof Element;
export const isDate = (value) => value instanceof Date;
export const isPromise = (value) => value && typeof value.then === 'function';

// ============================================
// STRING UTILITIES
// ============================================

export const capitalize = (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

export const capitalizeAll = (str) => {
    if (!str) return '';
    return str.replace(/\b\w/g, char => char.toUpperCase());
};

export const camelCase = (str) => {
    return str.replace(/[-_](.)/g, (_, c) => c.toUpperCase());
};

export const kebabCase = (str) => {
    return str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
};

export const truncate = (str, maxLength = 100, suffix = '...') => {
    if (!str || str.length <= maxLength) return str;
    return str.substring(0, maxLength) + suffix;
};

export const escapeHtml = (text) => {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
};

export const unescapeHtml = (text) => {
    if (!text) return '';
    const map = {
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&#039;': "'",
        '&#39;': "'"
    };
    return text.replace(/&amp;|&lt;|&gt;|&quot;|&#039;|&#39;/g, m => map[m]);
};

export const stripHtml = (html) => {
    if (!html) return '';
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
};

// ============================================
// OBJECT UTILITIES
// ============================================

export const deepClone = (obj) => {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.reduce((arr, item, i) => {
        arr[i] = deepClone(item);
        return arr;
    }, []);
    if (typeof obj === 'object') return Object.keys(obj).reduce((newObj, key) => {
        newObj[key] = deepClone(obj[key]);
        return newObj;
    }, {});
    return obj;
};

export const merge = (target, ...sources) => {
    sources.forEach(source => {
        Object.keys(source).forEach(key => {
            if (source[key] && isObject(source[key])) {
                if (!target[key] || !isObject(target[key])) {
                    target[key] = {};
                }
                merge(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        });
    });
    return target;
};

export const pick = (obj, keys) => {
    const result = {};
    keys.forEach(key => {
        if (obj.hasOwnProperty(key)) result[key] = obj[key];
    });
    return result;
};

export const omit = (obj, keys) => {
    const result = { ...obj };
    keys.forEach(key => delete result[key]);
    return result;
};

// ============================================
// ARRAY UTILITIES
// ============================================

export const unique = (array) => [...new Set(array)];

export const chunk = (array, size) => {
    const chunks = [];
    for (let i = 0; i < array.length; i += size) {
        chunks.push(array.slice(i, i + size));
    }
    return chunks;
};

export const flatten = (array) => {
    return array.reduce((flat, next) => {
        return flat.concat(isArray(next) ? flatten(next) : next);
    }, []);
};

export const groupBy = (array, key) => {
    return array.reduce((groups, item) => {
        const val = item[key];
        groups[val] = groups[val] || [];
        groups[val].push(item);
        return groups;
    }, {});
};

export const sortBy = (array, key, order = 'asc') => {
    return [...array].sort((a, b) => {
        const aVal = a[key];
        const bVal = b[key];
        if (aVal < bVal) return order === 'asc' ? -1 : 1;
        if (aVal > bVal) return order === 'asc' ? 1 : -1;
        return 0;
    });
};

export const shuffle = (array) => {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
};

export const randomItem = (array) => {
    return array[Math.floor(Math.random() * array.length)];
};

// ============================================
// RANDOM UTILITIES
// ============================================

export const random = (min, max) => {
    return Math.floor(Math.random() * (max - min + 1)) + min;
};

export const randomFloat = (min, max) => {
    return Math.random() * (max - min) + min;
};

export const uuid = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
};

export const generateId = (prefix = 'id') => {
    return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

// ============================================
// VALIDATION UTILITIES
// ============================================

export const isValidEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

export const isValidUrl = (string) => {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
};

export const isValidPhone = (phone) => {
    const re = /^[\+]?[1-9][\d\s\-\(\)\.]{7,}$/;
    return re.test(phone.replace(/\s/g, ''));
};

// ============================================
// FORMATTING UTILITIES
// ============================================

export const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

export const formatTime = (ms) => {
    if (ms < 1000) return `${ms}ms`;
    const seconds = (ms / 1000).toFixed(2);
    return `${seconds}s`;
};

export const formatDate = (date, format = 'short', locale = 'en-US') => {
    const d = date instanceof Date ? date : new Date(date);
    if (isNaN(d.getTime())) return 'Invalid Date';

    if (typeof format === 'string') {
        const formats = {
            short: d.toLocaleDateString(locale),
            long: d.toLocaleDateString(locale, {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            }),
            time: d.toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' }),
            datetime: d.toLocaleString(locale),
            'YYYY-MM-DD': d.toISOString().split('T')[0],
            'DD/MM/YYYY': d.toLocaleDateString(locale, { day: '2-digit', month: '2-digit', year: 'numeric' })
        };
        return formats[format] || formats.short;
    }

    const formatter = new Intl.DateTimeFormat(locale, format);
    return formatter.format(d);
};

// ============================================
// JSON UTILITIES
// ============================================

export const safeParseJSON = (str, fallback = {}) => {
    try {
        return JSON.parse(str);
    } catch (e) {
        console.warn('Failed to parse JSON:', e);
        return fallback;
    }
};

export const safeStringifyJSON = (obj, fallback = '{}') => {
    try {
        return JSON.stringify(obj);
    } catch (e) {
        console.warn('Failed to stringify JSON:', e);
        return fallback;
    }
};

// ============================================
// URL & QUERY UTILITIES
// ============================================

export const getQueryParam = (name, url = window.location.href) => {
    name = name.replace(/[\[\]]/g, '\\$&');
    const regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)');
    const results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
};

export const getUrlParams = (url = window.location.href) => {
    const params = {};
    const urlParts = url.split('?');

    if (urlParts.length > 1) {
        const queryString = urlParts[1];
        const pairs = queryString.split('&');

        pairs.forEach(pair => {
            const [key, value] = pair.split('=');
            if (key) {
                params[decodeURIComponent(key)] = decodeURIComponent(value || '');
            }
        });
    }

    return params;
};

export const createUrl = (base, params = {}) => {
    const url = new URL(base, window.location.origin);
    Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
            url.searchParams.append(key, String(value));
        }
    });
    return url.toString();
};

// ============================================
// BROWSER UTILITIES
// ============================================

export const isMobile = () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
        window.innerWidth < 768;
};

export const isTouchDevice = () => {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
};

export const isOnline = () => navigator.onLine;

export const getScrollbarWidth = () => {
    const scrollDiv = document.createElement('div');
    scrollDiv.style.cssText = 'width:100px;height:100px;overflow:scroll;position:absolute;top:-9999px;';
    document.body.appendChild(scrollDiv);
    const width = scrollDiv.offsetWidth - scrollDiv.clientWidth;
    document.body.removeChild(scrollDiv);
    return width;
};

export const getScrollParent = (element) => {
    while (element) {
        const { overflow, overflowX, overflowY } = getComputedStyle(element);
        if (/(auto|scroll)/.test(overflow + overflowY + overflowX)) {
            return element;
        }
        element = element.parentElement;
    }
    return document.documentElement;
};

// ============================================
// CLIPBOARD UTILITIES
// ============================================

export const copyToClipboard = (text) => {
    return new Promise((resolve, reject) => {
        if (!text) {
            reject(new Error('No text provided'));
            return;
        }

        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(resolve).catch(reject);
        } else {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            try {
                document.execCommand('copy');
                document.body.removeChild(textArea);
                resolve();
            } catch (err) {
                document.body.removeChild(textArea);
                reject(err);
            }
        }
    });
};

// ============================================
// MATH UTILITIES
// ============================================

export const clamp = (value, min, max) => {
    return Math.min(Math.max(value, min), max);
};

export const lerp = (start, end, amount) => {
    return (1 - amount) * start + amount * end;
};

export const round = (value, decimals = 2) => {
    const factor = Math.pow(10, decimals);
    return Math.round(value * factor) / factor;
};

// ============================================
// EVENT UTILITIES
// ============================================

export const trigger = (element, eventName, detail = {}) => {
    const event = new CustomEvent(eventName, { 
        detail, 
        bubbles: true, 
        cancelable: true 
    });
    element.dispatchEvent(event);
};

// ============================================
// STORAGE UTILITIES
// ============================================

export const storage = {
    get: (key) => {
        try {
            return JSON.parse(localStorage.getItem(key));
        } catch {
            return localStorage.getItem(key);
        }
    },
    
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch {
            localStorage.setItem(key, String(value));
        }
    },
    
    remove: (key) => localStorage.removeItem(key),
    clear: () => localStorage.clear(),
    
    session: {
        get: (key) => {
            try {
                return JSON.parse(sessionStorage.getItem(key));
            } catch {
                return sessionStorage.getItem(key);
            }
        },
        
        set: (key, value) => {
            try {
                sessionStorage.setItem(key, JSON.stringify(value));
            } catch {
                sessionStorage.setItem(key, String(value));
            }
        },
        
        remove: (key) => sessionStorage.removeItem(key),
        clear: () => sessionStorage.clear()
    }
};

// ============================================
// PERFORMANCE UTILITIES
// ============================================

export const measure = (label, callback) => {
    const start = performance.now();
    const result = callback();
    const end = performance.now();
    console.log(`${label}: ${(end - start).toFixed(2)}ms`);
    return result;
};

// ============================================
// MAIN UTILITIES OBJECT
// ============================================

export const Utils = {
    // Type checking
    isString,
    isNumber,
    isBoolean,
    isFunction,
    isObject,
    isArray,
    isElement,
    isDate,
    isPromise,
    
    // String utilities
    capitalize,
    capitalizeAll,
    camelCase,
    kebabCase,
    truncate,
    escapeHtml,
    unescapeHtml,
    stripHtml,
    
    // Object utilities
    deepClone,
    merge,
    pick,
    omit,
    
    // Array utilities
    unique,
    chunk,
    flatten,
    groupBy,
    sortBy,
    shuffle,
    randomItem,
    
    // Timing utilities
    debounce,
    throttle,
    batchUpdates,
    sleep,
    
    // Random utilities
    random,
    randomFloat,
    uuid,
    generateId,
    
    // Validation utilities
    isValidEmail,
    isValidUrl,
    isValidPhone,
    
    // Formatting utilities
    formatBytes,
    formatTime,
    formatDate,
    
    // JSON utilities
    safeParseJSON,
    safeStringifyJSON,
    
    // URL utilities
    getQueryParam,
    getUrlParams,
    createUrl,
    
    // Browser utilities
    isMobile,
    isTouchDevice,
    isOnline,
    getScrollbarWidth,
    getScrollParent,
    
    // Clipboard
    copyToClipboard,
    
    // Math utilities
    clamp,
    lerp,
    round,
    
    // Event utilities
    trigger,
    
    // Storage utilities
    storage,
    
    // Performance utilities
    measure,
    
    // Utility functions
    waitFor: (condition, timeout = 10000, interval = 100) => {
        return new Promise((resolve, reject) => {
            const startTime = Date.now();

            function check() {
                if (condition()) {
                    resolve();
                } else if (Date.now() - startTime > timeout) {
                    reject(new Error('Timeout waiting for condition'));
                } else {
                    setTimeout(check, interval);
                }
            }

            check();
        });
    },
    
    loadScript: (src, options = {}) => {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.async = options.async !== false;
            script.defer = options.defer !== false;

            if (options.integrity) {
                script.integrity = options.integrity;
            }

            if (options.crossOrigin) {
                script.crossOrigin = options.crossOrigin;
            }

            script.onload = () => resolve(script);
            script.onerror = () => reject(new Error(`Failed to load script: ${src}`));

            document.head.appendChild(script);
        });
    },
    
    loadCSS: (href, options = {}) => {
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;

            if (options.integrity) {
                link.integrity = options.integrity;
            }

            if (options.crossOrigin) {
                link.crossOrigin = options.crossOrigin;
            }

            link.onload = () => resolve(link);
            link.onerror = () => reject(new Error(`Failed to load CSS: ${href}`));

            document.head.appendChild(link);
        });
    },
    
    onResize: (callback, delay = 250) => {
        const debouncedCallback = debounce(callback, delay);
        window.addEventListener('resize', debouncedCallback);
        return () => window.removeEventListener('resize', debouncedCallback);
    },
    
    onScroll: (callback, delay = 250) => {
        const debouncedCallback = debounce(callback, delay);
        window.addEventListener('scroll', debouncedCallback);
        return () => window.removeEventListener('scroll', debouncedCallback);
    }
};

export default Utils;



