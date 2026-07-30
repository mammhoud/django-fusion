import { useState, useMemo, useCallback, useEffect, useRef } from 'react';
import PageLayout from '../../components/layout/PageLayout';
import Card from '../../components/layout/Card';
import ColorSlider from '../../components/display/ColorSlider';
import {
  type OKLCHValue,
  type ThemeColorSet,
  type SavedTheme,
  getDefaultThemeColors,
  generateCustomCSSVars,
  generateThemeCSS,
  formatOKLCH,
  computeContrast,
  COLOR_LABELS,
  MAIN_COLOR_KEYS,
  BASE_COLOR_KEYS,
  STUDIO_THEMES,
  loadSavedThemes,
  saveTheme,
  deleteSavedTheme,
} from '../../utils/themeStudio';
import ThemePreviewModal from '../../components/display/ThemePreviewModal';

// ── Section wrapper for the component preview ──
function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-8">
      <h3 className="text-base font-bold text-base-content mb-3 flex items-center gap-2">
        <span className="w-1 h-4 rounded-full bg-primary" />
        {title}
      </h3>
      {children}
    </section>
  );
}

// ── Live WCAG contrast badge ──
function ContrastBadge({
  color,
  contentColor,
}: {
  color: OKLCHValue;
  contentColor: OKLCHValue;
}) {
  const { ratio, grade } = useMemo(() => computeContrast(color, contentColor), [color, contentColor]);

  const bgColor = formatOKLCH(color.l, color.c, color.h);
  const textColor = formatOKLCH(contentColor.l, contentColor.c, contentColor.h);

  // Grade indicator icons
  const gradeMeta =
    grade === 'AAA'
      ? { icon: 'tabler--shield-check', label: 'AAA' }
      : grade === 'AA'
        ? { icon: 'tabler--shield-check', label: 'AA' }
        : grade === 'AA Lg'
          ? { icon: 'tabler--shield-half', label: 'AA Lg' }
          : { icon: 'tabler--shield-x', label: 'Fail' };

  return (
    <span
      className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold leading-none border border-black/10 dark:border-white/10"
      style={{
        backgroundColor: bgColor,
        color: textColor,
      }}
      title={`Contrast ratio: ${ratio.toFixed(2)}:1 — ${grade}${grade === 'AA' ? ' (normal text ≥4.5:1)' : grade === 'AA Lg' ? ' (large text ≥3:1)' : grade === 'Fail' ? ' — fails all WCAG SC 1.4.3 thresholds' : ' (enhanced ≥7:1)'}`}
    >
      <span className={`icon-[${gradeMeta.icon}] w-2.5 h-2.5`} />
      <span>{gradeMeta.label}</span>
      <span className="opacity-60 font-normal">{ratio.toFixed(1)}:1</span>
    </span>
  );
}

