// ── OKLCH Color Value ─────────────────────────────────────────────
export interface OKLCHValue {
  /** Lightness 0–100 (stored as number, formatted with % in CSS) */
  l: number;
  /** Chroma 0–0.5+ */
  c: number;
  /** Hue 0–360 */
  h: number;
}

// ── Full set of editable theme color tokens ──────────────────────
export interface ThemeColorSet {
  primary: OKLCHValue;
  'primary-content': OKLCHValue;
  secondary: OKLCHValue;
  'secondary-content': OKLCHValue;
  accent: OKLCHValue;
  'accent-content': OKLCHValue;
  info: OKLCHValue;
  'info-content': OKLCHValue;
  success: OKLCHValue;
  'success-content': OKLCHValue;
  warning: OKLCHValue;
  'warning-content': OKLCHValue;
  error: OKLCHValue;
  'error-content': OKLCHValue;
  neutral: OKLCHValue;
  'neutral-content': OKLCHValue;
  'base-100': OKLCHValue;
  'base-200': OKLCHValue;
  'base-300': OKLCHValue;
  'base-content': OKLCHValue;
}

/** Human-readable labels for each token */
export const COLOR_LABELS: Record<keyof ThemeColorSet, string> = {
  primary: 'Primary',
  'primary-content': 'Primary Text',
  secondary: 'Secondary',
  'secondary-content': 'Secondary Text',
  accent: 'Accent',
  'accent-content': 'Accent Text',
  info: 'Info',
  'info-content': 'Info Text',
  success: 'Success',
  'success-content': 'Success Text',
  warning: 'Warning',
  'warning-content': 'Warning Text',
  error: 'Error',
  'error-content': 'Error Text',
  neutral: 'Neutral',
  'neutral-content': 'Neutral Text',
  'base-100': 'Surface',
  'base-200': 'Surface (elevated)',
  'base-300': 'Border / Muted',
  'base-content': 'Body Text',
};

/** Which token keys to show in the main editor (most impactful) */
export const MAIN_COLOR_KEYS: (keyof ThemeColorSet)[] = [
  'primary', 'primary-content',
  'secondary', 'secondary-content',
  'accent', 'accent-content',
  'info', 'info-content',
  'success', 'success-content',
  'warning', 'warning-content',
  'error', 'error-content',
  'neutral', 'neutral-content',
];

/** Base surface tokens (collapsed by default) */
export const BASE_COLOR_KEYS: (keyof ThemeColorSet)[] = [
  'base-100', 'base-200', 'base-300', 'base-content',
];

