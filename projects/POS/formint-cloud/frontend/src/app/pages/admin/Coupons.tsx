import { useState, useEffect, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../../components/layout/PageLayout';
import { useTranslation } from 'react-i18next';
import { Coupon } from '../../../types';
import AnimatePresence from '../../../components/ui/AnimatePresence';
import Button from '../../../components/ui/Button';
import SearchInput from '../../../components/ui/SearchInput';
import { useDebouncedSearch } from '../../../hooks/useDebouncedSearch';
import { useStatusToast } from '../../../hooks/useStatusToast';
import StatusToast from '../../../components/ui/StatusToast';
import ConfirmDialog from '../../../components/ui/ConfirmDialog';
import { useCurrency } from '../../../contexts/CurrencyContext';

const COUPON_KINDS: { value: 'percent' | 'fixed'; label: string }[] = [
  { value: 'percent', label: 'Percent' },
  { value: 'fixed', label: 'Fixed amount' },
];

interface CouponForm {
  code: string;
  kind: 'percent' | 'fixed';
  value: string;
  minSubtotal: string;
  is_active: boolean;
}

const EMPTY_FORM: CouponForm = { code: '', kind: 'percent', value: '', minSubtotal: '', is_active: true };

export default function Coupons() {
  const { t } = useTranslation();
  const { formatPrice } = useCurrency();
  const { status, showSuccess, showError, dismiss } = useStatusToast();

  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Coupon | null>(null);
  const [form, setForm] = useState<CouponForm>(EMPTY_FORM);
  const [activeOnly, setActiveOnly] = useState(false);
  const [togglingId, setTogglingId] = useState<number | null>(null);

  const {
    query: search,
    setQuery: setSearch,
    debouncedQuery: debouncedSearch,
    isPending: isFiltering,
  } = useDebouncedSearch();

  useEffect(() => {
    loadCoupons();
  }, []);

  const loadCoupons = async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const data = await invoke<Coupon[]>('get_coupons');
      setCoupons(data);
    } catch (error) {
      console.error('Error loading coupons:', error);
      showError(`${t('common.error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  };

  const canSave = form.code.trim().length > 0 && Number(form.value) > 0;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!canSave) return;
    try {
      const payload = {
        code: form.code.trim().toUpperCase(),
        kind: form.kind,
        value: Number(form.value),
        min_subtotal: form.minSubtotal.trim() ? Number(form.minSubtotal) : null,
        is_active: form.is_active,
      };
      if (editing) {
        await invoke('update_coupon', { id: editing.id, update: payload });
      } else {
        await invoke('add_coupon', { template: payload });
      }
      showSuccess(t('coupons.saved'));
      resetForm();
      loadCoupons({ quiet: true });
    } catch (error) {
      console.error('Error saving coupon:', error);
      showError(`${t('coupons.errorSaving')}: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const handleEdit = (coupon: Coupon) => {
    setEditing(coupon);
    setForm({
      code: coupon.code,
      kind: coupon.kind,
      value: String(coupon.value),
      minSubtotal: coupon.min_subtotal != null ? String(coupon.min_subtotal) : '',
      is_active: coupon.is_active,
    });
    setShowForm(true);
  };

  const [toDelete, setToDelete] = useState<Coupon | null>(null);

  const handleDelete = async () => {
    if (!toDelete) return;
    try {
      await invoke('delete_coupon', { id: toDelete.id });
      setToDelete(null);
      showSuccess(t('coupons.deleted'));
      loadCoupons({ quiet: true });
    } catch (error) {
      console.error('Error deleting coupon:', error);
      showError(`${t('coupons.errorDeleting')}: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const handleToggle = async (coupon: Coupon) => {
    setTogglingId(coupon.id);
    try {
      await invoke('update_coupon', { id: coupon.id, update: { is_active: !coupon.is_active } });
      showSuccess(t('coupons.saved'));
      loadCoupons({ quiet: true });
    } catch (error) {
      console.error('Error toggling coupon:', error);
      showError(`${t('coupons.errorSaving')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setTogglingId(null);
    }
  };

  const resetForm = () => {
    setShowForm(false);
    setEditing(null);
    setForm(EMPTY_FORM);
  };

  const q = debouncedSearch.trim().toLowerCase();
  const filteredCoupons = useMemo(() => {
    let result = coupons;
    if (q) {
      result = result.filter(c => c.code.toLowerCase().includes(q));
    }
    if (activeOnly) {
      result = result.filter(c => c.is_active);
    }
    return result;
  }, [coupons, q, activeOnly]);

  const activeCount = coupons.filter(c => c.is_active).length;

  const kindLabel = (kind: string) =>
    kind === 'percent' ? (t('coupons.percent') || 'Percent') : (t('coupons.fixed') || 'Fixed');

  return (
    <PageLayout title={t('coupons.title') || 'Coupons'}>
      <div className="space-y-4">
        {/* ── Header ── */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div>
            <h1 className="text-2xl font-bold text-base-content flex items-center gap-2">
              <span className="ri-ticket-2-line ri-24px text-primary" />
              {t('coupons.title') || 'Coupons'}
            </h1>
            <p className="text-sm text-base-content/50 mt-0.5">
              {coupons.length} {t('coupons.total', 'coupons')}
              {activeCount > 0 && ` · ${activeCount} ${t('coupons.active').toLowerCase()}`}
            </p>
          </div>
          <Button
            onClick={() => { setEditing(null); setForm(EMPTY_FORM); setShowForm(true); }}
            iconStart={<span className="ri-add-line ri-16px" />}
          >
            {t('coupons.addCoupon') || 'New Coupon'}
          </Button>
        </div>

        {/* ── Filter Bar ── */}
        <div className="bg-base-100/70 backdrop-blur-md border border-base-300/30 rounded-xl p-3 shadow-sm">
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
            <SearchInput
              value={search}
              onChange={setSearch}
              placeholder={t('coupons.searchPlaceholder') || 'Search coupons...'}
              ariaLabel={t('coupons.searchPlaceholder') || 'Search coupons'}
              testId="coupons-search-input"
              loading={isFiltering}
              className="flex-1"
            />
            <button
              type="button"
              onClick={() => setActiveOnly(f => !f)}
              aria-pressed={activeOnly}
              className={`tag tag--sm cursor-pointer transition-all ${
                activeOnly ? 'tag--success' : 'tag--ghost hover:tag--success'
              }`}
            >
              <span className="ri-toggle-line ri-12px" />
              {t('coupons.activeOnly') || 'Active only'}
            </button>
            <span className="text-xs text-base-content/40 whitespace-nowrap px-2">
              {filteredCoupons.length} / {coupons.length}
            </span>
          </div>
        </div>

        {/* ── Add/Edit Form (slide-up) ── */}
        <AnimatePresence>
          {showForm && (
            <form
              onSubmit={handleSubmit}
              className="bg-base-100/70 backdrop-blur-md border border-base-300/30 rounded-xl p-5 space-y-4 shadow-lg overflow-hidden"
            >
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-semibold text-base-content flex items-center gap-2">
                  <span className="ri-pencil-line ri-16px text-primary" />
                  {editing ? (t('coupons.editCoupon') || 'Edit Coupon') : (t('coupons.addCoupon') || 'New Coupon')}
                </h3>
                <button type="button" onClick={resetForm} className="btn btn-ghost btn-sm btn-square">
                  <span className="ri-close-line ri-16px" />
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Code */}
                <div>
                  <label className="block text-sm font-medium text-base-content/70 mb-1">
                    {t('coupons.code') || 'Code'}
                  </label>
                  <input
                    type="text"
                    value={form.code}
                    onChange={e => setForm({ ...form, code: e.target.value.toUpperCase() })}
                    placeholder={t('coupons.codePlaceholder') || 'e.g. SAVE20'}
                    required
                    className="input w-full uppercase"
                    autoFocus
                  />
                </div>

                {/* Kind */}
                <div>
                  <label className="block text-sm font-medium text-base-content/70 mb-1">
                    {t('coupons.kind') || 'Type'}
                  </label>
                  <select
                    value={form.kind}
                    onChange={e => setForm({ ...form, kind: e.target.value as 'percent' | 'fixed' })}
                    className="select w-full"
                  >
                    {COUPON_KINDS.map(k => (
                      <option key={k.value} value={k.value}>{k.label}</option>
                    ))}
                  </select>
                </div>

                {/* Value */}
                <div>
                  <label className="block text-sm font-medium text-base-content/70 mb-1">
                    {form.kind === 'percent'
                      ? (t('coupons.valuePercent') || 'Percent off')
                      : (t('coupons.valueFixed') || 'Amount off')}
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      value={form.value}
                      onChange={e => setForm({ ...form, value: e.target.value })}
                      placeholder={form.kind === 'percent' ? '10' : '5.00'}
                      min="0"
                      step={form.kind === 'percent' ? '1' : '0.5'}
                      required
                      className="input w-full"
                    />
                    <span className="text-sm text-base-content/50 shrink-0 w-6">
                      {form.kind === 'percent' ? '%' : ''}
                    </span>
                  </div>
                </div>

                {/* Min subtotal */}
                <div>
                  <label className="block text-sm font-medium text-base-content/70 mb-1">
                    {t('coupons.minSubtotal') || 'Minimum subtotal'}
                    <span className="text-base-content/40 font-normal"> ({t('coupons.optional') || 'optional'})</span>
                  </label>
                  <input
                    type="number"
                    value={form.minSubtotal}
                    onChange={e => setForm({ ...form, minSubtotal: e.target.value })}
                    placeholder={t('coupons.minSubtotalPlaceholder') || 'No minimum'}
                    min="0"
                    step="0.5"
                    className="input w-full"
                  />
                </div>
              </div>

              {/* Active toggle */}
              <label className="flex items-center gap-2 cursor-pointer group w-fit">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={e => setForm({ ...form, is_active: e.target.checked })}
                  className="toggle toggle-success toggle-sm"
                />
                <span className="text-sm text-base-content/70 group-hover:text-base-content transition-colors flex items-center gap-1.5">
                  <span className="ri-toggle-line ri-14px" />
                  {t('coupons.active') || 'Active'}
                </span>
              </label>

              <div className="flex gap-2 justify-end">
                <button type="button" onClick={resetForm} className="btn btn-ghost btn-sm">
                  {t('common.cancel')}
                </button>
                <button type="submit" className="btn btn-primary btn-sm gap-1.5" disabled={!canSave}>
                  <span className="ri-check-line ri-14px" />
                  {editing ? (t('common.update') || 'Update') : (t('common.save') || 'Save')}
                </button>
              </div>
            </form>
          )}
        </AnimatePresence>

        {/* ── List ── */}
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-[3px] border-primary border-t-transparent rounded-full animate-spin" />
              <span className="text-sm text-base-content/50">{t('common.loading')}</span>
            </div>
          </div>
        ) : filteredCoupons.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-base-content/40">
            <span className="ri-ticket-2-line w-16 h-16 mb-4 opacity-30" />
            <p className="text-lg font-medium">
              {q || activeOnly
                ? (t('coupons.noMatches') || 'No coupons match your search.')
                : (t('coupons.noCoupons') || 'No coupons yet. Create your first coupon!')}
            </p>
            {!q && !activeOnly && (
              <button onClick={() => { setEditing(null); setForm(EMPTY_FORM); setShowForm(true); }}
                className="btn btn-primary btn-sm mt-4 gap-2">
                <span className="ri-add-line ri-16px" />
                {t('coupons.addCoupon') || 'Create your first coupon'}
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {filteredCoupons.map(coupon => (
              <div
                key={coupon.id}
                className={`bg-base-100/70 backdrop-blur-sm border border-base-300/30 rounded-xl p-4
                  transition-all duration-200 hover:shadow-lg hover:shadow-base-300/20 hover:border-primary/30
                  ${coupon.is_active ? '' : 'opacity-60'}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="px-2.5 py-0.5 rounded-lg bg-primary/10 dark:bg-primary/20 text-primary dark:text-primary/80 text-sm font-bold tracking-wider">
                        {coupon.code}
                      </span>
                      <span className={`tag tag--sm ${coupon.kind === 'percent' ? 'tag--info' : 'tag--secondary'}`}>
                        <span className={coupon.kind === 'percent' ? 'ri-percent-line ri-12px' : 'ri-money-cny-circle-line ri-12px'} />
                        {kindLabel(coupon.kind)}
                      </span>
                      <span className={`tag tag--sm ${coupon.is_active ? 'tag--success' : 'tag--ghost'}`}>
                        {coupon.is_active ? (t('coupons.active') || 'Active') : (t('coupons.inactive') || 'Inactive')}
                      </span>
                    </div>
                    <p className="text-2xl font-extrabold text-base-content mt-2 tabular-nums">
                      {coupon.kind === 'percent' ? `${coupon.value}%` : formatPrice(coupon.value)}
                    </p>
                    <p className="text-xs text-base-content/50 mt-1">
                      {coupon.kind === 'percent'
                        ? `${t('coupons.offSubtotal', 'off subtotal')}`
                        : `${t('coupons.offSubtotal', 'off subtotal')}`}
                      {coupon.min_subtotal != null && (
                        <span> · {t('coupons.minSubtotalNote', 'min subtotal')} {formatPrice(coupon.min_subtotal)}</span>
                      )}
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-1.5 shrink-0">
                    <label className="flex items-center gap-1.5 cursor-pointer" title={t('coupons.toggleActive')}>
                      <input
                        type="checkbox"
                        checked={coupon.is_active}
                        onChange={() => handleToggle(coupon)}
                        disabled={togglingId === coupon.id}
                        className="toggle toggle-success toggle-sm"
                        aria-label={t('coupons.toggleActive') || 'Toggle active'}
                      />
                    </label>
                    <div className="flex gap-0.5">
                      <button
                        onClick={() => handleEdit(coupon)}
                        className="p-1.5 rounded-lg text-base-content/40 hover:text-primary hover:bg-primary/10 transition-colors"
                        title={t('common.edit')}
                      >
                        <span className="ri-pencil-line ri-14px" />
                      </button>
                      <button
                        onClick={() => setToDelete(coupon)}
                        className="p-1.5 rounded-lg text-base-content/40 hover:text-error hover:bg-error/10 transition-colors"
                        title={t('common.delete')}
                      >
                        <span className="ri-delete-bin-line ri-14px" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <ConfirmDialog
        isOpen={!!toDelete}
        onClose={() => setToDelete(null)}
        onConfirm={handleDelete}
        title={t('coupons.deleteTitle', 'Delete coupon')}
        message={t('coupons.deleteMessage', 'This will permanently remove the coupon')}
        itemName={toDelete?.code ?? ''}
        confirmLabel={t('common.delete')}
      />

      <StatusToast
        type={status?.type ?? 'success'}
        message={status?.message ?? ''}
        visible={!!status}
        onDismiss={dismiss}
      />
    </PageLayout>
  );
}
