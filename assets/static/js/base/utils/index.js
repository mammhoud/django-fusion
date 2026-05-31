/** Shared browser helpers used by all workspace sites. */
export function ready(callback) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', callback, { once: true });
    return;
  }
  callback();
}

export function siteName(defaultName = 'workspace') {
  return document.documentElement?.dataset?.site || window?.STRUCTA_SITE || defaultName;
}
