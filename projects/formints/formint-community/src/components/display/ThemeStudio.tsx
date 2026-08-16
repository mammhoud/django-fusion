import { useEffect, useRef, useState } from 'react';
import { useTheme } from '../../contexts/ThemeContext';

// ── Token tree — mirrors the CSS variable families defined for every
//    FlyonUI variant in assets/styles/index.css (via @plugin "flyonui/theme").
//    Values are read live from the active theme using getComputedStyle, so the
//    tree always matches the current variant + light/dark mode.
const TOKEN_GROUPS: { label: string; icon: string; tokens: string[] }[] = [
  {
    label: 'Surfaces',
    icon: 'ri-layout-3-line',
    tokens: [
      '--color-base-100',
      '--color-base-200',
      '--color-base-300',
      '--color-base-content',
    ],
  },
  {
    label: 'Brand',
    icon: 'ri-palette-line',
    tokens: [
      '--color-primary',
      '--color-primary-content',
      '--color-secondary',
      '--color-secondary-content',
      '--color-accent',
      '--color-accent-content',
      '--color-neutral',
      '--color-neutral-content',
    ],
  },
  {
    label: 'Semantic',
    icon: 'ri-error-warning-line',
    tokens: [
      '--color-info',
      '--color-info-content',
      '--color-success',
      '--color-success-content',
      '--color-warning',
      '--color-warning-content',
      '--color-error',
      '--color-error-content',
    ],
  },
  {
    label: 'Shape & Effects',
    icon: 'ri-shape-line',
    tokens: [
      '--radius-selector',
      '--radius-field',
      '--radius-box',
      '--size-selector',
      '--size-field',
      '--border',
      '--depth',
      '--noise',
    ],
  },
];

const ALL_TOKENS = TOKEN_GROUPS.flatMap(g => g.tokens);

// Tokens that hold colors (get a swatch) vs lengths/numbers (get a mono chip)
const COLOR_PREFIX = '--color-';

export default function ThemeStudio() {
  const { resolvedTheme } = useTheme();
  const [values, setValues] = useState<Record<string, string>>({});
  const [copied, setCopied] = useState<string | null>(null);
  // Reading from a local wrapper that carries the resolved data-theme (same
  // pattern as ThemePreviewModal) — avoids reading stale variables when the
  // provider's <html data-theme> effect runs after this component's effect.
  const themeRef = useRef<HTMLDivElement>(null);

  // Re-read the computed variables whenever the resolved theme changes
  useEffect(() => {
    const el = themeRef.current;
    if (!el) return;
    const cs = window.getComputedStyle(el);
    const next: Record<string, string> = {};
    for (const token of ALL_TOKENS) {
      next[token] = cs.getPropertyValue(token).trim();
    }
    setValues(next);
  }, [resolvedTheme]);

  const copyToken = async (token: string) => {
    const text = `${token}: ${values[token] || 'inherit'};`;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
      }
      setCopied(token);
      window.setTimeout(() => setCopied(cur => (cur === token ? null : cur)), 1600);
    } catch {
      // Clipboard unavailable — ignore
    }
  };

  return (
    <div ref={themeRef} data-theme={resolvedTheme} className="space-y-5">
      {/* Active theme badge */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-base-content/50">Resolved theme:</span>
        <span className="badge badge-soft badge-primary text-xs font-mono">{resolvedTheme}</span>
        <span className="text-[11px] text-base-content/40">— click a token to copy</span>
      </div>

      {TOKEN_GROUPS.map(group => (
        <div key={group.label}>
          <p className="text-xs font-semibold text-base-content/50 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <span className={`${group.icon} ri-14px`} />
            {group.label}
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-1">
            {group.tokens.map(token => {
              const value = values[token] || '';
              const isColor = token.startsWith(COLOR_PREFIX);
              const isCopied = copied === token;
              return (
                <button
                  key={token}
                  type="button"
                  onClick={() => copyToken(token)}
                  title={`${token}: ${value || 'inherit'}`}
                  className="flex items-center gap-2 px-2 py-1.5 rounded-lg text-left cursor-pointer
                    hover:bg-base-200/60 active:scale-[0.99] transition-all"
                >
                  {isColor ? (
                    <span
                      className="w-5 h-5 rounded-md ring-1 ring-base-content/10 shrink-0"
                      style={{ backgroundColor: value || 'transparent' }}
                    />
                  ) : (
                    <span className="w-5 h-5 rounded-md bg-base-200 ring-1 ring-base-content/10 shrink-0 flex items-center justify-center text-[9px] font-mono text-base-content/50">
                      #
                    </span>
                  )}
                  <span className="font-mono text-[11px] text-base-content/70 truncate min-w-0 flex-1">
                    {token}
                  </span>
                  <span className="font-mono text-[10px] text-base-content/40 truncate max-w-[8rem]">
                    {value || '—'}
                  </span>
                  <span
                    className={`${isCopied ? 'ri-check-line text-success' : 'ri-file-copy-line text-base-content/30'} ri-14px shrink-0`}
                  />
                </button>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
