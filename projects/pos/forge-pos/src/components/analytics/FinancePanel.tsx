import { useState, useEffect, useCallback, useMemo } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useTranslation } from 'react-i18next';
import {
  FinanceTransaction, NewFinanceTransaction, Budget, NewBudget,
  FinanceSummary, INVOICE_CATEGORIES,
} from '../../types';
import StatCard from '../ui/StatCard';
import FormModal from '../ui/FormModal';
import Card from '../ui/Card';
import Button from '../ui/Button';
import ConfirmDialog from '../ui/ConfirmDialog';
import StatusToast from '../ui/StatusToast';
import { useDebouncedSearch } from '../../hooks/useDebouncedSearch';
import SearchInput from '../ui/SearchInput';

type TxModal = { mode: 'add' } | { mode: 'edit'; tx: FinanceTransaction } | null;
type BudgetModal = { mode: 'add' } | { mode: 'edit'; budget: Budget } | null;

const EMPTY_TX: NewFinanceTransaction = {
  date: new Date().toISOString().slice(0, 10),
  category_id: 'products',
  direction: 'collection',
  amount: 0,
  description: null,
  reference: null,
};

const EMPTY_BUDGET: NewBudget = {
  category_id: null,
  period_start: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0, 10),
  period_end: new Date(new Date().getFullYear(), new Date().getMonth() + 1, 0).toISOString().slice(0, 10),
  amount: 0,
};

const CATEGORY_LABELS: Record<string, string> = Object.fromEntries(
  INVOICE_CATEGORIES.map((c) => [c.id, c.label]),
);

/**
 * Finance & Budget panel — rendered inside the Reports page as the "Finance" tab.
 *
 * Self-contained (fetches its own data via get_finance_summary /
 * get_finance_transactions / get_budgets), so it only loads when opened.
 * Includes:
 * - summary stat row (income, expense, net, over-budget count)
 * - income/outcome ledger with add/edit/delete + debounced search
 * - per-category budget limits with remaining tracking and over-budget warnings
 */
