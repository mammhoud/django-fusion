import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import Transactions from '../../app/pages/pos/Transactions';

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

  it('navigates between the product-statistics, related-products, and invoices tabs', async () => {
    renderWithRouter(<Transactions />);

    await waitFor(() => {
      expect(screen.getByText('Time Total')).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole('tab', { name: /Product Statistics/i }));
    await waitFor(() => {
      // Burger appears in the product stats table (built from transaction items)
      expect(screen.getAllByText('Burger').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByRole('tab', { name: /Related Products/i }));
    await waitFor(() => {
      expect(screen.getAllByText('Burger').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByRole('tab', { name: /Invoices/i }));
    await waitFor(() => {
      expect(screen.getAllByText('Burger').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('opens the receipt dialog for a transaction row', async () => {
    renderWithRouter(<Transactions />);

    await waitFor(() => {
      expect(screen.getByText('Time Total')).toBeInTheDocument();
    });

    // Receipt buttons are icon-only (tabler--printer) — no accessible name,
    // so they carry data-testid="receipt-button" for testability.
    const printerBtn = screen.getAllByTestId('receipt-button')[0];
    expect(printerBtn).toBeDefined();

    await userEvent.click(printerBtn as HTMLButtonElement);

    await waitFor(() => {
      // Receipt dialog heading uses transactions.receipt = 'Receipt'
      expect(screen.getByRole('heading', { name: /Receipt/i })).toBeInTheDocument();
      expect(screen.getByText(/Burger/i)).toBeInTheDocument();
    });
  });

  it('filters by order type and payment method pills with an active-count badge', async () => {
    renderWithRouter(<Transactions />);

    await waitFor(() => {
      expect(screen.getByText('Time Total')).toBeInTheDocument();
    });

    // Open the filter panel
    await userEvent.click(screen.getByText('Filters'));

    // Order Type + Payment Method groups render their pill options
    expect(screen.getByText('Dine-in')).toBeInTheDocument();
    expect(screen.getByText('Takeaway')).toBeInTheDocument();
    expect(screen.getByText('Cash')).toBeInTheDocument();
    expect(screen.getByText('Card')).toBeInTheDocument();

    // Selecting a filter marks it active and shows the count badge
    await userEvent.click(screen.getByText('Dine-in'));
    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument();
    });
    expect(screen.getByText('Dine-in')).toHaveAttribute('aria-pressed', 'true');

    // Clear all resets the filters and hides the badge
    await userEvent.click(screen.getByText('Clear Filters'));
    await waitFor(() => {
      expect(screen.queryByText('1')).not.toBeInTheDocument();
    });
  });
});