// ── Parse `oklch(54.61% 0.2152 262.88)` → { l, c, h } ─────────
export function parseOKLCH(value: string): OKLCHValue | null {
  const match = value.match(/oklch\(\s*([\d.]+)%?\s+([\d.]+)\s+([\d.]+)/);
  if (!match) return null;
  return {
    l: parseFloat(match[1]),
    c: parseFloat(match[2]),
    h: parseFloat(match[3]),
  };
}

// ── Format → CSS oklch() string ─────────────────────────────────
export function formatOKLCH(l: number, c: number, h: number): string {
  return `oklch(${l.toFixed(2)}% ${c.toFixed(4)} ${h.toFixed(2)})`;
}

// ── Generate CSS custom properties for inline style override ─────
export function generateCustomCSSVars(colors: ThemeColorSet): Record<string, string> {
  const vars: Record<string, string> = {};
  for (const [key, value] of Object.entries(colors)) {
    const oklch = value as OKLCHValue;
    vars[`--color-${key}`] = formatOKLCH(oklch.l, oklch.c, oklch.h);
  }
  return vars;
}

// ── Helper to parse a raw oklch string into a key-value pair ────
function parseLine(line: string): [string, OKLCHValue] | null {
  const keyMatch = line.match(/--color-([\w-]+):\s*oklch/);
  if (!keyMatch) return null;
  const key = keyMatch[1];
  const oklch = parseOKLCH(line);
  if (!oklch) return null;
  return [key, oklch];
}

// ── Parse a full theme block from index.css into ThemeColorSet ──
function parseThemeBlock(block: string): ThemeColorSet | null {
  const lines = block.split('\n');
  const entries: Record<string, OKLCHValue> = {};
  for (const line of lines) {
    const parsed = parseLine(line);
    if (parsed) {
      entries[parsed[0]] = parsed[1];
    }
  }
  // Validate required keys
  const requiredKeys: (keyof ThemeColorSet)[] = [
    'primary', 'primary-content',
    'secondary', 'secondary-content',
    'accent', 'accent-content',
    'info', 'info-content',
    'success', 'success-content',
    'warning', 'warning-content',
    'error', 'error-content',
    'neutral', 'neutral-content',
    'base-100', 'base-200', 'base-300', 'base-content',
  ];
  for (const k of requiredKeys) {
    if (!entries[k]) return null;
  }
  return entries as unknown as ThemeColorSet;
}

// ── Default theme values pre-parsed from index.css ──────────────

/**
 * Raw oklch() theme blocks — parses into typed ThemeColorSet defaults.
 *
 * ⚠️ These values are DUPLICATED from src/index.css.
 * When updating a theme in index.css, update the corresponding block here too.
 *
 * Keeping them inline avoids runtime parsing of compiled CSS and makes the
 * studio work even if index.css hasn't been parsed yet. A future improvement
 * could extract these from the CSS at build time.
 */
const RAW_THEMES: Record<string, string> = {
  light: `
    --color-base-100: oklch(100% 0 0);
    --color-base-200: oklch(96.83% 0.0030 247.86);
    --color-base-300: oklch(50.00% 0.0400 257.42);
    --color-base-content: oklch(27.95% 0.0368 260.03);
    --color-primary: oklch(54.61% 0.2152 262.88);
    --color-primary-content: oklch(100% 0 0);
    --color-secondary: oklch(62.31% 0.1880 259.81);
    --color-secondary-content: oklch(100% 0 0);
    --color-accent: oklch(71.48% 0.1257 215.22);
    --color-accent-content: oklch(100% 0 0);
    --color-neutral: oklch(50.00% 0.0400 257.42);
    --color-neutral-content: oklch(100% 0 0);
    --color-info: oklch(68.47% 0.1479 237.32);
    --color-info-content: oklch(100% 0 0);
    --color-success: oklch(69.59% 0.1491 162.48);
    --color-success-content: oklch(100% 0 0);
    --color-warning: oklch(76.86% 0.1647 70.08);
    --color-warning-content: oklch(100% 0 0);
    --color-error: oklch(63.68% 0.2078 25.33);
    --color-error-content: oklch(100% 0 0);
  `,
  dark: `
    --color-base-100: oklch(20.77% 0.0398 265.75);
    --color-base-200: oklch(27.95% 0.0368 260.03);
    --color-base-300: oklch(35.00% 0.0350 260.00);
    --color-base-content: oklch(92.88% 0.0126 255.51);
    --color-primary: oklch(62.31% 0.1880 259.81);
    --color-primary-content: oklch(100% 0 0);
    --color-secondary: oklch(58.54% 0.2041 277.12);
    --color-secondary-content: oklch(100% 0 0);
    --color-accent: oklch(79.71% 0.1339 211.53);
    --color-accent-content: oklch(100% 0 0);
    --color-neutral: oklch(45.00% 0.0300 260.00);
    --color-neutral-content: oklch(92.88% 0.0126 255.51);
    --color-info: oklch(75.35% 0.1390 232.66);
    --color-info-content: oklch(100% 0 0);
    --color-success: oklch(77.29% 0.1535 163.22);
    --color-success-content: oklch(100% 0 0);
    --color-warning: oklch(83.69% 0.1644 84.43);
    --color-warning-content: oklch(100% 0 0);
    --color-error: oklch(71.06% 0.1661 22.22);
    --color-error-content: oklch(100% 0 0);
  `,
  'corporate-light': `
    --color-base-100: oklch(98.42% 0.0034 247.86);
    --color-base-200: oklch(96.83% 0.0069 247.90);
    --color-base-300: oklch(55.44% 0.0407 257.42);
    --color-base-content: oklch(27.95% 0.0368 260.03);
    --color-primary: oklch(54.61% 0.2152 262.88);
    --color-primary-content: oklch(100% 0 0);
    --color-secondary: oklch(62.31% 0.1880 259.81);
    --color-secondary-content: oklch(100% 0 0);
    --color-accent: oklch(71.48% 0.1257 215.22);
    --color-accent-content: oklch(100% 0 0);
    --color-neutral: oklch(55.44% 0.0407 257.42);
    --color-neutral-content: oklch(100% 0 0);
    --color-info: oklch(68.47% 0.1479 237.32);
    --color-info-content: oklch(100% 0 0);
    --color-success: oklch(69.59% 0.1491 162.48);
    --color-success-content: oklch(100% 0 0);
    --color-warning: oklch(76.86% 0.1647 70.08);
    --color-warning-content: oklch(100% 0 0);
    --color-error: oklch(63.68% 0.2078 25.33);
    --color-error-content: oklch(100% 0 0);
  `,
  'corporate-dark': `
    --color-base-100: oklch(20.77% 0.0398 265.75);
    --color-base-200: oklch(27.95% 0.0368 260.03);
    --color-base-300: oklch(35.00% 0.0350 260.00);
    --color-base-content: oklch(92.88% 0.0126 255.51);
    --color-primary: oklch(62.31% 0.1880 259.81);
    --color-primary-content: oklch(100% 0 0);
    --color-secondary: oklch(58.54% 0.2041 277.12);
    --color-secondary-content: oklch(100% 0 0);
    --color-accent: oklch(79.71% 0.1339 211.53);
    --color-accent-content: oklch(100% 0 0);
    --color-neutral: oklch(45.00% 0.0300 260.00);
    --color-neutral-content: oklch(92.88% 0.0126 255.51);
    --color-info: oklch(75.35% 0.1390 232.66);
    --color-info-content: oklch(100% 0 0);
    --color-success: oklch(77.29% 0.1535 163.22);
    --color-success-content: oklch(100% 0 0);
    --color-warning: oklch(83.69% 0.1644 84.43);
    --color-warning-content: oklch(100% 0 0);
    --color-error: oklch(71.06% 0.1661 22.22);
    --color-error-content: oklch(100% 0 0);
  `,
  'luxury-light': `
    --color-base-100: oklch(98.48% 0.0013 106.42);
    --color-base-200: oklch(95.00% 0.0050 90.00);
    --color-base-300: oklch(50.00% 0.0400 70.00);
    --color-base-content: oklch(26.85% 0.0063 34.30);
    --color-primary: oklch(68.06% 0.1423 75.83);
    --color-primary-content: oklch(100% 0 0);
    --color-secondary: oklch(55.53% 0.1455 49.00);
    --color-secondary-content: oklch(100% 0 0);
    --color-accent: oklch(66.58% 0.1574 58.32);
    --color-accent-content: oklch(100% 0 0);
    --color-neutral: oklch(50.00% 0.0200 60.00);
    --color-neutral-content: oklch(100% 0 0);
    --color-info: oklch(60.00% 0.1000 230.00);
    --color-info-content: oklch(100% 0 0);
    --color-success: oklch(52.73% 0.1371 150.07);
    --color-success-content: oklch(100% 0 0);
    --color-warning: oklch(70.00% 0.1600 70.00);
    --color-warning-content: oklch(100% 0 0);
    --color-error: oklch(50.54% 0.1905 27.52);
    --color-error-content: oklch(100% 0 0);
  `,
  'luxury-dark': `
    --color-base-100: oklch(21.61% 0.0061 56.04);
    --color-base-200: oklch(26.00% 0.0080 55.00);
    --color-base-300: oklch(15.00% 0.0100 60.00);
    --color-base-content: oklch(98.48% 0.0013 106.42);
    --color-primary: oklch(79.52% 0.1617 86.05);
    --color-primary-content: oklch(100% 0 0);
    --color-secondary: oklch(55.34% 0.1739 38.40);
    --color-secondary-content: oklch(100% 0 0);
    --color-accent: oklch(70.49% 0.1867 47.60);
    --color-accent-content: oklch(100% 0 0);
    --color-neutral: oklch(40.00% 0.0200 55.00);
    --color-neutral-content: oklch(98.48% 0.0013 106.42);
    --color-info: oklch(55.00% 0.0700 235.00);
    --color-info-content: oklch(100% 0 0);
    --color-success: oklch(72.27% 0.1920 149.58);
    --color-success-content: oklch(100% 0 0);
    --color-warning: oklch(76.00% 0.1500 85.00);
    --color-warning-content: oklch(100% 0 0);
    --color-error: oklch(63.68% 0.2078 25.33);
    --color-error-content: oklch(100% 0 0);
  `,
  'pastel-light': `
    --color-base-100: oklch(97.14% 0.0141 343.20);
    --color-base-200: oklch(94.00% 0.0200 340.00);
    --color-base-300: oklch(60.00% 0.0800 310.00);
    --color-base-content: oklch(29.32% 0.1309 325.66);
    --color-primary: oklch(59.16% 0.2180 0.58);
    --color-primary-content: oklch(100% 0 0);
    --color-secondary: oklch(54.13% 0.2466 293.01);
    --color-secondary-content: oklch(100% 0 0);
    --color-accent: oklch(71.48% 0.1257 215.22);
    --color-accent-content: oklch(100% 0 0);
    --color-neutral: oklch(50.00% 0.0600 310.00);
    --color-neutral-content: oklch(100% 0 0);
    --color-info: oklch(65.00% 0.1200 230.00);
    --color-info-content: oklch(100% 0 0);
    --color-success: oklch(59.60% 0.1274 163.23);
    --color-success-content: oklch(100% 0 0);
    --color-warning: oklch(75.00% 0.1600 75.00);
    --color-warning-content: oklch(100% 0 0);
    --color-error: oklch(57.71% 0.2152 27.33);
    --color-error-content: oklch(100% 0 0);
  `,
  'pastel-dark': `
    --color-base-100: oklch(25.39% 0.0432 324.94);
    --color-base-200: oklch(30.00% 0.0350 320.00);
    --color-base-300: oklch(35.00% 0.0300 315.00);
    --color-base-content: oklch(94.82% 0.0276 342.26);
    --color-primary: oklch(72.53% 0.1752 349.76);
    --color-primary-content: oklch(100% 0 0);
    --color-secondary: oklch(70.90% 0.1592 293.54);
    --color-secondary-content: oklch(100% 0 0);
    --color-accent: oklch(86.51% 0.1153 207.08);
    --color-accent-content: oklch(100% 0 0);
    --color-neutral: oklch(50.00% 0.0400 320.00);
    --color-neutral-content: oklch(94.82% 0.0276 342.26);
    --color-info: oklch(65.00% 0.1200 230.00);
    --color-info-content: oklch(100% 0 0);
    --color-success: oklch(77.29% 0.1535 163.22);
    --color-success-content: oklch(100% 0 0);
    --color-warning: oklch(80.00% 0.1500 85.00);
    --color-warning-content: oklch(100% 0 0);
    --color-error: oklch(80.77% 0.1035 19.57);
    --color-error-content: oklch(100% 0 0);
  `,
  'cyberpunk-light': `
    --color-base-100: oklch(96.00% 0.0050 90.00);
    --color-base-200: oklch(93.00% 0.0080 90.00);
    --color-base-300: oklch(50.00% 0.0150 90.00);
    --color-base-content: oklch(20.00% 0.0100 90.00);
    --color-primary: oklch(58.00% 0.2700 328.36);
    --color-primary-content: oklch(100% 0 0);
    --color-secondary: oklch(60.00% 0.1200 194.77);
    --color-secondary-content: oklch(100% 0 0);
    --color-accent: oklch(70.00% 0.1800 109.77);
    --color-accent-content: oklch(100% 0 0);
    --color-neutral: oklch(45.00% 0.0100 90.00);
    --color-neutral-content: oklch(100% 0 0);
    --color-info: oklch(60.00% 0.1200 230.00);
    --color-info-content: oklch(100% 0 0);
    --color-success: oklch(55.00% 0.1500 144.47);
    --color-success-content: oklch(100% 0 0);
    --color-warning: oklch(70.00% 0.1800 109.77);
    --color-warning-content: oklch(100% 0 0);
    --color-error: oklch(55.00% 0.2200 20.85);
    --color-error-content: oklch(100% 0 0);
  `,
  cyberpunk: `
    --color-base-100: oklch(14.48% 0.0000 89.88);
    --color-base-200: oklch(20.00% 0.0100 90.00);
    --color-base-300: oklch(25.00% 0.0150 90.00);
    --color-base-content: oklch(86.86% 0.2776 144.47);
    --color-primary: oklch(70.17% 0.3225 328.36);
    --color-primary-content: oklch(0% 0 0);
    --color-secondary: oklch(90.54% 0.1546 194.77);
    --color-secondary-content: oklch(0% 0 0);
    --color-accent: oklch(96.80% 0.2110 109.77);
    --color-accent-content: oklch(0% 0 0);
    --color-neutral: oklch(30.00% 0.0100 90.00);
    --color-neutral-content: oklch(86.86% 0.2776 144.47);
    --color-info: oklch(70.00% 0.1500 230.00);
    --color-info-content: oklch(0% 0 0);
    --color-success: oklch(86.86% 0.2776 144.47);
    --color-success-content: oklch(0% 0 0);
    --color-warning: oklch(96.80% 0.2110 109.77);
    --color-warning-content: oklch(0% 0 0);
    --color-error: oklch(63.22% 0.2542 20.85);
    --color-error-content: oklch(0% 0 0);
  `,
};

// ── Parse all themes into typed defaults ─────────────────────────
const parsedThemes = new Map<string, ThemeColorSet>();
for (const [key, block] of Object.entries(RAW_THEMES)) {
  const parsed = parseThemeBlock(block);
  if (parsed) {
    parsedThemes.set(key, parsed);
  }
}

/** Get default color set for a given FlyonUI theme key */
export function getDefaultThemeColors(themeKey: string): ThemeColorSet {
  const cached = parsedThemes.get(themeKey);
  if (cached) return deepCloneColors(cached);
  // Fallback to light if not found
  const fallback = parsedThemes.get('light');
  return fallback ? deepCloneColors(fallback) : createFallbackColors();
}

/** Deep-clone a ThemeColorSet (avoids mutating defaults) */
export function deepCloneColors(colors: ThemeColorSet): ThemeColorSet {
  const clone: Record<string, OKLCHValue> = {};
  for (const [key, val] of Object.entries(colors)) {
    clone[key] = { ...(val as OKLCHValue) };
  }
  return clone as unknown as ThemeColorSet;
}

/** Hard-coded fallback if no theme parses */
function createFallbackColors(): ThemeColorSet {
  const f: OKLCHValue = { l: 100, c: 0, h: 0 };
  return {
    primary: { l: 50, c: 0.2, h: 260 },
    'primary-content': { l: 100, c: 0, h: 0 },
    secondary: { l: 60, c: 0.15, h: 260 },
    'secondary-content': f,
    accent: { l: 70, c: 0.12, h: 215 },
    'accent-content': f,
    info: { l: 65, c: 0.14, h: 237 },
    'info-content': f,
    success: { l: 65, c: 0.14, h: 162 },
    'success-content': f,
    warning: { l: 75, c: 0.16, h: 70 },
    'warning-content': f,
    error: { l: 60, c: 0.2, h: 25 },
    'error-content': f,
    neutral: { l: 50, c: 0.04, h: 257 },
    'neutral-content': f,
    'base-100': { l: 100, c: 0, h: 0 },
    'base-200': { l: 97, c: 0.003, h: 248 },
    'base-300': { l: 50, c: 0.04, h: 257 },
    'base-content': { l: 28, c: 0.036, h: 260 },
  };
}

// ── WCAG Contrast Helper (OKLCH → relative luminance → ratio) ──

/**
 * Convert OKLCH to linear sRGB using the OKLab to sRGB matrix.
 * Returns { r, g, b } each in [0, 1] (linear space, not gamma-compressed).
 */
export function oklchToLinearSRGB(l: number, c: number, h: number): { r: number; g: number; b: number } {
  // OKLCH → OKLab
  const L = l / 100;
  const a = c * Math.cos((h * Math.PI) / 180);
  const bL = c * Math.sin((h * Math.PI) / 180);

  // OKLab → linear LMS
  const lLms = L + 0.3963377774 * a + 0.2158037573 * bL;
  const mLms = L - 0.1055613458 * a - 0.0638541728 * bL;
  const sLms = L - 0.0894841775 * a - 1.2914855480 * bL;

  // Cube LMS (OKLab uses cube root encoding)
  const lCubed = lLms ** 3;
  const mCubed = mLms ** 3;
  const sCubed = sLms ** 3;

  // Linear LMS → linear sRGB
  const r = 4.0767416621 * lCubed - 3.3077115913 * mCubed + 0.2309699292 * sCubed;
  const g = -1.2684380046 * lCubed + 2.6097574011 * mCubed - 0.3413193965 * sCubed;
  const b_lin = -0.0041960863 * lCubed - 0.7034186147 * mCubed + 1.7076147010 * sCubed;

  return { r: Math.max(0, Math.min(1, r)), g: Math.max(0, Math.min(1, g)), b: Math.max(0, Math.min(1, b_lin)) };
}

/** Relative luminance from linear sRGB components */
export function relativeLuminance(r: number, g: number, b: number): number {
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** WCAG contrast ratio between two relative luminances */
export function contrastRatio(lum1: number, lum2: number): number {
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Compute WCAG contrast grade for a color+content pair.
 *
 * grade | ratio  | WCAG criterion
 * ------|--------|---------------
 * AAA   | ≥ 7:1  | Enhanced contrast (normal text)
 * AA    | ≥ 4.5:1| Normal contrast (normal text)
 * AA Lg | ≥ 3:1  | Large text only
 * Fail  | < 3:1  | Fails all WCAG SC 1.4.3 thresholds
 */
export function computeContrast(
  color: OKLCHValue,
  contentColor: OKLCHValue,
): { ratio: number; grade: 'AAA' | 'AA' | 'AA Lg' | 'Fail' } {
  const c1 = oklchToLinearSRGB(color.l, color.c, color.h);
  const c2 = oklchToLinearSRGB(contentColor.l, contentColor.c, contentColor.h);
  const lum1 = relativeLuminance(c1.r, c1.g, c1.b);
  const lum2 = relativeLuminance(c2.r, c2.g, c2.b);
  const ratio = contrastRatio(lum1, lum2);

  if (ratio >= 7) return { ratio, grade: 'AAA' };
  if (ratio >= 4.5) return { ratio, grade: 'AA' };
  if (ratio >= 3) return { ratio, grade: 'AA Lg' };
  return { ratio, grade: 'Fail' };
}

/** Available theme key names for the studio selector */
export const STUDIO_THEMES = [
  { id: 'light', label: 'Default Light', icon: '☀️' },
  { id: 'dark', label: 'Default Dark', icon: '🌙' },
  { id: 'corporate-light', label: 'Corporate Light', icon: '💼' },
  { id: 'corporate-dark', label: 'Corporate Dark', icon: '💼' },
  { id: 'luxury-light', label: 'Luxury Light', icon: '👑' },
  { id: 'luxury-dark', label: 'Luxury Dark', icon: '👑' },
  { id: 'pastel-light', label: 'Pastel Light', icon: '🌸' },
  { id: 'pastel-dark', label: 'Pastel Dark', icon: '🌸' },
  { id: 'cyberpunk-light', label: 'Cyberpunk Light', icon: '⚡' },
  { id: 'cyberpunk', label: 'Cyberpunk Dark', icon: '⚡' },
];

/** Get the default content-color luminance based on a token name's semantic role */
export function defaultContentLuminance(token: string, baseL: number): number {
  // Content colors should be nearly black on light surfaces, nearly white on dark
  if (token.includes('content')) {
    return baseL > 50 ? 0 : 100;
  }
  return baseL;
}

// ── Structural token defaults per theme ─────────────────────────
export interface ThemeStructuralDefaults {
  name: string;
  colorScheme: 'light' | 'dark';
  radiusSelector: string;
  radiusField: string;
  radiusBox: string;
  sizeSelector: string;
  sizeField: string;
  border: string;
  depth: number;
  noise: number;
}

export const THEME_STRUCTURAL_DEFAULTS: Record<string, ThemeStructuralDefaults> = {
  'light':         { name: 'custom-light', colorScheme: 'light', radiusSelector: '0.25rem',    radiusField: '0.375rem', radiusBox: '0.5rem',    sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 0 },
  'dark':          { name: 'custom-dark',  colorScheme: 'dark',  radiusSelector: '0.25rem',    radiusField: '0.375rem', radiusBox: '0.5rem',    sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 0 },
  'corporate-light': { name: 'corporate-light', colorScheme: 'light', radiusSelector: '0.25rem',    radiusField: '0.375rem', radiusBox: '0.5rem',    sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 0 },
  'corporate-dark':  { name: 'corporate-dark',  colorScheme: 'dark',  radiusSelector: '0.25rem',    radiusField: '0.375rem', radiusBox: '0.5rem',    sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 0 },
  'luxury-light':    { name: 'luxury-light',    colorScheme: 'light', radiusSelector: '0.1875rem',  radiusField: '0.375rem', radiusBox: '0.5625rem', sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 0 },
  'luxury-dark':     { name: 'luxury-dark',     colorScheme: 'dark',  radiusSelector: '0.1875rem',  radiusField: '0.375rem', radiusBox: '0.5625rem', sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 0 },
  'pastel-light':    { name: 'pastel-light',    colorScheme: 'light', radiusSelector: '2rem',       radiusField: '2rem',      radiusBox: '2rem',       sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 0 },
  'pastel-dark':     { name: 'pastel-dark',     colorScheme: 'dark',  radiusSelector: '2rem',       radiusField: '2rem',      radiusBox: '2rem',       sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 0 },
  'cyberpunk-light': { name: 'cyberpunk-light', colorScheme: 'light', radiusSelector: '0.25rem',    radiusField: '0.25rem',   radiusBox: '0.375rem',   sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 0 },
  'cyberpunk':       { name: 'cyberpunk',       colorScheme: 'dark',  radiusSelector: '0.25rem',    radiusField: '0.25rem',   radiusBox: '0.375rem',   sizeSelector: '0.25rem', sizeField: '0.25rem', border: '1px', depth: 1, noise: 1 },
};

/**
 * Generate a complete `@plugin "flyonui/theme"` CSS block from current colors
 * and the base theme's structural defaults.
 */
export function generateThemeCSS(
  colors: ThemeColorSet,
  baseThemeKey: string,
  customName?: string
): string {
  const structural = THEME_STRUCTURAL_DEFAULTS[baseThemeKey] ?? THEME_STRUCTURAL_DEFAULTS['light'];
  const name = customName || `${structural.name}-custom`;

  const lines: string[] = [];
  lines.push('@plugin "flyonui/theme" {');
  lines.push(`  name: "${name}";`);
  lines.push(`  color-scheme: ${structural.colorScheme};`);
  lines.push('');

  // Base colors
  const baseKeys = ['base-100', 'base-200', 'base-300', 'base-content'] as const;
  for (const key of baseKeys) {
    const val = colors[key as keyof ThemeColorSet];
    if (val) {
      lines.push(`  --color-${key}: oklch(${val.l.toFixed(2)}% ${val.c.toFixed(4)} ${val.h.toFixed(2)});`);
    }
  }

  lines.push('');

  // Semantic colors + content colors
  const semanticKeys: (keyof ThemeColorSet)[] = [
    'primary', 'primary-content',
    'secondary', 'secondary-content',
    'accent', 'accent-content',
    'neutral', 'neutral-content',
    'info', 'info-content',
    'success', 'success-content',
    'warning', 'warning-content',
    'error', 'error-content',
  ];
  for (const key of semanticKeys) {
    const val = colors[key];
    if (val) {
      lines.push(`  --color-${key}: oklch(${val.l.toFixed(2)}% ${val.c.toFixed(4)} ${val.h.toFixed(2)});`);
    }
  }

  lines.push('');

  // Structural defaults
  lines.push(`  --radius-selector: ${structural.radiusSelector};`);
  lines.push(`  --radius-field: ${structural.radiusField};`);
  lines.push(`  --radius-box: ${structural.radiusBox};`);
  lines.push(`  --size-selector: ${structural.sizeSelector};`);
  lines.push(`  --size-field: ${structural.sizeField};`);
  lines.push(`  --border: ${structural.border};`);
  lines.push(`  --depth: ${structural.depth};`);
  lines.push(`  --noise: ${structural.noise};`);

  lines.push('}');
  return lines.join('\n');
}

// ── Saved Custom Themes ──────────────────────────────────────────
export interface SavedTheme {
  /** User-given name (e.g. "My Warm Theme") */
  name: string;
  /** Base theme this was derived from */
  baseThemeKey: string;
  /** The full color set */
  colors: ThemeColorSet;
  /** Auto-generated timestamp */
  createdAt: string;
}

const STORAGE_KEY = 'theme-studio-saved';

/** Load all saved themes from localStorage */
export function loadSavedThemes(): SavedTheme[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as SavedTheme[];
  } catch {
    return [];
  }
}

/** Save or update a theme. Returns the updated list. */
export function saveTheme(name: string, baseThemeKey: string, colors: ThemeColorSet): SavedTheme[] {
  const all = loadSavedThemes();
  // Replace existing theme with same name, or add new
  const existing = all.findIndex(t => t.name === name);
  const entry: SavedTheme = { name, baseThemeKey, colors: deepCloneColors(colors), createdAt: new Date().toISOString() };
  if (existing >= 0) {
    all[existing] = entry;
  } else {
    all.push(entry);
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  return all;
}

/** Delete a saved theme by name. Returns the updated list. */
export function deleteSavedTheme(name: string): SavedTheme[] {
  const all = loadSavedThemes().filter(t => t.name !== name);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(all));
  return all;
}

/** Check if a name is already taken */
export function isThemeNameTaken(name: string): boolean {
  return loadSavedThemes().some(t => t.name === name);
}
