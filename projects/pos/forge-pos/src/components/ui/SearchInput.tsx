import { iconClass } from '../../lib/icons';

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  /** Placeholder text (already i18n-translated by the caller) */
  placeholder: string;
  /** Accessible label for the input (already i18n-translated) */
  ariaLabel: string;
  /** Stable test id — passed straight through to the <input> */
  testId?: string;
  /** Shows a small spinner in place of the clear button while filtering */
  loading?: boolean;
  /** Disables the input (e.g. while page data is still loading) */
  disabled?: boolean;
  /** Extra width/flex utility classes, e.g. "flex-1 max-w-xs" */
  className?: string;
  /** Optional explicit clear handler; defaults to clearing the value */
  onClear?: () => void;
  /** aria-label for the clear button */
  clearLabel?: string;
}

/**
 * Reusable search input built on the BEM `.searchbar` component.
 *
 * Replaces the verbose `.input.field--sm > .field__wrapper > .input`
 * markup that was duplicated across ProductManager, KitchenDisplay, Notes,
 * Roles and TaxReports. Provides the search icon, debounced-loading spinner
 * and clear button out of the box.
 *
 * Usage:
 *   <SearchInput
 *     value={search}
 *     onChange={setSearch}
 *     placeholder={t('kitchen.searchPlaceholder') || 'Search...'}
 *     ariaLabel={t('kitchen.searchPlaceholder') || 'Search kitchen tickets'}
 *     testId="kds-search-input"
 *     loading={isFiltering}
 *     className="flex-1 sm:w-48"
 *   />
 */
export default function SearchInput({
  value,
  onChange,
  placeholder,
  ariaLabel,
  testId,
  loading = false,
  disabled = false,
  className = '',
  onClear,
  clearLabel = 'Clear search',
}: SearchInputProps) {
  return (
    <div className={`searchbar searchbar--sm ${className}`}>
      <span className={`searchbar__icon ${iconClass('tabler:search', 'w-4 h-4')}`} />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        aria-label={ariaLabel}
        data-testid={testId}
        disabled={disabled}
        className="searchbar__field"
      />
      {loading ? (
        <span
          className="searchbar__spinner"
          aria-label="filtering"
        >
          <span className="block w-3 h-3 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </span>
      ) : value ? (
        <button
          type="button"
          onClick={() => (onClear ? onClear() : onChange(''))}
          aria-label={clearLabel}
          className="searchbar__clear"
        >
          <span className={iconClass('tabler:x', 'w-3 h-3')} />
        </button>
      ) : null}
    </div>
  );
}
