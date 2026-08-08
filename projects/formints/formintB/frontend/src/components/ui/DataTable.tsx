import { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import Card from './Card';
import { useTranslation } from 'react-i18next';
export interface Column<T> {
  key: string;
  label: string;
  sortable?: boolean;
  render: (row: T) => React.ReactNode;
  className?: string;
  hideOnMobile?: boolean;
  colSpan?: number;
  /** Enable inline editing for this column */
  editable?: boolean;
  /** Input type for the edit field (default: 'text') */
  editType?: 'text' | 'number';
}

export interface BulkAction<T> {
  /** Unique key (used as the React key). */
  key: string;
  /** Button label. */
  label: string;
  /** Optional leading icon. */
  icon?: React.ReactNode;
  /** Extra button classes (e.g. `btn-error btn-soft`). */
  className?: string;
  /** Optional data-testid forwarded to the button. */
  testId?: string;
  /** Fired with the currently selected rows. */
  onClick: (rows: T[]) => void | Promise<void>;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string | number;
  emptyMessage?: string;
  mobileRender?: (row: T) => React.ReactNode;

  // ── Row Selection ──
  selectable?: boolean;
  /** Controlled selected IDs */
  selectedIds?: Set<string | number>;
  /** Fired whenever selection changes */
  onSelectionChange?: (ids: Set<string | number>) => void;
  /** Bulk actions rendered in the toolbar while rows are selected. */
  bulkActions?: BulkAction<T>[];

  // ── Inline Editing ──
  /** Called when an inline edit is confirmed. Return a promise to show a saving indicator. */
  onEditSave?: (row: T, key: string, value: string) => void | Promise<void>;

  // ── CSV Export ──
  exportable?: boolean;
  /** File name (without extension). Default: "export" */
  fileName?: string;
}

function getGridTemplate<T>(columns: Column<T>[]): string {
  const hasColSpan = columns.some(c => c.colSpan);
  if (hasColSpan) {
    return columns.map(c => `${c.colSpan || 1}fr`).join(' ');
  }
  return `repeat(${columns.length}, 1fr)`;
}

/** Generate a CSV string from visible data rows, respecting column order. */
function generateCsv<T>(
  columns: Column<T>[],
  data: T[],
): string {
  const visibleCols = columns.filter(c => !c.hideOnMobile);
  const header = visibleCols.map(c => escapeCsvField(c.label)).join(',');
  const rows = data.map((row) =>
    visibleCols
      .map((col) => {
        const raw = (row as Record<string, unknown>)[col.key];
        return escapeCsvField(raw != null ? String(raw) : '');
      })
      .join(','),
  );
  return [header, ...rows].join('\n');
}

function escapeCsvField(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

/** Download a string as a file using the browser's download mechanism. */
function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export default function DataTable<T>({
  columns,
  data,
  keyExtractor,
  emptyMessage,
  mobileRender,
  selectable = false,
  selectedIds: controlledSelectedIds,
  onSelectionChange,
  bulkActions,
  exportable = false,
  fileName = 'export',
  onEditSave,
}: DataTableProps<T>) {
  const { t } = useTranslation();
  const emptyMsg = emptyMessage ?? t('common.noDataFound');
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  // ── Internal selection state (uncontrolled) ──
  const [internalSelectedIds, setInternalSelectedIds] = useState<Set<string | number>>(new Set());
  const isControlled = controlledSelectedIds !== undefined;
  const selectedIds = isControlled ? controlledSelectedIds : internalSelectedIds;

  const updateSelection = useCallback(
    (fn: (prev: Set<string | number>) => Set<string | number>) => {
      if (isControlled) {
        const next = fn(new Set(controlledSelectedIds!));
        onSelectionChange?.(next);
      } else {
        setInternalSelectedIds((prev) => {
          const next = fn(prev);
          onSelectionChange?.(next);
          return next;
        });
      }
    },
    [isControlled, controlledSelectedIds, onSelectionChange],
  );

  // ── Inline edit state ──
  const [editingCell, setEditingCell] = useState<{
    key: string;
    rowKey: string | number;
  } | null>(null);
  const [editValue, setEditValue] = useState('');
  const [isSavingEdit, setIsSavingEdit] = useState(false);
  const editInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (editingCell && editInputRef.current) {
      editInputRef.current.focus();
      editInputRef.current.select();
    }
  }, [editingCell]);

  // ── Sorting ──
  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[sortKey];
      const bVal = (b as Record<string, unknown>)[sortKey];
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDir === 'asc' ? aVal - bVal : bVal - aVal;
      }
      const comparison = String(aVal).localeCompare(String(bVal), undefined, { numeric: true });
      return sortDir === 'asc' ? comparison : -comparison;
    });
  }, [data, sortKey, sortDir]);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      setSortDir((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  // ── Selection helpers ──
  const toggleSelectAll = useCallback(() => {
    if (selectedIds.size === data.length) {
      updateSelection(() => new Set());
    } else {
      updateSelection(() => new Set(data.map((r) => keyExtractor(r))));
    }
  }, [data, keyExtractor, selectedIds.size, updateSelection]);

  const toggleRow = useCallback(
    (id: string | number) => {
      updateSelection((prev) => {
        const next = new Set(prev);
        if (next.has(id)) next.delete(id);
        else next.add(id);
        return next;
      });
    },
    [updateSelection],
  );

  const allSelected = data.length > 0 && selectedIds.size === data.length;
  const someSelected = selectedIds.size > 0 && selectedIds.size < data.length;

  // ── Inline editing ──
  const startEditing = useCallback(
    (row: T, col: Column<T>, rowKey: string | number) => {
      if (!col.editable) return;
      const raw = (row as Record<string, unknown>)[col.key];
      setEditValue(raw != null ? String(raw) : '');
      setEditingCell({ key: col.key, rowKey });
    },
    [],
  );

  const cancelEditing = useCallback(() => {
    setEditingCell(null);
    setEditValue('');
  }, []);

  const confirmEditing = useCallback(async () => {
    if (!editingCell || !onEditSave) return;
    setIsSavingEdit(true);
    try {
      const row = data.find((r) => keyExtractor(r) === editingCell.rowKey);
      if (row) {
        await onEditSave(row, editingCell.key, editValue);
      }
    } finally {
      setIsSavingEdit(false);
      setEditingCell(null);
      setEditValue('');
    }
  }, [editingCell, onEditSave, data, keyExtractor, editValue]);

  // ── CSV export ──
  const handleExport = useCallback(() => {
    const csv = generateCsv(columns, sortedData);
    downloadFile(csv, `${fileName}.csv`, 'text/csv;charset=utf-8;');
  }, [columns, sortedData, fileName]);

  // ── Empty state ──
  if (data.length === 0 && !exportable) {
    return (
      <Card padding="2xl" center variant="bordered" className="text-base-content/60">
        {emptyMsg}
      </Card>
    );
  }

  // ── Build column list (prepend checkbox column if selectable) ──
  const allColumns: (Column<T> | 'selection')[] = selectable
    ? ['selection', ...columns]
    : columns;

  const gridTemplate = getGridTemplate(
    columns.map((c) => ({
      ...c,
      colSpan: c.colSpan ?? 1,
    })),
  );
  // Adjustment: when selectable, first column is the checkbox (fixed width 48px)
  const gridTemplateWithCheckbox = selectable
    ? `48px ${gridTemplate}`
    : gridTemplate;

  return (
    <Card variant="bordered" className="overflow-hidden">
      {/* Toolbar */}
      {(selectable || exportable) && (
        <div className="flex items-center justify-between gap-2 px-4 py-2 border-b border-base-300 flex-wrap">
          <div className="flex items-center gap-2 flex-wrap">
            {selectable && selectedIds.size > 0 && (
              <span className="text-xs text-base-content/50 font-medium whitespace-nowrap">
                {t('common.selected', { count: selectedIds.size })}
              </span>
            )}
            {/* Bulk actions — shown while rows are selected */}
            {selectable && selectedIds.size > 0 && bulkActions && bulkActions.length > 0 && (
              <div className="flex items-center gap-1.5 flex-wrap">
                {bulkActions.map((action) => {
                  const selectedRows = data.filter((row) => selectedIds.has(keyExtractor(row)));
                  return (
                    <button
                      key={action.key}
                      type="button"
                      data-testid={action.testId}
                      onClick={() => { void action.onClick(selectedRows); }}
                      className={`btn btn-sm text-xs gap-1.5 ${action.className || 'btn-soft'}`}
                    >
                      {action.icon}
                      {action.label}
                    </button>
                  );
                })}
              </div>
            )}
          </div>
          {exportable && (
            <button
              type="button"
              onClick={handleExport}
              className="btn btn-soft btn-sm text-xs gap-1.5"
            >
              <span className="ri-download-line ri-12px" />
              {t('common.csv')}
            </button>
          )}
        </div>
      )}

      {/* Desktop Header */}
      <div
        className="hidden sm:grid gap-4 p-4 border-b border-base-300 rtl:text-right"
        style={{ gridTemplateColumns: gridTemplateWithCheckbox }}
      >
        {allColumns.map((item) => {
          if (item === 'selection') {
            return (
              <div key="_sel" className="flex items-center">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el) => {
                    if (el) el.indeterminate = someSelected;
                  }}
                  onChange={toggleSelectAll}
                  className="checkbox checkbox-sm checkbox-primary cursor-pointer"
                />
              </div>
            );
          }
          const col = item;
          return (
            <div
              key={col.key}
              className={`flex items-center gap-1 text-base-content font-semibold text-sm rtl:text-right
                ${col.className || ''} ${col.hideOnMobile ? 'hidden sm:flex' : ''}`}
            >
              {col.sortable ? (
                <button
                  onClick={() => handleSort(col.key)}
                  className="flex items-center gap-1 hover:text-emerald-500 dark:hover:text-emerald-400 transition-colors"
                >
                  {col.label}
                  {sortKey === col.key &&
                    (sortDir === 'asc' ? (
                      <span className="ri-arrow-up-line ri-14px" />
                    ) : (
                      <span className="ri-arrow-down-line ri-14px" />
                    ))}
                </button>
              ) : (
                col.label
              )}
            </div>
          );
        })}
      </div>

      {/* Rows */}
      {sortedData.length === 0 ? (
        <div className="p-8 text-center text-base-content/50 text-sm">
          {emptyMsg}
        </div>
      ) : (
        sortedData.map((row, _idx) => {
          const rowKey = keyExtractor(row);
          const isSelected = selectedIds.has(rowKey);

          return (
            <div
              key={rowKey}
              className={`transition-colors border-b border-base-300 last:border-b-0
                ${isSelected ? 'bg-primary/10' : ''}
                hover:bg-base-200`}
            >
              {/* Desktop */}
              <div
                className="hidden sm:grid gap-4 p-4"
                style={{ gridTemplateColumns: gridTemplateWithCheckbox }}
              >
                {allColumns.map((item) => {
                  if (item === 'selection') {
                    return (
                      <div key="_sel" className="flex items-center">
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => toggleRow(rowKey)}
                          className="checkbox checkbox-sm checkbox-primary cursor-pointer"
                        />
                      </div>
                    );
                  }
                  const col = item;

                  // Inline editing
                  const isEditing =
                    col.editable &&
                    editingCell?.key === col.key &&
                    editingCell?.rowKey === rowKey;

                  return (
                    <div
                      key={col.key}
                      className={`text-base-content text-sm relative rtl:text-right
                        ${col.className || ''}
                        ${col.hideOnMobile ? 'hidden sm:block' : ''}
                        ${col.editable ? 'cursor-pointer group' : ''}`}
                      onClick={() => {
                        if (col.editable && !isEditing && !isSavingEdit) {
                          startEditing(row, col, rowKey);
                        }
                      }}
                    >
                      {isEditing ? (
                        <div className="flex items-center gap-1">
                          <input
                            ref={editInputRef}
                            type={col.editType || 'text'}
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === 'Enter') confirmEditing();
                              if (e.key === 'Escape') cancelEditing();
                            }}
                            onBlur={confirmEditing}
                            className="input input-sm w-full"
                            onClick={(e) => e.stopPropagation()}
                            step={col.editType === 'number' ? 'any' : undefined}
                          />
                          {isSavingEdit && (
                            <div className="w-3.5 h-3.5 border-2 border-teal-400 border-t-transparent rounded-full shrink-0 animate-spin" />
                          )}
                          {!isSavingEdit && (
                            <div className="flex gap-0.5 shrink-0">
                              <button
                                type="button"
                                onMouseDown={(e) => {
                                  e.preventDefault();
                                  confirmEditing();
                                }}
                                className="p-1 rounded text-success hover:bg-success/10 transition-colors"
                              >
                                <span className="ri-check-line ri-12px" />
                              </button>
                              <button
                                type="button"
                                onMouseDown={(e) => {
                                  e.preventDefault();
                                  cancelEditing();
                                }}
                                className="p-1 rounded text-red-500 hover:bg-red-500/10 transition-colors"
                              >
                                <span className="ri-close-line ri-12px" />
                              </button>
                            </div>
                          )}
                        </div>
                      ) : (
                        <>
                          {col.render(row)}
                          {col.editable && (
                            <span className="absolute inset-0 rounded border-2 border-transparent
                              group-hover:border-primary/40 group-hover:bg-teal-400/5
                              transition-all pointer-events-none" />
                          )}
                        </>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* Mobile */}
              {mobileRender && (
                <div className="sm:hidden p-4">
                  <div className="flex items-start gap-3">
                    {selectable && (
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleRow(rowKey)}
                        className="checkbox checkbox-sm checkbox-primary shrink-0 mt-1"
                      />
                    )}
                    <div className="flex-1">{mobileRender(row)}</div>
                  </div>
                </div>
              )}
            </div>
          );
        })
      )}
    </Card>
  );
}

