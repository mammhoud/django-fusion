const state = {
  token: localStorage.getItem('planing-token'),
  user: null,
  categories: [],
  tags: [],
  notes: [],
  workspaces: [],
  activeWorkspace: null,
  selected: 'notes',
  noteView: 'all',
  tagFilter: null,
  search: '',
  view: 'notes',
  settingsTab: 'general',
  workspace: null,
  appearanceOptions: null,
  // People tab: which roles this member may hand out, and how long invitation
  // codes stay open. Both come from the server so the UI never invents a rule.
  grantableRoles: [],
  inviteTtlDays: 14,
  editing: null,
  editingCategory: null,
  // Graph view: cached payload, orphan visibility, and timeline playback.
  graphData: null,
  graphHideOrphans: false,
  graphTimeline: { enabled: false, playing: false, current: 0, speed: 1 },
  graphHeatmap: false,
  graphLaneFilter: null,
  graphSelected: null,
  // Kanban editor: kanbanEditing holds an open card id; kanbanNewStatus opens
  // the editor for a brand-new card in that column. Both null = closed.
  kanbanEditing: null,
  kanbanNewStatus: null,
  kanbanBoard: null,
  // Calendar editor: the note id of the event being edited, its event list
  // snapshot, and the anchor date for new events.
  calendarEditingEvent: null,
  calendarEvents: [],
  // Support tickets: list cache, field definitions, filters, and the modal
  // state (ticketEditing holds an open ticket id; ticketCreating opens a blank
  // form). Both null = closed.
  tickets: [],
  ticketFieldDefs: null,
  ticketStatusFilter: null,
  ticketSearch: null,
  ticketEditing: null,
  ticketCreating: null,
  pending: [],
  authMode: 'register',
  isFirstAdmin: false,
  theme: localStorage.getItem('planing-theme') || 'light',
  locale: localStorage.getItem('planing-locale') || 'en',
};

import { translations, locales, translate } from './i18n.mjs';


import { renderMarkdown } from './markdown.mjs';

const $ = (id) => document.getElementById(id);
const t = (key) => translate(state.locale, key);
const setMessage = (id, message = '') => { $(id).textContent = message; };
const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
const fileUrl = (attachment, download = false) => `/files/${encodeURIComponent(attachment.id)}/${encodeURIComponent(attachment.name)}?token=${encodeURIComponent(state.token || '')}${download ? '&download=1' : ''}`;
const formatSize = (bytes) => (bytes < 1024 ? `${bytes} B` : bytes < 1048576 ? `${(bytes / 1024).toFixed(1)} KB` : `${(bytes / 1048576).toFixed(1)} MB`);

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData) && options.body !== undefined) headers['content-type'] = 'application/json';
  if (state.token) headers.authorization = `Bearer ${state.token}`;
  const response = await fetch(path, { ...options, headers });
  const body = response.status === 204 ? null : await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body?.error || `Request failed (${response.status})`);
  return body;
}

/* ---------- Optimistic mutations ----------
   Mutations apply to the local note list immediately. Network failures are
   queued in an outbox and retried with backoff while the optimistic change
   stays visible; permanent (4xx) rejections roll back and surface the error. */
let outboxTimer = null;
let outboxAttempts = 0;
const outbox = [];

function renderOutboxBanner() {
  const banner = $('outbox-banner');
  if (!banner) return;
  banner.classList.toggle('hidden', outbox.length === 0);
  banner.querySelector('[data-outbox-count]').textContent = String(outbox.length);
}

function scheduleOutboxRetry() {
  if (!outbox.length || outboxTimer) return;
  outboxAttempts += 1;
  const delay = Math.min(1500 * outboxAttempts, 15000);
  outboxTimer = setTimeout(async () => {
    outboxTimer = null;
    if (!outbox.length) { outboxAttempts = 0; return; }
    const entry = outbox.shift();
    try {
      await entry.send();
      outboxAttempts = 0;
      renderOutboxBanner();
      await loadNotes();
      if (outbox.length) scheduleOutboxRetry();
    } catch (error) {
      if (error.permanent) {
        setMessage('app-message', t('outboxFailed'));
        renderOutboxBanner();
        await loadNotes();
        scheduleOutboxRetry();
      } else {
        outbox.unshift(entry);
        scheduleOutboxRetry();
      }
    }
  }, delay);
}

function markPermanent(error) { error.permanent = true; return error; }

async function sendMutation(path, options) {
  try { return await request(path, options); }
  catch (error) {
    if (!navigator.onLine || error.message === 'Failed to fetch') throw error;
    throw markPermanent(error);
  }
}

function applyNoteChange(id, transform) {
  const note = state.notes.find((item) => item.id === id);
  if (!note) return;
  transform(note);
  renderNotes(state.notes);
}

async function runNoteMutation(id, body, { method = 'PATCH', optimistic, path = `/api/notes/${encodeURIComponent(id)}` } = {}) {
  const send = () => sendMutation(path, { method, body: JSON.stringify(body) });
  if (optimistic) applyNoteChange(id, optimistic);
  try {
    await send();
  } catch (error) {
    if (error.permanent) {
      await loadNotes();
      setMessage('app-message', error.message);
      return;
    }
    outbox.push({ send, apply: optimistic, applyTargets: [id], describe: `${method} ${path}` });
    renderOutboxBanner();
    scheduleOutboxRetry();
    return;
  }
  // Tags are derived from notes, so any mutation can change the tag rail.
  await Promise.all([loadNotes(), loadTags()]);
}

/* ---------- Locale / theme ---------- */
function applyLocale() {
  document.documentElement.lang = state.locale;
  document.documentElement.dir = state.locale === 'ar' ? 'rtl' : 'ltr';
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    const value = t(element.dataset.i18n);
    if (element.tagName === 'LABEL') element.childNodes[0].nodeValue = value;
    else element.textContent = value;
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => { element.placeholder = t(element.dataset.i18nPlaceholder); });
  document.querySelectorAll('[data-i18n-content]').forEach((element) => { element.setAttribute('content', t(element.dataset.i18nContent)); });
  // Only the document <title> element sets the page title; other elements
  // carrying data-i18n-title get it as their own tooltip.
  document.querySelectorAll('[data-i18n-title]').forEach((element) => {
    const value = t(element.dataset.i18nTitle);
    if (element.tagName === 'TITLE') document.title = value;
    else element.setAttribute('title', value);
  });
  document.querySelectorAll('[data-i18n-aria-label]').forEach((element) => { element.setAttribute('aria-label', t(element.dataset.i18nAriaLabel)); });
  $('locale-toggle').textContent = state.locale === 'ar' ? 'English' : 'العربية';
  $('locale-toggle').setAttribute('aria-label', t('switchLanguage'));
  applyTheme();
  renderAuth();
  if (state.categories.length) { renderCategories(); renderTags(); }
  if (state.notes.length) renderNotes(state.notes);
  if (state.workspace) renderAppearanceOptions();
}

function resolveTheme() {
  if (state.workspace?.theme && state.workspace.theme !== 'system') return state.workspace.theme;
  const override = localStorage.getItem('planing-theme-override');
  if (override) return override;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme() {
  const resolved = resolveTheme();
  document.documentElement.dataset.theme = resolved;
  document.documentElement.dataset.accent = state.workspace?.accent || 'violet';
  document.documentElement.dataset.themeVariant = state.workspace?.themeVariant || 'default';
  document.documentElement.dataset.buttonStyle = state.workspace?.buttonStyle || 'default';
  document.documentElement.dataset.badgeStyle = state.workspace?.badgeStyle || 'default';
  $('theme-toggle').textContent = resolved === 'dark' ? t('lightMode') : t('darkMode');
  $('theme-toggle').setAttribute('aria-pressed', String(resolved === 'dark'));
}

// Appearance presets: pure PATCH bundles over the orthogonal token axes, per
// the appearance plan's decision record. Applying one never invents new CSS.
const appearancePresets = {
  industrial: { theme: 'light', themeVariant: 'default', accent: 'violet', fontScale: 'default', styleVariant: 'sharp', radiusScale: 'subtle', edgeStrength: 'strong', shadowDepth: 'default', density: 'cozy', buttonStyle: 'default', badgeStyle: 'default' },
  paper: { theme: 'light', themeVariant: 'default', accent: 'blue', fontScale: 'large', styleVariant: 'rounded', radiusScale: 'soft', edgeStrength: 'soft', shadowDepth: 'flat', density: 'comfortable', buttonStyle: 'outline', badgeStyle: 'tinted' },
  focus: { theme: 'light', themeVariant: 'perplexity', accent: 'blue', fontScale: 'default', styleVariant: 'compact', radiusScale: 'subtle', edgeStrength: 'soft', shadowDepth: 'flat', density: 'compact', buttonStyle: 'ghost', badgeStyle: 'outline' },
  midnight: { theme: 'dark', themeVariant: 'corporate', accent: 'violet', fontScale: 'default', styleVariant: 'rounded', radiusScale: 'soft', edgeStrength: 'default', shadowDepth: 'floating', density: 'cozy', buttonStyle: 'solid', badgeStyle: 'solid' },
};

function applyPreset(name) {
  const preset = appearancePresets[name];
  if (!preset || !state.workspace) return;
  Object.assign(state.workspace, preset);
  localStorage.removeItem('planing-theme-override');
  applyTheme(); applyFontScale(); applyStyleVariant(); applyAppearanceTokens();
  renderAppearanceOptions();
  request('/api/settings', { method: 'PATCH', body: JSON.stringify(preset) }).then(() => setMessage('appearance-message', t('appearanceSaved'))).catch((error) => setMessage('appearance-message', error.message));
}

function renderPresetCards() {
  if (!state.workspace) return;
  const current = Object.entries(appearancePresets).find(([, values]) =>
    Object.entries(values).every(([key, value]) => (state.workspace[key] ?? (key === 'styleVariant' ? 'sharp' : key === 'density' ? 'cozy' : 'default')) === value)
  );
  const cards = [
    { id: 'industrial', name: t('presetIndustrial'), desc: t('presetIndustrialDesc'), swatches: ['#171717', '#7143d8', '#ffffff'] },
    { id: 'paper', name: t('presetPaper'), desc: t('presetPaperDesc'), swatches: ['#2563eb', '#f2ece2', '#ffffff'] },
    { id: 'focus', name: t('presetFocus'), desc: t('presetFocusDesc'), swatches: ['#4f46e5', '#f1f2f3', '#ffffff'] },
    { id: 'midnight', name: t('presetMidnight'), desc: t('presetMidnightDesc'), swatches: ['#7aa2ff', '#222d40', '#101828'] },
  ];
  $('preset-cards').innerHTML = cards.map((card) => `
    <button class="preset-card ${current && current[0] === card.id ? 'active' : ''}" data-preset="${card.id}" type="button">
      <span class="preset-swatches" aria-hidden="true">${card.swatches.map((color) => `<i style="background:${color}"></i>`).join('')}</span>
      <span class="preset-card-name">${escapeHtml(card.name)}</span>
      <span class="preset-card-desc">${escapeHtml(card.desc)}</span>
    </button>`).join('');
  document.querySelectorAll('#preset-cards [data-preset]').forEach((card) => card.addEventListener('click', () => applyPreset(card.dataset.preset)));
}

function applyFontScale() {
  document.documentElement.dataset.fontScale = state.workspace?.fontScale || 'default';
}

// Surface style variant: sharp (default), rounded, compact, wide. Stored per
// workspace and exposed to CSS as a data attribute so styles stay declarative.
function applyStyleVariant() {
  document.documentElement.dataset.styleVariant = state.workspace?.styleVariant || 'sharp';
}

// Tier-1 appearance axes. Each is a pure token axis: CSS reads the data
// attribute and remaps custom properties, components never branch on values.
function applyAppearanceTokens() {
  const root = document.documentElement;
  root.dataset.radiusScale = state.workspace?.radiusScale || 'default';
  root.dataset.edgeStrength = state.workspace?.edgeStrength || 'default';
  root.dataset.shadowDepth = state.workspace?.shadowDepth || 'default';
  root.dataset.density = state.workspace?.density || 'cozy';
}

function setStorageStatus(online) {
  const label = online ? t('storageConnected') : t('storageUnavailable');
  const flag = $('storage-flag');
  if (flag) {
    flag.classList.toggle('offline', !online);
    $('storage-flag-label').textContent = online ? t('storageFlagConnected') : t('storageFlagDisconnected');
  }
}

async function refreshStorageStatus() {
  try { const response = await fetch('/health'); const health = await response.json(); setStorageStatus(response.ok && health.storage?.connected); }
  catch { setStorageStatus(false); }
}

/* ---------- Sidebar ---------- */
function selectedCategory() { return state.categories.find((category) => category.slug === state.selected) || state.categories[0]; }

const laneColors = ['#f97316', '#2563eb', '#7c3aed', '#0d9488', '#e11d48', '#f59e0b'];

function renderCategoryEditor() {
  const mount = $('category-editor');
  if (!mount) return;
  const category = state.categories.find((item) => item.slug === state.editingCategory) || null;
  if (!category) { mount.classList.add('hidden'); mount.innerHTML = ''; return; }
  const swatches = laneColors.map((color) => `<button class="swatch ${category.color === color ? 'active' : ''}" data-swatch="${color}" type="button" style="background:${color}" aria-label="${color}"></button>`).join('');
  mount.innerHTML = `
    <form id="category-edit-form" class="panel category-editor">
      <div class="editor-topline"><p class="eyebrow" data-i18n="editLane">${escapeHtml(t('editLane'))}</p><button class="text-action muted-action" id="category-editor-close" type="button" aria-label="${escapeHtml(t('closeLaneEditor'))}">✕</button></div>
      <p class="muted editor-hint">${escapeHtml(t('editLaneHint'))}</p>
      <label for="category-name-input">${escapeHtml(t('laneName'))}${category.isSystem ? `<input id="category-name-input" value="${escapeHtml(category.name)}" maxlength="40" disabled>` : `<input id="category-name-input" value="${escapeHtml(category.name)}" maxlength="40" required>`}</label>
      <p class="editor-label">${escapeHtml(t('laneColor'))}</p>
      <div class="swatch-row">${swatches}</div>
      <div class="editor-inline"><p class="editor-label">${escapeHtml(t('laneIcon'))}</p><input id="category-icon-input" value="${escapeHtml(category.icon || '')}" maxlength="2" class="icon-input"></div>
      <div class="editor-actions"><button class="link-button danger" id="category-delete" type="button">${escapeHtml(t('deleteLane'))}</button><button class="button button-small" type="submit">${escapeHtml(t('saveLane'))}</button></div>
      <p id="category-edit-message" class="message" role="alert"></p>
    </form>`;
  mount.classList.remove('hidden');
  mount.querySelectorAll('[data-swatch]').forEach((swatch) => swatch.addEventListener('click', () => {
    category.color = swatch.dataset.swatch;
    mount.querySelectorAll('[data-swatch]').forEach((other) => other.classList.toggle('active', other === swatch));
  }));
  mount.querySelector('#category-editor-close').addEventListener('click', () => { state.editingCategory = null; renderCategoryEditor(); });
  mount.querySelector('#category-edit-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const body = { color: category.color, icon: mount.querySelector('#category-icon-input').value.trim() || category.name.slice(0, 1).toUpperCase() };
    if (!category.isSystem) body.name = mount.querySelector('#category-name-input').value.trim();
    try {
      const updated = await request(`/api/categories/${encodeURIComponent(category.slug)}`, { method: 'PATCH', body: JSON.stringify(body) });
      const index = state.categories.findIndex((item) => item.slug === category.slug);
      if (index >= 0) state.categories[index] = updated;
      state.editingCategory = null;
      renderCategories(); updateSelectedCategory(); renderCategoryEditor();
      setMessage('app-message', t('laneSaved'));
    } catch (error) { setMessage('category-edit-message', error.message); }
  });
  mount.querySelector('#category-delete').addEventListener('click', async () => {
    if (!window.confirm(t('deleteLaneConfirm'))) return;
    try {
      await request(`/api/categories/${encodeURIComponent(category.slug)}`, { method: 'DELETE' });
      state.categories = state.categories.filter((item) => item.slug !== category.slug);
      state.editingCategory = null;
      if (state.selected === category.slug) state.selected = 'notes';
      renderCategories(); updateSelectedCategory(); renderCategoryEditor(); await loadNotes();
      setMessage('app-message', t('laneDeleted'));
    } catch (error) { setMessage('category-edit-message', error.message); }
  });
}

function renderCategories() {
  const canManage = state.canManageCategories;
  $('category-buttons').innerHTML = state.categories.map((category) => {
    const manage = canManage ? `<button class="lane-manage" data-lane-edit="${escapeHtml(category.slug)}" type="button" aria-label="${escapeHtml(t('editLane'))} — ${escapeHtml(category.name)}">✎</button>` : '';
    return `<div class="category-row"><button class="category-button ${category.slug === state.selected && !state.tagFilter ? 'active' : ''}" data-category="${escapeHtml(category.slug)}" type="button"><span class="icon" ${category.color ? `style="background:${escapeHtml(category.color)}"` : ''}>${escapeHtml(category.icon || category.name[0])}</span><span>${escapeHtml(category.name)}</span><span class="category-arrow">↗</span></button>${manage}</div>`;
  }).join('');
  $('category-buttons').querySelectorAll('[data-category]').forEach((button) => button.addEventListener('click', async () => {
    state.selected = button.dataset.category; state.tagFilter = null; renderCategories(); renderTags(); updateSelectedCategory(); await loadNotes();
  }));
  $('category-buttons').querySelectorAll('[data-lane-edit]').forEach((button) => button.addEventListener('click', (event) => {
    event.stopPropagation();
    state.editingCategory = button.dataset.laneEdit;
    renderCategoryEditor();
  }));
  $('default-category').innerHTML = state.categories.map((category) => `<option value="${escapeHtml(category.slug)}">${escapeHtml(category.name)}</option>`).join('');
  renderMarkdownExportLanes();
  updateSelectedCategory();
}

function updateSelectedCategory() {
  const category = selectedCategory();
  $('selected-category-icon').textContent = category?.icon || category?.name?.[0] || 'B';
  $('selected-category-name').textContent = category?.name || state.selected;
}

function renderTags() {
  // The API includes zero-count tags (e.g. cross-workspace tags, or a tag whose
  // last note was just untagged). They cannot filter anything here, so the rail
  // hides them instead of showing dead chips.
  const tags = (state.tags || []).filter((tag) => Number(tag.count || 0) > 0);
  // Two mounts: the visible horizontal chip strip in the notes toolbar and a
  // hidden mirror in the sidebar for keyboard/screen-reader navigation.
  const chipHtml = tags.length ? tags.map((tag) => `<button class="tag-chip ${state.tagFilter === tag.name ? 'active' : ''}" data-tag="${escapeHtml(tag.name)}" type="button"><span class="tag-chip-name">#${escapeHtml(tag.name)}</span><span class="tag-chip-count">${tag.count || 0}</span></button>`).join('') : `<span class="muted tag-empty">${escapeHtml(t('emptyAttachments'))}</span>`;
  $('tag-chips').innerHTML = chipHtml;
  $('tag-buttons').innerHTML = tags.map((tag) => `<button class="tag-chip ${state.tagFilter === tag.name ? 'active' : ''}" data-tag="${escapeHtml(tag.name)}" type="button">#${escapeHtml(tag.name)}</button>`).join('');
  document.querySelectorAll('#tag-chips [data-tag], #tag-buttons [data-tag]').forEach((button) => button.addEventListener('click', async () => {
    state.tagFilter = state.tagFilter === button.dataset.tag ? null : button.dataset.tag;
    renderCategories(); renderTags(); await loadNotes();
  }));
  $('tag-clear').classList.toggle('hidden', !state.tagFilter);
}