export default function FinancePanel() {
  const { t } = useTranslation();

  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [txs, setTxs] = useState<FinanceTransaction[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [txModal, setTxModal] = useState<TxModal>(null);
  const [txForm, setTxForm] = useState<NewFinanceTransaction>({ ...EMPTY_TX });
  const [budgetModal, setBudgetModal] = useState<BudgetModal>(null);
  const [budgetForm, setBudgetForm] = useState<NewBudget>({ ...EMPTY_BUDGET });
  const [deleteTx, setDeleteTx] = useState<FinanceTransaction | null>(null);
  const [deleteBudget, setDeleteBudget] = useState<Budget | null>(null);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const { query, setQuery, debouncedQuery } = useDebouncedSearch();

  const showStatus = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3000);
  };

  const loadData = useCallback(async (opts: { quiet?: boolean } = {}) => {
    const { quiet = false } = opts;
    if (!quiet) setIsLoading(true);
    try {
      const [sum, txRows, budgetRows] = await Promise.all([
        invoke<FinanceSummary>('get_finance_summary'),
        invoke<FinanceTransaction[]>('get_finance_transactions'),
        invoke<Budget[]>('get_budgets'),
      ]);
      setSummary(sum);
      setTxs(txRows);
      setBudgets(budgetRows);
    } catch (error) {
      console.error('Error loading finance data:', error);
    } finally {
      if (!quiet) setIsLoading(false);
    }
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  // ── Ledger helpers ──
  const openAddTx = () => {
    setTxForm({ ...EMPTY_TX });
    setTxModal({ mode: 'add' });
  };

  const openEditTx = (tx: FinanceTransaction) => {
    setTxForm({
      date: tx.date,
      category_id: tx.category_id,
      direction: tx.direction,
      amount: tx.amount,
      description: tx.description ?? null,
      reference: tx.reference ?? null,
    });
    setTxModal({ mode: 'edit', tx });
  };

  const handleSaveTx = async () => {
    if (!txForm.date || !txForm.category_id || txForm.amount <= 0) return;
    const editing = txModal?.mode === 'edit' ? txModal.tx : null;
    try {
      if (editing) {
        await invoke('update_finance_transaction', { id: editing.id, update: txForm });
        showStatus('success', t('finance.txUpdated') || 'Transaction updated!');
      } else {
        await invoke('add_finance_transaction', { tx: txForm });
        showStatus('success', t('finance.txAdded') || 'Transaction added!');
      }
      setTxModal(null);
      await loadData({ quiet: true });
    } catch (e) {
      showStatus('error', String(e));
    }
  };

  const handleDeleteTx = async () => {
    if (!deleteTx) return;
    try {
      await invoke('delete_finance_transaction', { id: deleteTx.id });
      setDeleteTx(null);
      await loadData({ quiet: true });
      showStatus('success', t('finance.txDeleted') || 'Transaction deleted.');
    } catch (e) {
      showStatus('error', String(e));
    }
  };

  // ── Budget helpers ──
  const openAddBudget = () => {
    setBudgetForm({ ...EMPTY_BUDGET });
    setBudgetModal({ mode: 'add' });
  };

  const openEditBudget = (b: Budget) => {
    setBudgetForm({
      category_id: b.category_id ?? null,
      period_start: b.period_start,
      period_end: b.period_end,
      amount: b.amount,
    });
    setBudgetModal({ mode: 'edit', budget: b });
  };

  const handleSaveBudget = async () => {
    if (!budgetForm.period_start || !budgetForm.period_end || budgetForm.amount <= 0) return;
    const editing = budgetModal?.mode === 'edit' ? budgetModal.budget : null;
    try {
      if (editing) {
        await invoke('update_budget', { id: editing.id, update: budgetForm });
        showStatus('success', t('finance.budgetUpdated') || 'Budget updated!');
      } else {
        await invoke('add_budget', { budget: budgetForm });
        showStatus('success', t('finance.budgetAdded') || 'Budget added!');
      }
      setBudgetModal(null);
      await loadData({ quiet: true });
    } catch (e) {
      showStatus('error', String(e));
    }
  };

  const handleDeleteBudget = async () => {
    if (!deleteBudget) return;
    try {
      await invoke('delete_budget', { id: deleteBudget.id });
      setDeleteBudget(null);
      await loadData({ quiet: true });
      showStatus('success', t('finance.budgetDeleted') || 'Budget deleted.');
    } catch (e) {
      showStatus('error', String(e));
    }
  };

  // ── Derived ──
  const filteredTxs = useMemo(() => {
    const q = debouncedQuery.trim().toLowerCase();
    if (!q) return txs;
    return txs.filter((tx) =>
      tx.description?.toLowerCase().includes(q) ||
      tx.reference?.toLowerCase().includes(q) ||
      tx.category_id.toLowerCase().includes(q) ||
      tx.date.includes(q),
    );
  }, [txs, debouncedQuery]);

  const overBudgetCount = summary?.budgets.filter((b) => b.over).length ?? 0;

  const directionIcon = (d: string) =>
    d === 'payment' ? 'ri-arrow-up-circle-line text-error' : 'ri-arrow-down-circle-line text-success';
  const directionLabel = (d: string) =>
    d === 'payment' ? (t('finance.expense') || 'Expense') : (t('finance.income') || 'Income');

  return (
    <div className="space-y-6">
      {/* ── Summary stat row ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 md:gap-4">
        <StatCard
          title={t('finance.totalIncome') || 'Total Income'}
          value={summary ? summary.total_income.toLocaleString() : '—'}
          icon={<span className="ri-arrow-down-circle-line ri-24px" />}
          color="success"
          compact
        />
        <StatCard
          title={t('finance.totalExpense') || 'Total Expense'}
          value={summary ? summary.total_expense.toLocaleString() : '—'}
          icon={<span className="ri-arrow-up-circle-line ri-24px" />}
          color="error"
          compact
        />
        <StatCard
          title={t('finance.net') || 'Net'}
          value={summary ? summary.net.toLocaleString() : '—'}
          icon={<span className="ri-scales-3-line ri-24px" />}
          color={summary && summary.net < 0 ? 'error' : 'primary'}
          compact
        />
        <StatCard
          title={t('finance.overBudget') || 'Over budget'}
          value={isLoading ? '—' : String(overBudgetCount)}
          icon={<span className="ri-alarm-warning-line ri-24px" />}
          color={overBudgetCount > 0 ? 'warning' : 'info'}
          compact
        />
      </div>

      {/* ── Income / outcome ledger ── */}
      <Card padding="sm" variant="bordered">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
          <h3 className="flex items-center gap-2 font-semibold text-base-content">
            <span className="ri-exchange-funds-line text-primary" /> {t('finance.ledger') || 'Transactions'}
          </h3>
          <div className="flex flex-wrap items-center gap-2">
            <SearchInput
              value={query}
              onChange={setQuery}
              placeholder={t('finance.searchTx') || 'Search transactions…'}
              ariaLabel={t('finance.searchTx') || 'Search transactions'}
              testId="finance-tx-search"
            />
            <Button onClick={openAddTx} className="btn-primary">
              <span className="ri-add-line" /> {t('finance.addTx') || 'Add Transaction'}
            </Button>
          </div>
        </div>
        {isLoading ? (
          <p className="text-sm text-base-content/50 py-6 text-center">Loading…</p>
        ) : filteredTxs.length === 0 ? (
          <p className="text-sm text-base-content/50 py-6 text-center">
            {t('finance.noTx') || 'No transactions yet — add your first income or expense record.'}
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 dark:border-white/10 text-left text-xs uppercase tracking-wider text-base-content/50">
                  <th className="px-4 py-2.5 font-medium">{t('finance.date') || 'Date'}</th>
                  <th className="px-4 py-2.5 font-medium">{t('finance.type') || 'Type'}</th>
                  <th className="px-4 py-2.5 font-medium">{t('finance.category') || 'Category'}</th>
                  <th className="px-4 py-2.5 font-medium">{t('finance.description') || 'Description'}</th>
                  <th className="px-4 py-2.5 font-medium">{t('finance.reference') || 'Reference'}</th>
                  <th className="px-4 py-2.5 font-medium text-right">{t('finance.amount') || 'Amount'}</th>
                  <th className="px-4 py-2.5 font-medium text-right">{t('common.actions') || 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {filteredTxs.map((tx) => (
                  <tr key={tx.id} className="border-b border-slate-100 dark:border-white/5 last:border-0 hover:bg-base-200/30 dark:hover:bg-white/5 transition-colors">
                    <td className="px-4 py-2.5 text-base-content/70 tabular-nums">{tx.date}</td>
                    <td className="px-4 py-2.5">
                      <span className={`inline-flex items-center gap-1.5 ${tx.direction === 'payment' ? 'text-error' : 'text-success'}`}>
                        <span className={directionIcon(tx.direction)} /> {directionLabel(tx.direction)}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-base-content/80">{CATEGORY_LABELS[tx.category_id] || tx.category_id}</td>
                    <td className="px-4 py-2.5 text-base-content/80 max-w-[220px] truncate">{tx.description || '—'}</td>
                    <td className="px-4 py-2.5 text-base-content/50">{tx.reference || '—'}</td>
                    <td className={`px-4 py-2.5 text-right tabular-nums font-semibold ${tx.direction === 'payment' ? 'text-error' : 'text-success'}`}>
                      {tx.direction === 'payment' ? '−' : '+'}{tx.amount.toLocaleString()}
                    </td>
                    <td className="px-4 py-2.5">
                      <div className="flex justify-end gap-1">
                        <button onClick={() => openEditTx(tx)} title={t('common.edit')}
                          className="text-info hover:text-info/70 p-1.5 rounded-lg hover:bg-info/10">
                          <span className="ri-pencil-line ri-16px" />
                        </button>
                        <button onClick={() => setDeleteTx(tx)} title={t('common.delete')}
                          className="text-error hover:text-error/70 p-1.5 rounded-lg hover:bg-error/10">
                          <span className="ri-delete-bin-line ri-16px" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* ── Budgets ── */}
      <Card padding="sm" variant="bordered">
        <div className="flex items-center justify-between gap-3 mb-4">
          <h3 className="flex items-center gap-2 font-semibold text-base-content">
            <span className="ri-wallet-3-line text-secondary" /> {t('finance.budgets') || 'Budgets'}
          </h3>
          <Button onClick={openAddBudget} className="btn-secondary">
            <span className="ri-add-line" /> {t('finance.addBudget') || 'Add Budget'}
          </Button>
        </div>
        {isLoading ? (
          <p className="text-sm text-base-content/50 py-6 text-center">Loading…</p>
        ) : (summary?.budgets.length ?? 0) === 0 ? (
          <p className="text-sm text-base-content/50 py-6 text-center">
            {t('finance.noBudgets') || 'No budgets set — add a spending limit per category or for the whole period.'}
          </p>
        ) : (
          <div className="space-y-3">
            {summary!.budgets.map((bt) => {
              const pct = bt.budget_amount > 0 ? Math.min(100, Math.round((bt.spent / bt.budget_amount) * 100)) : 0;
              return (
                <div key={bt.budget_id} className="bg-base-100/50 border border-slate-200 dark:border-white/10 rounded-xl p-4">
                  <div className="flex items-start justify-between gap-3 mb-2">
                    <div className="min-w-0">
                      <p className="font-semibold text-base-content">
                        {bt.category_id ? (CATEGORY_LABELS[bt.category_id] || bt.category_id) : (t('finance.globalBudget') || 'Global budget')}
                      </p>
                      <p className="text-xs text-base-content/50 tabular-nums">{bt.period_start} → {bt.period_end}</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {bt.over && (
                        <span className="px-2 py-0.5 rounded-full bg-error/15 text-error text-xs font-semibold">
                          {t('finance.over') || 'Over'} {Math.round((bt.spent / Math.max(bt.budget_amount, 0.01) - 1) * 100)}%
                        </span>
                      )}
                      <button onClick={() => openEditBudget(budgets.find((b) => b.id === bt.budget_id)!)}
                        title={t('common.edit')} className="text-info hover:text-info/70 p-1.5 rounded-lg hover:bg-info/10">
                        <span className="ri-pencil-line ri-16px" />
                      </button>
                      <button onClick={() => setDeleteBudget(budgets.find((b) => b.id === bt.budget_id)!)}
                        title={t('common.delete')} className="text-error hover:text-error/70 p-1.5 rounded-lg hover:bg-error/10">
                        <span className="ri-delete-bin-line ri-16px" />
                      </button>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 h-2 rounded-full bg-base-300/50 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all ${bt.over ? 'bg-error' : 'bg-success'}`}
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className={`text-xs tabular-nums font-medium whitespace-nowrap ${bt.over ? 'text-error' : 'text-base-content/70'}`}>
                      {bt.spent.toLocaleString()} / {bt.budget_amount.toLocaleString()}
                      <span className="text-base-content/40"> ({bt.remaining >= 0 ? '+' : ''}{bt.remaining.toLocaleString()})</span>
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </Card>

      {/* ── Add/Edit Transaction modal ── */}
      <FormModal
        isOpen={!!txModal}
        onClose={() => setTxModal(null)}
        title={txModal?.mode === 'edit' ? t('finance.editTxTitle') || 'Edit Transaction' : t('finance.addTxTitle') || 'Add Transaction'}
        size="md"
        submitLabel={txModal?.mode === 'edit' ? t('common.update') : t('finance.addTx') || 'Add Transaction'}
        cancelLabel={t('common.cancel')}
        submitDisabled={!txForm.date || !txForm.category_id || txForm.amount <= 0}
        onSubmit={handleSaveTx}
        submitClassName="btn-primary"
        contentTestId="finance-tx-modal"
      >
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <label className="field">
              <span className="field__label">{t('finance.date') || 'Date'}</span>
              <input
                type="date"
                value={txForm.date}
                onChange={(e) => setTxForm({ ...txForm, date: e.target.value })}
                className="input"
              />
            </label>
            <label className="field">
              <span className="field__label">{t('finance.type') || 'Type'}</span>
              <select
                value={txForm.direction}
                onChange={(e) => setTxForm({ ...txForm, direction: e.target.value })}
                className="select"
              >
                <option value="collection">{t('finance.income') || 'Income'}</option>
                <option value="payment">{t('finance.expense') || 'Expense'}</option>
              </select>
            </label>
          </div>
          <label className="field">
            <span className="field__label">{t('finance.category') || 'Category'}</span>
            <select
              value={txForm.category_id}
              onChange={(e) => setTxForm({ ...txForm, category_id: e.target.value })}
              className="select"
            >
              {INVOICE_CATEGORIES.map((c) => (
                <option key={c.id} value={c.id}>{c.label}</option>
              ))}
            </select>
          </label>
          <label className="field">
            <span className="field__label">{t('finance.amount') || 'Amount'}</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={txForm.amount || ''}
              onChange={(e) => setTxForm({ ...txForm, amount: Number(e.target.value) })}
              className="input"
              placeholder="0"
            />
          </label>
          <label className="field">
            <span className="field__label">{t('finance.description') || 'Description'}</span>
            <input
              type="text"
              value={txForm.description ?? ''}
              onChange={(e) => setTxForm({ ...txForm, description: e.target.value || null })}
              className="input"
            />
          </label>
          <label className="field">
            <span className="field__label">{t('finance.reference') || 'Reference'}</span>
            <input
              type="text"
              value={txForm.reference ?? ''}
              onChange={(e) => setTxForm({ ...txForm, reference: e.target.value || null })}
              className="input"
              placeholder={t('finance.referencePlaceholder') || 'Invoice #, receipt #…'}
            />
          </label>
        </div>
      </FormModal>

      {/* ── Add/Edit Budget modal ── */}
      <FormModal
        isOpen={!!budgetModal}
        onClose={() => setBudgetModal(null)}
        title={budgetModal?.mode === 'edit' ? t('finance.editBudgetTitle') || 'Edit Budget' : t('finance.addBudgetTitle') || 'Add Budget'}
        size="md"
        submitLabel={budgetModal?.mode === 'edit' ? t('common.update') : t('finance.addBudget') || 'Add Budget'}
        cancelLabel={t('common.cancel')}
        submitDisabled={!budgetForm.period_start || !budgetForm.period_end || budgetForm.amount <= 0}
        onSubmit={handleSaveBudget}
        submitClassName="btn-secondary"
        contentTestId="finance-budget-modal"
      >
        <div className="space-y-4">
          <label className="field">
            <span className="field__label">{t('finance.category') || 'Category'}</span>
            <select
              value={budgetForm.category_id ?? ''}
              onChange={(e) => setBudgetForm({ ...budgetForm, category_id: e.target.value || null })}
              className="select"
            >
              <option value="">{t('finance.globalBudget') || 'Global budget (all categories)'}</option>
              {INVOICE_CATEGORIES.map((c) => (
                <option key={c.id} value={c.id}>{c.label}</option>
              ))}
            </select>
          </label>
          <div className="grid grid-cols-2 gap-3">
            <label className="field">
              <span className="field__label">{t('finance.periodStart') || 'Period start'}</span>
              <input
                type="date"
                value={budgetForm.period_start}
                onChange={(e) => setBudgetForm({ ...budgetForm, period_start: e.target.value })}
                className="input"
              />
            </label>
            <label className="field">
              <span className="field__label">{t('finance.periodEnd') || 'Period end'}</span>
              <input
                type="date"
                value={budgetForm.period_end}
                onChange={(e) => setBudgetForm({ ...budgetForm, period_end: e.target.value })}
                className="input"
              />
            </label>
          </div>
          <label className="field">
            <span className="field__label">{t('finance.budgetAmount') || 'Budget amount'}</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={budgetForm.amount || ''}
              onChange={(e) => setBudgetForm({ ...budgetForm, amount: Number(e.target.value) })}
              className="input"
              placeholder="0"
            />
          </label>
        </div>
      </FormModal>

      <ConfirmDialog
        isOpen={!!deleteTx}
        onClose={() => setDeleteTx(null)}
        onConfirm={handleDeleteTx}
        title={t('finance.deleteTxTitle') || 'Delete transaction?'}
        message={t('finance.deleteTxConfirm') || 'Delete this finance transaction?'}
        itemName={deleteTx?.description || deleteTx?.reference || String(deleteTx?.amount ?? '')}
        description={t('finance.deleteTxDesc') || 'This will remove the income/expense record and update the summary.'}
        confirmLabel="Delete"
      />

      <ConfirmDialog
        isOpen={!!deleteBudget}
        onClose={() => setDeleteBudget(null)}
        onConfirm={handleDeleteBudget}
        title={t('finance.deleteBudgetTitle') || 'Delete budget?'}
        message={t('finance.deleteBudgetConfirm') || 'Delete this budget?'}
        itemName={deleteBudget?.category_id ? (CATEGORY_LABELS[deleteBudget.category_id] || deleteBudget.category_id) : (t('finance.globalBudget') || 'Global budget')}
        description={t('finance.deleteBudgetDesc') || 'Budget tracking for this period will be removed.'}
        confirmLabel="Delete"
      />

      <StatusToast type={toast?.type || 'success'} message={toast?.message || ''} visible={!!toast} onDismiss={() => setToast(null)} />
    </div>
  );
}
