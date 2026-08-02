import { ReactNode, useState } from 'react';
import { Category } from '../../types';
import { hexToRgba } from './ProductCard';
import { iconClass } from '../../lib/icons';

interface CategoryFilterPillsProps {
  categories: Category[];
  selected: number | 'all';
  onChange: (value: number | 'all') => void;
  /** Label for the "All categories" pill */
  allLabel: string;
  /** aria-label for the pill group (e.g. t('sale.categoryFilter')) */
  ariaLabel?: string;
  /** testid prefix for per-category pills → `${testIdPrefix}-${id}` */
  testIdPrefix: string;
  /** testid for the "All" pill — defaults to `${testIdPrefix}-all` */
  allTestId?: string;
  /** Optional per-category product counts → rendered as small badges */
  counts?: Record<number, number>;
  /** Optional trailing content — e.g. a Manage categories button */
  children?: ReactNode;
  /** Custom hover-tooltip text for a category pill — receives the category + its count */
  tooltipFormatter?: (cat: Category, count: number | undefined) => string;
  /** Show an expandable color-legend toggle (with per-category counts) */
  showLegend?: boolean;
  /** Accessible label for the legend toggle button + panel heading */
  legendLabel?: string;
}

/**
 * Reusable colored category filter pills (BEM `.tag` component).
 *
 * Renders an "All" pill plus one pill per category. Each category pill shows a
 * color dot (from `category.color`) and a tinted border via `hexToRgba`, and
 * follows the toggle-to-reset interaction: clicking the already-selected pill
 * resets the filter back to "All". Used by ProductManager and Sale for a
 * consistent category-filter UX across the app.
 *
 * When `showLegend` is set, an extra toggle button expands a color legend panel
 * listing every category with its color swatch, name, and product count — so
 * staff can quickly map pill colors to categories without hovering each pill.
 */
export default function CategoryFilterPills({
  categories,
  selected,
  onChange,
  allLabel,
  ariaLabel,
  testIdPrefix,
  allTestId,
  counts,
  children,
  tooltipFormatter,
  showLegend = false,
  legendLabel = 'Legend',
}: CategoryFilterPillsProps) {
  const [legendOpen, setLegendOpen] = useState(false);
  const allTestIdValue = allTestId ?? `${testIdPrefix}-all`;

  const totalCount = counts
    ? Object.values(counts).reduce((sum, n) => sum + n, 0)
    : undefined;

  const pillTitle = (cat: Category, count: number | undefined): string => {
    if (tooltipFormatter) return tooltipFormatter(cat, count);
    return count !== undefined ? `${cat.name} — ${count} products` : cat.name;
  };

  return (
    <div
      role="group"
      aria-label={ariaLabel}
      className="flex flex-wrap items-center gap-1.5"
    >
      <button
        onClick={() => onChange('all')}
        data-testid={allTestIdValue}
        data-value="all"
        aria-pressed={selected === 'all'}
        title={allLabel}
        className={`tag tag--sm cursor-pointer transition-all ${
          selected === 'all' ? 'tag--primary' : 'tag--ghost hover:tag--primary'
        }`}
      >
        {allLabel}
      </button>
      {categories.map(cat => {
        const count = counts ? counts[cat.id] : undefined;
        return (
          <button
            key={cat.id}
            onClick={() => onChange(selected === cat.id ? 'all' : cat.id)}
            data-testid={`${testIdPrefix}-${cat.id}`}
            data-value={String(cat.id)}
            aria-pressed={selected === cat.id}
            title={pillTitle(cat, count)}
            className={`tag tag--sm cursor-pointer transition-all flex items-center gap-1.5 ${
              selected === cat.id ? 'tag--primary' : 'tag--ghost hover:tag--primary'
            }`}
            style={cat.color ? { borderColor: hexToRgba(cat.color, 0.5) } : undefined}
          >
            {cat.color && (
              <span
                className="w-2 h-2 rounded-full shrink-0"
                style={{ backgroundColor: cat.color }}
              />
            )}
            {cat.name}
            {count !== undefined && (
              <span className="badge badge-xs badge-ghost tabular-nums">{count}</span>
            )}
          </button>
        );
      })}
      {children}
      {showLegend && (
        <button
          type="button"
          onClick={() => setLegendOpen(open => !open)}
          aria-expanded={legendOpen}
          aria-controls={`${testIdPrefix}-legend`}
          title={legendLabel}
          data-testid={`${testIdPrefix}-legend-toggle`}
          className={`tag tag--sm cursor-pointer transition-all flex items-center gap-1 ${
            legendOpen ? 'tag--primary' : 'tag--ghost hover:tag--primary'
          }`}
        >
          <span className={iconClass('palette', 'w-3.5 h-3.5')} />
          <span className="hidden sm:inline">{legendLabel}</span>
        </button>
      )}
      {legendOpen && (
        <div
          id={`${testIdPrefix}-legend`}
          data-testid={`${testIdPrefix}-legend`}
          className="w-full basis-full rounded-xl border border-base-300/50 bg-base-100/80 p-3 backdrop-blur-sm"
        >
          <p className="text-xs font-medium text-base-content/70 mb-2 flex items-center justify-between gap-2">
            <span>{legendLabel}</span>
            {totalCount !== undefined && (
              <span className="badge badge-xs badge-ghost tabular-nums">
                {allLabel}: {totalCount}
              </span>
            )}
          </p>
          <ul className="flex flex-wrap gap-x-4 gap-y-2">
            {categories.map(cat => {
              const count = counts ? counts[cat.id] : undefined;
              return (
                <li
                  key={cat.id}
                  className="flex items-center gap-1.5 text-xs text-base-content/80"
                >
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0 ring-1 ring-base-300/50"
                    style={{ backgroundColor: cat.color || '#94a3b8' }}
                  />
                  <span>{cat.name}</span>
                  {count !== undefined && (
                    <span className="badge badge-xs badge-ghost tabular-nums">{count}</span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