/* ---------- Notes ---------- */
function parseTagInput(value) {
  return String(value).split(/[\s,]+/).map((tag) => tag.replace(/^#/, '').trim()).filter(Boolean).slice(0, 12);
}

function attachmentChips(attachments) {
  if (!attachments.length) return '';
  return `<div class="note-attachments"><span class="note-attachments-title">${escapeHtml(t('attachmentsTitle'))}</span>${attachments.map((attachment) => {
    const isImage = (attachment.type || '').startsWith('image/');
    const preview = isImage ? `<img class="attachment-thumb" src="${escapeHtml(fileUrl(attachment))}" alt="${escapeHtml(attachment.name)}" loading="lazy">` : `<span class="attachment-icon">◧</span>`;
    // Files whose text was extracted can be turned into a note directly, or
    // queued for an AI summary (the summary lands as a new linked note).
    const asNote = attachment.hasText ? `<button class="link-button" data-attachment-note="${escapeHtml(attachment.id)}" type="button">${escapeHtml(t('attachmentAddNote'))}</button>` : '';
    const summarize = attachment.hasText && state.user?.permissions?.includes('notes:write') ? `<button class="link-button" data-attachment-summarize="${escapeHtml(attachment.id)}" type="button" title="${escapeHtml(t('summarizeQueued'))}">${escapeHtml(t('summarizeAction'))}</button>` : '';
    return `<span class="attachment-chip">${preview}<span class="attachment-name">${escapeHtml(attachment.name)}</span><small>${formatSize(attachment.size)}</small><a class="link-button" href="${escapeHtml(fileUrl(attachment))}" target="_blank" rel="noopener">${escapeHtml(t('viewFile'))}</a><a class="link-button" href="${escapeHtml(fileUrl(attachment, true))}" download>${escapeHtml(t('downloadFile'))}</a>${asNote}${summarize}</span>`;
  }).join('')}</div>`;
}

function noteActions(note) {
  const canWrite = state.user?.permissions?.includes('notes:write');
  if (!canWrite) return '';
  if (state.noteView === 'recycle') {
    return `<div class="note-actions"><button class="link-button" data-note-action="restore" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('restore'))}</button><button class="link-button danger" data-note-action="delete-forever" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('deleteForever'))}</button></div>`;
  }
  if (state.noteView === 'archive') {
    return `<div class="note-actions"><button class="link-button" data-note-action="restore" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('restore'))}</button><button class="link-button danger" data-note-action="recycle" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('moveToBin'))}</button></div>`;
  }
  const pin = note.isTop
    ? `<button class="link-button" data-note-action="unpin" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('unpin'))}</button>`
    : `<button class="link-button" data-note-action="pin" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('pin'))}</button>`;
  const sharedActions = note.isShare
    ? `<a class="link-button" href="/share/${encodeURIComponent(note.id)}" target="_blank" rel="noopener">${escapeHtml(t('openPreview'))}</a><button class="link-button" data-note-action="copy-link" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('copyLink'))}</button>`
    : '';
  const sharedBadge = note.isShare ? `<span class="shared-badge" title="${escapeHtml(t('share'))}">◎ ${escapeHtml(t('share'))}</span>` : '';
  const summarize = state.user?.permissions?.includes('notes:write') ? `<button class="link-button" data-note-summarize="${escapeHtml(note.id)}" type="button" title="${escapeHtml(t('summarizeQueued'))}">${escapeHtml(t('summarizeAction'))}</button>` : '';
  return `<div class="note-actions">${pin}<button class="link-button" data-note-action="edit" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('edit'))}</button><button class="link-button" data-note-action="cards" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('cards'))}</button>${summarize}<button class="link-button" data-note-action="links" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('linksToggle'))}</button><button class="link-button" data-note-action="comments" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('commentsToggle'))}</button><button class="link-button" data-note-action="history" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('historyToggle'))}</button><button class="link-button" data-note-action="archive" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('moveToArchive'))}</button><button class="link-button" data-note-action="${note.isShare ? 'unshare' : 'share'}" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(note.isShare ? t('unshare') : t('share'))}</button>${sharedBadge}${sharedActions}<button class="link-button danger" data-note-action="recycle" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('moveToBin'))}</button></div>`;
}

function noteCard(note) {
  if (state.editing === note.id) {
    // The editor opens wide by default with the same toolbar and live preview as
    // the composer, so editing a long markdown note is not a cramped 6-row box.
    return `<article class="note editing" data-note-id="${escapeHtml(note.id)}">
      <div class="composer-topline">
        <span class="category-signal"><span>✎</span></span>
        <div><p class="eyebrow">${escapeHtml(t('editLaneHint'))}</p><strong>${escapeHtml(t('edit'))}</strong></div>
        <div class="composer-topline-actions">
          <button class="chip-toggle" data-edit-preview type="button" aria-pressed="false" title="${escapeHtml(t('tooltipPreview'))}"><span>${escapeHtml(t('previewLabel'))}</span></button>
          <button class="chip-toggle" data-edit-expand type="button" aria-pressed="true" title="${escapeHtml(t('tooltipExpand'))}"><span aria-hidden="true">⤢</span><span>${escapeHtml(t('expandLabel'))}</span></button>
        </div>
      </div>
      <div class="editor-toolbar" role="toolbar" aria-label="${escapeHtml(t('editorToolbarAria'))}">${editorToolbarMarkup()}</div>
      <div class="editor-surface is-wide">
        <textarea class="edit-content" rows="14" placeholder="${escapeHtml(t('notePlaceholder'))}">${escapeHtml(note.content)}</textarea>
        <div class="editor-preview markdown-body hidden"></div>
      </div>
      <label class="edit-tags-label">${escapeHtml(t('editTags'))}<input class="edit-tags" value="${escapeHtml(note.tags.map((tag) => tag.name).join(' '))}" title="${escapeHtml(t('tooltipTags'))}"></label>
      <div class="note-actions"><button class="link-button" data-note-action="save-edit" data-id="${escapeHtml(note.id)}" type="button" title="${escapeHtml(t('tooltipSave'))}">${escapeHtml(t('saveEdit'))}</button><button class="link-button danger" data-note-action="cancel-edit" type="button">${escapeHtml(t('cancelEdit'))}</button><span class="editor-metrics" data-editor-metrics></span></div>
    </article>`;
  }
  const tagChips = note.tags.length ? `<div class="note-tags">${note.tags.map((tag) => `<button class="tag-chip" data-tag-jump="${escapeHtml(tag.name)}" type="button">#${escapeHtml(tag.name)}</button>`).join('')}</div>` : '';
  const pinnedBadge = note.isTop ? `<span class="pin-badge">▲ ${escapeHtml(t('pinned'))}</span>` : '';
  const editedBadge = note.createdAt && note.updatedAt && new Date(note.updatedAt).getTime() - new Date(note.createdAt).getTime() > 60000 ? `<span class="edited-badge">${escapeHtml(t('edited'))}</span>` : '';
  const copyButton = `<button class="link-button note-copy" data-note-action="copy-md" data-id="${escapeHtml(note.id)}" type="button">${escapeHtml(t('copyMarkdown'))}</button>`;
  return `<article class="note ${note.isTop ? 'is-pinned' : ''}">
    ${pinnedBadge}
    <div class="note-content markdown-body">${renderMarkdown(note.content)}</div>
    ${tagChips}
    ${attachmentChips(note.attachments || [])}
    <div class="note-meta"><span>${escapeHtml(note.category?.name || '—')}</span><span class="note-date">${new Date(note.updatedAt).toLocaleDateString(state.locale === 'ar' ? 'ar' : 'en')}${editedBadge}</span></div>
    <div class="note-actions">${copyButton}${noteActions(note).replace('<div class="note-actions">', '').replace('</div>', '')}</div>
    <div class="note-links hidden" data-links-for="${escapeHtml(note.id)}"></div>
    <div class="note-comments hidden" data-comments-for="${escapeHtml(note.id)}"></div>
    <div class="note-history hidden" data-history-for="${escapeHtml(note.id)}"></div>
  </article>`;
}

function renderNotes(notes) {
  state.notes = notes;
  const visible = notes.filter((note) => !note.isDeleted);
  const list = $('notes-list');
  list.setAttribute('aria-busy', 'false');
  list.classList.remove('is-loading', 'has-error');
  $('note-count').textContent = `${visible.length} ${visible.length === 1 ? t('notesOne') : t('notesMany')}`;
  $('note-total').textContent = visible.filter((note) => !note.isRecycle && !note.isArchived).length || visible.length;
  $('notes-empty').classList.toggle('hidden', visible.length > 0);
  list.innerHTML = visible.map(noteCard).join('');
  bindNoteActions();
  bindWikilinks();
}

function renderNotesLoading() {
  const list = $('notes-list');
  list.setAttribute('aria-busy', 'true');
  list.classList.add('is-loading');
  list.classList.remove('has-error');
  $('notes-empty').classList.add('hidden');
  list.innerHTML = Array.from({ length: 4 }, (_, index) => `
    <article class="note-skeleton" style="--stagger:${index}">
      <span class="skeleton-line skeleton-line-wide"></span>
      <span class="skeleton-line skeleton-line-medium"></span>
      <span class="skeleton-block"></span>
      <span class="skeleton-line skeleton-line-short"></span>
    </article>`).join('');
}

function renderNotesError(error) {
  const list = $('notes-list');
  list.setAttribute('aria-busy', 'false');
  list.classList.remove('is-loading');
  list.classList.add('has-error');
  $('notes-empty').classList.add('hidden');
  list.innerHTML = `<div class="inline-error" role="alert"><strong>${escapeHtml(t('loadError') || 'Could not load notes')}</strong><span>${escapeHtml(error.message || 'Try again in a moment.')}</span><button class="link-button" type="button" data-notes-retry>${escapeHtml(t('retryNow') || 'Retry now')}</button></div>`;
  list.querySelector('[data-notes-retry]')?.addEventListener('click', () => loadNotes());
}

// Wiki-link chips resolve against the workspace: jump to a matching note by
// searching for its title, or prefill the composer when nothing matches yet.
function bindWikilinks() {
  $('notes-list').querySelectorAll('[data-wikilink]').forEach((chip) => chip.addEventListener('click', async () => {
    const target = chip.dataset.wikilink;
    state.noteView = 'all'; state.tagFilter = null;
    document.querySelectorAll('[data-note-view]').forEach((element) => element.classList.toggle('active', element.dataset.noteView === 'all'));
    $('note-search').value = target;
    state.search = target;
    await loadNotes();
  }));
}

// The comment thread for one note. Threads are workspace-scoped on the server:
// both the note and every comment are filtered on the active workspace, so this
// panel only ever shows the conversation of the workspace you are in.
async function renderNoteComments(id, panel) {
  let data;
  try {
    data = await request(`/api/notes/${encodeURIComponent(id)}/comments`);
  } catch (error) {
    panel.innerHTML = `<p class="panel-copy">${escapeHtml(error.message)}</p>`;
    return;
  }
  const thread = data.comments.length
    ? data.comments.map((comment) => `
      <div class="comment${comment.isDeleted ? ' is-deleted' : ''}" data-comment-id="${escapeHtml(comment.id)}">
        <div class="comment-meta"><strong>${escapeHtml(comment.authorName || '—')}</strong><time>${escapeHtml(formatWhen(comment.createdAt))}${comment.edited ? ` · ${escapeHtml(t('edited'))}` : ''}</time></div>
        ${comment.isDeleted
          ? `<p class="comment-body comment-removed">${escapeHtml(t('commentRemoved'))}</p>`
          : `<div class="comment-body markdown-body">${renderMarkdown(comment.body)}</div>`}
        <div class="comment-actions">${comment.canEdit ? `<button class="link-button" data-comment-edit="${escapeHtml(comment.id)}" type="button">${escapeHtml(t('edit'))}</button>` : ''}${comment.canDelete ? `<button class="link-button danger" data-comment-delete="${escapeHtml(comment.id)}" type="button">${escapeHtml(t('deleteLabel'))}</button>` : ''}</div>
      </div>`).join('')
    : `<p class="panel-copy">${escapeHtml(t('noComments'))}</p>`;
  panel.innerHTML = `
    <div class="comment-thread">
      <span class="link-group-title">${escapeHtml(t('commentsTitle'))} · ${Number(data.count || 0)}</span>
      ${thread}
    </div>
    ${data.canComment
      ? `<form class="comment-form"><label class="sr-only" for="comment-input-${escapeHtml(id)}">${escapeHtml(t('commentPlaceholder'))}</label><textarea id="comment-input-${escapeHtml(id)}" rows="2" maxlength="4000" placeholder="${escapeHtml(t('commentPlaceholder'))}"></textarea><button class="button" type="submit">${escapeHtml(t('commentAdd'))}</button></form>`
      : `<p class="panel-copy">${escapeHtml(t('commentReadOnly'))}</p>`}
    <p class="comment-message message" role="alert"></p>`;
  const message = (text) => { const host = panel.querySelector('.comment-message'); if (host) host.textContent = text; };
  const commentById = (commentId) => data.comments.find((entry) => entry.id === commentId);
  const hostFor = (commentId) => [...panel.querySelectorAll('[data-comment-id]')].find((node) => node.dataset.commentId === commentId);

  const form = panel.querySelector('.comment-form');
  if (form) form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const field = form.querySelector('textarea');
    const body = field.value.trim();
    if (!body) { message(t('commentEmpty')); return; }
    try {
      await request(`/api/notes/${encodeURIComponent(id)}/comments`, { method: 'POST', body: JSON.stringify({ body }) });
      await renderNoteComments(id, panel);
      setMessage('app-message', t('commentAdded'));
    } catch (error) { message(error.message); }
  });

  panel.querySelectorAll('[data-comment-delete]').forEach((button) => button.addEventListener('click', async () => {
    if (!window.confirm(t('commentDeleteConfirm'))) return;
    try {
      await request(`/api/comments/${encodeURIComponent(button.dataset.commentDelete)}`, { method: 'DELETE' });
      await renderNoteComments(id, panel);
    } catch (error) { message(error.message); }
  }));

  panel.querySelectorAll('[data-comment-edit]').forEach((button) => button.addEventListener('click', () => {
    const comment = commentById(button.dataset.commentEdit);
    const host = hostFor(button.dataset.commentEdit);
    if (!comment || !host) return;
    host.querySelector('.comment-body').innerHTML = `<textarea class="comment-edit" rows="3" maxlength="4000">${escapeHtml(comment.body)}</textarea>`;
    host.querySelector('.comment-actions').innerHTML = `<button class="link-button" data-comment-save type="button">${escapeHtml(t('saveEdit'))}</button><button class="link-button danger" data-comment-cancel type="button">${escapeHtml(t('cancelEdit'))}</button>`;
    host.querySelector('[data-comment-save]').addEventListener('click', async () => {
      try {
        await request(`/api/comments/${encodeURIComponent(comment.id)}`, { method: 'PATCH', body: JSON.stringify({ body: host.querySelector('.comment-edit').value }) });
        await renderNoteComments(id, panel);
      } catch (error) { message(error.message); }
    });
    host.querySelector('[data-comment-cancel]').addEventListener('click', () => { renderNoteComments(id, panel); });
    host.querySelector('.comment-edit').focus();
  }));
}

// Per-note activity timeline: the same mutation story the workspace audit
// carries, filtered to this note. Read-only, so any role that can see the note
// can read what happened to it.
const historyActionKeys = {
  'note.created': 'historyActionCreated',
  'note.updated': 'historyActionUpdated',
  'note.deleted': 'historyActionDeleted',
};

async function renderNoteHistory(id, panel) {
  try {
    const events = await request(`/api/notes/${encodeURIComponent(id)}/activity`);
    if (!events.length) {
      panel.innerHTML = `<span class="link-empty">${escapeHtml(t('historyEmpty'))}</span>`;
      return;
    }
    panel.innerHTML = `
      <span class="link-group-title">${escapeHtml(t('historyTitle'))}</span>
      <ol class="history-list">
        ${events.map((event) => {
          const actionKey = historyActionKeys[event.action];
          const label = actionKey ? t(actionKey) : event.action;
          const who = event.actorName || event.actor || '';
          const when = new Date(event.createdAt).toLocaleString(state.locale === 'ar' ? 'ar' : 'en', { dateStyle: 'medium', timeStyle: 'short' });
          return `<li class="history-entry"><span class="history-dot" aria-hidden="true"></span><div><strong>${escapeHtml(label)}</strong>${who ? `<span class="history-actor"> · ${escapeHtml(who)}</span>` : ''}<time class="history-time">${escapeHtml(when)}</time></div></li>`;
        }).join('')}
      </ol>`;
  } catch (error) {
    panel.innerHTML = `<span class="link-empty">${escapeHtml(error.message)}</span>`;
  }
}

// The note graph: outgoing [[wiki links]] and incoming backlinks, rendered
// inline under the note so study notes can be navigated without leaving the
// stream. Missing targets offer the composer prefill path used by wikilinks.
async function renderNoteLinks(id, panel) {
  try {
    const graph = await request(`/api/notes/${encodeURIComponent(id)}/backlinks`);
    const chip = (note, label) => note
      ? `<button class="link-button" data-tag-jump="${escapeHtml(label)}" type="button">↗ ${escapeHtml(label)}</button>`
      : `<span class="link-missing">${escapeHtml(label)} · ${escapeHtml(t('missingNote'))}</span>`;
    const outgoing = graph.links.length
      ? graph.links.map((link) => chip(link.note, link.note ? labelOf(link.note) : link.title)).join('')
      : `<span class="link-empty">${escapeHtml(t('noLinks'))}</span>`;
    const incoming = graph.backlinks.length
      ? graph.backlinks.map((note) => chip(note, labelOf(note))).join('')
      : `<span class="link-empty">${escapeHtml(t('noBacklinks'))}</span>`;
    panel.innerHTML = `
      <div class="link-group"><span class="link-group-title">${escapeHtml(t('linksTitle'))}</span><div class="link-chips">${outgoing}</div></div>
      <div class="link-group"><span class="link-group-title">${escapeHtml(t('backlinksTitle'))}</span><div class="link-chips">${incoming}</div></div>`;
    panel.querySelectorAll('[data-tag-jump]').forEach((element) => element.addEventListener('click', async () => {
      state.noteView = 'all'; state.tagFilter = null; state.search = element.dataset.tagJump;
      document.querySelectorAll('[data-note-view]').forEach((entry) => entry.classList.toggle('active', entry.dataset.noteView === 'all'));
      $('note-search').value = state.search;
      await loadNotes();
    }));
  } catch (error) { panel.innerHTML = `<span class="link-empty">${escapeHtml(error.message)}</span>`; }
}