// ── Color group editor (one semantic color + its content color) ──
function ColorGroupEditor({
  token,
  color,
  contentColor,
  onColorChange,
  onContentChange: _onContentChange,
}: {
  token: string;
  color: OKLCHValue;
  contentColor: OKLCHValue;
  onColorChange: (c: OKLCHValue) => void;
  onContentChange: (c: OKLCHValue) => void;
}) {
  const label = COLOR_LABELS[token as keyof typeof COLOR_LABELS] || token;
  const contentLabel = COLOR_LABELS[`${token}-content` as keyof typeof COLOR_LABELS] || `${label} Text`;
  const swatchColor = formatOKLCH(color.l, color.c, color.h);
  const contentSwatch = formatOKLCH(contentColor.l, contentColor.c, contentColor.h);

  return (
    <div className="border border-base-300/50 rounded-xl p-3 bg-base-100/50">
      {/* Header with swatches */}
      <div className="flex items-center gap-3 mb-2">
        {/* Main color swatch */}
        <div
          className="w-8 h-8 rounded-lg shadow-sm shrink-0 border border-base-300"
          style={{ backgroundColor: swatchColor }}
        />
        <div className="flex-1 min-w-0">
          <span className="text-sm font-semibold text-base-content block truncate">{label}</span>
          <div className="flex items-center gap-1.5 mt-0.5">
            {/* Content color mini swatch */}
            <div
              className="w-3.5 h-3.5 rounded-sm shrink-0 border border-base-300"
              style={{ backgroundColor: contentSwatch }}
            />
            <span className="text-[10px] text-base-content/50 mr-2">{contentLabel}</span>
            {/* Live WCAG contrast badge */}
            <ContrastBadge color={color} contentColor={contentColor} />
          </div>
        </div>
      </div>

      {/* L slider */}
      <ColorSlider
        label="L"
        value={color.l}
        min={0}
        max={100}
        step={0.1}
        suffix="%"
        trackColor={swatchColor}
        onChange={(v) => onColorChange({ ...color, l: v })}
      />

      {/* C slider */}
      <ColorSlider
        label="C"
        value={color.c}
        min={0}
        max={0.4}
        step={0.001}
        suffix=""
        trackColor={swatchColor}
        onChange={(v) => onColorChange({ ...color, c: v })}
      />

      {/* H slider */}
      <ColorSlider
        label="H"
        value={color.h}
        min={0}
        max={360}
        step={0.1}
        suffix="°"
        trackColor={swatchColor}
        onChange={(v) => onColorChange({ ...color, h: v })}
      />
    </div>
  );
}

// ── Helper to create a color editor for a base surface token ──
function BaseColorEditor({
  token,
  color,
  onChange,
}: {
  token: string;
  color: OKLCHValue;
  onChange: (c: OKLCHValue) => void;
}) {
  const label = COLOR_LABELS[token as keyof typeof COLOR_LABELS] || token;
  const swatchColor = formatOKLCH(color.l, color.c, color.h);

  return (
    <div className="border border-base-300/50 rounded-xl p-3 bg-base-100/50">
      <div className="flex items-center gap-3 mb-2">
        <div
          className="w-8 h-8 rounded-lg shadow-sm shrink-0 border border-base-300"
          style={{ backgroundColor: swatchColor }}
        />
        <span className="text-sm font-semibold text-base-content">{label}</span>
      </div>
      <ColorSlider label="L" value={color.l} min={0} max={100} step={0.1} suffix="%" trackColor={swatchColor} onChange={(v) => onChange({ ...color, l: v })} />
      <ColorSlider label="C" value={color.c} min={0} max={0.4} step={0.001} suffix="" trackColor={swatchColor} onChange={(v) => onChange({ ...color, c: v })} />
      <ColorSlider label="H" value={color.h} min={0} max={360} step={0.1} suffix="°" trackColor={swatchColor} onChange={(v) => onChange({ ...color, h: v })} />
    </div>
  );
}

