import { type ReactNode } from 'react';
import SearchInput from '../ui/SearchInput';
import CategoryFilterPills from '../pos/CategoryFilterPills';
import type { Category } from '../../types';

/**
 * Shared compact search + filter + sort bar (rounded glass card).
 *
 * Extracted from the duplicated markup that previously lived inline in both
 * ProductManager and Sale. Both pages render the same visual block:
 *
 *   ┌─────────────────────────────────────────────────────────────┐
 *   │ [ Search……  ] [type ▾] [sort ▾] [view] [+ Add]  actions   │
 *   │ [ All ] [ Burgers ] [ Sides ]      (category pills)       │
 *   │ footer (result counter / legend etc.)                       │
 *   └─────────────────────────────────────────────────────────────┘
 *
 * Any extra controls (selects, view toggles, action buttons) go into
 * `topRowActions`; extra pills (e.g. a "Manage categories" button) go into
 * `pillsChildren`; a bottom row (result counter, legend hint) goes into
 * `footer`.
 *
 * @see docs/shared-components.md — how to add this bar to any page.
 */
export interface ProductFilterBarProps {
  // ── Search input ──
  searchValue: string;
  onSearchChange: (value: string) => void;
  searchPlaceholder: string;
  searchAriaLabel: string;
  searchTestId?: string;
  searchLoading?: boolean;
  searchDisabled?: boolean;
  /** Extra classes for the SearchInput wrapper (default: `flex-1 min-w-[10rem] max-w-xs`) */
  searchClassName?: string;

  // ── Top row extras (rendered right of the search input) ──
  topRowActions?: ReactNode;

  // ── Category filter pills ──
  categories: Category[];
  selectedCategory: number | 'all';
  onCategoryChange: (value: number | 'all') => void;
  categoryAllLabel: string;
  categoryAriaLabel?: string;
  categoryTestIdPrefix: string;
  categoryAllTestId?: string;
  categoryCounts?: Record<number, number>;
  showLegend?: boolean;
  legendLabel?: string;
  categoryTooltipFormatter?: (cat: Category, count: number | undefined) => string;
  /** Extra content inside the pills row (e.g. "Manage categories" button) */
  pillsChildren?: ReactNode;

  /** Optional bottom row (result counter, hint text, …) */
  footer?: ReactNode;

  /** Container className (default: the standard glass bar styles) */
  className?: string;
}

export default function ProductFilterBar({
  searchValue,
  onSearchChange,
  searchPlaceholder,
  searchAriaLabel,
  searchTestId,
  searchLoading = false,
  searchDisabled = false,
  searchClassName = 'flex-1 min-w-[10rem] max-w-xs',
  topRowActions,
  categories,
  selectedCategory,
  onCategoryChange,
  categoryAllLabel,
  categoryAriaLabel,
  categoryTestIdPrefix,
  categoryAllTestId,
  categoryCounts,
  showLegend = false,
  legendLabel,
  categoryTooltipFormatter,
  pillsChildren,
  footer,
  className = '',
}: ProductFilterBarProps) {
  return (
    <div
      className={`bg-base-100/70 backdrop-blur-md border border-base-300/30 rounded-2xl p-3 mb-4 shadow-sm space-y-2 ${className}`}
    >
      {/* Search + top-row actions — single compact row */}
      <div className="flex flex-wrap items-center gap-2">
        <SearchInput
          value={searchValue}
          onChange={onSearchChange}
          placeholder={searchPlaceholder}
          ariaLabel={searchAriaLabel}
          testId={searchTestId}
          loading={searchLoading}
          disabled={searchDisabled}
          className={searchClassName}
        />
        {topRowActions}
      </div>

      {/* Category filter — colored tag pills */}
      <CategoryFilterPills
        categories={categories}
        selected={selectedCategory}
        onChange={onCategoryChange}
        allLabel={categoryAllLabel}
        ariaLabel={categoryAriaLabel}
        testIdPrefix={categoryTestIdPrefix}
        allTestId={categoryAllTestId}
        counts={categoryCounts}
        showLegend={showLegend}
        legendLabel={legendLabel}
        tooltipFormatter={categoryTooltipFormatter}
      >
        {pillsChildren}
      </CategoryFilterPills>

      {footer}
    </div>
  );
}