function labelOf(note) {
  const line = String(note.content || '').split('\n').map((row) => row.trim()).find((row) => row.length > 0) || '';
  return line.replace(/^#+\s*/, '').trim().slice(0, 70) || t('openNote');
}

function bindNoteActions() {
  $('notes-list').querySelectorAll('[data-note-action]').forEach((button) => button.addEventListener('click', async () => {
    const action = button.dataset.noteAction;
    const id = button.dataset.id;
    const mutate = (body, optimistic) => runNoteMutation(id, body, { optimistic });
    try {
      if (action === 'copy-md') {
        const source = state.notes.find((item) => item.id === id);
        try { await navigator.clipboard.writeText(source ? source.content : ''); setMessage('app-message', t('markdownCopied')); } catch { /* clipboard unavailable */ }
        return;
      }
      if (action === 'pin' || action === 'unpin') await mutate({ isTop: action === 'pin' }, (note) => { note.isTop = action === 'pin'; });
      else if (action === 'archive') await mutate({ isArchived: true }, (note) => { note.isArchived = true; });
      else if (action === 'recycle') await mutate({ isRecycle: true }, (note) => { note.isRecycle = true; });
      else if (action === 'restore') await mutate({ isRecycle: false, isArchived: false }, (note) => { note.isRecycle = false; note.isArchived = false; });
      else if (action === 'copy-link') {
        try { await navigator.clipboard.writeText(`${location.origin}/share/${encodeURIComponent(id)}`); setMessage('app-message', t('linkCopied')); } catch { /* clipboard unavailable */ }
        return;
      }
      else if (action === 'cards') {
        const result = await request('/api/study/generate', { method: 'POST', body: JSON.stringify({ noteId: id, mode: 'auto' }) });
        setMessage('app-message', result.created > 0 ? t('cardsCreated').replace('{count}', result.created) : t('cardsNone'));
        return;
      }
      else if (action === 'links') {
        const panel = button.closest('.note')?.querySelector('.note-links');
        if (!panel) return;
        if (!panel.classList.contains('hidden')) { panel.classList.add('hidden'); return; }
        panel.classList.remove('hidden');
        panel.innerHTML = `<p class="panel-copy">…</p>`;
        await renderNoteLinks(id, panel);
        return;
      }
      else if (action === 'comments') {
        const panel = button.closest('.note')?.querySelector('.note-comments');
        if (!panel) return;
        if (!panel.classList.contains('hidden')) { panel.classList.add('hidden'); return; }
        panel.classList.remove('hidden');
        panel.innerHTML = `<p class="panel-copy">…</p>`;
        await renderNoteComments(id, panel);
        return;
      }
      else if (action === 'history') {
        const panel = button.closest('.note')?.querySelector('.note-history');
        if (!panel) return;
        if (!panel.classList.contains('hidden')) { panel.classList.add('hidden'); return; }
        panel.classList.remove('hidden');
        panel.innerHTML = `<p class="panel-copy">…</p>`;
        await renderNoteHistory(id, panel);
        return;
      }
      else if (action === 'share' || action === 'unshare') {
        const makeShared = action === 'share';
        // The share flag rides in the mutation body — passing it as an option
        // sent an empty payload and silently wrote is_share=false.
        await runNoteMutation(id, { share: makeShared }, { method: 'PATCH', path: `/api/notes/${encodeURIComponent(id)}/share`, optimistic: (note) => { note.isShare = makeShared; } });
        if (makeShared) {
          try { await navigator.clipboard.writeText(`${location.origin}/share/${encodeURIComponent(id)}`); setMessage('app-message', t('shareLinkCopied')); } catch { /* clipboard unavailable */ }
        }
      }
      else if (action === 'delete-forever') {
        if (!window.confirm(t('removeMemberConfirm'))) return;
        const optimisticRemove = () => {};
        applyNoteChange(id, (note) => { note.isDeleted = true; });
        try { await sendMutation(`/api/notes/${encodeURIComponent(id)}`, { method: 'DELETE' }); await loadNotes(); }
        catch (error) {
          if (error.permanent) { await loadNotes(); setMessage('app-message', error.message); }
          else { applyNoteChange(id, (note) => { delete note.isDeleted; }); outbox.push({ send: () => sendMutation(`/api/notes/${encodeURIComponent(id)}`, { method: 'DELETE' }), apply: optimisticRemove, describe: `DELETE /api/notes/${id}` }); renderOutboxBanner(); scheduleOutboxRetry(); }
        }
      }
      else if (action === 'edit') { state.editing = id; renderNotes(state.notes); }
      else if (action === 'cancel-edit') { state.editing = null; renderNotes(state.notes); }
      else if (action === 'save-edit') {
        const card = button.closest('.note');
        const content = card.querySelector('.edit-content').value.trim();
        const tags = parseTagInput(card.querySelector('.edit-tags').value);
        if (!content) throw new Error(t('noNotes'));
        state.editing = null;
        await runNoteMutation(id, { content, tags }, { optimistic: (note) => { note.content = content; note.tags = tags.map((name) => ({ id: name, name })); } });
      }
    } catch (error) { setMessage('app-message', error.message); }
  }));
  $('notes-list').querySelectorAll('[data-tag-jump]').forEach((chip) => chip.addEventListener('click', async () => {
    state.tagFilter = chip.dataset.tagJump; renderCategories(); renderTags(); await loadNotes();
  }));
  // Extracted attachment text becomes a note in one click.
  $('notes-list').querySelectorAll('[data-attachment-note]').forEach((button) => button.addEventListener('click', async () => {
    try {
      const name = button.closest('.attachment-chip')?.querySelector('.attachment-name')?.textContent || '';
      await request(`/api/attachments/${encodeURIComponent(button.dataset.attachmentNote)}/to-note`, { method: 'POST', body: JSON.stringify({}) });
      setMessage('app-message', t('attachmentNoteCreated').replace('{name}', name));
      await loadNotes();
    } catch (error) { setMessage('app-message', error.message); }
  }));
  // Extracted attachment text is queued for an AI summary note.
  $('notes-list').querySelectorAll('[data-attachment-summarize]').forEach((button) => button.addEventListener('click', async () => {
    try {
      await request('/api/ai/jobs', { method: 'POST', body: JSON.stringify({ kind: 'summarize.note', attachmentId: button.dataset.attachmentSummarize }) });
      setMessage('app-message', t('summarizeQueued'));
    } catch (error) { setMessage('app-message', error.message); }
  }));
  // A note is queued for an AI summary note linked back to it.
  $('notes-list').querySelectorAll('[data-note-summarize]').forEach((button) => button.addEventListener('click', async () => {
    try {
      await request('/api/ai/jobs', { method: 'POST', body: JSON.stringify({ kind: 'summarize.note', noteId: button.dataset.noteSummarize }) });
      setMessage('app-message', t('summarizeQueued'));
    } catch (error) { setMessage('app-message', error.message); }
  }));
}

async function loadCategories() {
  state.categories = await request('/api/categories');
  if (!state.categories.some((category) => category.slug === state.selected)) state.selected = state.categories[0]?.slug || 'notes';
  renderCategories();
  return state.categories;
}

// The sidebar chrome reflects the active workspace, not just the settings copy.
function applyWorkspaceChrome() {
  const active = (state.workspaces || []).find((workspace) => workspace.id === state.activeWorkspace);
  if (!active) return;
  $('workspace-title').textContent = active.name;
  $('workspace-description').textContent = active.description || t('defaultWorkspaceDescription');
}

async function loadNotes() {
  const params = new URLSearchParams();
  if (state.noteView === 'all' && !state.tagFilter && state.search) params.set('q', state.search);
  if (state.noteView !== 'all') params.set('view', state.noteView);
  if (state.noteView === 'all' && !state.tagFilter) params.set('category', state.selected);
  if (state.tagFilter) params.set('tag', state.tagFilter.replace(/^#/, ''));
  renderNotesLoading();
  try {
    const notes = await request(`/api/notes?${params.toString()}`);
    // Keep optimistic, still-unsynced changes visible over fresh server data.
    for (const entry of outbox) if (entry.apply) for (const note of notes) if (entry.applyTargets?.includes(note.id)) entry.apply(note);
    renderNotes(notes);
  }
  catch (error) { renderNotesError(error); setMessage('app-message', error.message); }
}

async function loadTags() {
  try { state.tags = await request('/api/tags'); renderTags(); }
  catch { state.tags = []; }
}

/* ---------- Attachments ---------- */
async function uploadFiles(files) {
  for (const file of files) {
    const response = await fetch('/api/attachments', {
      method: 'POST',
      headers: { authorization: `Bearer ${state.token}`, 'x-file-name': file.name, 'x-file-type': file.type || 'application/octet-stream' },
      body: file,
    });
    if (!response.ok) { const body = await response.json().catch(() => ({})); throw new Error(body?.error || 'Upload failed'); }
    state.pending.push(await response.json());
  }
  renderPending();
}

function renderPending() {
  $('pending-attachments').innerHTML = state.pending.map((attachment) => `<span class="attachment-chip pending"><span class="attachment-icon">◧</span><span class="attachment-name">${escapeHtml(attachment.name)}</span><small>${formatSize(attachment.size)}</small></span>`).join('');
}

/* ---------- Views ---------- */
/* ---------- Support tickets ---------- */

const ticketStatusMeta = {
  new: { cls: 'new' }, open: { cls: 'open' }, pending: { cls: 'pending' }, resolved: { cls: 'resolved' }, closed: { cls: 'closed' },
};

function ticketStatusLabel(status) {
  return { new: t('ticketStatusNew'), open: t('ticketStatusOpen'), pending: t('ticketStatusPending'), resolved: t('ticketStatusResolved'), closed: t('ticketStatusClosed') }[status] || status;
}

function ticketPriorityLabel(priority) {
  return { low: t('ticketPriorityLow'), medium: t('ticketPriorityMedium'), high: t('ticketPriorityHigh'), urgent: t('ticketPriorityUrgent') }[priority] || priority;
}

async function loadTickets() {
  renderTicketsLoading();
  try {
    const params = new URLSearchParams();
    if (state.ticketStatusFilter) params.set('status', state.ticketStatusFilter);
    if (state.ticketSearch) params.set('q', state.ticketSearch);
    const query = params.toString();
    state.tickets = await request(`/api/tickets${query ? `?${query}` : ''}`);
    renderTickets(state.tickets);
  } catch (error) { setMessage('tickets-message', error.message); }
}

function renderTicketsLoading() {
  const mount = $('tickets-list');
  if (mount) mount.innerHTML = `<p class="muted">${escapeHtml(t('loading'))}</p>`;
}

function renderTickets(tickets) {
  const mount = $('tickets-list');
  if (!mount) return;
  if (!tickets.length) { mount.innerHTML = `<p class="muted">${escapeHtml(t('ticketsEmpty'))}</p>`; return; }
  mount.innerHTML = tickets.map((ticket) => {
    const fieldDefs = state.ticketFieldDefs || [];
    const customSummary = fieldDefs
      .filter((field) => ticket.customFields?.[field.id])
      .slice(0, 3)
      .map((field) => `<span class="ticket-custom-chip">${escapeHtml(field.label)}: ${escapeHtml(ticket.customFields[field.id])}</span>`)
      .join('');
    const when = new Date(ticket.updatedAt || ticket.createdAt).toLocaleDateString(state.locale === 'ar' ? 'ar' : 'en');
    return `<button class="ticket-card ticket-status-${ticketStatusMeta[ticket.status]?.cls || 'new'}" data-ticket-open="${escapeHtml(ticket.id)}" type="button">
      <div class="ticket-card-main">
        <span class="ticket-subject">${escapeHtml(ticket.subject)}</span>
        ${customSummary ? `<span class="ticket-card-custom">${customSummary}</span>` : ''}
      </div>
      <div class="ticket-card-meta">
        <span class="ticket-status-chip status-${ticketStatusMeta[ticket.status]?.cls || 'new'}">${escapeHtml(ticketStatusLabel(ticket.status))}</span>
        <span class="ticket-priority-chip priority-${ticket.priority}">${escapeHtml(ticketPriorityLabel(ticket.priority))}</span>
        ${ticket.replyCount ? `<span class="ticket-replies-chip">💬 ${ticket.replyCount}</span>` : ''}
        <span class="ticket-date">${escapeHtml(when)}</span>
      </div>
    </button>`;
  }).join('');
  mount.querySelectorAll('[data-ticket-open]').forEach((card) => card.addEventListener('click', () => openTicketEditor(card.dataset.ticketOpen)));
}

function renderTicketFieldInputs(ticket, defs) {
  return defs.map((field) => {
    const value = ticket?.customFields?.[field.id] ?? '';
    const id = `ticket-cf-${escapeHtml(field.id)}`;
    if (field.type === 'select') {
      return `<div class="ticket-form-row"><label for="${id}">${escapeHtml(field.label)}${field.required ? ' *' : ''}</label><select id="${id}" data-cf-id="${escapeHtml(field.id)}"><option value="">—</option>${field.options.map((option) => `<option value="${escapeHtml(option)}" ${value === option ? 'selected' : ''}>${escapeHtml(option)}</option>`).join('')}</select></div>`;
    }
    if (field.type === 'textarea') {
      return `<div class="ticket-form-row"><label for="${id}">${escapeHtml(field.label)}${field.required ? ' *' : ''}</label><textarea id="${id}" data-cf-id="${escapeHtml(field.id)}" rows="2">${escapeHtml(value)}</textarea></div>`;
    }
    if (field.type === 'checkbox') {
      return `<div class="ticket-form-row ticket-form-checkbox"><label><input id="${id}" data-cf-id="${escapeHtml(field.id)}" type="checkbox" ${value === 'true' ? 'checked' : ''}> ${escapeHtml(field.label)}</label></div>`;
    }
    const inputType = field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : 'text';
    return `<div class="ticket-form-row"><label for="${id}">${escapeHtml(field.label)}${field.required ? ' *' : ''}</label><input id="${id}" data-cf-id="${escapeHtml(field.id)}" type="${inputType}" value="${escapeHtml(value)}"></div>`;
  }).join('');
}

function collectTicketCustomFields(scope) {
  const custom = {};
  scope.querySelectorAll('[data-cf-id]').forEach((input) => {
    custom[input.dataset.cfId] = input.type === 'checkbox' ? (input.checked ? 'true' : 'false') : input.value;
  });
  return custom;
}

function renderTicketEditor() {
  const mount = $('ticket-editor');
  if (!mount) return;
  if (!state.ticketEditing && !state.ticketCreating) { mount.classList.add('hidden'); mount.innerHTML = ''; return; }
  const ticket = state.ticketEditing ? (state.tickets || []).find((item) => item.id === state.ticketEditing) : null;
  const defs = state.ticketFieldDefs || [];
  const statuses = Object.keys(ticketStatusMeta);
  const priorities = ['low', 'medium', 'high', 'urgent'];
  const statusChip = (value) => `<span class="ticket-status-chip status-${ticketStatusMeta[value]?.cls || 'new'}">${escapeHtml(ticketStatusLabel(value))}</span>`;

  // Full record display for existing tickets: every stored field the API returns.
  const recordRows = ticket ? [
    [t('ticketStatus'), statusChip(ticket.status)],
    [t('ticketPriority'), `<span class="ticket-priority-chip priority-${ticket.priority}">${escapeHtml(ticketPriorityLabel(ticket.priority))}</span>`],
    [t('ticketRequester'), escapeHtml(ticket.requester || '—')],
    [t('ticketAssignee'), escapeHtml(ticket.assignee || '—')],
    [t('recordCreated'), new Date(ticket.createdAt).toLocaleString(state.locale === 'ar' ? 'ar' : 'en')],
    [t('recordUpdated'), new Date(ticket.updatedAt).toLocaleString(state.locale === 'ar' ? 'ar' : 'en')],
    ...defs.map((field) => [escapeHtml(field.label), ticket.customFields?.[field.id] ? escapeHtml(String(ticket.customFields[field.id])) : '—']),
  ] : [];

  mount.innerHTML = `
    <div class="modal-backdrop" data-ticket-close></div>
    <div class="modal-dialog" role="dialog" aria-modal="true" aria-label="${escapeHtml(ticket ? t('ticketEdit') : t('ticketNew'))}">
      <div class="modal-head"><p class="eyebrow">${escapeHtml(ticket ? t('ticketEdit') : t('ticketNew'))}</p><button class="text-action muted-action" data-ticket-close type="button" aria-label="${escapeHtml(t('cancelEdit'))}">✕</button></div>
      <form id="ticket-form" class="modal-body">
        <div class="ticket-form-row"><label for="ticket-subject">${escapeHtml(t('ticketSubject'))} *</label><input id="ticket-subject" type="text" value="${escapeHtml(ticket?.subject || '')}" required></div>
        <div class="ticket-form-row"><label for="ticket-description">${escapeHtml(t('ticketDescription'))}</label><textarea id="ticket-description" rows="3">${escapeHtml(ticket?.description || '')}</textarea></div>
        <div class="ticket-form-grid">
          <div class="ticket-form-row"><label for="ticket-status">${escapeHtml(t('ticketStatus'))}</label><select id="ticket-status">${statuses.map((status) => `<option value="${status}" ${ticket?.status === status ? 'selected' : ''}>${escapeHtml(ticketStatusLabel(status))}</option>`).join('')}</select></div>
          <div class="ticket-form-row"><label for="ticket-priority">${escapeHtml(t('ticketPriority'))}</label><select id="ticket-priority">${priorities.map((priority) => `<option value="${priority}" ${ticket?.priority === priority ? 'selected' : ''}>${escapeHtml(ticketPriorityLabel(priority))}</option>`).join('')}</select></div>
        </div>
        ${defs.length ? `<p class="appearance-sublabel">${escapeHtml(t('ticketCustomFields'))}</p>${renderTicketFieldInputs(ticket, defs)}` : ''}
        ${recordRows.length ? `<details class="ticket-record-details"><summary>${escapeHtml(t('recordDetails'))}</summary><div class="record-details-grid">${recordRows.map(([label, value]) => `<div class="record-detail"><span>${label}</span><strong>${value}</strong></div>`).join('')}</div></details>` : ''}
        <div class="record-modal-actions">
          ${ticket ? `<button class="link-button danger" type="button" id="ticket-delete">${escapeHtml(t('deleteLabel'))}</button>` : ''}
          <button class="button button-small" type="submit">${escapeHtml(ticket ? t('saveEdit') : t('ticketCreate'))}</button>
        </div>
      </form>
      ${ticket ? `
      <div class="ticket-replies-section modal-replies">
        <p class="appearance-sublabel">${escapeHtml(t('ticketReplies'))} (${ticket.replyCount || 0})</p>
        <div id="ticket-replies-list" class="ticket-replies-list"></div>
        <form id="ticket-reply-form" class="ticket-reply-form">
          <textarea id="ticket-reply-body" rows="2" placeholder="${escapeHtml(t('ticketReplyPlaceholder'))}" required></textarea>
          <button class="button button-small" type="submit">${escapeHtml(t('ticketReplySend'))}</button>
        </form>
      </div>` : ''}
    </div>`;
  mount.classList.remove('hidden');

  mount.querySelectorAll('[data-ticket-close]').forEach((closer) => closer.addEventListener('click', () => { state.ticketEditing = null; state.ticketCreating = null; renderTicketEditor(); }));
  mount.addEventListener('keydown', (event) => { if (event.key === 'Escape') { state.ticketEditing = null; state.ticketCreating = null; renderTicketEditor(); } }, { once: true });

  $('ticket-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const subject = $('ticket-subject').value.trim();
    if (!subject) return;
    const payload = {
      subject,
      description: $('ticket-description').value,
      status: $('ticket-status').value,
      priority: $('ticket-priority').value,
      customFields: collectTicketCustomFields(mount),
    };
    try {
      if (ticket) await request(`/api/tickets/${encodeURIComponent(ticket.id)}`, { method: 'PATCH', body: JSON.stringify(payload) });
      else await request('/api/tickets', { method: 'POST', body: JSON.stringify(payload) });
      state.ticketEditing = null; state.ticketCreating = null;
      renderTicketEditor();
      await loadTicketFieldDefs();
      await loadTickets();
    } catch (error) { setMessage('tickets-message', error.message); }
  });

  const deleteButton = $('ticket-delete');
  if (deleteButton) deleteButton.addEventListener('click', async () => {
    if (!window.confirm(t('ticketDeleteConfirm'))) return;
    try { await request(`/api/tickets/${encodeURIComponent(ticket.id)}`, { method: 'DELETE' }); state.ticketEditing = null; renderTicketEditor(); await loadTickets(); }
    catch (error) { setMessage('tickets-message', error.message); }
  });

  if (ticket) {
    loadTicketReplies(ticket);
    $('ticket-reply-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const body = $('ticket-reply-body').value.trim();
      if (!body) return;
      try {
        await request(`/api/tickets/${encodeURIComponent(ticket.id)}/replies`, { method: 'POST', body: JSON.stringify({ body }) });
        $('ticket-reply-body').value = '';
        await loadTicketReplies(ticket);
        const fresh = await request(`/api/tickets/${encodeURIComponent(ticket.id)}`);
        ticket.replyCount = fresh.replyCount;
        const repliesLabel = mount.querySelector('.ticket-replies-section .appearance-sublabel');
        if (repliesLabel) repliesLabel.textContent = `${t('ticketReplies')} (${fresh.replyCount})`;
      } catch (error) { setMessage('tickets-message', error.message); }
    });
  }
}

async function loadTicketReplies(ticket) {
  try {
    const detail = await request(`/api/tickets/${encodeURIComponent(ticket.id)}`);
    const list = $('ticket-replies-list');
    if (list) list.innerHTML = detail.replies.length
      ? detail.replies.map((reply) => `<div class="ticket-reply"><div class="ticket-reply-head"><strong>${escapeHtml(reply.author || '—')}</strong><span>${new Date(reply.createdAt).toLocaleString(state.locale === 'ar' ? 'ar' : 'en')}</span></div><p>${escapeHtml(reply.body)}</p></div>`).join('')
      : `<p class="muted">${escapeHtml(t('ticketNoReplies'))}</p>`;
  } catch { /* replies stay as-is on transient errors */ }
}

async function openTicketEditor(id) {
  try {
    const detail = await request(`/api/tickets/${encodeURIComponent(id)}`);
    if (!state.tickets) state.tickets = [];
    const index = state.tickets.findIndex((item) => item.id === id);
    if (index >= 0) state.tickets[index] = detail; else state.tickets.push(detail);
    state.ticketCreating = null;
    state.ticketEditing = id;
    renderTicketEditor();
  } catch (error) { setMessage('tickets-message', error.message); }
}

async function loadTicketFieldDefs() {
  try { state.ticketFieldDefs = await request('/api/tickets/fields'); }
  catch { state.ticketFieldDefs = []; }
}

function renderTicketFieldsAdmin() {
  const list = $('ticket-fields-list');
  if (!list) return;
  const defs = state.ticketFieldDefs || [];
  list.innerHTML = defs.length ? defs.map((field) => `
    <div class="ticket-field-row">
      <div><strong>${escapeHtml(field.label)}</strong><small>${escapeHtml(field.type)}${field.options?.length ? ` · ${field.options.map(escapeHtml).join(' / ')}` : ''}${field.required ? ' · *' : ''}</small></div>
      <button class="link-button danger" data-ticket-field-delete="${escapeHtml(field.id)}" type="button">${escapeHtml(t('deleteLabel'))}</button>
    </div>`).join('') : `<p class="muted">${escapeHtml(t('ticketFieldsEmpty'))}</p>`;
  list.querySelectorAll('[data-ticket-field-delete]').forEach((button) => button.addEventListener('click', async () => {
    try { await request(`/api/tickets/fields/${encodeURIComponent(button.dataset.ticketFieldDelete)}`, { method: 'DELETE' }); await loadTicketFieldDefs(); renderTicketFieldsAdmin(); }
    catch (error) { setMessage('ticket-fields-message', error.message); }
  }));
}

function setView(view) {
  state.view = view;
  document.querySelectorAll('.view').forEach((element) => element.classList.toggle('hidden', element.id !== `${view}-view`));
  document.querySelectorAll('[data-view]').forEach((button) => button.classList.toggle('active', button.dataset.view === view));
  $('notes-navigation').classList.toggle('hidden', view !== 'notes');
  if (view === 'settings') { loadSettings(); loadMembers(); loadWorkspaceAdmin(); }
  if (view === 'chat' && window.chatApp) window.chatApp.enter();
  if (view === 'study') loadStudy();
  if (view === 'graph') loadGraph();
  if (view === 'kanban') loadKanban();
  if (view === 'calendar') loadCalendar();
  if (view === 'tickets') { loadTicketFieldDefs().then(loadTickets); }
}

function setSettingsTab(tab) {
  state.settingsTab = tab;
  document.querySelectorAll('.settings-page').forEach((element) => element.classList.toggle('hidden', element.id !== `settings-${tab}`));
  // A few settings panels live beside the tab pages (workspace admin) and carry
  // a page name instead, so they follow the same tab switch.
  document.querySelectorAll('[data-settings-page]').forEach((element) => element.classList.toggle('hidden', element.dataset.settingsPage !== tab));
  document.querySelectorAll('[data-settings-tab]').forEach((button) => button.classList.toggle('active', button.dataset.settingsTab === tab));
  if (tab === 'tickets') { loadTicketFieldDefs().then(renderTicketFieldsAdmin); }
  if (tab === 'data') { loadStorageSnapshot(); renderRetention(); }
  if (tab === 'activity') loadAudit();
  if (tab === 'people') loadMembers();
  if (tab === 'ai') {
    if (window.providerAdmin) window.providerAdmin.load();
    if (window.promptAdmin) window.promptAdmin.load();
    if (window.contextRootsAdmin) window.contextRootsAdmin.load();
    if (window.aiPolicyAdmin) window.aiPolicyAdmin.load();
    if (window.aiRunsAdmin) window.aiRunsAdmin.load();
    if (window.aiJobsAdmin) window.aiJobsAdmin.load();
  }
  if (tab === 'activity') loadSecurityEvents();
}

/* ---------- Workspaces: switcher + management ---------- */
async function loadWorkspaces() {
  try {
    const data = await request('/api/workspaces');
    state.workspaces = data.workspaces || [];
    state.activeWorkspace = data.activeId || null;
    const active = state.workspaces.find((workspace) => workspace.id === state.activeWorkspace) || state.workspaces[0] || null;
    const select = $('workspace-select');
    if (select) {
      select.innerHTML = state.workspaces
        .map((workspace) => `<option value="${escapeHtml(workspace.id)}"${workspace.id === state.activeWorkspace ? ' selected' : ''}>${escapeHtml(workspace.name)} · ${Number(workspace.notes || 0)}</option>`)
        .join('');
    }
    return active;
  } catch { return null; }
}

// Switching re-reads everything that belongs to the workspace, so no view keeps
// showing the previous workspace's notes, chats, or study queue.
async function switchWorkspace(id) {
  if (!id || id === state.activeWorkspace) return;
  try {
    setMessage('workspace-admin-message');
    await request(`/api/workspaces/${encodeURIComponent(id)}/active`, { method: 'POST', body: JSON.stringify({}) });
  } catch (error) {
    setMessage('workspace-admin-message', error.message);
    await loadWorkspaces();
    return;
  }
  state.selected = 'notes';
  state.tagFilter = null;
  state.search = '';
  state.editing = null;
  state.pending = [];
  if (window.chatApp) { window.chatApp.sessions = []; window.chatApp.sessionId = null; window.chatApp.messages = []; window.chatApp.contextFiles = []; window.chatApp.contextRoots = []; window.chatApp.rootId = ''; }
  await refreshWorkspaceData();
  setMessage('app-message', t('workspaceSwitched').replace('{name}', (await loadWorkspaces())?.name || id));
}

async function refreshWorkspaceData() {
  await Promise.all([
    loadCategories().catch(() => {}),
    loadTags().catch(() => {}),
    loadNotes().catch(() => {}),
    loadWorkspaces(),
  ]);
  applyWorkspaceChrome();
  applySettings(await request('/api/settings').catch(() => null));
  if (state.view === 'study') loadStudy().catch(() => {});
  if (state.view === 'graph') loadGraph().catch(() => {});
  if (state.view === 'kanban') loadKanban().catch(() => {});
  if (state.view === 'calendar') loadCalendar().catch(() => {});
  if (state.view === 'chat' && window.chatApp) window.chatApp.enter().catch(() => {});
  if (state.view === 'settings') { loadMembers().catch(() => {}); if (window.contextRootsAdmin) window.contextRootsAdmin.load(); }
}

// --- workspace switcher + creation form -----------------------------------
$('workspace-select').addEventListener('change', (event) => { switchWorkspace(event.target.value); });
$('workspace-create-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const input = $('workspace-new-name');
  const name = input.value.trim();
  if (name.length < 2) { setMessage('workspace-admin-message', t('workspaceNameTooShort')); return; }
  setMessage('workspace-admin-message');
  try {
    await request('/api/workspaces', { method: 'POST', body: JSON.stringify({ name }) });
  } catch (error) {
    setMessage('workspace-admin-message', error.message);
    return;
  }
  input.value = '';
  setMessage('workspace-admin-message', t('workspaceCreated').replace('{name}', name));
  state.selected = 'notes'; state.search = ''; state.tagFilter = null; state.editing = null;
  await refreshWorkspaceData();
  await loadWorkspaceAdmin();
});

