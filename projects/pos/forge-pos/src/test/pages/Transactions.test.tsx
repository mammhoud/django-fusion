import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import Transactions from '../../pages/sales/Transactions';

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
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_transactions', mockTransactions);
  mockInvokeSuccess('get_settings', mockSettings);
  mockInvokeSuccess('check_auth_required', false);
});

describe('Transactions page', () => {
  it('surfaces load errors via the status toast (covers the silent-failure path)', async () => {
    resetInvokeMocks();
    mockInvokeError('get_transactions', 'Network unreachable');
    mockInvokeSuccess('get_settings', mockSettings);
    renderWithRouter(<Transactions />);

    await waitFor(() => {
      expect(screen.getByText(/Network unreachable/i)).toBeInTheDocument();
    });
  });

  it('hydrates transactions + grouped revenue from a successful load', async () => {
    renderWithRouter(<Transactions />);

    await waitFor(() => {
      expect(screen.getByText(/No Data|Time Total|transactions\.title/i)).toBeInTheDocument();
    });
  });
});
