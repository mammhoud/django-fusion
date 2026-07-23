import { describe, it, expect, beforeEach, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import {
  renderWithRouter,
  screen,
  waitFor,
} from '../test-utils';
import Transactions from '../../pages/Transactions';

const mocks = vi.hoisted(() => ({
  getTransactions: vi.fn(),
  getSettings: vi.fn(),
  deleteTransaction: vi.fn(),
}));

vi.mock('../../store/api/endpoints/legacy', () => ({
  useGetTransactionsQuery: mocks.getTransactions,
}));

vi.mock('../../store/api/endpoints/core', () => ({
  useGetSettingsQuery: mocks.getSettings,
}));

vi.mock('../../store/api/endpoints/kitchen', () => ({
  useDeleteTransactionMutation: () => [mocks.deleteTransaction],
}));

const mockTransactions = [
  {
    id: 1001,
    date: '2026-01-15',
    time: '12:00',
    currency: 'USD',
    total_amount: 35,
    order_type: 'dine-in',
    status: 'completed',
    items: [
      { name: 'Burger', price: 10, quantity: 2, subtotal: 20, unit: 'piece' },
      { name: 'Fries', price: 5, quantity: 3, subtotal: 15, unit: 'piece' },
    ],
  },
  {
    id: 1002,
    date: '2026-01-16',
    time: '13:30',
    currency: 'USD',
    total_amount: 12,
    order_type: 'takeaway',
    status: 'completed',
    items: [
      { name: 'Burger', price: 12, quantity: 1, subtotal: 12, unit: 'piece' },
    ],
  },
];

const mockSettings = {
  id: 1,
  restaurant_name: 'Test Restaurant',
  address: '123 Main St',
  phone: '03001234567',
  email: 'hello@example.test',
  currency: 'USD',
  receipt_footer: 'Thank you!',
  logo: null,
  tax_rate: '0',
};

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getTransactions.mockReturnValue({ data: mockTransactions, isLoading: false, error: undefined });
  mocks.getSettings.mockReturnValue({ data: mockSettings });
  mocks.deleteTransaction.mockResolvedValue({ data: undefined });
});

describe('Transactions page', () => {
  it('surfaces load errors via the status toast (covers the silent-failure path)', async () => {
    mocks.getTransactions.mockReturnValue({ data: [], isLoading: false, error: { message: 'Network unreachable' } });

    renderWithRouter(<Transactions />);

    await waitFor(() => {
      expect(screen.getByText(/Network unreachable/i)).toBeInTheDocument();
    });
  });

  it('hydrates the default time-total tab from sidecar data', async () => {
    renderWithRouter(<Transactions />);

    await waitFor(() => {
      expect(screen.getByText('transactions.allTimeTotal')).toBeInTheDocument();
    });
    expect(screen.getAllByText(/USD 47\.00/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/transactions.orders/).length).toBeGreaterThan(0);
  });

  it('shows product totals after switching to the product statistics tab', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Transactions />);

    await user.click(await screen.findByText('transactions.productStats'));

    expect(screen.getByText('reports.totalProductsSold')).toBeInTheDocument();
    expect(screen.getByText('transactions.uniqueProducts')).toBeInTheDocument();
    expect(screen.getAllByText('Burger').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Fries').length).toBeGreaterThan(0);
    expect(screen.getAllByText(/USD 32\.00|USD 15\.00/).length).toBeGreaterThan(0);
  });

  it('shows related product invoice data after switching tabs', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Transactions />);

    await user.click(await screen.findByText('transactions.relatedProducts'));

    expect(screen.getByText('Burger')).toBeInTheDocument();
    expect(screen.getByText(/3 transactions.units sold across 2 transactions.invoices/)).toBeInTheDocument();
    expect(screen.getByText('Fries')).toBeInTheDocument();
    expect(screen.getByText(/3 transactions.units sold across 1 transactions.invoices/)).toBeInTheDocument();
  });

  it('shows invoice cards after switching to the invoices tab', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Transactions />);

    await user.click(await screen.findByText('transactions.invoices'));

    expect(screen.getByText('#1001')).toBeInTheDocument();
    expect(screen.getByText('#1002')).toBeInTheDocument();
    expect(screen.getAllByText('Burger').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Fries').length).toBeGreaterThan(0);
    expect(screen.getByText(/USD 35\.00/)).toBeInTheDocument();
  });
});