async function loadWorkspaceAdmin() {
  const workspaces = await loadWorkspaces();
  const host = $('workspace-list');
  if (!host) return;
  host.innerHTML = (state.workspaces || []).map((workspace) => `
    <div class="provider-row" data-workspace-row="${escapeHtml(workspace.id)}"${workspace.isActive ? ' class="provider-row active"' : ''}>
      <span class="provider-identity"><strong>${escapeHtml(workspace.name)}</strong><small>${escapeHtml(workspace.role || '')} · ${Number(workspace.notes || 0)} ${escapeHtml(t('notesCountLabel'))}</small></span>
      <span class="provider-flags">${workspace.isActive ? `<code data-i18n="workspaceActive">${escapeHtml(t('workspaceActive'))}</code>` : ''}${workspace.isArchived ? '<code>ARCHIVED</code>' : ''}</span>
      <span class="provider-row-actions">
        <button class="link-button" type="button" data-workspace-action="switch" data-id="${escapeHtml(workspace.id)}"${workspace.isActive ? ' disabled' : ''}>${escapeHtml(t('workspaceSwitch'))}</button>
        <button class="link-button" type="button" data-workspace-action="rename" data-id="${escapeHtml(workspace.id)}">${escapeHtml(t('edit'))}</button>
        <button class="link-button danger" type="button" data-workspace-action="archive" data-id="${escapeHtml(workspace.id)}">${escapeHtml(t('workspaceArchive'))}</button>
      </span>
    </div>`).join('');
  host.querySelectorAll('[data-workspace-action]').forEach((button) => button.addEventListener('click', async () => {
    const { workspaceAction: action, id } = button.dataset;
    if (action === 'switch') return switchWorkspace(id);
    if (action === 'rename') {
      const next = window.prompt(t('workspaceRenamePrompt'), (state.workspaces.find((workspace) => workspace.id === id) || {}).name || '');
      if (!next || !next.trim()) return;
      try {
        await request(`/api/workspaces/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify({ name: next.trim() }) });
        setMessage('workspace-admin-message', t('workspaceRenamed'));
      } catch (error) { setMessage('workspace-admin-message', error.message); return; }
    }
    if (action === 'archive') {
      if (!window.confirm(t('workspaceArchiveConfirm'))) return;
      try {
        await request(`/api/workspaces/${encodeURIComponent(id)}/archive`, { method: 'POST', body: JSON.stringify({}) });
        setMessage('workspace-admin-message', t('workspaceArchived'));
      } catch (error) { setMessage('workspace-admin-message', error.message); return; }
    }
    await loadWorkspaceAdmin();
    await refreshWorkspaceData();
  }));
  return workspaces;
}

/* ---------- Settings ---------- */
// One application path for the settings payload, used by the Settings view and
// by every workspace switch, so the effective role, grantable roles, and
// appearance always describe the workspace currently in scope.
function applySettings(data) {
  if (!data?.workspace) return;
  state.workspace = data.workspace;
  state.appearanceOptions = data.appearance || state.appearanceOptions;
  state.roles = data.roles || [];
  state.grantableRoles = data.grantableRoles || [];
  state.inviteTtlDays = data.inviteTtlDays ?? 14;
  $('workspace-name').value = data.workspace.name;
  $('workspace-description-input').value = data.workspace.description || '';
  $('ai-context').value = data.workspace.aiContext || '';
  $('default-category').value = data.workspace.defaultCategory || 'notes';
  $('workspace-kicker').textContent = (data.workspace.name || '').toUpperCase().slice(0, 24);
  $('workspace-description').textContent = data.workspace.description || t('defaultWorkspaceDescription');
  // The effective role is the membership role in *this* workspace, so the
  // sidebar chip and every permission gate follow the workspace, not the
  // account's legacy global role.
  if (state.user && data.workspaceRole) {
    state.user.role = data.workspaceRole;
    const entry = state.roles.find((role) => role.name === data.workspaceRole);
    if (entry) state.user.permissions = entry.permissions;
    renderUser();
  }
  applyFontScale(); applyTheme(); applyStyleVariant(); applyAppearanceTokens(); renderAppearanceOptions(); renderRoleReference(state.roles);
  syncRoleOptions();
  renderPeopleScope();
}

async function loadSettings() {
  try {
    applySettings(await request('/api/settings'));
  } catch (error) { setMessage('app-message', error.message); }
}

// Only the roles this member may actually grant stay selectable; the server
// rejects the rest, so offering them would be a lie.
function syncRoleOptions() {
  const grantable = new Set(state.grantableRoles.length ? state.grantableRoles : ['viewer']);
  for (const id of ['member-role', 'invite-role']) {
    const select = $(id);
    if (!select) continue;
    for (const option of [...select.options]) {
      option.hidden = !grantable.has(option.value);
      option.disabled = !grantable.has(option.value);
    }
    if (select.selectedOptions[0]?.disabled) {
      const first = [...select.options].find((option) => !option.disabled);
      if (first) select.value = first.value;
    }
  }
}

function renderPeopleScope() {
  const host = $('people-scope');
  if (!host) return;
  const name = state.workspace?.name || '';
  host.textContent = name ? t('peopleScope').replace('{workspace}', name).replace('{role}', roleLabel(state.user?.role || '')) : '';
}

function optionButton(group, value, label, isActive) {
  return `<button class="option-button ${isActive ? 'active' : ''}" data-option-group="${group}" data-option-value="${escapeHtml(value)}" type="button">${escapeHtml(label)}</button>`;
}

function renderAppearanceOptions() {
  if (!state.appearanceOptions || !state.workspace) return;
  const themeLabels = { light: t('themeLight'), dark: t('themeDark'), system: t('themeSystem') };
  const accentLabels = { violet: t('accentViolet'), blue: t('accentBlue'), green: t('accentGreen'), orange: t('accentOrange'), red: t('accentRed') };
  const scaleLabels = { compact: t('scaleCompact'), default: t('scaleDefault'), large: t('scaleLarge') };
  const styleLabels = { sharp: t('styleSharp'), rounded: t('styleRounded'), compact: t('styleCompact'), wide: t('styleWide') };
  const radiusLabels = { none: t('radiusNone'), subtle: t('radiusSubtle'), default: t('radiusDefault'), soft: t('radiusSoft'), full: t('radiusFull') };
  const edgeLabels = { soft: t('edgeSoft'), default: t('edgeDefault'), strong: t('edgeStrong') };
  const shadowLabels = { flat: t('shadowFlat'), default: t('shadowDefault'), floating: t('shadowFloating') };
  const densityLabels = { compact: t('densityCompact'), cozy: t('densityCozy'), comfortable: t('densityComfortable') };
  const variantLabels = { default: t('variantDefault'), corporate: t('variantCorporate'), luxury: t('variantLuxury'), pastel: t('variantPastel'), perplexity: t('variantPerplexity') };
  const buttonLabels = { default: t('buttonDefault'), outline: t('buttonOutline'), solid: t('buttonSolid'), ghost: t('buttonGhost') };
  const badgeLabels = { default: t('badgeDefault'), tinted: t('badgeTinted'), outline: t('badgeOutline'), solid: t('badgeSolid') };
  $('theme-options').innerHTML = state.appearanceOptions.themes.map((theme) => optionButton('theme', theme, themeLabels[theme] || theme, state.workspace.theme === theme)).join('');
  $('theme-variant-options').innerHTML = (state.appearanceOptions.themeVariants || ['default']).map((variant) => optionButton('themeVariant', variant, variantLabels[variant] || variant, (state.workspace.themeVariant || 'default') === variant)).join('');
  $('button-style-options').innerHTML = (state.appearanceOptions.buttonStyles || ['default']).map((value) => optionButton('buttonStyle', value, buttonLabels[value] || value, (state.workspace.buttonStyle || 'default') === value)).join('');
  $('badge-style-options').innerHTML = (state.appearanceOptions.badgeStyles || ['default']).map((value) => optionButton('badgeStyle', value, badgeLabels[value] || value, (state.workspace.badgeStyle || 'default') === value)).join('');
  renderPresetCards();
  $('accent-options').innerHTML = state.appearanceOptions.accents.map((accent) => optionButton('accent', accent, accentLabels[accent] || accent, state.workspace.accent === accent)).join('');
  $('font-scale-options').innerHTML = state.appearanceOptions.fontScales.map((scale) => optionButton('fontScale', scale, scaleLabels[scale] || scale, state.workspace.fontScale === scale)).join('');
  $('style-options').innerHTML = (state.appearanceOptions.styleVariants || ['sharp', 'rounded', 'compact', 'wide']).map((variant) => optionButton('styleVariant', variant, styleLabels[variant] || variant, (state.workspace.styleVariant || 'sharp') === variant)).join('');
  $('radius-options').innerHTML = (state.appearanceOptions.radiusScales || []).map((value) => optionButton('radiusScale', value, radiusLabels[value] || value, (state.workspace.radiusScale || 'default') === value)).join('');
  $('edge-options').innerHTML = (state.appearanceOptions.edgeStrengths || []).map((value) => optionButton('edgeStrength', value, edgeLabels[value] || value, (state.workspace.edgeStrength || 'default') === value)).join('');
  $('shadow-options').innerHTML = (state.appearanceOptions.shadowDepths || []).map((value) => optionButton('shadowDepth', value, shadowLabels[value] || value, (state.workspace.shadowDepth || 'default') === value)).join('');
  $('density-options').innerHTML = (state.appearanceOptions.densities || []).map((value) => optionButton('density', value, densityLabels[value] || value, (state.workspace.density || 'cozy') === value)).join('');
  document.querySelectorAll('[data-option-group]').forEach((button) => button.addEventListener('click', async () => {
    const group = button.dataset.optionGroup;
    const body = { theme: state.workspace.theme, themeVariant: state.workspace.themeVariant || 'default', accent: state.workspace.accent, fontScale: state.workspace.fontScale, styleVariant: state.workspace.styleVariant || 'sharp', radiusScale: state.workspace.radiusScale || 'default', edgeStrength: state.workspace.edgeStrength || 'default', shadowDepth: state.workspace.shadowDepth || 'default', density: state.workspace.density || 'cozy', buttonStyle: state.workspace.buttonStyle || 'default', badgeStyle: state.workspace.badgeStyle || 'default' };
    body[group] = button.dataset.optionValue;
    if (group === 'theme') { state.workspace.theme = button.dataset.optionValue; localStorage.removeItem('planing-theme-override'); applyTheme(); }
    if (group === 'themeVariant') { state.workspace.themeVariant = button.dataset.optionValue; applyTheme(); }
    if (group === 'buttonStyle') { state.workspace.buttonStyle = button.dataset.optionValue; applyTheme(); }
    if (group === 'badgeStyle') { state.workspace.badgeStyle = button.dataset.optionValue; applyTheme(); }
    if (group === 'accent') { state.workspace.accent = button.dataset.optionValue; applyTheme(); }
    if (group === 'fontScale') { state.workspace.fontScale = button.dataset.optionValue; applyFontScale(); }
    if (group === 'styleVariant') { state.workspace.styleVariant = button.dataset.optionValue; applyStyleVariant(); }
    if (group === 'radiusScale') { state.workspace.radiusScale = button.dataset.optionValue; applyAppearanceTokens(); }
    if (group === 'edgeStrength') { state.workspace.edgeStrength = button.dataset.optionValue; applyAppearanceTokens(); }
    if (group === 'shadowDepth') { state.workspace.shadowDepth = button.dataset.optionValue; applyAppearanceTokens(); }
    if (group === 'density') { state.workspace.density = button.dataset.optionValue; applyAppearanceTokens(); }
    renderAppearanceOptions();
    try { await request('/api/settings', { method: 'PATCH', body: JSON.stringify(body) }); setMessage('appearance-message', t('appearanceSaved')); }
    catch (error) { setMessage('appearance-message', error.message); }
  }));
}

function roleLabel(role) {
  if (!role) return '';
  return t(`role${role[0].toUpperCase()}${role.slice(1)}`) || role;
}

function renderRoleReference(roles) {
  $('role-reference').innerHTML = roles.map((role) => `<div class="role-card"><strong>${escapeHtml(roleLabel(role.name))}</strong><small>${escapeHtml(role.permissions.join(' · '))}</small></div>`).join('');
}

const formatWhen = (value) => (value ? new Date(value).toLocaleString(state.locale === 'ar' ? 'ar' : 'en') : '—');

async function loadInvitations() {
  const panel = $('invite-panel');
  if (!panel) return;
  if (!state.user?.permissions?.includes('members:write')) { panel.classList.add('hidden'); return; }
  panel.classList.remove('hidden');
  try {
    const invites = await request('/api/invitations');
    $('invitations-list').innerHTML = invites.length
      ? invites.map((invite) => `<div class="invite-row-item"><code>${escapeHtml(invite.code)}</code><span class="invite-role-name">${escapeHtml(roleLabel(invite.role))}</span><span class="invite-meta">${escapeHtml(t('invitedBy'))} ${escapeHtml(invite.createdBy || '—')} · ${escapeHtml(t('inviteExpiresShort'))} ${escapeHtml(formatWhen(invite.expiresAt))}</span><span class="spacer"></span><button class="link-button" data-copy-invite="${escapeHtml(invite.code)}" type="button">${escapeHtml(t('copyCode'))}</button><button class="link-button danger" data-revoke-invite="${escapeHtml(invite.code)}" type="button">${escapeHtml(t('revoke'))}</button></div>`).join('')
      : `<p class="panel-copy">${escapeHtml(t('noInvites'))}</p>`;
    $('invitations-list').querySelectorAll('[data-copy-invite]').forEach((button) => button.addEventListener('click', async () => {
      try { await navigator.clipboard.writeText(`${location.origin}/?invite=${encodeURIComponent(button.dataset.copyInvite)}`); setMessage('invite-message', t('copied')); } catch { setMessage('invite-message', button.dataset.copyInvite); }
    }));
    $('invitations-list').querySelectorAll('[data-revoke-invite]').forEach((button) => button.addEventListener('click', async () => {
      try { await request(`/api/invitations/${encodeURIComponent(button.dataset.revokeInvite)}`, { method: 'DELETE' }); setMessage('invite-message', t('inviteRevoked')); await loadInvitations(); }
      catch (error) { setMessage('invite-message', error.message); }
    }));
  } catch (error) { setMessage('invite-message', error.message); }
}

async function loadAudit() {
  if (!state.user?.permissions?.includes('settings:write')) return;
  // Primary render path: htmx fetches the server-rendered fragment. The
  // JSON fallback keeps the tab working if htmx failed to load.
  if (window.htmx) {
    window.htmx.ajax('GET', '/fragments/audit', { target: '#audit-list', swap: 'innerHTML', headers: { authorization: `Bearer ${state.token}` } });
    return;
  }
  try {
    const events = await request('/api/audit');
    $('audit-list').innerHTML = events.length
      ? events.map((event) => `<div class="audit-row"><code>${escapeHtml(event.action)}</code><span>${escapeHtml(event.actor || '—')}</span>${event.target ? `<code>${escapeHtml(event.target)}</code>` : ''}<time>${escapeHtml(new Date(event.createdAt).toLocaleString(state.locale === 'ar' ? 'ar' : 'en'))}</time></div>`).join('')
      : `<p class="panel-copy">${escapeHtml(t('activityEmpty'))}</p>`;
  } catch (error) { setMessage('app-message', error.message); }
}

// Security events: auth failures, rate-limit blocks, invalid tokens. Settings
// gate applies — these rows carry names and IPs.
async function loadSecurityEvents() {
  if (!state.user?.permissions?.includes('settings:write')) return;
  const host = $('security-list');
  if (!host) return;
  try {
    const events = await request('/api/security/events?limit=60');
    host.innerHTML = events.length
      ? events.map((event) => {
          const when = new Date(event.createdAt).toLocaleString(state.locale === 'ar' ? 'ar' : 'en');
          const who = event.name || '—';
          const where = event.ip && event.ip !== 'unknown' ? `<code>${escapeHtml(event.ip)}</code>` : '';
          return `<div class="audit-row"><code>${escapeHtml(event.kind)}</code><span>${escapeHtml(who)}</span>${where}<time>${escapeHtml(when)}</time></div>`;
        }).join('')
      : `<p class="panel-copy">${escapeHtml(t('securityEmpty'))}</p>`;
  } catch (error) { setMessage('security-message', error.message); }
}

async function loadMembers() {
  const canManage = state.user?.permissions?.includes('members:write');
  $('member-form')?.classList.toggle('hidden', !canManage);
  renderPeopleScope();
  if (!canManage) {
    // A viewer or commenter still gets to see who is here and to join another
    // workspace with a code, but not the management controls.
    $('members-list').innerHTML = `<p class="panel-copy">${escapeHtml(t('peopleReadOnly'))}</p>`;
    loadInvitations();
    return;
  }
  loadInvitations();
  try {
    const members = await request('/api/members');
    const allRoles = ['owner', 'admin', 'editor', 'commenter', 'viewer'];
    $('members-list').innerHTML = members.map((member) => {
      const selectable = [...new Set([member.role, ...allRoles])].filter((role) => role === member.role || state.grantableRoles.includes(role));
      const roleControl = member.canManage
        ? `<select class="member-role" data-member="${escapeHtml(member.id)}" aria-label="${escapeHtml(roleLabel(member.role))} — ${escapeHtml(member.name)}">${selectable.map((role) => `<option value="${role}" ${role === member.role ? 'selected' : ''}>${escapeHtml(roleLabel(role))}</option>`).join('')}</select>`
        : `<span class="member-role-static" data-member-role="${escapeHtml(member.role)}">${escapeHtml(roleLabel(member.role))}</span>`;
      const badges = `${member.role === 'owner' || member.role === 'superadmin' ? `<code class="owner-badge">${escapeHtml(t('ownerBadge'))}</code>` : ''}${member.isSelf ? `<code class="self-badge">${escapeHtml(t('memberYou'))}</code>` : ''}`;
      return `<article class="member-row"><span class="avatar">${escapeHtml(member.name.slice(0, 1).toUpperCase())}</span><span class="member-identity"><strong>${escapeHtml(member.name)}</strong><small>${member.permissions.length} ${escapeHtml(t('memberPermissions'))}</small>${badges}</span>${roleControl}${member.canManage ? `<button class="link-button remove-member" data-remove-member="${escapeHtml(member.id)}" type="button">${escapeHtml(t('removeLabel'))}</button>` : ''}</article>`;
    }).join('');
    $('members-list').querySelectorAll('.member-role').forEach((select) => select.addEventListener('change', async () => {
      try { await request(`/api/members/${encodeURIComponent(select.dataset.member)}`, { method: 'PATCH', body: JSON.stringify({ role: select.value }) }); setMessage('member-message', t('roleUpdated')); }
      catch (error) { setMessage('member-message', error.message); await loadMembers(); }
    }));
    $('members-list').querySelectorAll('[data-remove-member]').forEach((button) => button.addEventListener('click', async () => {
      if (!window.confirm(t('removeMemberConfirm'))) return;
      try { await request(`/api/members/${encodeURIComponent(button.dataset.removeMember)}`, { method: 'DELETE' }); setMessage('member-message', t('memberRemoved')); await loadMembers(); }
      catch (error) { setMessage('member-message', error.message); }
    }));
  } catch (error) { setMessage('member-message', error.message); }
}

async function loadStorageSnapshot() {
  try {
    const data = await request('/api/health/storage');
    $('storage-snapshot').innerHTML = [
      [data.notes, 'snapshotNotes'], [data.categories, 'snapshotCategories'], [data.tags, 'snapshotTags'], [data.attachments, 'snapshotAttachments'], [data.accounts, 'snapshotAccounts'],
    ].map(([value, key]) => `<span class="snapshot-item"><b>${value}</b> ${escapeHtml(t(key))}</span>`).join('');
  } catch (error) { setMessage('app-message', error.message); }
}

async function downloadExport(event) {
  event.preventDefault();
  try {
    const response = await request('/api/export');
    const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url; link.download = 'planing-export.json'; link.click();
    URL.revokeObjectURL(url);
  } catch (error) { setMessage('app-message', error.message); }
}

/* ---------- Auth / user ---------- */
function renderUser() {
  if (!state.user) return;
  $('current-user').textContent = state.user.name;
  $('current-role').textContent = roleLabel(state.user.role);
  $('user-avatar').textContent = state.user.name.slice(0, 1).toUpperCase();
}

function renderAuth() {
  const register = state.authMode === 'register';
  $('auth-title').textContent = register ? t('createAdmin') : t('signInTitle');
  $('auth-action').textContent = register ? t('createAccount') : t('signIn');
  $('switch-auth').textContent = register ? t('switchToLogin') : t('switchToRegister');
  $('password').autocomplete = register ? 'new-password' : 'current-password';
  // Once the workspace has an admin, sign-up needs an invitation code.
  const inviteField = $('invite-field');
  if (inviteField) inviteField.classList.toggle('hidden', !register || state.isFirstAdmin);
}

async function isFirstAdminPending() {
  try { const health = await (await fetch('/health')).json(); return Number(health.storage?.accounts || 0) === 0; }
  catch { return false; }
}

async function enterApp() {
  const profile = await request('/api/auth/profile');
  state.user = profile.user;
  state.canManageCategories = state.user.permissions.includes('categories:write');
  const settings = await request('/api/settings');
  state.workspace = settings.workspace;
  state.appearanceOptions = settings.appearance;
  await loadCategories();
  $('auth-panel').classList.add('hidden'); $('app-panel').classList.remove('hidden'); $('logout').classList.remove('hidden');
  renderUser(); renderCategories(); applyFontScale(); applyTheme(); applyStyleVariant(); applyAppearanceTokens(); setView('notes'); await Promise.all([loadNotes(), loadTags(), loadWorkspaces()]);
  applyWorkspaceChrome();
  $('workspace-description').textContent = state.workspace.description || t('defaultWorkspaceDescription');
}

/* ---------- Events ---------- */
$('auth-form').addEventListener('submit', async (event) => {
  event.preventDefault(); setMessage('auth-message');
  try {
    const body = await request(state.authMode === 'register' ? '/api/auth/register' : '/api/auth/login', { method: 'POST', body: JSON.stringify({ name: $('username').value.trim(), password: $('password').value, invite: $('invite-code')?.value.trim() || undefined }) });
    state.token = body.token; localStorage.setItem('planing-token', state.token); await enterApp();
  } catch (error) { setMessage('auth-message', error.message); }
});
$('switch-auth').addEventListener('click', () => { state.authMode = state.authMode === 'register' ? 'login' : 'register'; renderAuth(); });
/* ---------- Ticket events ---------- */
document.querySelectorAll('[data-ticket-status]').forEach((button) => button.addEventListener('click', () => {
  state.ticketStatusFilter = button.dataset.ticketStatus || null;
  document.querySelectorAll('[data-ticket-status]').forEach((chip) => chip.classList.toggle('active', chip === button));
  loadTickets();
}));
let ticketSearchTimer = null;
$('ticket-search').addEventListener('input', (event) => {
  clearTimeout(ticketSearchTimer);
  ticketSearchTimer = setTimeout(() => { state.ticketSearch = event.target.value.trim() || null; loadTickets(); }, 250);
});
$('ticket-new').addEventListener('click', async () => {
  state.ticketEditing = null; state.ticketCreating = true;
  if (!state.ticketFieldDefs) await loadTicketFieldDefs();
  renderTicketEditor();
});
$('ticket-field-form').addEventListener('submit', async (event) => {
  event.preventDefault(); setMessage('ticket-fields-message');
  const type = $('ticket-field-type').value;
  try {
    await request('/api/tickets/fields', { method: 'POST', body: JSON.stringify({
      label: $('ticket-field-label').value,
      type,
      options: type === 'select' ? $('ticket-field-options').value : undefined,
      required: $('ticket-field-required').checked,
    }) });
    $('ticket-field-label').value = ''; $('ticket-field-options').value = ''; $('ticket-field-required').checked = false;
    setMessage('ticket-fields-message', t('ticketFieldAdded'));
    await loadTicketFieldDefs();
    renderTicketFieldsAdmin();
  } catch (error) { setMessage('ticket-fields-message', error.message); }
});
$('locale-toggle').addEventListener('click', () => {
  // Cycle through the catalogue's locales so adding one needs no handler edit.
  const next = locales[(locales.indexOf(state.locale) + 1) % locales.length] || 'en';
  state.locale = next;
  localStorage.setItem('planing-locale', state.locale);
  applyLocale();
});
$('theme-toggle').addEventListener('click', () => {
  const resolved = resolveTheme();
  localStorage.setItem('planing-theme-override', resolved === 'dark' ? 'light' : 'dark');
  state.theme = resolved === 'dark' ? 'light' : 'dark';
  localStorage.setItem('planing-theme', state.theme);
  applyTheme();
});
$('logout').addEventListener('click', () => { localStorage.removeItem('planing-token'); location.reload(); });
document.querySelectorAll('[data-view]').forEach((button) => button.addEventListener('click', () => setView(button.dataset.view)));
document.querySelectorAll('[data-settings-tab]').forEach((button) => button.addEventListener('click', () => setSettingsTab(button.dataset.settingsTab)));
document.querySelectorAll('[data-note-view]').forEach((button) => button.addEventListener('click', async () => {
  state.noteView = button.dataset.noteView;
  document.querySelectorAll('[data-note-view]').forEach((element) => element.classList.toggle('active', element === button));
  await loadNotes();
}));
$('category-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const category = await request('/api/categories', { method: 'POST', body: JSON.stringify({ name: $('new-category').value.trim() }) });
    state.categories.push(category); state.selected = category.slug; state.tagFilter = null; $('new-category').value = '';
    renderCategories(); await loadNotes();
  } catch (error) { setMessage('app-message', error.message); }
});
$('tag-filter-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const value = $('tag-search').value.replace(/^#/, '').trim();
  state.tagFilter = value || null;
  renderCategories(); renderTags(); await loadNotes();
});
$('tag-clear').addEventListener('click', async () => { state.tagFilter = null; $('tag-search').value = ''; renderCategories(); renderTags(); await loadNotes(); });

$('outbox-retry').addEventListener('click', async () => {
  if (outboxTimer) { clearTimeout(outboxTimer); outboxTimer = null; }
  outboxAttempts = 0;
  while (outbox.length) {
    const entry = outbox.shift();
    try { await entry.send(); }
    catch (error) {
      if (error.permanent) { setMessage('app-message', t('outboxFailed')); renderOutboxBanner(); await loadNotes(); break; }
      outbox.unshift(entry);
      break;
    }
  }
  renderOutboxBanner();
  await loadNotes();
  if (outbox.length) scheduleOutboxRetry();
});

window.addEventListener('online', () => { outboxAttempts = 0; if (outbox.length) scheduleOutboxRetry(); });
window.addEventListener('offline', () => renderOutboxBanner());

let searchTimer;
$('note-search').addEventListener('input', () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(async () => { state.search = $('note-search').value.trim(); await loadNotes(); }, 300);
});

$('note-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    const note = await request('/api/notes', { method: 'POST', body: JSON.stringify({ content: $('note-content').value, category: state.selected, tags: parseTagInput($('note-tags').value) }) });
    for (const attachment of state.pending) await request(`/api/attachments/${encodeURIComponent(attachment.id)}`, { method: 'PATCH', body: JSON.stringify({ note: note.id }) });
    state.pending = []; renderPending();
    $('note-content').value = ''; $('note-tags').value = '';
    if (state.noteView !== 'all' || state.tagFilter) { state.noteView = 'all'; state.tagFilter = null; document.querySelectorAll('[data-note-view]').forEach((element) => element.classList.toggle('active', element.dataset.noteView === 'all')); }
    await Promise.all([loadNotes(), loadTags()]);
  } catch (error) { setMessage('app-message', error.message); }
});
$('attach-button').addEventListener('click', () => $('file-input').click());
$('md-import-button').addEventListener('click', () => $('md-file-input').click());
$('md-file-input').addEventListener('change', async (event) => {
  const file = event.target.files?.[0];
  event.target.value = '';
  if (!file) return;
  try {
    const raw = await file.text();
    // Drop YAML frontmatter but keep its title line when present.
    const frontmatter = raw.match(/^---\n([\s\S]*?)\n---\n?/);
    let body = frontmatter ? raw.slice(frontmatter[0].length) : raw;
    const fmTitle = frontmatter?.[1]?.match(/^title:\s*(.+)$/m)?.[1]?.replace(/^["']|["']$/g, '').trim();
    if (fmTitle && !/^#\s/m.test(body)) body = `# ${fmTitle}\n\n${body}`;
    $('note-content').value = body.trim();
    const heading = body.match(/^#\s+(.+)$/m)?.[1]?.trim();
    if (heading && !$('note-tags').value) {
      const slug = heading.toLowerCase().replace(/[^a-z0-9\u0600-\u06ff]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 32);
      if (slug) $('note-tags').value = `#${slug}`;
    }
    setMessage('app-message', t('mdFileLoaded').replace('{name}', file.name));
  } catch (error) { setMessage('app-message', error.message); }
});
$('file-input').addEventListener('change', async (event) => {
  try { await uploadFiles([...event.target.files]); }
  catch (error) { setMessage('app-message', error.message); }
  event.target.value = '';
});

$('settings-form').addEventListener('submit', async (event) => {
  event.preventDefault(); setMessage('settings-message');
  try {
    const body = await request('/api/settings', { method: 'PATCH', body: JSON.stringify({ name: $('workspace-name').value.trim(), description: $('workspace-description-input').value.trim(), defaultCategory: $('default-category').value }) });
    state.workspace = body.workspace;
    $('workspace-kicker').textContent = body.workspace.name.toUpperCase().slice(0, 24);
    $('workspace-description').textContent = body.workspace.description || t('defaultWorkspaceDescription');
    setMessage('settings-message', t('settingsSaved'));
  } catch (error) { setMessage('settings-message', error.message); }
});
$('ai-form').addEventListener('submit', async (event) => {
  event.preventDefault(); setMessage('ai-message');
  try { await request('/api/settings', { method: 'PATCH', body: JSON.stringify({ aiContext: $('ai-context').value.trim() }) }); setMessage('ai-message', t('aiSaved')); }
  catch (error) { setMessage('ai-message', error.message); }
});
$('member-form').addEventListener('submit', async (event) => {
  event.preventDefault(); setMessage('member-message');
  try {
    await request('/api/members', { method: 'POST', body: JSON.stringify({ name: $('member-name').value.trim(), password: $('member-password').value, role: $('member-role').value }) });
    event.target.reset(); setMessage('member-message', t('memberAdded')); await loadMembers();
  } catch (error) { setMessage('member-message', error.message); }
});
$('export-link').addEventListener('click', downloadExport);

// Phase 2 closeout: retention controls. The form saves the recycle-bin
// window; "Purge now" runs the same sweep the hourly timer runs, so the
// effect is observable without waiting.
function renderRetention() {
  const field = $('retention-days');
  if (!field) return;
  field.value = state.workspace?.retentionDays != null ? String(state.workspace.retentionDays) : '';
}

$('retention-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  setMessage('retention-message');
  try {
    const raw = $('retention-days').value.trim();
    const retentionDays = raw === '' ? null : Number(raw);
    const body = { retentionDays };
    await request('/api/settings', { method: 'PATCH', body: JSON.stringify(body) });
    state.workspace.retentionDays = retentionDays;
    setMessage('retention-message', retentionDays == null ? t('retentionSavedForever') : t('retentionSaved').replace('{days}', String(retentionDays)));
  } catch (error) { setMessage('retention-message', error.message); }
});
$('retention-purge').addEventListener('click', async () => {
  setMessage('retention-message');
  try {
    const result = await request('/api/retention/purge', { method: 'POST', body: '{}' });
    setMessage('retention-message', t('retentionPurged').replace('{notes}', String(result.purgedNotes || 0)));
    await Promise.all([loadNotes(), loadTags()]);
  } catch (error) { setMessage('retention-message', error.message); }
});


$('samples-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  setMessage('samples-message');
  try {
    const result = await request('/api/samples', { method: 'POST', body: '{}' });
    const { notes = 0, updated = 0, skipped = 0 } = result.imported || {};
    // Curated samples are keyed by fixed ids, so a second run refreshes their
    // content (fresh wiki links included) rather than duplicating anything.
    const message = notes > 0
      ? t('samplesLoaded').replace('{notes}', notes).replace('{skipped}', skipped)
      : (updated > 0 ? t('samplesRefreshed').replace('{updated}', updated) : t('samplesAlready'));
    setMessage('samples-message', message);
    state.categories = await request('/api/categories');
    renderCategories();
    await Promise.all([loadNotes(), loadTags()]);
    if (typeof refreshStorageStatus === 'function') await refreshStorageStatus();
    document.querySelector('[data-view="notes"]')?.click();
  } catch (error) { setMessage('samples-message', error.message); }
});

$('invite-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  setMessage('invite-message');
  try {
    const invite = await request('/api/invitations', { method: 'POST', body: JSON.stringify({ role: $('invite-role').value }) });
    setMessage('invite-message', `${t('inviteCreated')} ${invite.code}`);
    await loadInvitations();
  } catch (error) { setMessage('invite-message', error.message); }
});

// Joining with a code adds a membership to the account that redeems it and then
// switches to the workspace it belongs to, so the sidebar reflects the change.
$('join-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const input = $('join-code');
  const code = input.value.trim();
  if (!code) { setMessage('join-message', t('joinMissingCode')); return; }
  setMessage('join-message');
  try {
    const result = await request('/api/invitations/redeem', { method: 'POST', body: JSON.stringify({ code }) });
    input.value = '';
    setMessage('join-message', t('joinSuccess').replace('{name}', result.workspace?.name || code));
    state.selected = 'notes'; state.search = ''; state.tagFilter = null; state.editing = null; state.pending = [];
    await refreshWorkspaceData();
    await loadWorkspaceAdmin();
    await loadMembers();
  } catch (error) { setMessage('join-message', error.message); }
});

// A workspace bundle is the portable unit: it exports the workspace this session
// is in, and importing one always lands as a new workspace, so a move never
// overwrites what is already on the target deployment.
$('bundle-export').addEventListener('click', async () => {
  try {
    const bundle = await request(`/api/workspaces/${encodeURIComponent(state.activeWorkspace || 'default')}/bundle`);
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${(bundle.workspace.name || 'workspace').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'workspace'}-bundle.json`;
    link.click();
    URL.revokeObjectURL(url);
    setMessage('bundle-message', t('bundleExported').replace('{notes}', bundle.notes.length));
  } catch (error) { setMessage('bundle-message', error.message); }
});

$('bundle-import').addEventListener('click', async () => {
  const file = $('bundle-file').files?.[0];
  if (!file) { setMessage('bundle-message', t('bundleNoFile')); return; }
  setMessage('bundle-message');
  try {
    const payload = JSON.parse(await file.text());
    const result = await request('/api/workspaces/import', { method: 'POST', body: JSON.stringify(payload) });
    setMessage('bundle-message', t('bundleImported').replace('{name}', result.workspace.name).replace('{notes}', result.imported.notes));
    $('bundle-file').value = '';
    state.selected = 'notes'; state.search = ''; state.tagFilter = null; state.editing = null; state.pending = [];
    await refreshWorkspaceData();
    await loadWorkspaceAdmin();
  } catch (error) { setMessage('bundle-message', error.message); }
});

$('import-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  setMessage('import-message');
  const file = $('import-file').files?.[0];
  if (!file) { setMessage('import-message', t('importNoFile')); return; }
  try {
    const payload = JSON.parse(await file.text());
    const result = await request('/api/import', { method: 'POST', body: JSON.stringify(payload) });
    setMessage('import-message', t('importSuccess').replace('{notes}', result.imported.notes).replace('{categories}', result.imported.categories));
    state.categories = await request('/api/categories');
    renderCategories();
    await loadNotes();
    if (typeof refreshStorageStatus === 'function') await refreshStorageStatus();
  } catch (error) {
    setMessage('import-message', error.message);
  }
});

// Markdown file import: choose or drop .md files and they become notes.
// Identical files are skipped server-side, so re-importing a folder is safe.
async function sendMarkdownFiles(files) {
  setMessage('markdown-import-message');
  try {
    const result = await request('/api/notes/import-markdown', { method: 'POST', body: JSON.stringify({ files }) });
    setMessage('markdown-import-message', t('markdownImportSuccess').replace('{notes}', result.imported.notes).replace('{skipped}', result.imported.skipped));
    await loadNotes();
    if (typeof refreshStorageStatus === 'function') await refreshStorageStatus();
  } catch (error) { setMessage('markdown-import-message', error.message); }
}

const markdownImportForm = $('markdown-import-form');
// Snapshot and clear the picker *before* awaiting the upload, otherwise a
// second selection made while the first import is still in flight is wiped by
// the late reset and its files are silently dropped.
markdownImportForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const selected = [...$('markdown-files').files];
  event.target.reset();
  sendPickedMarkdown(selected);
});
markdownImportForm.addEventListener('dragover', (event) => { event.preventDefault(); markdownImportForm.classList.add('dragging'); });
markdownImportForm.addEventListener('dragleave', () => markdownImportForm.classList.remove('dragging'));
markdownImportForm.addEventListener('drop', (event) => {
  event.preventDefault();
  markdownImportForm.classList.remove('dragging');
  sendPickedMarkdown([...(event.dataTransfer?.files || [])]);
});

// Read the picked File objects immediately (they stay valid after the input is
// reset) and hand the plain payload to the importer.
async function sendPickedMarkdown(fileList) {
  const picked = [...(fileList || [])];
  if (!picked.length) { setMessage('markdown-import-message', t('markdownImportNoFile')); return; }
  const files = await Promise.all(picked
    .filter((file) => /\.(md|markdown|mdx|txt)$/i.test(file.name))
    .map(async (file) => ({ name: file.name, text: await file.text() })));
  if (!files.length) { setMessage('markdown-import-message', t('markdownImportNoFile')); return; }
  await sendMarkdownFiles(files);
}

/* ---------- Markdown editor: shared by the composer and inline note editing ---------- */

const mdTools = [
  { kind: 'bold', glyph: '<b>B</b>', title: 'tooltipBold' },
  { kind: 'italic', glyph: '<i>I</i>', title: 'tooltipItalic' },
  { kind: 'strike', glyph: '<s>S</s>', title: 'tooltipStrike' },
  { kind: 'highlight', glyph: '▨', title: 'tooltipHighlight' },
  { separator: true },
  { kind: 'heading', glyph: 'H', title: 'tooltipHeading' },
  { kind: 'quote', glyph: '❝', title: 'tooltipQuote' },
  { kind: 'code', glyph: '&lt;/&gt;', title: 'tooltipCode' },
  { kind: 'inline-code', glyph: '`', title: 'tooltipInlineCode' },
  { separator: true },
  { kind: 'list', glyph: '•', title: 'tooltipList' },
  { kind: 'ordered', glyph: '1.', title: 'tooltipOrdered' },
  { kind: 'task', glyph: '☑', title: 'tooltipTask' },
  { separator: true },
  { kind: 'link', glyph: '↗', title: 'tooltipLink' },
  { kind: 'wikilink', glyph: '[[', title: 'tooltipWikilink' },
  { kind: 'table', glyph: '▦', title: 'tooltipTable' },
  { kind: 'divider', glyph: '—', title: 'tooltipDivider' },
];

function editorToolbarMarkup() {
  return mdTools.map((tool) => (tool.separator
    ? '<span class="editor-toolbar-sep" aria-hidden="true"></span>'
    : `<button type="button" data-md-insert="${tool.kind}" title="${escapeHtml(t(tool.title))}">${tool.glyph}</button>`)).join('');
}

// Selection-aware markdown insertion. Wrapping tools keep the selection so the
// next keystroke replaces the placeholder; line tools rewrite every selected line.
function applyMarkdownTool(area, kind) {
  const value = area.value;
  const start = area.selectionStart ?? value.length;
  const end = area.selectionEnd ?? value.length;
  const selected = value.slice(start, end);
  let next = value;
  let selectionStart = start;
  let selectionEnd = end;

  const wrap = (before, after, placeholder) => {
    const body = selected || placeholder;
    next = `${value.slice(0, start)}${before}${body}${after}${value.slice(end)}`;
    selectionStart = start + before.length;
    selectionEnd = selectionStart + body.length;
  };
  const prefixLines = (makePrefix) => {
    const lineStart = value.lastIndexOf('\n', start - 1) + 1;
    const block = value.slice(lineStart, end);
    const lines = (block || '').split('\n');
    const prefixed = lines.map((line, index) => makePrefix(line, index)).join('\n');
    next = `${value.slice(0, lineStart)}${prefixed}${value.slice(end)}`;
    selectionStart = lineStart;
    selectionEnd = lineStart + prefixed.length;
  };
  const insertBlock = (text) => {
    const needsLeadingBreak = start > 0 && !value.slice(0, start).endsWith('\n\n');
    next = `${value.slice(0, start)}${needsLeadingBreak ? '\n\n' : ''}${text}${value.slice(end)}`;
    selectionStart = selectionEnd = start + (needsLeadingBreak ? 2 : 0) + text.length;
  };

  switch (kind) {
    case 'bold': wrap('**', '**', 'bold text'); break;
    case 'italic': wrap('*', '*', 'italic text'); break;
    case 'strike': wrap('~~', '~~', 'struck text'); break;
    case 'highlight': wrap('==', '==', 'highlighted'); break;
    case 'inline-code': wrap('`', '`', 'code'); break;
    case 'link': wrap('[', '](https://)', selected || 'link label'); break;
    case 'wikilink': wrap('[[', ']]', selected || 'Note title'); break;
    case 'code': insertBlock(`\`\`\`\n${selected || '# code'}\n\`\`\`\n`); break;
    case 'heading': prefixLines((line, index) => `${'#'.repeat(Math.min(2 + index, 6))} ${line.replace(/^#+\s*/, '')}`); break;
    case 'quote': prefixLines((line) => `> ${line}`); break;
    case 'list': prefixLines((line) => `- ${line.replace(/^[-*]\s+/, '')}`); break;
    case 'ordered': prefixLines((line, index) => `${index + 1}. ${line.replace(/^\d+\.\s+/, '')}`); break;
    case 'task': prefixLines((line) => `- [ ] ${line.replace(/^[-*]\s+(\[[ xX]\]\s+)?/, '')}`); break;
    case 'table': insertBlock('| Column | Value |\n| :----- | ----: |\n| item | 1 |\n'); break;
    case 'divider': insertBlock('\n---\n'); break;
    default: return;
  }
  area.value = next;
  area.setSelectionRange(selectionStart, selectionEnd);
  area.dispatchEvent(new Event('input', { bubbles: true }));
  area.focus();
}

// One delegated listener covers the composer and every inline editor, including
// cards re-rendered long after this runs.
function bindMarkdownToolbars(root = document) {
  root.addEventListener('click', (event) => {
    const button = event.target.closest?.('[data-md-insert]');
    if (!button) return;
    const surface = button.closest('form, article')?.querySelector('textarea');
    if (!surface) return;
    event.preventDefault();
    applyMarkdownTool(surface, button.dataset.mdInsert);
  });
}

function editorMetrics(text) {
  const words = String(text || '').trim().split(/\s+/).filter(Boolean).length;
  const links = (String(text || '').match(/\[\[[^\]]+\]\]/g) || []).length;
  const minutes = Math.max(1, Math.round(words / 200));
  return `${words} ${t('metricsWords')} · ${t('metricsRead').replace('{minutes}', minutes)}${links ? ` · ${links} ${t('metricsLinks')}` : ''}`;
}

function autoGrow(area) {
  area.style.height = 'auto';
  area.style.height = `${Math.min(Math.max(area.scrollHeight, 160), 900)}px`;
}

// Live preview + metrics + shortcuts for one editor surface.
function bindEditorSurface(area, { preview, metrics, expanded = false } = {}) {
  const paint = () => {
    if (preview && !preview.classList.contains('hidden')) preview.innerHTML = renderMarkdown(area.value);
    const target = metrics || area.closest('form, article')?.querySelector('[data-editor-metrics], #composer-metrics');
    if (target) target.textContent = editorMetrics(area.value);
    autoGrow(area);
  };
  area.addEventListener('input', paint);
  area.addEventListener('keydown', (event) => {
    const accel = event.metaKey || event.ctrlKey;
    if (!accel) return;
    const key = event.key.toLowerCase();
    const map = { b: 'bold', i: 'italic', k: 'link', e: 'code' };
    if (map[key]) { event.preventDefault(); applyMarkdownTool(area, map[key]); return; }
    if (event.key === 'Enter') {
      event.preventDefault();
      area.closest('form')?.requestSubmit();
      area.closest('article')?.querySelector('[data-note-action="save-edit"]')?.click();
    }
  });
  paint();
  if (expanded) autoGrow(area);
}

const composerPreview = $('composer-preview');
const composerTextarea = $('note-content');
bindEditorSurface(composerTextarea, { preview: composerPreview, metrics: $('composer-metrics'), expanded: true });
$('composer-preview-toggle').addEventListener('click', (event) => {
  const active = composerPreview.classList.toggle('hidden');
  event.currentTarget.setAttribute('aria-pressed', String(!active));
  composerTextarea.classList.toggle('hidden', !active);
  if (!active) composerPreview.innerHTML = renderMarkdown(composerTextarea.value);
});
$('composer-expand-toggle').addEventListener('click', (event) => {
  const wide = $('composer').classList.toggle('is-wide');
  event.currentTarget.setAttribute('aria-pressed', String(wide));
  localStorage.setItem('planing-composer-wide', wide ? '1' : '0');
  autoGrow(composerTextarea);
});
if (localStorage.getItem('planing-composer-wide') === '1') $('composer').classList.add('is-wide');
bindMarkdownToolbars();

// Inline editors are re-rendered constantly, so their per-card controls are
// bound whenever the note list paints.
function bindInlineEditors() {
  $('notes-list').querySelectorAll('.note.editing').forEach((card) => {
    const area = card.querySelector('.edit-content');
    const preview = card.querySelector('.editor-preview');
    if (area && !area.dataset.bound) {
      area.dataset.bound = '1';
      bindEditorSurface(area, { preview, metrics: card.querySelector('[data-editor-metrics]'), expanded: true });
    }
    card.querySelector('[data-edit-preview]')?.addEventListener('click', (event) => {
      const hidden = preview.classList.toggle('hidden');
      event.currentTarget.setAttribute('aria-pressed', String(!hidden));
      area.classList.toggle('hidden', !hidden);
      if (!hidden) preview.innerHTML = renderMarkdown(area.value);
    });
    card.querySelector('[data-edit-expand]')?.addEventListener('click', (event) => {
      const wide = card.querySelector('.editor-surface').classList.toggle('is-wide');
      event.currentTarget.setAttribute('aria-pressed', String(wide));
      autoGrow(area);
    });
  });
}

/* ---------- Study: spaced-recall review queue ---------- */

function renderStudyStats(stats) {
  state.studyStats = stats;
  $('study-counts').innerHTML = `
    <span class="study-stat"><strong>${Number(stats.due || 0)}</strong> ${escapeHtml(t('studyDueCount').replace('{count}', '').trim())}</span>
    <span class="study-stat"><strong>${Number(stats.total || 0)}</strong> ${escapeHtml(t('studyTotalCount').replace('{count}', '').trim())}</span>`;
  const boxes = stats.boxes || [];
  $('study-boxes').innerHTML = boxes.length
    ? boxes.map((entry) => `<span class="study-box" title="${escapeHtml(t('studyBox'))}">${escapeHtml(t('studyBox'))} ${entry.box}<strong>${entry.count}</strong></span>`).join('')
    : '';
}

async function loadStudy() {
  setMessage('study-message');
  try {
    const [due, stats, analytics] = await Promise.all([
      request('/api/study/due?limit=25'),
      request('/api/study/stats'),
      request('/api/study/analytics').catch(() => null),
    ]);
    state.studyQueue = due.items || [];
    state.studyIndex = 0;
    renderStudyStats(stats);
    renderStudyQueue();
    if (analytics) renderStudyAnalytics(analytics);
  } catch (error) { setMessage('study-message', t('studyLoadFailed')); }
}

// Retention is shown only where there is something to measure: a tag with no
// reviews keeps a dash rather than a misleading 100%.
function renderStudyAnalytics(data) {
  const totals = data.totals || {};
  $('study-analytics-totals').innerHTML = [
    ['studyAnalyticsRetention', totals.retention === null || totals.retention === undefined ? '—' : `${totals.retention}%`],
    ['studyAnalyticsReviews', Number(totals.reviews || 0)],
    ['studyAnalyticsLapses', Number(totals.lapses || 0)],
    ['studyAnalyticsCards', `${Number(totals.reviewedCards || 0)}/${Number(totals.cards || 0)}`],
    ['studyAnalyticsAverageBox', Number(totals.averageBox || 0)],
    ['studyAnalyticsDueNow', Number(totals.dueNow || 0)],
  ].map(([key, value]) => `<span class="study-stat" data-study-total="${key}"><strong>${escapeHtml(String(value))}</strong> ${escapeHtml(t(key))}</span>`).join('');
  $('study-analytics-empty').classList.toggle('hidden', Number(totals.reviews || 0) > 0);

  const tags = (data.tags || []).filter((entry) => entry.tag);
  $('study-analytics-tags').innerHTML = tags.length ? tags.map((entry) => {
    const retention = entry.retention === null ? '—' : `${entry.retention}%`;
    const width = entry.retention === null ? 0 : Math.max(2, Math.min(100, entry.retention));
    return `<div class="study-tag-row" data-study-tag="${escapeHtml(entry.tag)}">
      <span class="study-tag-name">#${escapeHtml(entry.tag)}</span>
      <span class="study-tag-bar" role="img" aria-label="${escapeHtml(retention)}"><span style="width: ${width}%"></span></span>
      <span class="study-tag-value">${escapeHtml(retention)}</span>
      <small>${escapeHtml(t('studyAnalyticsTagMeta').replace('{cards}', entry.cards).replace('{reviews}', entry.reviews).replace('{lapses}', entry.lapses))}</small>
    </div>`;
  }).join('') : `<p class="link-empty">${escapeHtml(t('studyAnalyticsNoTags'))}</p>`;

  const hotspots = data.hotspots || [];
  $('study-analytics-hotspots').innerHTML = hotspots.length ? hotspots.map((item) => `
    <button class="study-hotspot" type="button" data-study-hotspot="${escapeHtml(item.id)}">
      <span class="study-hotspot-question">${escapeHtml(item.question)}</span>
      <span class="study-hotspot-meta">${escapeHtml(t('studyAnalyticsHotspotMeta').replace('{lapses}', item.lapses).replace('{reviews}', item.reviewCount).replace('{box}', item.box))}</span>
    </button>`).join('') : `<p class="link-empty">${escapeHtml(t('studyAnalyticsNoHotspots'))}</p>`;
  $('study-analytics-hotspots').querySelectorAll('[data-study-hotspot]').forEach((button) => button.addEventListener('click', () => {
    $('study-analytics-tags').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }));

  const forecast = data.forecast || [];
  const peak = Math.max(1, ...forecast.map((day) => day.count));
  $('study-analytics-forecast').innerHTML = forecast.map((day) => `
    <div class="study-day" data-study-forecast="${escapeHtml(day.date)}">
      <span class="study-day-bar"><span style="height: ${Math.round((day.count / peak) * 100)}%"></span></span>
      <strong>${day.count}</strong>
      <small>${escapeHtml(day.offset === 0 ? t('studyAnalyticsToday') : day.date.slice(5))}</small>
    </div>`).join('');

  const activity = data.activity || [];
  const activityPeak = Math.max(1, ...activity.map((day) => day.reviews));
  $('study-analytics-activity').innerHTML = activity.map((day) => `
    <span class="study-activity-day" data-study-activity="${escapeHtml(day.date)}" title="${escapeHtml(day.date)} · ${day.reviews}" style="--level: ${Math.round((day.reviews / activityPeak) * 100)}%"></span>`).join('');
}

function renderStudyQueue() {
  const queue = state.studyQueue || [];
  const card = queue[state.studyIndex];
  const host = $('study-cards');
  $('study-empty').classList.toggle('hidden', Boolean(card));
  if (!card) {
    host.innerHTML = queue.length ? `<div class="panel study-empty"><p class="panel-copy">${escapeHtml(t('studyEmpty'))}</p></div>` : '';
    return;
  }
  host.innerHTML = `<article class="panel study-card" data-study-card="${escapeHtml(card.id)}">
    <div class="study-card-head"><span class="eyebrow">${escapeHtml(t('studyQuestion'))}</span><span class="study-progress">${state.studyIndex + 1} / ${queue.length}</span></div>
    <h3 class="study-question">${escapeHtml(card.question)}</h3>
    ${card.noteTitle ? `<p class="study-source">${escapeHtml(t('studyFrom'))} <button class="link-button" data-study-note="${escapeHtml(card.noteTitle)}" type="button">${escapeHtml(card.noteTitle)}</button></p>` : ''}
    <div class="study-answer hidden"><span class="eyebrow">${escapeHtml(t('studyAnswer'))}</span><div class="markdown-body">${renderMarkdown(card.answer)}</div></div>
    <div class="study-actions">
      <button class="button ghost" data-study-reveal type="button">${escapeHtml(t('studyShowAnswer'))}</button>
      <div class="study-grades hidden">${['again', 'hard', 'good', 'easy'].map((grade) => `<button class="link-button" data-study-grade="${grade}" type="button">${escapeHtml(t(`studyGrade${grade[0].toUpperCase()}${grade.slice(1)}`))}</button>`).join('')}</div>
    </div>
    <p class="study-meta">${escapeHtml(t('studyBox'))} ${Number(card.box || 0)} · ${Number(card.reviewCount || 0)}×</p>
  </article>`;
  bindStudyCard();
}

function bindStudyCard() {
  const card = $('study-cards').querySelector('.study-card');
  if (!card) return;
  card.querySelector('[data-study-reveal]')?.addEventListener('click', (event) => {
    card.querySelector('.study-answer').classList.remove('hidden');
    card.querySelector('.study-grades').classList.remove('hidden');
    event.currentTarget.classList.add('hidden');
  });
  card.querySelector('[data-study-note]')?.addEventListener('click', async (event) => {
    state.noteView = 'all'; state.tagFilter = null; state.search = event.currentTarget.dataset.studyNote;
    $('note-search').value = state.search;
    setView('notes');
    await loadNotes();
  });
  card.querySelectorAll('[data-study-grade]').forEach((button) => button.addEventListener('click', async () => {
    button.disabled = true;
    try {
      const result = await request(`/api/study/items/${encodeURIComponent(card.dataset.studyCard)}/review`, { method: 'POST', body: JSON.stringify({ grade: button.dataset.studyGrade }) });
      $('study-counts').innerHTML = `<span class="study-stat"><strong>${Number(result.due || 0)}</strong> ${escapeHtml(t('studyDueCount').replace('{count}', '').trim())}</span><span class="study-stat"><strong>${Number(result.total || 0)}</strong> ${escapeHtml(t('studyTotalCount').replace('{count}', '').trim())}</span>`;
      state.studyIndex += 1;
      renderStudyQueue();
      // The grade just moved a card, so the retention picture changed too.
      request('/api/study/analytics').then(renderStudyAnalytics).catch(() => {});
    } catch (error) {
      button.disabled = false;
      setMessage('study-message', error.message);
    }
  }));
}

$('study-refresh').addEventListener('click', loadStudy);

/* ---------- Graph: force-directed map of notes and wiki links ---------- */

// Physics configuration. Values follow Anytype's production force parameters
// (charge -250, link distance 100, alpha decay 0.05, alphaMin 0.01) scaled to
// the 1000x620 viewport. One simulation per workspace load; positions persist
// across filter/timeline re-renders so nodes never jump.
const graphForceConfig = { charge: 250, linkDistance: 100, alphaDecay: 0.05, alphaMin: 0.01, collide: 16, center: 0.05, maxTicks: 300 };
const graphView = { width: 1000, height: 620 };
// Main-thread simulation state (kept even when a worker is available, as the
// synchronous fallback and the source of truth for the last rendered frame).
let graphSim = null;
let graphRafId = 0;
let graphWorker = null;
let graphWorkerReady = false;

// ---- worker source: d3-style force integration on a Float32Array. Built as a
// Blob URL at runtime so the runtime stays a dependency-free static bundle.
function graphWorkerSource() {
  return `
let nodes = null, links = null, alpha = 1, cfg = null, running = false;
const idx = new Map();
function initialize(msg) {
  cfg = msg.cfg;
  nodes = msg.nodes.map((n, i) => { idx.set(n.id, i); return { id: n.id, x: n.x, y: n.y, vx: 0, vy: 0, degree: n.degree || 0 }; });
  links = msg.edges.map(e => ({ s: idx.get(e.source), t: e.target != null ? idx.get(e.target) : -1 }))
    .filter(l => l.s != null && l.t != null && l.t >= 0);
  alpha = 1; running = true;
}
function step() {
  // repulsion (O(n^2), fine at the 500-node cap) — charge is negative
  for (let i = 0; i < nodes.length; i++) {
    const a = nodes[i];
    for (let j = i + 1; j < nodes.length; j++) {
      const b = nodes[j];
      let dx = a.x - b.x, dy = a.y - b.y;
      let d2 = dx * dx + dy * dy;
      if (d2 < 1) { d2 = 1; dx = (Math.random() - .5); dy = (Math.random() - .5); }
      const f = cfg.charge / d2;
      const d = Math.sqrt(d2);
      const fx = dx / d * f, fy = dy / d * f;
      a.vx += fx / Math.max(a.degree, 1); a.vy += fy / Math.max(a.degree, 1);
      b.vx -= fx / Math.max(b.degree, 1); b.vy -= fy / Math.max(b.degree, 1);
    }
  }
  // springs
  for (const l of links) {
    const a = nodes[l.s], b = nodes[l.t];
    let dx = b.x - a.x, dy = b.y - a.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const f = (d - cfg.linkDistance) / d * 0.5 * Math.min(alpha * 2, 1);
    a.vx += dx * f; a.vy += dy * f;
    b.vx -= dx * f; b.vy -= dy * f;
  }
  // collision (soft)
  for (let i = 0; i < nodes.length; i++) {
    const a = nodes[i];
    for (let j = i + 1; j < nodes.length; j++) {
      const b = nodes[j];
      const dx = a.x - b.x, dy = a.y - b.y;
      const d2 = dx * dx + dy * dy;
      if (d2 < cfg.collide * cfg.collide && d2 > 0) {
        const d = Math.sqrt(d2), push = (cfg.collide - d) / d * 0.25;
        a.x += dx * push; a.y += dy * push; b.x -= dx * push; b.y -= dy * push;
      }
    }
  }
  // centering + integrate
  const cx = ${'${'}cfg.width / 2${'}'} * 0 + ${'${'}cfg.width / 2${'}'};
  for (const n of nodes) {
    n.vx += (cfg.width / 2 - n.x) * cfg.center;
    n.vy += (cfg.height / 2 - n.y) * cfg.center;
    n.vx *= 0.6; n.vy *= 0.6;
    n.x += Math.max(-30, Math.min(30, n.vx));
    n.y += Math.max(-30, Math.min(30, n.vy));
  }
  alpha += (0 - alpha) * cfg.alphaDecay * 8;
  if (alpha < cfg.alphaMin) running = false;
}
self.onmessage = (e) => {
  const msg = e.data;
  if (msg.type === 'update') { initialize(msg); let ticks = 0; while (running && ticks < cfg.maxTicks) { step(); ticks++; }
    const out = new Float32Array(nodes.length * 2);
    nodes.forEach((n, i) => { out[i * 2] = n.x; out[i * 2 + 1] = n.y; });
    self.postMessage({ type: 'positions', ids: msg.nodes.map(n => n.id), positions: out }, [out.buffer]); }
  else if (msg.type === 'step') { running = true; let ticks = 0; while (running && ticks < 30) { step(); ticks++; }
    const out = new Float32Array(nodes.length * 2);
    nodes.forEach((n, i) => { out[i * 2] = n.x; out[i * 2 + 1] = n.y; });
    self.postMessage({ type: 'positions', ids: nodes.map(n => n.id), positions: out }, [out.buffer]); }
};
`;
}

function ensureGraphWorker() {
  if (graphWorker || graphWorkerReady) return graphWorker;
  try {
    const blob = new Blob([graphWorkerSource()], { type: 'text/javascript' });
    graphWorker = new Worker(URL.createObjectURL(blob));
    graphWorker.onmessage = (event) => {
      if (event.data.type === 'positions') applyGraphPositions(event.data.ids, event.data.positions);
    };
    graphWorker.onerror = () => { graphWorker = null; };
  } catch { graphWorker = null; }
  return graphWorker;
}

// ---- simulation state on the main thread
function buildGraphSim(nodes, edges) {
  const sim = {
    ids: nodes.map((node) => node.id),
    index: new Map(nodes.map((node, i) => [node.id, i])),
    x: new Float32Array(nodes.length),
    y: new Float32Array(nodes.length),
    vx: new Float32Array(nodes.length),
    vy: new Float32Array(nodes.length),
    degree: nodes.map((node) => Math.max(node.incoming + node.outgoing, 1)),
    links: [],
  };
  // Seed positions on the ring so first paint is already orderly.
  const ordered = [...nodes].sort((a, b) => String(a.lane).localeCompare(String(b.lane)) || String(a.title).localeCompare(String(b.title)));
  const radius = Math.min(graphView.width, graphView.height) / 2 - 80;
  ordered.forEach((node, i) => {
    const angle = (i / Math.max(ordered.length, 1)) * Math.PI * 2 - Math.PI / 2;
    const j = sim.index.get(node.id);
    sim.x[j] = graphView.width / 2 + Math.cos(angle) * radius;
    sim.y[j] = graphView.height / 2 + Math.sin(angle) * radius;
  });
  for (const edge of edges) {
    const s = sim.index.get(edge.source);
    const t = edge.target ? sim.index.get(edge.target) : -1;
    if (s != null && t != null && t >= 0) sim.links.push([s, t]);
  }
  return sim;
}

function graphSimStep(sim) {
  const cfg = graphForceConfig;
  let alpha = sim.alpha ?? 1;
  // repulsion
  for (let i = 0; i < sim.ids.length; i++) {
    for (let j = i + 1; j < sim.ids.length; j++) {
      let dx = sim.x[i] - sim.x[j], dy = sim.y[i] - sim.y[j];
      let d2 = dx * dx + dy * dy;
      if (d2 < 1) { d2 = 1; dx = Math.random() - 0.5; dy = Math.random() - 0.5; }
      const d = Math.sqrt(d2);
      const f = cfg.charge / d2;
      const fx = dx / d * f, fy = dy / d * f;
      sim.vx[i] += fx / sim.degree[i]; sim.vy[i] += fy / sim.degree[i];
      sim.vx[j] -= fx / sim.degree[j]; sim.vy[j] -= fy / sim.degree[j];
    }
  }
  // springs
  for (const [s, t] of sim.links) {
    const dx = sim.x[t] - sim.x[s], dy = sim.y[t] - sim.y[s];
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const f = (d - cfg.linkDistance) / d * 0.5 * Math.min(alpha * 2, 1);
    sim.vx[s] += dx * f; sim.vy[s] += dy * f;
    sim.vx[t] -= dx * f; sim.vy[t] -= dy * f;
  }
  // Collision resolution, mirroring the worker path. Without it the main-thread
  // fallback and the reduced-motion settle can park two nodes on top of each
  // other: repulsion falls off as charge/d² while the centering pull keeps
  // growing, so a pair reaches equilibrium well inside the collision radius
  // (a settled pair was measured 4.5px apart). Applied positionally, as a
  // separation pass, not as another velocity term.
  for (let i = 0; i < sim.ids.length; i++) {
    for (let j = i + 1; j < sim.ids.length; j++) {
      const dx = sim.x[j] - sim.x[i], dy = sim.y[j] - sim.y[i];
      const d2 = dx * dx + dy * dy;
      if (d2 < cfg.collide * cfg.collide && d2 > 0) {
        const d = Math.sqrt(d2), push = (cfg.collide - d) / d * 0.5;
        sim.x[i] -= dx * push; sim.y[i] -= dy * push;
        sim.x[j] += dx * push; sim.y[j] += dy * push;
      }
    }
  }
  // centering + integrate with velocity decay
  for (let i = 0; i < sim.ids.length; i++) {
    sim.vx[i] += (graphView.width / 2 - sim.x[i]) * cfg.center;
    sim.vy[i] += (graphView.height / 2 - sim.y[i]) * cfg.center;
    sim.vx[i] *= 0.6; sim.vy[i] *= 0.6;
    sim.x[i] += Math.max(-30, Math.min(30, sim.vx[i]));
    sim.y[i] += Math.max(-30, Math.min(30, sim.vy[i]));
  }
  alpha += (0 - alpha) * cfg.alphaDecay * 8;
  sim.alpha = alpha;
  return alpha >= cfg.alphaMin;
}

function animateGraph() {
  const svg = $('graph-canvas')?.querySelector('svg');
  if (!svg || !graphSim) return;
  const active = graphSimStep(graphSim);
  patchGraphPositions();
  if (active) graphRafId = requestAnimationFrame(animateGraph);
}

function patchGraphPositions() {
  const svg = $('graph-canvas')?.querySelector('svg');
  if (!svg || !graphSim) return;
  svg.querySelectorAll('.graph-node').forEach((element) => {
    const i = graphSim.index.get(element.dataset.graphNode);
    if (i == null) return;
    const circle = element.querySelector('circle');
    const text = element.querySelector('text');
    const r = Number(circle.getAttribute('r')) || 7;
    circle.setAttribute('cx', graphSim.x[i].toFixed(1));
    circle.setAttribute('cy', graphSim.y[i].toFixed(1));
    if (text) {
      text.setAttribute('x', graphSim.x[i].toFixed(1));
      text.setAttribute('y', (graphSim.y[i] + r + 13).toFixed(1));
    }
  });
  svg.querySelectorAll('.graph-edge').forEach((edge) => {
    const s = graphSim.index.get(edge.dataset.from);
    const t = edge.dataset.to ? graphSim.index.get(edge.dataset.to) : -1;
    if (s == null) return;
    edge.setAttribute('x1', graphSim.x[s].toFixed(1));
    edge.setAttribute('y1', graphSim.y[s].toFixed(1));
    const endX = t >= 0 ? graphSim.x[t] : graphView.width / 2;
    const endY = t >= 0 ? graphSim.y[t] : graphView.height / 2;
    edge.setAttribute('x2', endX.toFixed(1));
    edge.setAttribute('y2', endY.toFixed(1));
  });
}

function applyGraphPositions(ids, positions) {
  if (!graphSim) return;
  ids.forEach((id, i) => {
    const j = graphSim.index.get(id);
    if (j != null) { graphSim.x[j] = positions[i * 2]; graphSim.y[j] = positions[i * 2 + 1]; }
  });
  patchGraphPositions();
}

function runGraphSimulation(nodes, edges) {
  const prev = graphSim;
  graphSim = buildGraphSim(nodes, edges);
  // Carry settled positions forward so filtering/timeline changes glide
  // instead of re-randomizing the layout.
  if (prev) {
    for (const [id, i] of graphSim.index) {
      const j = prev.index.get(id);
      if (j != null) { graphSim.x[i] = prev.x[j]; graphSim.y[i] = prev.y[j]; }
    }
  }
  cancelAnimationFrame(graphRafId);
  const reduceMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  const worker = ensureGraphWorker();
  if (worker && nodes.length > 120 && !reduceMotion) {
    worker.postMessage({ type: 'update', nodes: graphSim.ids.map((id, i) => ({ id, x: graphSim.x[i], y: graphSim.y[i], degree: graphSim.degree[i] })), edges: graphSim.links.map(([s, t]) => ({ source: graphSim.ids[s], target: graphSim.ids[t] })), cfg: { ...graphForceConfig, width: graphView.width, height: graphView.height } });
  } else if (!reduceMotion) {
    graphSim.alpha = 1;
    graphRafId = requestAnimationFrame(animateGraph);
  } else {
    // Reduced motion: settle instantly, no animation.
    graphSim.alpha = 1;
    let guard = 0;
    while (graphSimStep(graphSim) && guard < graphForceConfig.maxTicks) guard++;
    patchGraphPositions();
  }
}

function graphVisibleNodes() {
  const data = state.graphData;
  if (!data) return [];
  let nodes = data.nodes || [];
  if (state.graphHideOrphans) nodes = nodes.filter((node) => (node.incoming + node.outgoing) > 0);
  if (state.graphTimeline.enabled) {
    const cutoff = state.graphTimeline.current;
    nodes = nodes.filter((node) => !node.updatedAt || new Date(node.updatedAt).getTime() <= cutoff);
  }
  return nodes;
}

function graphVisibleEdges(nodes) {
  const data = state.graphData;
  if (!data) return [];
  const ids = new Set(nodes.map((node) => node.id));
  return (data.edges || []).filter((edge) => ids.has(edge.source) && (!edge.target || ids.has(edge.target)));
}

function graphTimelineBounds() {
  const times = (state.graphData?.nodes || []).map((node) => node.updatedAt ? new Date(node.updatedAt).getTime() : 0).filter(Boolean);
  if (!times.length) return { min: Date.now(), max: Date.now() };
  return { min: Math.min(...times), max: Math.max(...times) };
}

let graphTimelineTimer = null;
function graphTimelineTick() {
  const range = graphTimelineBounds();
  const step = Math.max((range.max - range.min) / 220, 1000) * state.graphTimeline.speed;
  state.graphTimeline.current = Math.min(state.graphTimeline.current + step, range.max);
  if (state.graphTimeline.current >= range.max) {
    state.graphTimeline.playing = false;
    if (graphTimelineTimer) { clearInterval(graphTimelineTimer); graphTimelineTimer = null; }
  }
  renderGraph();
  syncGraphTimelineUi();
}

function toggleGraphTimelinePlay() {
  if (state.graphTimeline.playing) {
    state.graphTimeline.playing = false;
    if (graphTimelineTimer) { clearInterval(graphTimelineTimer); graphTimelineTimer = null; }
  } else {
    if (state.graphTimeline.current >= graphTimelineBounds().max) state.graphTimeline.current = graphTimelineBounds().min;
    state.graphTimeline.playing = true;
    graphTimelineTimer = setInterval(graphTimelineTick, 90);
  }
  syncGraphTimelineUi();
}

function syncGraphTimelineUi() {
  const slider = $('graph-timeline');
  const button = $('graph-timeline-play');
  if (!slider || !button) return;
  const range = graphTimelineBounds();
  slider.min = String(range.min);
  slider.max = String(range.max);
  slider.value = String(state.graphTimeline.current);
  button.textContent = state.graphTimeline.playing ? '⏸' : '▶';
  button.setAttribute('aria-label', state.graphTimeline.playing ? t('graphPause') : t('graphPlay'));
  button.classList.toggle('active', state.graphTimeline.playing);
}

// ---- hover tooltip + selection drawer
let graphTooltipTimer = 0;
function showGraphTooltip(node, anchor) {
  const tip = $('graph-tooltip');
  if (!tip || !node) return;
  const degree = node.incoming + node.outgoing;
  tip.innerHTML = `
    <strong>${escapeHtml(node.title)}</strong>
    <span class="graph-tooltip-lane"><i style="background:${escapeHtml(node.color || '#7c3aed')}"></i>${escapeHtml(node.laneName || node.lane || '')}</span>
    <small>${escapeHtml(t('graphEdges'))}: ${degree} · ${escapeHtml(t('graphNotes'))}: ${node.updatedAt ? new Date(node.updatedAt).toLocaleDateString(state.locale, { month: 'short', day: 'numeric' }) : '—'}</small>`;
  tip.classList.add('visible');
  const panel = tip.parentElement;
  const bounds = panel.getBoundingClientRect();
  const x = Math.min(anchor.x + 14, bounds.width - tip.offsetWidth - 8);
  const y = Math.min(anchor.y + 14, bounds.height - tip.offsetHeight - 8);
  tip.style.left = `${Math.max(8, x)}px`;
  tip.style.top = `${Math.max(8, y)}px`;
}

function hideGraphTooltip() {
  $('graph-tooltip')?.classList.remove('visible');
}

function openGraphDrawer(node) {
  state.graphSelected = node.id;
  const drawer = $('graph-drawer');
  if (!drawer) return;
  const data = state.graphData;
  const incoming = (data.edges || []).filter((edge) => edge.target === node.id);
  const outgoing = (data.edges || []).filter((edge) => edge.source === node.id);
  const titleOf = (id) => (data.nodes || []).find((n) => n.id === id)?.title || id;
  const chip = (id) => `<button class="tag-chip" data-graph-jump="${escapeHtml(id)}" type="button">${escapeHtml(titleOf(id))}</button>`;
  drawer.innerHTML = `
    <div class="modal-head"><p class="eyebrow">${escapeHtml(t('graphDrawerTitle'))}</p><button class="text-action muted-action" data-drawer-close type="button" aria-label="${escapeHtml(t('cancelEdit'))}">✕</button></div>
    <div class="drawer-body">
      <h3>${escapeHtml(node.title)}</h3>
      <span class="graph-tooltip-lane"><i style="background:${escapeHtml(node.color || '#7c3aed')}"></i>${escapeHtml(node.laneName || node.lane || '')}</span>
      <dl class="modal-record-row">
        <div class="modal-record-row"><dt>${escapeHtml(t('graphEdges'))}</dt><dd>${node.incoming + node.outgoing}</dd></div>
        <div class="modal-record-row"><dt>${escapeHtml(t('recordUpdated'))}</dt><dd>${node.updatedAt ? new Date(node.updatedAt).toLocaleString(state.locale, { dateStyle: 'medium', timeStyle: 'short' }) : '—'}</dd></div>
      </dl>
      <p class="eyebrow">${escapeHtml(t('linksTitle'))} (${outgoing.length})</p>
      <div class="drawer-chips">${outgoing.map((edge) => edge.target ? chip(edge.target) : `<span class="tag-chip unresolved">${escapeHtml(edge.label || '·')}</span>`).join('') || `<span class="muted">${escapeHtml(t('noLinks'))}</span>`}</div>
      <p class="eyebrow">${escapeHtml(t('backlinksTitle'))} (${incoming.length})</p>
      <div class="drawer-chips">${incoming.map((edge) => chip(edge.source)).join('') || `<span class="muted">${escapeHtml(t('noBacklinks'))}</span>`}</div>
      <div class="editor-actions"><button class="button button-small" id="graph-drawer-open" type="button">${escapeHtml(t('graphOpen'))}</button></div>
    </div>`;
  drawer.classList.remove('hidden');
  drawer.querySelector('[data-drawer-close]').addEventListener('click', () => { state.graphSelected = null; drawer.classList.add('hidden'); });
  drawer.querySelector('#graph-drawer-open').addEventListener('click', () => openGraphNode(node));
  drawer.querySelectorAll('[data-graph-jump]').forEach((element) => element.addEventListener('click', () => {
    const target = (data.nodes || []).find((n) => n.id === element.dataset.graphJump);
    if (target) openGraphDrawer(target);
  }));
}

function openGraphNode(node) {
  state.graphSelected = null;
  $('graph-drawer')?.classList.add('hidden');
  state.noteView = 'all';
  state.tagFilter = null;
  state.search = node.title;
  $('note-search').value = state.search;
  setView('notes');
  loadNotes();
}

// ---- viewport zoom / pan / reset
const graphViewport = { k: 1, x: 0, y: 0 };
function applyGraphViewport() {
  const group = $('graph-canvas')?.querySelector('.graph-viewport');
  if (group) group.setAttribute('transform', `translate(${graphViewport.x} ${graphViewport.y}) scale(${graphViewport.k})`);
  const badge = $('graph-zoom-reset');
  if (badge) badge.classList.toggle('visible', graphViewport.k !== 1 || graphViewport.x !== 0 || graphViewport.y !== 0);
}

function renderGraph(data) {
  if (data) state.graphData = data;
  const source = state.graphData;
  if (!source) return;
  const nodes = graphVisibleNodes();
  const edges = graphVisibleEdges(nodes);
  const stats = { ...source.stats, visible: nodes.length };
  if (!nodes.length) {
    $('graph-canvas').innerHTML = `<p class="panel-copy">${escapeHtml(t('graphEmpty'))}</p>`;
    $('graph-stats').innerHTML = '';
    $('graph-legend').innerHTML = '';
    $('graph-filter').innerHTML = '';
    return;
  }
  // Reuse settled positions: build a sim from the previous state each render.
  const prevSim = graphSim;
  graphSim = buildGraphSim(nodes, edges);
  if (prevSim) {
    for (const [id, i] of graphSim.index) {
      const j = prevSim.index.get(id);
      if (j != null) { graphSim.x[i] = prevSim.x[j]; graphSim.y[i] = prevSim.y[j]; }
    }
  }
  // Heatmap underlay (G3): radial gradients sized by weighted degree.
  const heat = state.graphHeatmap ? nodes.map((node) => {
    const i = graphSim.index.get(node.id);
    const weight = Math.min(node.incoming + node.outgoing, 8) / 8;
    const r = 26 + weight * 34;
    return `<circle class="graph-heat" cx="${graphSim.x[i].toFixed(1)}" cy="${graphSim.y[i].toFixed(1)}" r="${r.toFixed(1)}" fill="rgba(180,71,92,${(0.05 + weight * 0.16).toFixed(3)})"/>`;
  }).join('') : '';
  const line = (edge) => {
    const s = graphSim.index.get(edge.source);
    if (s == null) return '';
    const t = edge.target ? graphSim.index.get(edge.target) : -1;
    const endX = t >= 0 ? graphSim.x[t] : graphView.width / 2;
    const endY = t >= 0 ? graphSim.y[t] : graphView.height / 2;
    return `<line class="graph-edge${edge.resolved ? '' : ' is-unresolved'}" data-from="${escapeHtml(edge.source)}" data-to="${escapeHtml(edge.target || '')}" x1="${graphSim.x[s].toFixed(1)}" y1="${graphSim.y[s].toFixed(1)}" x2="${endX.toFixed(1)}" y2="${endY.toFixed(1)}"></line>`;
  };
  const circles = nodes.map((node) => {
    const i = graphSim.index.get(node.id);
    const size = 7 + Math.min(7, (node.incoming + node.outgoing) * 1.3);
    return `<g class="graph-node" data-graph-node="${escapeHtml(node.id)}" data-graph-title="${escapeHtml(node.title)}" data-graph-degree="${node.incoming + node.outgoing}" tabindex="0" role="button" aria-label="${escapeHtml(`${t('graphOpen')}: ${node.title}`)}">
      <circle cx="${graphSim.x[i].toFixed(1)}" cy="${graphSim.y[i].toFixed(1)}" r="${size.toFixed(1)}" fill="${escapeHtml(node.color || '#7c3aed')}"></circle>
      <text x="${graphSim.x[i].toFixed(1)}" y="${(graphSim.y[i] + size + 13).toFixed(1)}" text-anchor="middle">${escapeHtml(String(node.title).slice(0, 24))}</text>
    </g>`;
  }).join('');
  const statsHtml = `<span class="graph-stat"><strong>${stats.notes}</strong> ${escapeHtml(t('graphNotes'))}</span><span class="graph-stat"><strong>${stats.edges}</strong> ${escapeHtml(t('graphEdges'))}</span><span class="graph-stat"><strong>${stats.resolved}</strong> ${escapeHtml(t('graphResolved'))}</span><span class="graph-stat"><strong>${stats.unresolved}</strong> ${escapeHtml(t('graphUnresolved'))}</span><span class="graph-stat"><strong>${stats.visible}</strong> ${escapeHtml(t('graphVisible'))}</span>`;
  $('graph-stats').innerHTML = statsHtml;
  $('graph-canvas').innerHTML = `<svg class="graph-svg" viewBox="0 0 ${graphView.width} ${graphView.height}" role="img" aria-label="${escapeHtml(t('graphTitle'))}">
    <g class="graph-viewport">${heat}<g class="graph-edges">${edges.map(line).join('')}</g><g class="graph-nodes">${circles}</g></g>
  </svg>`;
  const lanes = [...new Map(nodes.map((node) => [node.lane, node])).values()];
  $('graph-legend').innerHTML = `<span class="eyebrow">${escapeHtml(t('graphLegend'))}</span>${lanes.map((lane) => `<span class="graph-legend-item"><i style="background:${escapeHtml(lane.color || '#7c3aed')}"></i>${escapeHtml(lane.laneName)}</span>`).join('')}`;
  renderGraphFilters();
  syncGraphTimelineControls(source);
  bindGraphInteractions();
  runGraphSimulation(nodes, edges);
}

function renderGraphFilters() {
  const lanes = [...new Map((state.graphData?.nodes || []).map((node) => [node.lane, node])).values()];
  $('graph-filter').innerHTML = `
    <button class="chip-toggle ${state.graphHideOrphans ? 'active' : ''}" id="graph-orphans" type="button" aria-pressed="${state.graphHideOrphans}">${escapeHtml(t('graphShowOrphans'))}</button>
    <button class="chip-toggle ${state.graphHeatmap ? 'active' : ''}" id="graph-heat" type="button" aria-pressed="${state.graphHeatmap}">${escapeHtml(t('graphHeatmap'))}</button>
    ${lanes.map((lane) => `<button class="tag-chip ${state.graphLaneFilter && state.graphLaneFilter !== lane.lane ? 'is-dim' : ''} ${state.graphLaneFilter === lane.lane ? 'active' : ''}" data-graph-lane="${escapeHtml(lane.lane)}" type="button"><i style="background:${escapeHtml(lane.color || '#7c3aed')}"></i>${escapeHtml(lane.laneName)}</button>`).join('')}`;
  $('graph-orphans')?.addEventListener('click', () => { state.graphHideOrphans = !state.graphHideOrphans; renderGraph(); });
  $('graph-heat')?.addEventListener('click', () => { state.graphHeatmap = !state.graphHeatmap; renderGraph(); });
  document.querySelectorAll('[data-graph-lane]').forEach((button) => button.addEventListener('click', () => {
    state.graphLaneFilter = state.graphLaneFilter === button.dataset.graphLane ? null : button.dataset.graphLane;
    renderGraph();
  }));
}

function syncGraphTimelineControls(source) {
  const controls = $('graph-timeline-controls');
  const slider = $('graph-timeline');
  if (!controls || !slider) return;
  const dated = (source.nodes || []).some((node) => node.updatedAt);
  controls.classList.toggle('disabled', !dated);
  $('graph-timeline-play').onclick = () => toggleGraphTimelinePlay();
  slider.oninput = (event) => {
    state.graphTimeline.current = Number(event.target.value);
    if (state.graphTimeline.playing) toggleGraphTimelinePlay();
    renderGraph();
  };
  document.querySelectorAll('.graph-speed').forEach((button) => button.onclick = () => {
    state.graphTimeline.speed = Number(button.dataset.speed) || 1;
    document.querySelectorAll('.graph-speed').forEach((other) => other.setAttribute('aria-pressed', String(other === button)));
  });
}

function bindGraphInteractions() {
  const canvas = $('graph-canvas');
  if (!canvas) return;
  const spotEdges = (id) => canvas.querySelectorAll('.graph-edge').forEach((edge) => edge.classList.toggle('is-active', Boolean(id) && (edge.dataset.from === id || edge.dataset.to === id)));
  const spotlight = (id) => {
    const neighbors = new Set();
    if (id) canvas.querySelectorAll(`.graph-edge[data-from="${CSS.escape(id)}"], .graph-edge[data-to="${CSS.escape(id)}"]`).forEach((edge) => { neighbors.add(edge.dataset.from); edge.dataset.to && neighbors.add(edge.dataset.to); });
    canvas.querySelectorAll('.graph-node').forEach((element) => element.classList.toggle('is-dim', Boolean(id) && element.dataset.graphNode !== id && !neighbors.has(element.dataset.graphNode)));
    spotEdges(id);
  };
  canvas.querySelectorAll('.graph-node').forEach((element) => {
    const node = (state.graphData.nodes || []).find((n) => n.id === element.dataset.graphNode);
    element.addEventListener('mouseenter', (event) => {
      spotlight(element.dataset.graphNode);
      if (node) showGraphTooltip(node, { x: event.offsetX, y: event.offsetY });
    });
    element.addEventListener('mousemove', (event) => { if (node && $('graph-tooltip')?.classList.contains('visible')) showGraphTooltip(node, { x: event.offsetX, y: event.offsetY }); });
    element.addEventListener('mouseleave', () => { spotlight(null); hideGraphTooltip(); });
    element.addEventListener('focus', () => spotlight(element.dataset.graphNode));
    element.addEventListener('blur', () => { spotlight(null); hideGraphTooltip(); });
    element.addEventListener('click', () => { if (node) openGraphDrawer(node); });
    element.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); if (node) openGraphDrawer(node); } });
  });
  // zoom / pan on the viewport group
  const svg = canvas.querySelector('svg');
  if (!svg) return;
  svg.addEventListener('wheel', (event) => {
    event.preventDefault();
    const factor = event.deltaY < 0 ? 1.12 : 1 / 1.12;
    const next = Math.min(4, Math.max(0.4, graphViewport.k * factor));
    const rect = svg.getBoundingClientRect();
    const px = (event.clientX - rect.left) / rect.width * graphView.width;
    const py = (event.clientY - rect.top) / rect.height * graphView.height;
    graphViewport.x = px - (px - graphViewport.x) * (next / graphViewport.k);
    graphViewport.y = py - (py - graphViewport.y) * (next / graphViewport.k);
    graphViewport.k = next;
    applyGraphViewport();
  }, { passive: false });
  let panning = null;
  svg.addEventListener('mousedown', (event) => { panning = { x: event.clientX, y: event.clientY, vx: graphViewport.x, vy: graphViewport.y }; });
  window.addEventListener('mousemove', (event) => {
    if (!panning) return;
    const rect = svg.getBoundingClientRect();
    graphViewport.x = panning.vx + (event.clientX - panning.x) / rect.width * graphView.width;
    graphViewport.y = panning.vy + (event.clientY - panning.y) / rect.height * graphView.height;
    applyGraphViewport();
  });
  window.addEventListener('mouseup', () => { panning = null; });
  $('graph-zoom-reset')?.addEventListener('click', () => { graphViewport.k = 1; graphViewport.x = 0; graphViewport.y = 0; applyGraphViewport(); });
}

