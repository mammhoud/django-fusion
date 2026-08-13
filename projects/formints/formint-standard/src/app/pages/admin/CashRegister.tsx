import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import PageLayout from '../../../components/layout/PageLayout';
import Card from '../../../components/ui/Card';
import StatusToast from '../../../components/ui/StatusToast';
import { useStatusToast } from '../../../hooks/useStatusToast';
import { useCurrency } from '../../../contexts/CurrencyContext';
import { useTranslation } from 'react-i18next';
import { Shift } from '../../../types';

function validAmount(value: string): boolean {
  const amount = Number(value);
  return Number.isFinite(amount) && amount >= 0;
}

export default function CashRegister() {
  const { t } = useTranslation();
  const { formatPrice } = useCurrency();
  const [shift, setShift] = useState<Shift | null>(null);
  const [history, setHistory] = useState<Shift[]>([]);
  const [openingCash, setOpeningCash] = useState('0');
  const [closingCash, setClosingCash] = useState('');
  const [notes, setNotes] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const { status, showSuccess, showError, dismiss } = useStatusToast();

  useEffect(() => {
    void loadRegister();
  }, []);

  const loadRegister = async () => {
    try {
      setIsLoading(true);
      const [active, shifts] = await Promise.all([
        invoke<Shift | null>('get_active_shift'),
        invoke<Shift[]>('get_shifts', { status: null }),
      ]);
      setShift(active ?? null);
      setHistory((shifts ?? []).filter(item => item.shift_status === 'closed').slice(0, 8));
    } catch (error) {
      showError(`${t('common.error', 'Error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpen = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!validAmount(openingCash)) {
      showError(t('register.invalidAmount', 'Opening cash must be a non-negative amount.'));
      return;
    }
    try {
      setIsSaving(true);
      const opened = await invoke<Shift>('open_shift', {
        shift: { opening_cash: Number(openingCash), shift_notes: notes || null },
      });
      setShift(opened);
      setNotes('');
      showSuccess(t('register.opened', 'Cash shift opened.'));
      await loadRegister();
    } catch (error) {
      showError(`${t('common.error', 'Error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleClose = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!shift || !validAmount(closingCash)) {
      showError(t('register.invalidAmount', 'Closing cash must be a non-negative amount.'));
      return;
    }
    try {
      setIsSaving(true);
      await invoke('close_shift', {
        id: shift.id,
        closingCash: Number(closingCash),
        notes: notes || null,
      });
      setClosingCash('');
      setNotes('');
      showSuccess(t('register.closed', 'Cash shift closed and reconciled.'));
      await loadRegister();
    } catch (error) {
      showError(`${t('common.error', 'Error')}: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDrawer = async () => {
    try {
      await invoke('trigger_cash_drawer');
      showSuccess(t('register.drawerOpened', 'Cash drawer opened.'));
    } catch (error) {
      showError(`${t('register.drawerError', 'Could not open drawer')}: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  return (
    <PageLayout title={t('register.title', 'Cash Register')}>
      <div className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-base-content">{t('register.title', 'Cash Register')}</h1>
            <p className="text-sm text-base-content/55">{t('register.subtitle', 'Open a till, reconcile cash, and control the connected drawer.')}</p>
          </div>
          <button type="button" onClick={handleDrawer} disabled={!shift || isSaving} className="btn btn-outline btn-primary gap-2">
            <span className="ri-inbox-unarchive-line" /> {t('register.openDrawer', 'Open Drawer')}
          </button>
        </div>

        {isLoading ? (
          <div className="py-16 text-center text-base-content/50">{t('common.loading')}</div>
        ) : shift ? (
          <div className="grid grid-cols-1 lg:grid-cols-[1.2fr_0.8fr] gap-4">
            <Card padding="lg" className="border-success/30 bg-success/5">
              <div className="flex items-start justify-between gap-4 mb-6">
                <div>
                  <span className="badge badge-success badge-soft mb-2">{t('register.open', 'Open')}</span>
                  <h2 className="text-xl font-semibold">{t('register.currentShift', 'Current Shift')}</h2>
                  <p className="text-sm text-base-content/55">{new Date(shift.opened_at).toLocaleString()}</p>
                </div>
                <span className="ri-cash-line ri-32px text-success" />
              </div>
              <div className="grid grid-cols-2 gap-3 mb-6">
                <div className="rounded-xl bg-base-100/70 p-4"><p className="text-xs text-base-content/50">{t('register.openingCash', 'Opening cash')}</p><p className="text-xl font-semibold">{formatPrice(shift.opening_cash)}</p></div>
                <div className="rounded-xl bg-base-100/70 p-4"><p className="text-xs text-base-content/50">{t('register.expectedAtClose', 'Expected at close')}</p><p className="text-xl font-semibold">{shift.expected_cash == null ? '—' : formatPrice(shift.expected_cash)}</p></div>
              </div>
              <form onSubmit={handleClose} className="space-y-3">
                <label className="label"><span className="label-text font-medium">{t('register.closingCash', 'Counted closing cash')}</span></label>
                <input aria-label={t('register.closingCash', 'Counted closing cash')} className="input input-lg w-full" type="number" min="0" step="0.01" value={closingCash} onChange={event => setClosingCash(event.target.value)} placeholder="0.00" required />
                <input aria-label={t('register.notes', 'Notes')} className="input w-full" value={notes} onChange={event => setNotes(event.target.value)} placeholder={t('register.notesPlaceholder', 'Optional reconciliation note')} />
                <button type="submit" disabled={isSaving} className="btn btn-error gap-2"><span className="ri-lock-line" /> {t('register.closeShift', 'Close Shift')}</button>
              </form>
            </Card>
            <Card padding="lg">
              <h2 className="text-lg font-semibold mb-2">{t('register.reconciliation', 'Reconciliation')}</h2>
              <p className="text-sm text-base-content/55 mb-5">{t('register.reconciliationHint', 'Expected cash includes the opening float and completed cash sales only. Card and digital payments are excluded.')}</p>
              <div className="flex items-center gap-3 rounded-xl bg-base-200/60 p-4">
                <span className="ri-shield-check-line ri-24px text-success" />
                <span className="text-sm">{t('register.cashOnly', 'Cash-only reconciliation is active')}</span>
              </div>
            </Card>
          </div>
        ) : (
          <Card padding="lg" className="max-w-xl">
            <div className="flex items-center gap-3 mb-5"><div className="w-11 h-11 rounded-xl bg-primary/10 text-primary flex items-center justify-center"><span className="ri-cash-line ri-24px" /></div><div><h2 className="text-xl font-semibold">{t('register.openShift', 'Open a Cash Shift')}</h2><p className="text-sm text-base-content/55">{t('register.openShiftHint', 'Record the cash float before taking cash payments.')}</p></div></div>
            <form onSubmit={handleOpen} className="space-y-3">
              <label className="label"><span className="label-text font-medium">{t('register.openingCash', 'Opening cash')}</span></label>
              <input aria-label={t('register.openingCash', 'Opening cash')} className="input w-full" type="number" min="0" step="0.01" value={openingCash} onChange={event => setOpeningCash(event.target.value)} required />
              <input aria-label={t('register.notes', 'Notes')} className="input w-full" value={notes} onChange={event => setNotes(event.target.value)} placeholder={t('register.notesPlaceholder', 'Optional shift note')} />
              <button type="submit" disabled={isSaving} className="btn btn-primary gap-2"><span className="ri-lock-unlock-line" /> {t('register.openShift', 'Open a Cash Shift')}</button>
            </form>
          </Card>
        )}

        {history.length > 0 && (
          <Card padding="lg">
            <h2 className="text-lg font-semibold mb-4">{t('register.history', 'Recent Shifts')}</h2>
            <div className="overflow-x-auto"><table className="table"><thead><tr><th>{t('register.opened', 'Opened')}</th><th>{t('register.closed', 'Closed')}</th><th>{t('register.expected', 'Expected')}</th><th>{t('register.counted', 'Counted')}</th><th>{t('register.difference', 'Difference')}</th></tr></thead><tbody>{history.map(item => <tr key={item.id}><td>{new Date(item.opened_at).toLocaleString()}</td><td>{item.closed_at ? new Date(item.closed_at).toLocaleString() : '—'}</td><td>{item.expected_cash == null ? '—' : formatPrice(item.expected_cash)}</td><td>{item.closing_cash == null ? '—' : formatPrice(item.closing_cash)}</td><td className={item.cash_difference != null && item.cash_difference < 0 ? 'text-error font-semibold' : 'text-success font-semibold'}>{item.cash_difference == null ? '—' : formatPrice(item.cash_difference)}</td></tr>)}</tbody></table></div>
          </Card>
        )}
      </div>
      <StatusToast type={status?.type ?? 'success'} message={status?.message ?? ''} visible={!!status} onDismiss={dismiss} />
    </PageLayout>
  );
}

export { validAmount };
