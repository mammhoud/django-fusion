function buildModal({ title = '', message = '', buttons = {}, input = null, callback = null } = {}) {
  const modal = document.createElement('div');
  modal.className = 'modal fade bootbox';
  modal.tabIndex = -1;
  modal.setAttribute('role', 'dialog');
  const footerButtons = Object.entries(buttons).map(([name, config]) => {
    const label = typeof config === 'string' ? config : (config.label || name);
    const className = typeof config === 'object' && config.className ? config.className : 'btn-primary';
    return `<button type="button" class="btn ${className}" data-bb-handler="${name}">${label}</button>`;
  }).join('') || '<button type="button" class="btn btn-primary" data-bb-handler="ok">OK</button>';
  modal.innerHTML = `
    <div class="modal-dialog">
      <div class="modal-content">
        ${title ? `<div class="modal-header"><h5 class="modal-title">${title}</h5><button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button></div>` : ''}
        <div class="modal-body"><div class="bootbox-body">${message || ''}</div>${input || ''}</div>
        <div class="modal-footer">${footerButtons}</div>
      </div>
    </div>`;
  document.body.appendChild(modal);
  const instance = window.bootstrap?.Modal ? new window.bootstrap.Modal(modal) : null;
  modal.querySelectorAll('[data-bb-handler]').forEach((button) => {
    button.addEventListener('click', () => {
      const handler = button.getAttribute('data-bb-handler');
      const value = modal.querySelector('[data-bb-input]')?.value;
      const buttonConfig = buttons[handler];
      if (buttonConfig && typeof buttonConfig.callback === 'function') {
        buttonConfig.callback(value);
      } else if (typeof callback === 'function') {
        callback(handler === 'cancel' ? null : (value ?? true));
      }
      instance?.hide();
      if (!instance) modal.remove();
    });
  });
  modal.addEventListener('hidden.bs.modal', () => modal.remove(), { once: true });
  instance?.show();
  return { modal, hide: () => instance ? instance.hide() : modal.remove() };
}

const bootbox = {
  dialog(options = {}) {
    return buildModal(options);
  },
  alert(options = {}) {
    const opts = typeof options === 'string' ? { message: options } : options;
    return buildModal({ ...opts, buttons: { ok: { label: opts.okLabel || 'OK', className: 'btn-primary' } } });
  },
  confirm(options = {}) {
    const opts = typeof options === 'string' ? { message: options } : options;
    return buildModal({
      ...opts,
      buttons: {
        cancel: { label: opts.cancelLabel || 'Cancel', className: 'btn-secondary' },
        confirm: { label: opts.confirmLabel || 'OK', className: 'btn-primary' },
      },
      callback: (result) => opts.callback?.(result !== null),
    });
  },
  prompt(options = {}) {
    const opts = typeof options === 'string' ? { title: options } : options;
    return buildModal({
      ...opts,
      message: opts.message || '',
      input: `<input class="form-control" data-bb-input type="${opts.inputType || 'text'}" placeholder="${opts.placeholder || ''}">`,
      buttons: {
        cancel: { label: opts.cancelLabel || 'Cancel', className: 'btn-secondary' },
        confirm: { label: opts.confirmLabel || 'OK', className: 'btn-primary' },
      },
      callback: opts.callback,
    });
  },
};

export default bootbox;