async function loadGraph() {
  setMessage('graph-message');
  try {
    const data = await request('/api/graph');
    state.graphData = data;
    graphViewport.k = 1; graphViewport.x = 0; graphViewport.y = 0;
    if (!state.graphTimeline.current) state.graphTimeline.current = graphTimelineBounds().max;
    renderGraph();
    syncGraphTimelineUi();
  }
  catch (error) { setMessage('graph-message', t('graphLoadFailed')); }
}

/* ---------- Markdown bundle export ---------- */

async function loadKanban() {
  setMessage('kanban-message');
  try {
    const data = await request('/api/kanban');
    state.kanbanBoard = data;
    renderKanban(data);
  } catch (error) {
    setMessage('kanban-message', t('kanbanLoadFailed') || 'Failed to load kanban board');
  }
}

function renderKanban(data) {
  const container = $('kanban-columns');
  if (!container) return;

  // Snapshot the board so the card editor can re-render after mutations.
  state.kanbanBoard = data;
  const columns = data.columns || [];
  const notes = data.notes || [];
  const canWrite = Boolean(state.user?.permissions?.includes('notes:write'));
  const statusLabels = {
    backlog: t('kanbanBacklog') || 'Backlog',
    todo: t('kanbanTodo') || 'To do',
    doing: t('kanbanDoing') || 'Doing',
    review: t('kanbanReview') || 'Review',
    done: t('kanbanDone') || 'Done',
  };
  const priorityOrder = { urgent: 0, high: 1, medium: 2, low: 3 };

  container.innerHTML = '';

  columns.forEach((columnMeta) => {
    const status = columnMeta.status;
    const columnNotes = notes
      .filter((note) => (note.status || 'todo') === status)
      .sort((a, b) => (priorityOrder[a.priority] ?? 9) - (priorityOrder[b.priority] ?? 9) || (a.position || 0) - (b.position || 0));

    const column = document.createElement('div');
    column.className = `kanban-column kanban-column--${status}`;
    column.dataset.status = status;
    column.innerHTML = `
      <div class="kanban-column-header">
        <span class="kanban-column-status">${escapeHtml(statusLabels[status] || status)}</span>
        <span class="kanban-column-count">${columnNotes.length}</span>
      </div>
      <div class="kanban-cards" data-status="${status}"></div>
      <button class="kanban-add-card" type="button" data-kanban-add="${status}" aria-label="${escapeHtml(t('kanbanAddCard') || 'Add card')}">+ ${escapeHtml(t('kanbanAddCard') || 'Add card')}</button>
    `;
    const cardsContainer = column.querySelector('.kanban-cards');
    columnNotes.forEach((note) => {
      const card = document.createElement('div');
      card.className = `kanban-card kanban-card--${note.priority || 'medium'}`;
      card.dataset.noteId = note.id;
      card.dataset.status = status;
      card.draggable = canWrite;
      const category = note.category || {};
      const due = note.dueDate ? new Date(note.dueDate).toLocaleDateString(state.locale, { month: 'short', day: 'numeric' }) : '';
      card.innerHTML = `
        <div class="kanban-card-content">${escapeHtml(note.content.slice(0, 200))}${note.content.length > 200 ? '…' : ''}</div>
        <div class="kanban-card-meta">
          <span class="kanban-card-category" style="background: ${escapeHtml(category.color || '#0a0a0a')}">${escapeHtml(category.icon || '●')}</span>
          <span class="kanban-card-priority kanban-card-priority--${escapeHtml(note.priority || 'medium')}">${escapeHtml(note.priority || 'medium')}</span>
          ${due ? `<span class="kanban-card-due">${escapeHtml(due)}</span>` : ''}
        </div>
      `;
      if (canWrite) {
        card.addEventListener('click', (event) => {
          if (event.target.closest('a')) return;
          state.kanbanEditing = note.id;
          state.kanbanNewStatus = null;
          renderKanbanEditor();
        });
      }
      cardsContainer.appendChild(card);
    });
    container.appendChild(column);
  });

  if (canWrite) setupKanbanDragAndDrop();
  renderKanbanEditor();
}

