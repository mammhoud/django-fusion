import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderWithRouter, screen, waitFor, userEvent, within } from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import { getInvokeHistory } from '../setup';
import FinancePanel from '../../components/analytics/FinancePanel';

const mockSummary = {
  total_income: 1500,
  total_expense: 350,
  net: 1150,
  income_by_category: [{ category_id: 'products', direction: 'collection', total: 1500 }],
  expense_by_category: [
    { category_id: 'pay_supplier', direction: 'payment', total: 300 },
    { category_id: 'employee_meal', direction: 'payment', total: 50 },
  ],
  budgets: [
    { budget_id: 1, category_id: null, period_start: '2026-11-01', period_end: '2026-11-30', budget_amount: 400, spent: 350, remaining: 50, over: false },
    { budget_id: 2, category_id: 'pay_supplier', period_start: '2026-11-01', period_end: '2026-11-30', budget_amount: 200, spent: 300, remaining: -100, over: true },
  ],
};

const mockTxs = [
  { id: 1, date: '2026-11-01', category_id: 'products', direction: 'collection', amount: 1000, description: 'Daily sales', reference: 'INV-100', created_at: '2026-11-01T00:00:00', updated_at: '2026-11-01T00:00:00' },
  { id: 2, date: '2026-11-10', category_id: 'pay_supplier', direction: 'payment', amount: 300, description: 'Supplier payment', reference: null, created_at: '2026-11-10T00:00:00', updated_at: '2026-11-10T00:00:00' },
];

const mockBudgets = [
  { id: 1, category_id: null, period_start: '2026-11-01', period_end: '2026-11-30', amount: 400, created_at: '2026-11-01T00:00:00', updated_at: '2026-11-01T00:00:00' },
  { id: 2, category_id: 'pay_supplier', period_start: '2026-11-01', period_end: '2026-11-30', amount: 200, created_at: '2026-11-01T00:00:00', updated_at: '2026-11-01T00:00:00' },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_finance_summary', mockSummary);
  mockInvokeSuccess('get_finance_transactions', mockTxs);
  mockInvokeSuccess('get_budgets', mockBudgets);
});

