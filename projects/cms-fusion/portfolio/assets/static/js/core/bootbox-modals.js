import $ from 'jquery';
import bootbox from 'shared/js/utility/bootbox-shim.js';

// Cookie consent storage keys
const CONSENT_KEY = 'cookie_consent';
const CONSENT_SESSION_KEY = '__vresume_cookie_shown__';
let cookieDialogShowing = false;

function hasConsent() {
    return document.cookie.split(';').some(c => c.trim().startsWith(CONSENT_KEY + '='));
}

function hasShownCookieDialogThisSession() {
    return sessionStorage.getItem(CONSENT_SESSION_KEY) === 'true';
}

function markCookieDialogShownThisSession() {
    sessionStorage.setItem(CONSENT_SESSION_KEY, 'true');
}

function setConsent(value, categories) {
    const age = 365 * 24 * 60 * 60;
    document.cookie = `${CONSENT_KEY}=${value}; path=/; max-age=${age}; SameSite=Lax`;
    if (categories && categories.length) {
        document.cookie = `cookie_categories=${JSON.stringify(categories)}; path=/; max-age=${age}; SameSite=Lax`;
    }
}

export function showCookieConsent() {
    if (hasConsent() || cookieDialogShowing || hasShownCookieDialogThisSession()) return;
    cookieDialogShowing = true;
    markCookieDialogShownThisSession();

    const template = document.getElementById('cookie-consent-template');
    // Clone the entire template fragment (may contain multiple top-level nodes)
    const message = template ? template.content.cloneNode(true) : null;

    if (!message) {
        console.error('Cookie consent template not found');
        return;
    }

    // Privacy & Cookie Policy links — use event delegation
    const cookiePolicyLinks = message.querySelectorAll('.cookie-policy-link');
    cookiePolicyLinks.forEach(link => {
        link.addEventListener('click', e => {
            e.preventDefault();
            showPolicyModal(link.textContent.trim());
        });
    });

    bootbox.dialog({
        title: 'Cookie Preferences',
        message,
        closeButton: false,
        onEscape: false,
        backdrop: false,
        className: 'vresume-cookie-dialog',
        buttons: {
            reject: {
                label: 'Reject All',
                className: 'btn-outline-secondary',
                callback: () => { setConsent('declined', []); return true; },
            },
            selected: {
                label: 'Accept Selected',
                className: 'btn-outline-primary',
                callback: () => {
                    const cats = ['essential'];
                    if ($('#ck-analytics').is(':checked')) cats.push('analytics');
                    if ($('#ck-marketing').is(':checked')) cats.push('marketing');
                    if ($('#ck-preferences').is(':checked')) cats.push('preferences');
                    setConsent('accepted', cats);
                    return true;
                },
            },
            accept: {
                label: 'Accept All',
                className: 'btn-primary',
                callback: () => { setConsent('accepted', ['essential', 'analytics', 'marketing', 'preferences']); return true; },
            },
        },
    });
}

export function showPolicyModal(type) {
    const isPrivacy = type.toLowerCase().includes('privacy');
    const templateId = isPrivacy ? 'privacy-policy-template' : 'cookie-policy-template';
    const title = isPrivacy ? 'Privacy Policy' : 'Cookie Policy';

    const template = document.getElementById(templateId);
    const message = template ? template.content.cloneNode(true) : null;

    if (!message) {
        console.error('Policy template not found:', templateId);
        return;
    }

    bootbox.dialog({
        title,
        message,
        size: 'large',
        onEscape: true,
        backdrop: true,
        buttons: { close: { label: 'Close', className: 'btn-secondary' } }
    });
}

export default { showCookieConsent, showPolicyModal };