/* ---------- Kanban card editor ---------- */

// Inline editor under the board, following the lane-editor pattern: a new card
// opens with kanbanEditing = null and kanbanNewStatus set; an existing card
// opens with kanbanEditing set. Both write through the notes API.
function renderKanbanEditor() {
  const mount = $('kanban-editor');
  if (!mount) return;
  const board = state.kanbanBoard;
  if (state.kanbanEditing === null && !state.kanbanNewStatus) { mount.classList.add('hidden'); mount.innerHTML = ''; return; }

  const note = state.kanbanEditing ? (board?.notes || []).find((item) => item.id === state.kanbanEditing) : null;
  if (state.kanbanEditing && !note) { state.kanbanEditing = null; state.kanbanNewStatus = null; mount.classList.add('hidden'); mount.innerHTML = ''; return; }

  const lanes = state.categories.length ? state.categories : (board?.categories || board?.lanes || []);
  const priorities = ['low', 'medium', 'high', 'urgent'];
  const statuses = (board?.columns || []).map((column) => column.status).filter(Boolean);
  const statusLabel = (status) => ({ backlog: t('kanbanBacklog'), todo: t('kanbanTodo'), doing: t('kanbanDoing'), review: t('kanbanReview'), done: t('kanbanDone') })[status] || status;

  const title = note ? (note.content || '').split('\n').map((row) => row.trim()).find(Boolean) || '' : '';
  const priority = note ? (note.priority || 'medium') : 'medium';
  const status = note ? (note.status || 'todo') : (state.kanbanNewStatus || 'todo');
  const dueValue = note?.dueDate ? new Date(note.dueDate).toISOString().slice(0, 10) : '';
  const laneValue = note?.category?.slug || state.selected || (lanes[0]?.slug ?? 'notes');

  // Full record display: every stored field the API returns for this card.
  const recordRows = note ? [
    [t('kanbanCardLane'), note.category ? `${note.category.icon || ''} ${note.category.name}`.trim() : '—'],
    [t('kanbanColumns'), statusLabel(note.status || 'todo')],
    [t('kanbanCardPriority'), note.priority || 'medium'],
    [t('kanbanCardDue'), note.dueDate ? new Date(note.dueDate).toLocaleString(state.locale, { dateStyle: 'medium', timeStyle: 'short' }) : '—'],
    [t('calEventStart'), note.startDate ? new Date(note.startDate).toLocaleString(state.locale, { dateStyle: 'medium', timeStyle: 'short' }) : '—'],
    [t('calEventEnd'), note.endDate ? new Date(note.endDate).toLocaleString(state.locale, { dateStyle: 'medium', timeStyle: 'short' }) : '—'],
    [t('recordWords'), String(note.wordCount ?? 0)],
    [t('recordLinks'), String(note.linkCount ?? 0)],
    [t('recordTags'), (note.tags || []).map((tag) => `#${tag.name || tag}`).join(' ') || '—'],
    [t('recordCreated'), note.createdAt ? new Date(note.createdAt).toLocaleString(state.locale, { dateStyle: 'medium', timeStyle: 'short' }) : '—'],
    [t('recordUpdated'), note.updatedAt ? new Date(note.updatedAt).toLocaleString(state.locale, { dateStyle: 'medium', timeStyle: 'short' }) : '—'],
  ] : [];
  const recordHtml = !note ? '' : `
    <div class="modal-record">
      <p class="eyebrow">${escapeHtml(t('recordDetails'))}</p>
      <dl>${recordRows.map(([label, value]) => `<div class="modal-record-row"><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join('')}</dl>
    </div>`;

  mount.innerHTML = `
    <div class="modal-backdrop" data-modal-close></div>
    <div class="modal-dialog" role="dialog" aria-modal="true" aria-label="${escapeHtml(note ? t('kanbanEditCard') : t('kanbanAddCard'))}">
      <div class="modal-head"><p class="eyebrow">${escapeHtml(note ? t('kanbanEditCard') : t('kanbanAddCard'))}</p><button class="text-action muted-action" data-modal-close type="button" aria-label="${escapeHtml(t('cancelEdit'))}">✕</button></div>
      <form id="kanban-card-form" class="modal-body">
        <label for="kanban-card-title">${escapeHtml(t('kanbanCardTitle'))}<input id="kanban-card-title" value="${escapeHtml(title)}" placeholder="${escapeHtml(t('kanbanCardTitlePlaceholder'))}" maxlength="200" required></label>
        <div class="modal-grid">
          <label for="kanban-card-status">${escapeHtml(t('kanbanColumns'))}
            <select id="kanban-card-status">${statuses.map((option) => `<option value="${escapeHtml(option)}" ${option === status ? 'selected' : ''}>${escapeHtml(statusLabel(option))}</option>`).join('')}</select>
          </label>
          <label for="kanban-card-priority">${escapeHtml(t('kanbanCardPriority'))}
            <select id="kanban-card-priority">${priorities.map((option) => `<option value="${option}" ${option === priority ? 'selected' : ''}>${escapeHtml(option)}</option>`).join('')}</select>
          </label>
          <label for="kanban-card-due">${escapeHtml(t('kanbanCardDue'))}
            <input id="kanban-card-due" type="date" value="${escapeHtml(dueValue)}">
          </label>
          <label for="kanban-card-lane">${escapeHtml(t('kanbanCardLane'))}
            <select id="kanban-card-lane">${lanes.map((lane) => `<option value="${escapeHtml(lane.slug)}" ${lane.slug === laneValue ? 'selected' : ''}>${escapeHtml(lane.name)}</option>`).join('')}</select>
          </label>
        </div>
        ${recordHtml}
        <div class="editor-actions">
          ${note ? `<a class="link-button" href="/share/${encodeURIComponent(note.id)}" target="_blank" rel="noopener">${escapeHtml(t('kanbanCardOpen'))}</a><button class="link-button danger" id="kanban-card-delete" type="button">${escapeHtml(t('kanbanCardDelete'))}</button>` : ''}
          <button class="button button-small" type="submit">${escapeHtml(t('saveEdit'))}</button>
        </div>
        <p id="kanban-card-message" class="message" role="alert"></p>
      </form>
    </div>`;
  mount.classList.remove('hidden');

  mount.querySelectorAll('[data-modal-close]').forEach((closer) => closer.addEventListener('click', () => { state.kanbanEditing = null; state.kanbanNewStatus = null; renderKanbanEditor(); }));
  mount.addEventListener('keydown', (event) => { if (event.key === 'Escape') { state.kanbanEditing = null; state.kanbanNewStatus = null; renderKanbanEditor(); } }, { once: true });
  mount.querySelector('#kanban-card-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const content = mount.querySelector('#kanban-card-title').value.trim();
    if (!content) { setMessage('kanban-card-message', t('commentEmpty')); return; }
    const dueInput = mount.querySelector('#kanban-card-due').value;
    const body = {
      content,
      status: mount.querySelector('#kanban-card-status').value,
      priority: mount.querySelector('#kanban-card-priority').value,
      category: mount.querySelector('#kanban-card-lane').value,
      dueDate: dueInput ? new Date(`${dueInput}T12:00:00`).toISOString() : null,
    };
    try {
      if (note) {
        await request(`/api/notes/${encodeURIComponent(note.id)}`, { method: 'PATCH', body: JSON.stringify(body) });
      } else {
        await request('/api/notes', { method: 'POST', body: JSON.stringify(body) });
      }
      setMessage('app-message', t('kanbanCardSaved'));
      state.kanbanEditing = null; state.kanbanNewStatus = null;
      renderKanbanEditor();
      await loadKanban();
    } catch (error) { setMessage('kanban-card-message', error.message); }
  });
  const deleteButton = mount.querySelector('#kanban-card-delete');
  if (deleteButton) deleteButton.addEventListener('click', async () => {
    if (!note || !window.confirm(t('commentDeleteConfirm'))) return;
    try {
      await request(`/api/notes/${encodeURIComponent(note.id)}`, { method: 'DELETE' });
      state.kanbanEditing = null; state.kanbanNewStatus = null;
      renderKanbanEditor();
      setMessage('app-message', t('kanbanCardDeleted'));
      await loadKanban();
    } catch (error) { setMessage('kanban-card-message', error.message); }
  });
}

function setupKanbanDragAndDrop() {
  let draggedCard = null;
  const renumber = (container, status) => [...container.querySelectorAll('.kanban-card')].map((card, index) => ({ card, position: index, status }));

  document.querySelectorAll('.kanban-card').forEach((card) => {
    card.addEventListener('dragstart', (e) => {
      draggedCard = card;
      card.classList.add('dragging');
      e.dataTransfer.effectAllowed = 'move';
    });
    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
      draggedCard = null;
    });
  });

  document.querySelectorAll('.kanban-cards').forEach((column) => {
    column.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      column.classList.add('drag-over');
    });
    column.addEventListener('dragleave', () => {
      column.classList.remove('drag-over');
    });
    column.addEventListener('drop', async (e) => {
      e.preventDefault();
      column.classList.remove('drag-over');
      if (!draggedCard) return;

      const targetStatus = column.dataset.status;
      const noteId = draggedCard.dataset.noteId;
      if (!targetStatus || !noteId) return;

      column.appendChild(draggedCard);
      draggedCard.dataset.status = targetStatus;
      const position = [...column.querySelectorAll('.kanban-card')].indexOf(draggedCard);
      try {
        await request('/api/kanban/move', {
          method: 'POST',
          body: JSON.stringify({ noteId, status: targetStatus, position }),
        });
        loadKanban();
      } catch (error) {
        setMessage('kanban-message', error.message);
        loadKanban();
      }
    });
  });
}

document.querySelectorAll('[data-kanban-add]').forEach((button) => button.addEventListener('click', () => {
  state.kanbanEditing = null;
  state.kanbanNewStatus = button.dataset.kanbanAdd;
  renderKanbanEditor();
}));

async function loadCalendar() {
  setMessage('calendar-message');
  try {
    const data = await request('/api/calendar');
    state.calendarEvents = data.events || [];
    renderCalendar(data);
  } catch (error) {
    setMessage('calendar-message', t('calendarLoadFailed') || 'Failed to load calendar');
  }
}

function renderCalendar(data) {
  const grid = $('calendar-grid');
  if (!grid) return;
  
  const events = data.events || [];
  const view = state.calendarView || 'month';
  const currentDate = state.calendarCurrentDate || new Date();
  
  grid.innerHTML = '';
  
  if (view === 'month') {
    renderMonthView(grid, events, currentDate);
  } else if (view === 'week') {
    renderWeekView(grid, events, currentDate);
  } else {
    renderDayView(grid, events, currentDate);
  }
  
  const monthTitle = $('cal-current-month');
  if (monthTitle) {
    monthTitle.textContent = currentDate.toLocaleDateString(state.locale, { month: 'long', year: 'numeric' });
  }
}

function renderMonthView(grid, events, currentDate) {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const startDay = firstDay.getDay();
  const daysInMonth = lastDay.getDate();
  
  const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  dayHeaders.forEach((day) => {
    const header = document.createElement('div');
    header.className = 'cal-day-header';
    header.textContent = t('calDay' + day) || day;
    grid.appendChild(header);
  });
  
  for (let i = 0; i < startDay; i++) {
    const empty = document.createElement('div');
    empty.className = 'cal-day empty';
    grid.appendChild(empty);
  }
  
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day);
    const dayEvents = events.filter((event) => {
      const eventDate = new Date(event.start);
      return eventDate.getFullYear() === year && eventDate.getMonth() === month && eventDate.getDate() === day;
    });
    
    const cell = document.createElement('div');
    cell.className = 'cal-day';
    cell.dataset.date = date.toISOString().split('T')[0];
    
    const dayNumber = document.createElement('div');
    dayNumber.className = 'cal-day-number';
    dayNumber.textContent = day;
    if (date.toDateString() === new Date().toDateString()) {
      dayNumber.classList.add('today');
    }
    cell.appendChild(dayNumber);
    
    if (dayEvents.length > 0) {
      const eventsContainer = document.createElement('div');
      eventsContainer.className = 'cal-day-events';
      dayEvents.slice(0, 3).forEach((event) => {
        const eventEl = document.createElement('div');
        eventEl.className = 'cal-event';
        eventEl.style.borderLeftColor = event.color || 'var(--accent)';
        eventEl.textContent = event.title;
        eventEl.dataset.eventNote = event.noteId || '';
        eventsContainer.appendChild(eventEl);
      });
      if (dayEvents.length > 3) {
        const moreEl = document.createElement('div');
        moreEl.className = 'cal-event-more';
        moreEl.textContent = `+ ${dayEvents.length - 3} ${t('calMore') || 'more'}`;
        eventsContainer.appendChild(moreEl);
      }
      cell.appendChild(eventsContainer);
    }
    
    cell.addEventListener('click', () => {
      state.calendarCurrentDate = date;
      state.calendarView = 'day';
      syncCalendarViewSwitcher();
      loadCalendar();
    });
    
    grid.appendChild(cell);
  }
}

function syncCalendarViewSwitcher() {
  document.querySelectorAll('[data-cal-view]').forEach((button) => button.classList.toggle('active', button.dataset.calView === (state.calendarView || 'month')));
}

// Inline event editor under the calendar: creates or edits the note that backs
// a calendar event (a note with start/due dates). Reuses the notes API so
// permissions, audit, and search stay consistent.
function renderCalendarEditor(date) {
  const mount = $('calendar-editor');
  if (!mount) return;
  const canWrite = Boolean(state.user?.permissions?.includes('notes:write'));
  if (!canWrite || !date) { mount.classList.add('hidden'); mount.innerHTML = ''; return; }

  const event = state.calendarEditingEvent
    ? (state.calendarEvents || []).find((item) => item.noteId === state.calendarEditingEvent)
    : null;
  if (state.calendarEditingEvent && !event) { state.calendarEditingEvent = null; mount.classList.add('hidden'); mount.innerHTML = ''; return; }

  const day = date.toISOString().slice(0, 10);
  const title = event ? (event.title || '') : '';
  const startValue = event?.start && !event.allDay ? new Date(event.start).toISOString().slice(0, 16) : '';
  const endValue = event?.end && !event.allDay ? new Date(event.end).toISOString().slice(0, 16) : '';
  const color = event?.color || '#7c3aed';

  // Full record display for the event's backing note.
  const recordRows = event ? [
    [t('calEventDate'), day],
    [t('calEventStart'), event.start ? new Date(event.start).toLocaleString(state.locale, { dateStyle: 'medium', timeStyle: 'short' }) : t('calAllDay')],
    [t('calEventEnd'), event.end ? new Date(event.end).toLocaleString(state.locale, { dateStyle: 'medium', timeStyle: 'short' }) : '—'],
    [t('kanbanColumns'), ({ backlog: t('kanbanBacklog'), todo: t('kanbanTodo'), doing: t('kanbanDoing'), review: t('kanbanReview'), done: t('kanbanDone') })[event.status] || event.status || '—'],
    [t('kanbanCardPriority'), event.priority || '—'],
    [t('kanbanCardLane'), event.category || '—'],
  ] : [];
  const recordHtml = !event ? '' : `
    <div class="modal-record">
      <p class="eyebrow">${escapeHtml(t('recordDetails'))}</p>
      <dl>${recordRows.map(([label, value]) => `<div class="modal-record-row"><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd></div>`).join('')}</dl>
    </div>`;

  mount.innerHTML = `
    <div class="modal-backdrop" data-modal-close></div>
    <div class="modal-dialog" role="dialog" aria-modal="true" aria-label="${escapeHtml(event ? t('calEditEvent') : t('calNewEvent'))}">
      <div class="modal-head"><p class="eyebrow">${escapeHtml(event ? t('calEditEvent') : t('calNewEvent'))} · ${escapeHtml(day)}</p><button class="text-action muted-action" data-modal-close type="button" aria-label="${escapeHtml(t('cancelEdit'))}">✕</button></div>
      <form id="calendar-event-form" class="modal-body">
        <label for="cal-event-title">${escapeHtml(t('calEventTitle'))}<input id="cal-event-title" value="${escapeHtml(title)}" placeholder="${escapeHtml(t('calEventTitlePlaceholder'))}" maxlength="200" required></label>
        <div class="modal-grid">
          <label for="cal-event-start">${escapeHtml(t('calEventStart'))}<input id="cal-event-start" type="datetime-local" value="${escapeHtml(startValue)}"></label>
          <label for="cal-event-end">${escapeHtml(t('calEventEnd'))}<input id="cal-event-end" type="datetime-local" value="${escapeHtml(endValue)}"></label>
        </div>
        <p class="muted editor-hint">${escapeHtml(t('calEventAllDayHint'))}</p>
        <div class="editor-inline"><p class="editor-label">${escapeHtml(t('calEventColor'))}</p><input id="cal-event-color" type="color" value="${escapeHtml(color)}" class="cal-color-input"></div>
        ${recordHtml}
        <div class="editor-actions">
          ${event ? `<a class="link-button" href="/share/${encodeURIComponent(event.noteId)}" target="_blank" rel="noopener">${escapeHtml(t('calEventOpen'))}</a><button class="link-button danger" id="cal-event-delete" type="button">${escapeHtml(t('calEventDelete'))}</button>` : ''}
          <button class="button button-small" type="submit">${escapeHtml(t('saveEdit'))}</button>
        </div>
        <p id="cal-event-message" class="message" role="alert"></p>
      </form>
    </div>`;
  mount.classList.remove('hidden');

  mount.querySelectorAll('[data-modal-close]').forEach((closer) => closer.addEventListener('click', () => { state.calendarEditingEvent = null; renderCalendarEditor(); }));
  mount.addEventListener('keydown', (event) => { if (event.key === 'Escape') { state.calendarEditingEvent = null; renderCalendarEditor(); } }, { once: true });
  mount.querySelector('#calendar-event-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const titleValue = mount.querySelector('#cal-event-title').value.trim();
    if (!titleValue) { setMessage('cal-event-message', t('commentEmpty')); return; }
    const startRaw = mount.querySelector('#cal-event-start').value;
    const endRaw = mount.querySelector('#cal-event-end').value;
    const colorValue = mount.querySelector('#cal-event-color').value;
    const startIso = startRaw ? new Date(startRaw).toISOString() : null;
    const endIso = endRaw ? new Date(endRaw).toISOString() : null;
    const body = {
      content: `# ${titleValue}`,
      category: state.selected || 'notes',
      eventColor: colorValue,
      startDate: startIso,
      dueDate: endIso || startIso || new Date(`${date.toISOString().slice(0, 10)}T12:00:00`).toISOString(),
      endDate: endIso,
    };
    try {
      if (event) {
        await request(`/api/notes/${encodeURIComponent(event.noteId)}`, { method: 'PATCH', body: JSON.stringify(body) });
      } else {
        await request('/api/notes', { method: 'POST', body: JSON.stringify(body) });
      }
      setMessage('app-message', t('calEventSaved'));
      state.calendarEditingEvent = null;
      renderCalendarEditor();
      await loadCalendar();
    } catch (error) { setMessage('cal-event-message', error.message); }
  });
  const deleteButton = mount.querySelector('#cal-event-delete');
  if (deleteButton) deleteButton.addEventListener('click', async () => {
    if (!event || !window.confirm(t('commentDeleteConfirm'))) return;
    try {
      await request(`/api/notes/${encodeURIComponent(event.noteId)}`, { method: 'DELETE' });
      state.calendarEditingEvent = null;
      renderCalendarEditor();
      setMessage('app-message', t('calEventDeleted'));
      await loadCalendar();
    } catch (error) { setMessage('cal-event-message', error.message); }
  });
}

