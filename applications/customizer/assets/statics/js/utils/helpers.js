// ================================================================
//   HELPERS - Utility functions
// ================================================================

export function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

export function formatTime(timestamp) {
    if (!timestamp) return 'now';
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function truncateText(text, maxLength = 30) {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '…';
}

export function debounce(func, wait) {
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