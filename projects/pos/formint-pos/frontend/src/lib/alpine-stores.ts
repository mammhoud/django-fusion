// Formint POS — Alpine.js Store Definitions
// These are plain objects registered via Alpine.store() in Layout.astro

export const cartStore = {
  items: [] as { id: number; name: string; price: number; qty: number; modifiers?: string[] }[],
  customerId: null as number | null,
  customerName: '',
  notes: '',
  discount: 0,
  subtotal: 0,
  tax: 0,
  total: 0,

  init() {
    this.recalc();
  },

  add(product: { id: number; name: string; price: number }) {
    const existing = this.items.find(i => i.id === product.id);
    if (existing) {
      existing.qty += 1;
    } else {
      this.items.push({ ...product, qty: 1, modifiers: [] });
    }
    this.recalc();
  },

  remove(productId: number) {
    this.items = this.items.filter(i => i.id !== productId);
    this.recalc();
  },

  updateQty(productId: number, qty: number) {
    const item = this.items.find(i => i.id === productId);
    if (item) {
      item.qty = Math.max(1, qty);
      this.recalc();
    }
  },

  recalc() {
    this.subtotal = this.items.reduce((s, i) => s + i.price * i.qty, 0);
    this.tax = this.subtotal * 0.15;
    this.total = this.subtotal + this.tax - this.discount;
  },

  clear() {
    this.items = [];
    this.customerId = null;
    this.customerName = '';
    this.notes = '';
    this.discount = 0;
    this.recalc();
  },

  get isEmpty() {
    return this.items.length === 0;
  },

  get itemCount() {
    return this.items.reduce((s, i) => s + i.qty, 0);
  },
};

export const kdsStore = {
  filter: 'pending',
  sortOrder: 'newest',
  mutedUntil: null as number | null,
  chimeVariant: 'chime1',
  preferredPriorities: [1, 2, 3],
  selectedCategory: 'all' as string | number,

  init() {
    try {
      const saved = localStorage.getItem('kds-preferences');
      if (saved) Object.assign(this, JSON.parse(saved));
    } catch {}
  },

  persist() {
    localStorage.setItem('kds-preferences', JSON.stringify({
      sortOrder: this.sortOrder,
      chimeVariant: this.chimeVariant,
      preferredPriorities: this.preferredPriorities,
    }));
  },

  toggleMute(minutes = 30) {
    if (this.mutedUntil && this.mutedUntil > Date.now()) {
      this.mutedUntil = null;
    } else {
      this.mutedUntil = Date.now() + minutes * 60 * 1000;
    }
  },

  get isMuted() {
    return !!(this.mutedUntil && this.mutedUntil > Date.now());
  },

  get muteRemaining() {
    if (!this.isMuted || !this.mutedUntil) return null;
    const remaining = Math.ceil((this.mutedUntil - Date.now()) / 60000);
    return remaining > 0 ? `${remaining}m` : '<1m';
  },
};

export const uiStore = {
  theme: 'corporate',
  mode: 'light',
  sidebarOpen: false,
  rtl: false,
  toasts: [] as { id: number; message: string; type: string }[],

  init() {
    try {
      const saved = localStorage.getItem('formint-ui');
      if (saved) Object.assign(this, JSON.parse(saved));
    } catch {}
    this.applyTheme();
  },

  applyTheme() {
    const html = document.documentElement;
    if (this.mode === 'dark') {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
    html.setAttribute('dir', this.rtl ? 'rtl' : 'ltr');
  },

  toggleDark() {
    this.mode = this.mode === 'dark' ? 'light' : 'dark';
    this.applyTheme();
    localStorage.setItem('formint-ui', JSON.stringify({ theme: this.theme, mode: this.mode, rtl: this.rtl }));
  },

  toggleRTL() {
    this.rtl = !this.rtl;
    this.applyTheme();
    localStorage.setItem('formint-ui', JSON.stringify({ theme: this.theme, mode: this.mode, rtl: this.rtl }));
  },

  toast(message: string, type = 'info', duration = 4000) {
    const id = Date.now();
    this.toasts.push({ id, message, type });
    setTimeout(() => {
      this.toasts = this.toasts.filter(t => t.id !== id);
    }, duration);
  },

  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  },
};