function renderWeekView(grid, events, currentDate) {
  const day = currentDate.getDay();
  const monday = new Date(currentDate);
  monday.setDate(currentDate.getDate() - day + (day === 0 ? -6 : 1));
  
  for (let i = 0; i < 7; i++) {
    const date = new Date(monday);
    date.setDate(monday.getDate() + i);
    
    const dayEvents = events.filter((event) => {
      const eventDate = new Date(event.start);
      return eventDate.toDateString() === date.toDateString();
    });
    
    const column = document.createElement('div');
    column.className = 'cal-week-day';
    
    const header = document.createElement('div');
    header.className = 'cal-week-day-header';
    header.innerHTML = `
      <span class="cal-week-day-name">${date.toLocaleDateString(state.locale, { weekday: 'short' })}</span>
      <span class="cal-week-day-number">${date.getDate()}${date.toDateString() === new Date().toDateString() ? ' ' + t('calToday') : ''}</span>
    `;
    column.appendChild(header);
    
    const eventsContainer = document.createElement('div');
    eventsContainer.className = 'cal-week-day-events';
    dayEvents.forEach((event) => {
      const eventEl = document.createElement('div');
      eventEl.className = 'cal-event';
      eventEl.style.borderLeftColor = event.color || 'var(--accent)';
      const startTime = new Date(event.start).toLocaleTimeString(state.locale, { hour: '2-digit', minute: '2-digit' });
      eventEl.innerHTML = `<span class="cal-event-time">${startTime}</span> ${escapeHtml(event.title)}`;
      eventEl.dataset.eventNote = event.noteId || '';
      eventsContainer.appendChild(eventEl);
    });
    column.appendChild(eventsContainer);
    grid.appendChild(column);
  }
}