describe('FinancePanel', () => {
  it('renders summary stat cards with income/expense/net', async () => {
    renderWithRouter(<FinancePanel />);

    await waitFor(() => {
      expect(screen.getByText(/finance\.totalIncome|Total Income/)).toBeInTheDocument();
    });
    // Total income 1500, total expense 350
    expect(screen.getAllByText(/1,?500/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/350/).length).toBeGreaterThanOrEqual(1);
    // Over budget count = 1
    expect(screen.getAllByText('1', { exact: true }).length).toBeGreaterThanOrEqual(1);
  });

  it('lists income and outcome transactions with categories', async () => {
    renderWithRouter(<FinancePanel />);

    await waitFor(() => {
      expect(screen.getByText('Daily sales')).toBeInTheDocument();
    });
    expect(screen.getByText('Supplier payment')).toBeInTheDocument();
    // Direction labels in the ledger rows (Income / Expense)
    expect(screen.getAllByText('Income').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Expense').length).toBeGreaterThanOrEqual(1);
    // Category labels from INVOICE_CATEGORIES (Products income row + Pay Supplier expense row)
    expect(screen.getByText('Products')).toBeInTheDocument();
    expect(screen.getAllByText('Pay Supplier').length).toBeGreaterThanOrEqual(1);
    // Signed amounts: +1,000 income, −300 expense
    expect(screen.getByText('+1,000')).toBeInTheDocument();
    expect(screen.getByText('−300')).toBeInTheDocument();
  });

  it('shows budget tracking with over-budget warning', async () => {
    renderWithRouter(<FinancePanel />);

    await waitFor(() => {
      expect(screen.getAllByText('Budgets').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText('Global budget').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Pay Supplier').length).toBeGreaterThanOrEqual(1);
    // Over-budget badge (spent 300 of 200 = 50% over)
    expect(screen.getAllByText(/Over 50%/).length).toBeGreaterThanOrEqual(1);
    // Spent/budget ratio text
    expect(screen.getByText(/350\s*\/\s*400/)).toBeInTheDocument();
    expect(screen.getByText(/300\s*\/\s*200/)).toBeInTheDocument();
  });

  it('adds a finance transaction via the modal', async () => {
    mockInvokeSuccess('add_finance_transaction', { id: 3, date: '2026-11-15', category_id: 'products', direction: 'payment', amount: 75, description: 'Refund', reference: null, created_at: '', updated_at: '' });
    renderWithRouter(<FinancePanel />);

    await waitFor(() => {
      expect(screen.getByText('Daily sales')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/finance\.addTx|Add Transaction/));
    await waitFor(() => {
      expect(screen.getByTestId('finance-tx-modal')).toBeInTheDocument();
    });

    // Switch direction to expense, set amount + description.
    const modal = screen.getByTestId('finance-tx-modal');
    await userEvent.selectOptions(within(modal).getAllByRole('combobox')[0], 'payment');
    const amountInput = within(modal).getByPlaceholderText('0');
    await userEvent.clear(amountInput);
    await userEvent.type(amountInput, '75');
    const descInput = within(modal).getAllByRole('textbox')[0];
    await userEvent.type(descInput, 'Refund');

    await userEvent.click(screen.getByTestId('finance-tx-modal-submit'));

    await waitFor(() => {
      const call = getInvokeHistory().find(h => h.cmd === 'add_finance_transaction');
      expect(call).toBeDefined();
      expect(call?.args?.tx).toMatchObject({
        category_id: 'products',
        direction: 'payment',
        amount: 75,
        description: 'Refund',
      });
    });
  });

  it('adds a budget via the modal', async () => {
    mockInvokeSuccess('add_budget', { id: 3, category_id: 'products', period_start: '2026-11-01', period_end: '2026-11-30', amount: 500, created_at: '', updated_at: '' });
    renderWithRouter(<FinancePanel />);

    await waitFor(() => {
      expect(screen.getByText('Daily sales')).toBeInTheDocument();
    });

    // The header Add Budget button is the first matching button in the card.
    await userEvent.click(screen.getAllByText(/Add Budget/)[0]);
    await waitFor(() => {
      expect(screen.getByTestId('finance-budget-modal')).toBeInTheDocument();
    });

    const modal = screen.getByTestId('finance-budget-modal');
    // Category select (first combobox), amount input
    await userEvent.selectOptions(within(modal).getAllByRole('combobox')[0], 'products');
    const amountInput = within(modal).getByPlaceholderText('0');
    await userEvent.clear(amountInput);
    await userEvent.type(amountInput, '500');

    await userEvent.click(screen.getByTestId('finance-budget-modal-submit'));

    await waitFor(() => {
      const call = getInvokeHistory().find(h => h.cmd === 'add_budget');
      expect(call).toBeDefined();
      expect(call?.args?.budget).toMatchObject({
        category_id: 'products',
        amount: 500,
      });
    });
  });

  it('deletes a finance transaction after confirmation', async () => {
    mockInvokeSuccess('delete_finance_transaction', null);
    renderWithRouter(<FinancePanel />);

    await waitFor(() => {
      expect(screen.getByText('Daily sales')).toBeInTheDocument();
    });

    await userEvent.click(screen.getAllByTitle('Delete')[0]);
    await waitFor(() => {
      expect(screen.getByText(/finance\.deleteTxTitle|Delete transaction\?/)).toBeInTheDocument();
    });
    // ConfirmDialog confirm button — shows the i18n 'confirmDialog.deactivate'/'Delete' label.
    await userEvent.click(screen.getByText('Delete'));

    await waitFor(() => {
      const call = getInvokeHistory().find(h => h.cmd === 'delete_finance_transaction');
      expect(call).toBeDefined();
      expect(call?.args?.id).toBe(1);
    });
  });

  it('searches transactions by description', async () => {
    renderWithRouter(<FinancePanel />);

    await waitFor(() => {
      expect(screen.getByText('Daily sales')).toBeInTheDocument();
    });

    const search = screen.getByPlaceholderText(/finance\.searchTx|Search transactions/);
    await userEvent.type(search, 'Supplier');

    await waitFor(() => {
      expect(screen.getByText('Supplier payment')).toBeInTheDocument();
      expect(screen.queryByText('Daily sales')).not.toBeInTheDocument();
    });
  });
});
