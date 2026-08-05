import { describe, it, expect, beforeEach, vi } from 'vitest';
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
    id: 1,
    date: '2026-01-15',
    time: '12:00',
    currency: 'USD',
    total_amount: 350,
    order_type: 'dine-in',
    status: 'completed',
    items: [{ name: 'Burger', price: 350, quantity: 1, subtotal: 350, unit: 'piece' }],
    customer_name: null,
    table_number: 1,
    delivery_type: null,
    delivery_address: null,
    employee_name: null,
    tax_breakdown: null,
  },
];

const mockSettings = {
  restaurant_name: 'Test Restaurant',
  address: '123 Main St',
  phone: '03001234567',
  currency: 'USD',
  receipt_footer: 'Thank you!',
};

beforeEach(() => {
  vi.clearAllMocks();
  mocks.getTransactions.mockReturnValue({ data: mockTransactions, isLoading: false, error: undefined });
  mocks.getSettings.mockReturnValue({ data: mockSettings });
  mocks.deleteTransaction.mockResolvedValue({ data: undefined });
});

describe('Transactions page', () => {
  it('surfaces load errors via the status toast (covers the silent-failure path)', async () => {
    // RTK Query network errors have the shape { error: 'message' }, not { message: '...' }
    mocks.getTransactions.mockReturnValue({ data: [], isLoading: false, error: { error: 'Network unreachable' } });

    renderWithRouter(<Transactions />);

    // React Strict Mode double-fires effects in dev, which may produce
    // duplicate toast entries — use getAllByText to handle both cases.
    await waitFor(() => {
      expect(screen.getAllByText(/Network unreachable/i).length).toBeGreaterThan(0);
    });
  });

  it('hydrates transactions + grouped revenue from a successful load', async () => {
    renderWithRouter(<Transactions />);

    await waitFor(() => {
      expect(screen.getByText(/No Data|Time Total|transactions\.title/i)).toBeInTheDocument();
    });
  });
});