function renderDayView(grid, events, currentDate) {
  const dateStr = currentDate.toISOString().split('T')[0];
  const dayEvents = events.filter((event) => new Date(event.start).toISOString().split('T')[0] === dateStr);
  
  const header = document.createElement('div');
  header.className = 'cal-day-view-header';
  header.innerHTML = `
    <h3>${currentDate.toLocaleDateString(state.locale, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</h3>
    <span class="cal-day-event-count">${dayEvents.length} ${t('calEvents') || 'events'}</span>
  `;
  grid.appendChild(header);
  
  if (dayEvents.length === 0) {
    const empty = document.createElement('div');
    empty.className = 'cal-empty';
    empty.textContent = t('calNoEvents') || 'No events scheduled';
    grid.appendChild(empty);
    return;
  }
  
  dayEvents.sort((a, b) => new Date(a.start) - new Date(b.start)).forEach((event) => {
    const eventEl = document.createElement('div');
    eventEl.className = 'cal-event cal-event-day';
    eventEl.style.borderLeftColor = event.color || 'var(--accent)';
    const startTime = new Date(event.start).toLocaleTimeString(state.locale, { hour: '2-digit', minute: '2-digit' });
    const endTime = new Date(event.end).toLocaleTimeString(state.locale, { hour: '2-digit', minute: '2-digit' });
    eventEl.innerHTML = `
      <div class="cal-event-time">${startTime} - ${endTime}</div>
      <div class="cal-event-title">${escapeHtml(event.title)}</div>
      ${event.description ? `<div class="cal-event-desc">${escapeHtml(event.description)}</div>` : ''}
    `;
    grid.appendChild(eventEl);
  });
}

$('#cal-prev')?.addEventListener('click', () => {
  const current = state.calendarCurrentDate || new Date();
  if (state.calendarView === 'month') current.setMonth(current.getMonth() - 1);
  else if (state.calendarView === 'week') current.setDate(current.getDate() - 7);
  else current.setDate(current.getDate() - 1);
  state.calendarCurrentDate = current;
  loadCalendar();
});

$('#cal-next')?.addEventListener('click', () => {
  const current = state.calendarCurrentDate || new Date();
  if (state.calendarView === 'month') current.setMonth(current.getMonth() + 1);
  else if (state.calendarView === 'week') current.setDate(current.getDate() + 7);
  else current.setDate(current.getDate() + 1);
  state.calendarCurrentDate = current;
  loadCalendar();
});

$('#cal-today')?.addEventListener('click', () => {
  state.calendarCurrentDate = new Date();
  loadCalendar();
});

// Opens the calendar editor: for an existing event (noteId) or a fresh one on
// a given date. No noteId = create mode.
function openCalendarEditor(options = {}) {
  state.calendarEditingEvent = options.noteId || null;
  renderCalendarEditor(options.date || state.calendarCurrentDate || new Date());
}

$('#cal-new-event')?.addEventListener('click', () => openCalendarEditor({ date: state.calendarCurrentDate || new Date() }));

document.querySelectorAll('[data-cal-view]').forEach((btn) => {
  btn.addEventListener('click', () => {
    state.calendarView = btn.dataset.calView;
    syncCalendarViewSwitcher();
    loadCalendar();
  });
});

// Event chips (month/week views) open the editor instead of drilling to day
// view. Bound at the grid level so re-renders never lose the handler.
$('calendar-grid')?.addEventListener('click', (event) => {
  const chip = event.target.closest('[data-event-note]');
  if (!chip || !chip.dataset.eventNote) return;
  event.stopPropagation();
  openCalendarEditor({ noteId: chip.dataset.eventNote, date: state.calendarCurrentDate || new Date() });
});

/* ---------- Kanban board ---------- */




function renderMarkdownExportLanes() {
  const select = $('markdown-export-lane');
  if (!select) return;
  const previous = select.value;
  select.innerHTML = `<option value="all">${escapeHtml(t('markdownExportAll'))}</option>${state.categories.map((category) => `<option value="${escapeHtml(category.slug)}">${escapeHtml(category.name)}</option>`).join('')}`;
  if (previous) select.value = previous;
}

async function downloadMarkdownBundle(event) {
  event.preventDefault();
  setMessage('markdown-export-message');
  const params = new URLSearchParams();
  const lane = $('markdown-export-lane').value;
  const tag = $('markdown-export-tag').value.replace(/^#/, '').trim();
  if (lane && lane !== 'all') params.set('category', lane);
  if (tag) params.set('tag', tag);
  try {
    const response = await fetch(`/api/export/markdown?${params.toString()}`, { headers: { authorization: `Bearer ${state.token}` } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `planing-${lane && lane !== 'all' ? lane : (tag || 'notes')}.zip`;
    link.click();
    URL.revokeObjectURL(url);
    setMessage('markdown-export-message', t('markdownExportDone').replace('{count}', response.headers.get('x-note-count') || '0'));
  } catch (error) { setMessage('markdown-export-message', `${t('markdownExportFailed')} (${error.message})`); }
}

$('markdown-export-form').addEventListener('submit', downloadMarkdownBundle);

/* ---------- Alpine: chat + provider admin ---------- */
function chatApp() {
  return {
    sessions: [], sessionId: null, messages: [], prompts: [], promptId: '', draft: '', sending: false, providerName: '',
    contextOpen: false, contextRoots: [], rootId: '', rootPath: '', entries: [], contextFiles: [],
    async enter() {
      if (!state.token) return;
      if (!this.prompts.length) {
        try {
          this.prompts = await request('/api/prompts');
          const providers = await request('/api/providers').catch(() => []);
          const active = providers.find((provider) => provider.isActive);
          this.providerName = active ? `${active.name} · ${active.model}` : '';
        } catch { /* viewer without settings access still gets prompts */ }
      }
      if (!this.sessions.length) {
        try { this.sessions = await request('/api/chat/sessions'); } catch { /* ignore */ }
      }
      this.promptId = localStorage.getItem('planing-prompt') || '';
    },
    async newSession() {
      try {
        const session = await request('/api/chat/sessions', { method: 'POST', body: JSON.stringify({ promptId: this.promptId || undefined }) });
        this.sessions.unshift(session); this.sessionId = session.id; this.messages = [];
        // Attachments picked before the first message belong to the new chat.
        if (this.contextFiles.length) await this.persistContext();
      } catch (error) { setMessage('chat-message-status', error.message); }
    },
    async openSession(id) {
      try {
        const session = await request(`/api/chat/sessions/${encodeURIComponent(id)}`);
        this.sessionId = session.id; this.messages = session.messages; this.promptId = session.promptId || this.promptId;
        this.contextFiles = Array.isArray(session.contextFiles) ? session.contextFiles : [];
        document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
      } catch (error) { setMessage('chat-message-status', error.message); }
    },
    async savePromptChoice() {
      localStorage.setItem('planing-prompt', this.promptId);
      if (!this.sessionId) return;
      try { await request(`/api/chat/sessions/${encodeURIComponent(this.sessionId)}/messages`, { method: 'POST', body: JSON.stringify({ content: '__noop__' }) }); }
      catch { /* no-op placeholder is rejected server-side; choice persists client-side */ }
    },
    async send() {
      const content = this.draft.trim();
      if (!content || this.sending) return;
      setMessage('chat-message-status');
      if (!this.sessionId) await this.newSession();
      if (!this.sessionId) return;
      this.sending = true;
      const optimisticId = `pending-${Date.now()}`;
      this.messages.push({ id: optimisticId, role: 'user', content });
      this.draft = '';
      const scroller = document.getElementById('chat-messages');
      scroller.scrollTop = scroller.scrollHeight;
      try {
        const result = await request(`/api/chat/sessions/${encodeURIComponent(this.sessionId)}/messages`, { method: 'POST', body: JSON.stringify({ content, promptId: this.promptId || undefined, contextFiles: this.contextFiles }) });
        this.messages = this.messages.filter((message) => message.id !== optimisticId).concat([result.user, result.assistant]);
      } catch (error) {
        this.messages = this.messages.filter((message) => message.id !== optimisticId);
        setMessage('chat-message-status', error.message);
      } finally {
        this.sending = false;
        scroller.scrollTop = scroller.scrollHeight;
      }
    },
    async deleteSession() {
      if (!this.sessionId || !window.confirm(t('chatDeleteConfirm'))) return;
      try {
        await request(`/api/chat/sessions/${encodeURIComponent(this.sessionId)}`, { method: 'DELETE' });
        this.sessions = this.sessions.filter((session) => session.id !== this.sessionId);
        this.sessionId = null; this.messages = [];
      } catch (error) { setMessage('chat-message-status', error.message); }
    },
    rendered(content) {
      try { return renderMarkdown(content); } catch { return escapeHtml(content); }
    },
    t(key) { return t(key); },
    size(bytes) { return formatSize(bytes); },

    /* ---------- attached context: project + document files ---------- */
    contextStatus(message) { setMessage('chat-context-status', message); },
    async toggleContext() {
      this.contextOpen = !this.contextOpen;
      if (this.contextOpen && !this.contextRoots.length) await this.loadRoots();
    },
    async loadRoots() {
      try {
        this.contextRoots = await request('/api/context/roots');
        const first = this.contextRoots.find((root) => root.exists);
        if (first && !this.rootId) await this.openRoot(first.id);
      } catch (error) { this.contextStatus(error.message); }
    },
    async openRoot(id) {
      this.rootId = id; this.rootPath = ''; this.entries = [];
      await this.browse('');
    },
    async browse(path) {
      if (!this.rootId) return;
      try {
        const listing = await request(`/api/context/roots/${encodeURIComponent(this.rootId)}/tree?path=${encodeURIComponent(path || '')}`);
        this.rootPath = listing.path; this.entries = listing.entries;
      } catch (error) { this.contextStatus(error.message); }
    },
    async browseUp() {
      await this.browse(this.rootPath.split('/').slice(0, -1).join('/'));
    },
    contextLimit() { return Number(t('chatContextMaxFiles') || 12); },
    addContextRef(ref) {
      if (!ref || this.contextFiles.includes(ref)) return false;
      if (this.contextFiles.length >= this.contextLimit()) return false;
      this.contextFiles.push(ref);
      return true;
    },
    async toggleContextFile(ref) {
      if (this.contextFiles.includes(ref)) { await this.detachContext(ref); return; }
      if (!this.addContextRef(ref)) { this.contextStatus(t('chatContextLimit')); return; }
      await this.persistContext();
    },
    // Attaching a folder walks its tree (bounded by the same per-message limit)
    // so a whole project or notes directory can travel with one click.
    async attachFolder() {
      const queue = [this.rootPath];
      const picked = [];
      while (queue.length && this.contextFiles.length + picked.length < this.contextLimit()) {
        const current = queue.shift();
        let listing;
        try { listing = await request(`/api/context/roots/${encodeURIComponent(this.rootId)}/tree?path=${encodeURIComponent(current || '')}`); }
        catch { continue; }
        for (const entry of listing.entries) {
          if (this.contextFiles.length + picked.length >= this.contextLimit()) break;
          if (entry.type === 'dir') queue.push(entry.path);
          else if (entry.attachable && !this.contextFiles.includes(entry.ref) && !picked.includes(entry.ref)) picked.push(entry.ref);
        }
      }
      if (!picked.length) { this.contextStatus(t('chatContextEmpty')); return; }
      picked.forEach((ref) => this.addContextRef(ref));
      await this.persistContext();
      this.contextStatus(t('chatContextFolderAdded').replace('{count}', picked.length));
    },
    async detachContext(ref) {
      this.contextFiles = this.contextFiles.filter((entry) => entry !== ref);
      await this.persistContext();
    },
    async clearContext() {
      this.contextFiles = [];
      await this.persistContext();
    },
    // The session is the source of truth once it exists; before that the picks
    // simply travel with the first message that creates the session.
    async persistContext() {
      if (!this.sessionId) return;
      try {
        const result = await request(`/api/chat/sessions/${encodeURIComponent(this.sessionId)}/context`, { method: 'PATCH', body: JSON.stringify({ files: this.contextFiles }) });
        if (result.rejected) this.contextStatus(t('chatContextRejected').replace('{count}', result.rejected));
      } catch (error) { this.contextStatus(error.message); }
    },
    contextKind(entry) {
      return entry.kind || (entry.ref || entry.path || '').match(/\.([a-z0-9]+)$/i)?.[1] || '';
    },
    contextMark(entry) {
      if (entry.type === 'dir') return '▸';
      if (entry.kind === 'pdf') return '▤';
      if (entry.kind === 'image') return '▣';
      return this.contextFiles.includes(entry.ref) ? '◼' : '◻';
    },
    async saveAsNote(entry) {
      this.contextStatus('');
      try {
        const file = await request(`/api/context/roots/${encodeURIComponent(this.rootId)}/file?path=${encodeURIComponent(entry.path)}`);
        if (file.kind === 'image' || !String(file.content || '').trim()) {
          this.contextStatus(t('chatContextNoText').replace('{name}', entry.name));
          return;
        }
        await request('/api/notes', { method: 'POST', body: JSON.stringify({ content: file.content, category: state.selected || 'notes' }) });
        if (state.view === 'notes') await loadNotes();
        this.contextStatus(t('chatContextNoteSaved').replace('{name}', entry.name));
      } catch (error) { this.contextStatus(error.message); }
    },
  };
}

function promptAdmin() {
  return {
    prompts: [], editing: null,
    form: { id: '', title: '', body: '' },
    async load() {
      try { this.prompts = await request('/api/prompts'); } catch { this.prompts = []; }
      if (window.chatApp && !window.chatApp.prompts.length) window.chatApp.prompts = this.prompts;
    },
    edit(prompt) {
      this.editing = prompt.id;
      this.form = { id: prompt.id, title: prompt.title, body: prompt.body };
    },
    duplicate(prompt) {
      const base = `${prompt.id}-copy`;
      let id = base;
      let index = 2;
      while (this.prompts.some((entry) => entry.id === id)) { id = `${base}-${index}`; index += 1; }
      this.editing = null;
      this.form = { id, title: `${prompt.title} ${t('promptDuplicateSuffix')}`, body: prompt.body };
    },
    async save() {
      setMessage('prompt-message');
      try {
        if (this.editing) await request(`/api/prompts/${encodeURIComponent(this.editing)}`, { method: 'PATCH', body: JSON.stringify({ title: this.form.title, body: this.form.body }) });
        else await request('/api/prompts', { method: 'POST', body: JSON.stringify({ id: this.form.id, title: this.form.title, body: this.form.body }) });
        setMessage('prompt-message', t('promptSaved'));
        this.reset(); await this.load();
        if (window.chatApp) window.chatApp.prompts = this.prompts;
      } catch (error) { setMessage('prompt-message', error.message); }
    },
    async remove(prompt) {
      if (!window.confirm(t('promptDeleteConfirm'))) return;
      try {
        await request(`/api/prompts/${encodeURIComponent(prompt.id)}`, { method: 'DELETE' });
        setMessage('prompt-message', t('promptDeleted'));
        this.reset(); await this.load();
        if (window.chatApp) window.chatApp.prompts = this.prompts;
      } catch (error) { setMessage('prompt-message', error.message); }
    },
    reset() { this.editing = null; this.form = { id: '', title: '', body: '' }; },
  };
}

function contextRootsAdmin() {
  return {
    roots: [],
    async load() {
      try {
        // The workspace decides which roots are available, so the panel reads
        // the workspace view rather than the raw configured list.
        const workspaceId = state.activeWorkspace || 'default';
        const data = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/context-roots`);
        this.roots = (data.roots || []).map((root) => ({ ...root, enabled: root.enabled !== false }));
      } catch (error) {
        try { this.roots = (await request('/api/context/roots')).map((root) => ({ ...root, enabled: true })); }
        catch (inner) { setMessage('context-root-message', inner.message); }
      }
    },
    async toggleRoot(root) {
      const next = this.roots.map((entry) => (entry.id === root.id ? !entry.enabled : entry.enabled));
      this.roots = this.roots.map((entry, index) => ({ ...entry, enabled: next[index] }));
      setMessage('context-root-message');
      try {
        const workspaceId = state.activeWorkspace || 'default';
        const data = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/context-roots`, {
          method: 'PATCH',
          body: JSON.stringify({ roots: this.roots.filter((entry) => entry.enabled).map((entry) => entry.id) }),
        });
        this.roots = (data.roots || []).map((entry) => ({ ...entry, enabled: entry.enabled !== false }));
        if (window.chatApp) { window.chatApp.contextRoots = []; window.chatApp.rootId = ''; }
      } catch (error) {
        setMessage('context-root-message', error.message);
        await this.load();
      }
    },
    t(key) { return t(key); },
  };
}

// Settings → AI: per-workspace provider policy (allow-list, default, cap)
// plus the usage/cost summary for the run ledger.
function aiPolicyAdmin() {
  return {
    policy: { allowedProviders: [], defaultProvider: null, runCap: null, monthlyBudgetMicros: null },
    providers: [],
    usage: null,
    capInput: '',
    budgetInput: '',
    async load() {
      try {
        this.policy = await request('/api/ai/policy');
        this.providers = this.policy.providers || [];
        this.usage = this.policy.usage || null;
        this.capInput = this.policy.runCap ? String(this.policy.runCap) : '';
        this.budgetInput = this.policy.monthlyBudgetMicros ? String(this.policy.monthlyBudgetMicros / 1_000_000) : '';
      } catch { this.policy = { allowedProviders: [], defaultProvider: null, runCap: null, monthlyBudgetMicros: null }; this.providers = []; this.usage = null; this.budgetInput = ''; }
    },
    cost(micros) {
      const value = (Number(micros) || 0) / 1_000_000;
      if (!value) return '0';
      return value >= 0.01 ? value.toFixed(2) : value.toFixed(4);
    },
    async toggleProvider(provider) {
      const next = this.providers.filter((entry) => entry.id !== provider.id && entry.allowed).map((entry) => entry.id);
      if (!provider.allowed) next.push(provider.id);
      setMessage('ai-policy-message');
      try {
        this.policy = await request('/api/ai/policy', { method: 'PATCH', body: JSON.stringify({ allowedProviders: next }) });
        this.providers = (this.policy.providers || []).map((entry) => ({ ...entry, allowed: entry.allowed }));
        setMessage('ai-policy-message', t('aiPolicySaved'));
      } catch (error) { setMessage('ai-policy-message', error.message); await this.load(); }
    },
    async setDefault(provider) {
      setMessage('ai-policy-message');
      try {
        this.policy = await request('/api/ai/policy', { method: 'PATCH', body: JSON.stringify({ defaultProvider: provider.id }) });
        setMessage('ai-policy-message', t('aiPolicySaved'));
      } catch (error) { setMessage('ai-policy-message', error.message); }
    },
    async saveCap() {
      setMessage('ai-policy-message');
      const raw = this.capInput.trim();
      const budgetRaw = this.budgetInput.trim();
      const budgetMicros = budgetRaw === '' ? null : Math.round(Number(budgetRaw) * 1_000_000);
      try {
        this.policy = await request('/api/ai/policy', { method: 'PATCH', body: JSON.stringify({ runCap: raw ? Number(raw) : null, monthlyBudgetMicros: budgetMicros }) });
        this.usage = this.policy.usage || this.usage;
        setMessage('ai-policy-message', t('aiPolicySaved'));
      } catch (error) { setMessage('ai-policy-message', error.message); }
    },
    async clearLimits() {
      setMessage('ai-policy-message');
      this.capInput = '';
      this.budgetInput = '';
      try {
        this.policy = await request('/api/ai/policy', { method: 'PATCH', body: JSON.stringify({ runCap: null, monthlyBudgetMicros: null }) });
        setMessage('ai-policy-message', t('aiPolicySaved'));
      } catch (error) { setMessage('ai-policy-message', error.message); }
    },
    t(key) { return t(key); },
  };
}

// Settings → AI: the run ledger for the active workspace.
function aiRunsAdmin() {
  return {
    runs: [],
    async load() {
      try { this.runs = await request('/api/ai/runs?limit=100'); } catch { this.runs = []; }
    },
    cost(micros) {
      const value = (Number(micros) || 0) / 1_000_000;
      if (!value) return '0';
      return value >= 0.01 ? value.toFixed(2) : value.toFixed(4);
    },
    t(key) { return t(key); },
  };
}

// Settings → AI: queued AI runs with cancel.
function aiJobsAdmin() {
  return {
    jobs: [],
    async load() {
      try { this.jobs = await request('/api/ai/jobs'); } catch { this.jobs = []; }
    },
    async cancel(job) {
      setMessage('ai-jobs-message');
      try {
        await request(`/api/ai/jobs/${encodeURIComponent(job.id)}/cancel`, { method: 'POST', body: JSON.stringify({}) });
        setMessage('ai-jobs-message', t('aiJobCancelled'));
        await this.load();
      } catch (error) { setMessage('ai-jobs-message', error.message); }
    },
    t(key) { return t(key); },
  };
}

function providerAdmin() {
  return {
    providers: [], editing: null,
    form: { name: '', baseUrl: '', model: '', apiKey: '', activate: false },
    async load() {
      try { this.providers = await request('/api/providers'); } catch { this.providers = []; }
    },
    async save() {
      setMessage('provider-message');
      try {
        const body = { name: this.form.name, baseUrl: this.form.baseUrl, model: this.form.model, activate: this.form.activate };
        if (this.form.apiKey) body.apiKey = this.form.apiKey;
        if (this.editing) await request(`/api/providers/${encodeURIComponent(this.editing)}`, { method: 'POST', body: JSON.stringify(body) });
        else await request('/api/providers', { method: 'POST', body: JSON.stringify(body) });
        setMessage('provider-message', t('providerSaved'));
        this.reset(); await this.load();
      } catch (error) { setMessage('provider-message', error.message); }
    },
    edit(provider) {
      this.editing = provider.id;
      this.form = { name: provider.id, baseUrl: provider.baseUrl, model: provider.model, apiKey: '', activate: provider.isActive };
    },
    async activate(provider) {
      try { await request(`/api/providers/${encodeURIComponent(provider.id)}/active`, { method: 'PATCH' }); await this.load(); }
      catch (error) { setMessage('provider-message', error.message); }
    },
    async verify() {
      setMessage('provider-message');
      try {
        const result = await request(`/api/providers/${encodeURIComponent(this.editing)}/verify`, { method: 'POST', body: '{}' });
        setMessage('provider-message', result.ok ? t('providerVerified') : `${t('providerVerifyFailed')} (${result.status || 'unreachable'})`);
      } catch (error) { setMessage('provider-message', error.message); }
    },
    async remove() {
      if (!this.editing || !window.confirm(t('providerDeleteConfirm'))) return;
      try { await request(`/api/providers/${encodeURIComponent(this.editing)}`, { method: 'DELETE' }); this.reset(); await this.load(); }
      catch (error) { setMessage('provider-message', error.message); }
    },
    reset() {
      this.editing = null;
      this.form = { name: '', baseUrl: '', model: '', apiKey: '', activate: false };
    },
  };
}

// Alpine evaluates x-data expressions in global scope, so the component
// factories must be reachable from window (they live in this module's scope).
window.planingChatApp = chatApp;
window.planingProviderAdmin = providerAdmin;
window.planingPromptAdmin = promptAdmin;
window.planingContextRoots = contextRootsAdmin;
window.planingAiPolicy = aiPolicyAdmin;
window.planingAiRuns = aiRunsAdmin;
window.planingAiJobs = aiJobsAdmin;

/* ---------- Boot ---------- */
(async () => {
  state.isFirstAdmin = await isFirstAdminPending();
  renderAuth();
})();
refreshStorageStatus();
if (state.token) enterApp().catch(() => { localStorage.removeItem('planing-token'); state.token = null; });
applyLocale();