// ── Component Preview Section ──
function ComponentPreview({ themeKey, customVars }: { themeKey: string; customVars: Record<string, string> }) {
  const [previewTab, setPreviewTab] = useState(0);
  const tabs = ['All Items', 'Beverages', 'Food', 'Specials'];

  return (
    <div data-theme={themeKey} style={customVars as React.CSSProperties}>
      {/* Buttons */}
      <Section title="Buttons">
        <Card className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn btn-primary">Primary</button>
            <button type="button" className="btn btn-secondary">Secondary</button>
            <button type="button" className="btn btn-accent">Accent</button>
            <button type="button" className="btn btn-info">Info</button>
            <button type="button" className="btn btn-success">Success</button>
            <button type="button" className="btn btn-warning">Warning</button>
            <button type="button" className="btn btn-error">Error</button>
            <button type="button" className="btn btn-neutral">Neutral</button>
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" className="btn btn-soft btn-primary">Soft</button>
            <button type="button" className="btn btn-outline btn-primary">Outline</button>
            <button type="button" className="btn btn-ghost">Ghost</button>
            <button type="button" className="btn btn-dash">Dash</button>
            <button type="button" className="btn btn-primary" disabled>Disabled</button>
            <button type="button" className="btn btn-primary btn-active">Active</button>
            <button type="button" className="btn btn-primary btn-glass">Glass</button>
          </div>
        </Card>
      </Section>

      {/* Form Controls */}
      <Section title="Forms">
        <Card>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="label"><span className="label-text">Text Input</span></label>
              <input type="text" className="input input-bordered w-full" placeholder="Sample" defaultValue="Editable text" />
            </div>
            <div>
              <label className="label"><span className="label-text">Select</span></label>
              <select className="select select-bordered w-full">
                <option>Option 1</option>
                <option>Option 2</option>
              </select>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <label className="flex items-center gap-2"><input type="checkbox" className="checkbox checkbox-primary" defaultChecked /><span className="text-sm">Checkbox</span></label>
            <label className="flex items-center gap-2"><input type="radio" name="studio-radio" className="radio radio-primary" defaultChecked /><span className="text-sm">Radio</span></label>
            <label className="flex items-center gap-2"><span className="text-sm">Toggle</span><input type="checkbox" className="toggle toggle-primary" defaultChecked /></label>
          </div>
        </Card>
      </Section>

      {/* Alerts */}
      <Section title="Alerts">
        <div className="space-y-2">
          <div role="alert" className="alert alert-info"><span className="icon-[tabler--info-circle] w-5 h-5" /><span>Info alert — general information</span></div>
          <div role="alert" className="alert alert-success"><span className="icon-[tabler--check] w-5 h-5" /><span>Success — operation completed</span></div>
          <div role="alert" className="alert alert-warning"><span className="icon-[tabler--alert-triangle] w-5 h-5" /><span>Warning — please review</span></div>
          <div role="alert" className="alert alert-error"><span className="icon-[tabler--alert-circle] w-5 h-5" /><span>Error — something went wrong</span></div>
        </div>
      </Section>

      {/* Tabs */}
      <Section title="Tabs">
        <div className="tabs tabs-boxed gap-1 mb-3" role="tablist">
          {tabs.map((tab, i) => (
            <button key={tab} type="button" role="tab" className={`tab ${i === previewTab ? 'tab-active' : ''}`} onClick={() => setPreviewTab(i)}>{tab}</button>
          ))}
        </div>
        <div className="tabs tabs-lifted" role="tablist">
          {tabs.map((tab, i) => (
            <button key={tab} type="button" role="tab" className={`tab ${i === previewTab ? 'tab-active' : ''}`} onClick={() => setPreviewTab(i)}>{tab}</button>
          ))}
        </div>
      </Section>

      {/* Stats */}
      <Section title="Stats">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="stat"><div className="stat-title">Revenue</div><div className="stat-value text-primary">$12,450</div><div className="stat-desc"><span className="text-success">▲ 12.5%</span> vs last month</div></div>
          <div className="stat"><div className="stat-title">Orders</div><div className="stat-value text-secondary">84</div><div className="stat-desc"><span className="text-success">▲ 8.3%</span> vs yesterday</div></div>
          <div className="stat"><div className="stat-title">Avg Order</div><div className="stat-value text-accent">$24.50</div><div className="stat-desc"><span className="text-warning">→ 0.0%</span> unchanged</div></div>
          <div className="stat"><div className="stat-title">Tables</div><div className="stat-value text-info">12</div><div className="stat-desc"><span className="text-error">▼ 2</span> from peak</div></div>
        </div>
      </Section>

      {/* Badges */}
      <Section title="Badges">
        <div className="flex flex-wrap gap-2">
          <span className="badge badge-primary">Primary</span>
          <span className="badge badge-soft badge-secondary">Soft</span>
          <span className="badge badge-outline badge-accent">Outline</span>
          <span className="badge badge-success">Success</span>
          <span className="badge badge-warning">Warning</span>
          <span className="badge badge-error">Error</span>
          <span className="badge badge-neutral">Neutral</span>
        </div>
      </Section>

      {/* Progress */}
      <Section title="Progress">
        <div className="space-y-2">
          <progress className="progress progress-primary w-full" value={70} max={100} />
          <progress className="progress progress-success w-full" value={45} max={100} />
          <progress className="progress progress-error w-full" value={20} max={100} />
        </div>
      </Section>

      {/* Table */}
      <Section title="Table">
        <Card className="overflow-hidden p-0">
          <table className="table w-full">
            <thead>
              <tr><th>Name</th><th>Category</th><th>Price</th><th>Status</th></tr>
            </thead>
            <tbody>
              <tr><td className="font-medium">Classic Burger</td><td>Burgers</td><td>$12.99</td><td><span className="badge badge-success badge-sm">Active</span></td></tr>
              <tr><td className="font-medium">Margherita Pizza</td><td>Pizza</td><td>$15.50</td><td><span className="badge badge-success badge-sm">Active</span></td></tr>
              <tr><td className="font-medium">Caesar Salad</td><td>Salads</td><td>$9.99</td><td><span className="badge badge-warning badge-sm">Seasonal</span></td></tr>
            </tbody>
          </table>
        </Card>
      </Section>

      {/* Loading */}
      <Section title="Loading">
        <div className="flex flex-wrap items-center gap-3">
          <span className="loading loading-spinner loading-sm text-primary" />
          <span className="loading loading-spinner loading-md text-secondary" />
          <span className="loading loading-dots loading-md text-accent" />
          <span className="loading loading-ring loading-md text-info" />
          <span className="loading loading-infinity loading-md text-success" />
        </div>
      </Section>
    </div>
  );
}

// ── Main ThemeStudio Page ──
export default function ThemeStudio() {
  const [selectedTheme, setSelectedTheme] = useState<string>(() => {
    return localStorage.getItem('theme-studio-key') || 'corporate-light';
  });
  const [customColors, setCustomColors] = useState<ThemeColorSet>(() => {
    const saved = localStorage.getItem('theme-studio-custom');
    if (saved) {
      try { return JSON.parse(saved) as ThemeColorSet; } catch { /* corrupt */ localStorage.removeItem('theme-studio-custom'); }
    }
    return getDefaultThemeColors('corporate-light');
  });
  const [showSurfaces, setShowSurfaces] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [savedThemes, setSavedThemes] = useState<SavedTheme[]>(() => loadSavedThemes());
  const [_showSaveDialog, setShowSaveDialog] = useState(false); // eslint-disable-line
  const [saveName, setSaveName] = useState('');
  const [showSavedDropdown, setShowSavedDropdown] = useState(false);
  const [_showExportDialog, setShowExportDialog] = useState(false);
  const [exportCSS, setExportCSS] = useState('');
  const [copied, setCopied] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const saveDialogRef = useRef<HTMLDialogElement>(null);
  const exportDialogRef = useRef<HTMLDialogElement>(null);

  // Load default colors when theme changes (with unsaved-work guard)
  const handleThemeChange = useCallback((themeKey: string) => {
    if (hasUnsavedChanges && !window.confirm('Discard unsaved color changes and switch theme?')) return;
    setSelectedTheme(themeKey);
    setCustomColors(getDefaultThemeColors(themeKey));
    setHasUnsavedChanges(false);
  }, [hasUnsavedChanges]);

  // Update a single token's color
  const updateColor = useCallback((token: string, newColor: OKLCHValue) => {
    setCustomColors(prev => ({
      ...prev,
      [token]: newColor,
    }));
    setHasUnsavedChanges(true);
  }, []);

  // Open save dialog — auto-fill name if editing a saved theme
  const openSaveDialog = useCallback(() => {
    setSaveName('');
    setShowSaveDialog(true);
    setTimeout(() => saveDialogRef.current?.showModal(), 50);
  }, []);

  // Confirm save
  const handleSaveConfirm = useCallback(() => {
    const trimmed = saveName.trim();
    if (!trimmed) return;
    const updated = saveTheme(trimmed, selectedTheme, customColors);
    setSavedThemes(updated);
    setShowSaveDialog(false);
    saveDialogRef.current?.close();
  }, [saveName, selectedTheme, customColors]);

  // Load a saved theme's colors into the editor
  const handleLoadSavedTheme = useCallback((theme: SavedTheme) => {
    if (hasUnsavedChanges && !window.confirm('Discard unsaved changes and load saved theme?')) return;
    setSelectedTheme(theme.baseThemeKey);
    setCustomColors(theme.colors);
    setHasUnsavedChanges(false);
    setShowSavedDropdown(false);
  }, [hasUnsavedChanges]);

  // Delete a saved theme
  const handleDeleteSaved = useCallback((name: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm(`Delete saved theme "${name}"?`)) return;
    const updated = deleteSavedTheme(name);
    setSavedThemes(updated);
  }, []);

  // Open export dialog — generate CSS block from current colors
  const openExportDialog = useCallback(() => {
    const css = generateThemeCSS(customColors, selectedTheme);
    setExportCSS(css);
    setCopied(false);
    setShowExportDialog(true);
    setTimeout(() => exportDialogRef.current?.showModal(), 50);
  }, [customColors, selectedTheme]);

  // Copy CSS to clipboard
  const handleCopyCSS = useCallback(() => {
    navigator.clipboard.writeText(exportCSS).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }).catch(() => {
      // Fallback: select the textarea content
      const textarea = exportDialogRef.current?.querySelector('textarea');
      if (textarea) {
        textarea.select();
        document.execCommand('copy');
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    });
  }, [exportCSS]);

  // Generate CSS vars for the preview
  const customCSSVars = useMemo(() => generateCustomCSSVars(customColors), [customColors]);

  // Reset to defaults
  const handleReset = useCallback(() => {
    setCustomColors(getDefaultThemeColors(selectedTheme));
    setHasUnsavedChanges(false);
  }, [selectedTheme]);

  // Apply custom colors — persists to localStorage + sets CSS vars on :root
  const handleApply = useCallback(() => {
    const root = document.documentElement;
    const vars = generateCustomCSSVars(customColors);
    for (const [key, value] of Object.entries(vars)) {
      root.style.setProperty(key, value);
    }
    localStorage.setItem('theme-studio-custom', JSON.stringify(customColors));
    localStorage.setItem('theme-studio-key', selectedTheme);
    setHasUnsavedChanges(false);
  }, [customColors, selectedTheme]);

  // Apply saved CSS vars to :root on mount (state already initialized from localStorage)
  useEffect(() => {
    const saved = localStorage.getItem('theme-studio-custom');
    if (saved) {
      try {
        const colors = JSON.parse(saved) as ThemeColorSet;
        const root = document.documentElement;
        for (const [key, value] of Object.entries(generateCustomCSSVars(colors))) {
          root.style.setProperty(key, value);
        }
      } catch {
        localStorage.removeItem('theme-studio-custom');
        localStorage.removeItem('theme-studio-key');
      }
    }
  }, []);

  // Group main editor keys into pairs (color + content)
  const colorPairs: { token: string; contentToken: string }[] = [];
  for (let i = 0; i < MAIN_COLOR_KEYS.length; i += 2) {
    const token = MAIN_COLOR_KEYS[i];
    const contentToken = MAIN_COLOR_KEYS[i + 1];
    if (contentToken && contentToken.includes('content')) {
      colorPairs.push({ token, contentToken });
    }
  }

  return (
    <PageLayout
      title="Theme Studio"
      background="bg-base-200/50"
      padding="py-6"
    >
      <div className="max-w-7xl mx-auto">
        {/* ── Top Bar: Theme selector + actions ── */}
        <Card className="mb-6 shadow-md border border-base-300" padding="md">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="icon-[tabler--paint] w-6 h-6 text-primary" />
              <div>
                <h1 className="text-xl font-bold text-base-content">Theme Studio</h1>
                <p className="text-sm text-base-content/60">
                  Customize OKLCH color values and preview changes live
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3 flex-wrap">
              {/* Theme selector */}
              {/* Light themes */}
              <div className="flex items-center gap-1 bg-base-300/50 rounded-lg p-0.5">
                {STUDIO_THEMES.filter(t => t.id.includes('light') || t.id === 'light').map(t => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => handleThemeChange(t.id)}
                    className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                      selectedTheme === t.id
                        ? 'bg-base-100 text-base-content shadow-sm'
                        : 'text-base-content/50 hover:text-base-content'
                    }`}
                  >
                    <span className={`icon-[${t.icon}] w-3.5 h-3.5 mr-1`} />{t.label.split(' ')[0]}
                  </button>
                ))}
              </div>
              {/* Dark themes */}
              <div className="flex items-center gap-1 bg-base-300/50 rounded-lg p-0.5">
                {STUDIO_THEMES.filter(t => t.id.includes('dark') || t.id === 'dark' || t.id === 'cyberpunk').map(t => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => handleThemeChange(t.id)}
                    className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-all ${
                      selectedTheme === t.id
                        ? 'bg-base-100 text-base-content shadow-sm'
                        : 'text-base-content/50 hover:text-base-content'
                    }`}
                  >
                    <span className={`icon-[${t.icon}] w-3.5 h-3.5 mr-1`} />{t.label.split(' ')[0]}
                  </button>
                ))}
              </div>
              {/* Saved themes dropdown */}
              {savedThemes.length > 0 && (
                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setShowSavedDropdown(!showSavedDropdown)}
                    className="btn btn-ghost btn-sm gap-1.5"
                    title="Switch saved theme"
                  >
                    <span className="icon-[tabler--bookmark] w-4 h-4" />
                    <span className="hidden sm:inline text-xs">Saved</span>
                    <span className="badge badge-xs badge-soft badge-primary">{savedThemes.length}</span>
                  </button>
                  {showSavedDropdown && (
                    <>
                      <div className="fixed inset-0 z-40" onClick={() => setShowSavedDropdown(false)} />
                      <div className="absolute right-0 top-full mt-1 w-64 z-50 bg-base-100 border border-base-300 rounded-xl shadow-xl overflow-hidden">
                        <div className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-base-content/40 border-b border-base-300/50">
                          Saved Themes
                        </div>
                        <div className="py-1 max-h-48 overflow-y-auto">
                          {savedThemes.map(t => (
                            <button
                              key={t.name}
                              type="button"
                              onClick={() => handleLoadSavedTheme(t)}
                              className="w-full flex items-center gap-3 px-3 py-2 text-xs text-left
                                hover:bg-base-200/50 transition-colors group"
                            >
                              <span className="icon-[tabler--palette] w-3.5 h-3.5 text-primary/60 shrink-0" />
                              <span className="flex-1 truncate font-medium text-base-content">{t.name}</span>
                              <span className="badge badge-soft badge-xs text-[9px]">{t.baseThemeKey}</span>
                              <button
                                type="button"
                                onClick={(e) => handleDeleteSaved(t.name, e)}
                                className="opacity-0 group-hover:opacity-100 text-base-content/30 hover:text-error transition-all"
                                title={`Delete "${t.name}"`}
                              >
                                <span className="icon-[tabler--trash] w-3.5 h-3.5" />
                              </button>
                            </button>
                          ))}
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setShowPreview(true)}
                  className="btn btn-ghost btn-sm gap-1.5"
                  title="Preview theme components"
                >
                  <span className="icon-[tabler--eye] w-4 h-4" />
                  <span className="hidden sm:inline">Preview</span>
                </button>
                <button
                  type="button"
                  onClick={openExportDialog}
                  className="btn btn-ghost btn-sm gap-1.5"
                  title="Export as CSS theme block"
                >
                  <span className="icon-[tabler--code] w-4 h-4" />
                  <span className="hidden sm:inline">Export CSS</span>
                </button>
                <button
                  type="button"
                  onClick={openSaveDialog}
                  className="btn btn-ghost btn-sm gap-1.5"
                  title="Save current colors as a named theme"
                >
                  <span className="icon-[tabler--bookmark-plus] w-4 h-4" />
                  <span className="hidden sm:inline">Save</span>
                </button>
                <button
                  type="button"
                  onClick={handleReset}
                  className="btn btn-ghost btn-sm gap-1.5"
                >
                  <span className="icon-[tabler--refresh] w-4 h-4" />
                  Reset
                </button>
                <button
                  type="button"
                  onClick={handleApply}
                  disabled={!hasUnsavedChanges}
                  className="btn btn-primary btn-sm gap-1.5"
                >
                  <span className="icon-[tabler--device-floppy] w-4 h-4" />
                  Apply
                </button>
              </div>
            </div>
          </div>
          <div className="mt-3 flex items-center gap-2 text-xs text-base-content/50">
            <span className="badge badge-soft badge-primary badge-sm font-mono">{selectedTheme}</span>
            {hasUnsavedChanges && (
              <span className="badge badge-soft badge-warning badge-sm">
                <span className="icon-[tabler--edit] w-3 h-3 mr-1" />
                Unsaved changes
              </span>
            )}
          </div>
        </Card>

        {/* ── Save Dialog ── */}
        <dialog ref={saveDialogRef} className="modal">
          <div className="modal-box max-w-sm">
            <h3 className="font-bold text-lg text-base-content flex items-center gap-2 mb-4">
              <span className="icon-[tabler--bookmark-plus] w-5 h-5 text-primary" />
              Save Custom Theme
            </h3>
            <div className="space-y-4">
              <div>
                <label className="label">
                  <span className="label-text font-medium">Theme Name</span>
                </label>
                <input
                  type="text"
                  value={saveName}
                  onChange={e => setSaveName(e.target.value)}
                  placeholder="e.g. My Warm Theme"
                  className="input input-bordered w-full"
                  autoFocus
                  onKeyDown={e => e.key === 'Enter' && handleSaveConfirm()}
                />
              </div>
              <div className="flex items-center gap-2 text-xs text-base-content/50">
                <span className="icon-[tabler--info-circle] w-3.5 h-3.5" />
                Based on theme: <span className="badge badge-soft badge-primary badge-sm font-mono">{selectedTheme}</span>
              </div>
            </div>
            <div className="modal-action">
              <button
                type="button"
                onClick={() => { setShowSaveDialog(false); saveDialogRef.current?.close(); }}
                className="btn btn-ghost btn-sm"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveConfirm}
                disabled={!saveName.trim()}
                className="btn btn-primary btn-sm gap-1.5"
              >
                <span className="icon-[tabler--device-floppy] w-4 h-4" />
                Save Theme
              </button>
            </div>
          </div>
          <form method="dialog" className="modal-backdrop">
            <button type="button" onClick={() => { setShowSaveDialog(false); saveDialogRef.current?.close(); }}>close</button>
          </form>
        </dialog>

        {/* ── Export CSS Dialog ── */}
        <dialog ref={exportDialogRef} className="modal">
          <div className="modal-box max-w-2xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-lg text-base-content flex items-center gap-2">
                <span className="icon-[tabler--code] w-5 h-5 text-primary" />
                Export Theme as CSS
              </h3>
              <span className="badge badge-soft badge-primary badge-sm font-mono">{selectedTheme}</span>
            </div>
            <p className="text-sm text-base-content/60 mb-4">
              Paste this <code className="text-primary font-mono text-xs">@plugin "flyonui/theme"</code> block into your
              <code className="text-primary font-mono text-xs"> index.css</code> to register this as a permanent FlyonUI theme variant.
            </p>
            <div className="relative">
              <textarea
                readOnly
                value={exportCSS}
                className="textarea textarea-bordered w-full font-mono text-xs leading-relaxed p-4 h-80"
                onClick={e => (e.target as HTMLTextAreaElement).select()}
              />
              <button
                type="button"
                onClick={handleCopyCSS}
                className={`absolute top-3 right-3 btn btn-sm gap-1.5 ${copied ? 'btn-success' : 'btn-ghost'}`}
              >
                {copied ? (
                  <><span className="icon-[tabler--check] w-4 h-4" /> Copied!</>
                ) : (
                  <><span className="icon-[tabler--copy] w-4 h-4" /> Copy</>
                )}
              </button>
            </div>
            <div className="modal-action">
              <button
                type="button"
                onClick={() => { setShowExportDialog(false); exportDialogRef.current?.close(); }}
                className="btn btn-ghost btn-sm"
              >
                Close
              </button>
            </div>
          </div>
          <form method="dialog" className="modal-backdrop">
            <button type="button" onClick={() => { setShowExportDialog(false); exportDialogRef.current?.close(); }}>close</button>
          </form>
        </dialog>

        {/* ── Split Panel ── */}
        <div className="flex flex-col lg:flex-row gap-6">
          {/* ── Left: Color Editor ── */}
          <div className="w-full lg:w-[340px] xl:w-[380px] shrink-0 space-y-4">
            {/* Semantic colors */}
            <div>
              <h2 className="text-sm font-semibold text-base-content/70 uppercase tracking-wider mb-3 flex items-center gap-2">
                <span className="icon-[tabler--palette] w-4 h-4" />
                Semantic Colors
              </h2>
              <div className="space-y-3">
                {colorPairs.map(({ token, contentToken }) => (
                  <ColorGroupEditor
                    key={token}
                    token={token}
                    color={customColors[token as keyof ThemeColorSet]}
                    contentColor={customColors[contentToken as keyof ThemeColorSet]}
                    onColorChange={(c) => updateColor(token, c)}
                    onContentChange={(c) => updateColor(contentToken, c)}
                  />
                ))}
              </div>
            </div>

            {/* Surface colors — collapsible */}
            <div>
              <button
                type="button"
                onClick={() => setShowSurfaces(!showSurfaces)}
                className="text-sm font-semibold text-base-content/70 uppercase tracking-wider mb-3 flex items-center gap-2 w-full text-left"
              >
                <span className={`icon-[tabler--chevron-right] w-4 h-4 transition-transform ${showSurfaces ? 'rotate-90' : ''}`} />
                <span className="icon-[tabler--stack-2] w-4 h-4" />
                Surface Colors
              </button>
              {showSurfaces && (
                <div className="space-y-3">
                  {BASE_COLOR_KEYS.map(token => (
                    <BaseColorEditor
                      key={token}
                      token={token}
                      color={customColors[token as keyof ThemeColorSet]}
                      onChange={(c) => updateColor(token, c)}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Preview link */}
            <div className="hidden lg:block text-center pt-2">
              <p className="text-[10px] text-base-content/40">
                Changes apply live to the preview panel →
              </p>
            </div>
          </div>

          {/* ── Right: Live Component Preview ── */}
          <div className="flex-1 min-w-0">
            <Card className="shadow-md border border-base-300" padding="md">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-base-content/70 uppercase tracking-wider flex items-center gap-2">
                  <span className="icon-[tabler--eye] w-4 h-4" />
                  Live Preview
                </h2>
                <span className="badge badge-soft badge-primary badge-sm font-mono">{selectedTheme}</span>
              </div>
              <div
                key={selectedTheme}
                initial={{ opacity: 0.6, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                <ComponentPreview themeKey={selectedTheme} customVars={customCSSVars} />
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* ── Theme Preview Modal ── */}
      <ThemePreviewModal isOpen={showPreview} onClose={() => setShowPreview(false)} />
    </PageLayout>
  );
}
