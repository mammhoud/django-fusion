import { describe, it, expect, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Transactions from '@/app/pages/pos/Transactions';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import { clearInvokeHistory, getInvokeHistory } from '../setup';
import { renderWithRouter } from '../test-utils';

const mockSettings = {
  restaurant_name: 'Formint',
  address: '',
  phone: '',
  currency: 'USD',
  receipt_footer: 'Thank you for your business!',
};

const completedSale = {
  id: 1,
  items: [],
  total_amount: 25,
  currency: 'USD',
  date: '2026-08-01',
  time: '12:00',
  order_type: 'dine-in',
  status: 'completed',
  payment_method: 'cash',
  discount_amount: 0,
};

describe('Transactions refund flow', () => {
  beforeEach(() => {
    resetInvokeMocks();
    clearInvokeHistory();
    mockInvokeSuccess('get_settings', mockSettings);
  });

  it('refunds a completed sale and shows the refunded chip', async () => {
    mockInvokeSuccess('get_transactions', [completedSale]);
    renderWithRouter(<Transactions />);

    await waitFor(() =>
      expect(screen.getAllByText('USD 25.00').length).toBeGreaterThan(0),
    );

    const refundButton = await screen.findByRole('button', { name: /refund/i });
    await userEvent.click(refundButton);

    const confirm = await screen.findByRole('button', { name: /confirm refund/i });
    await userEvent.click(confirm);

    await waitFor(() =>
      expect(getInvokeHistory()).toContainEqual({
        cmd: 'refund_sale',
        args: { saleId: 1 },
      }),
    );
    // Local state flips the row to `refunded` — the chip renders immediately
    // and the success toast confirms the action.
    await waitFor(() => expect(screen.getByText('Refunded')).toBeTruthy());
    await waitFor(() => expect(screen.getByText('Refund successful')).toBeTruthy());
  });

  it('does not offer refund for an already refunded sale', async () => {
    mockInvokeSuccess('get_transactions', [{ ...completedSale, status: 'refunded' }]);
    renderWithRouter(<Transactions />);

    await waitFor(() => expect(screen.getByText('Refunded')).toBeTruthy());
    expect(screen.queryByRole('button', { name: /refund/i })).toBeNull();
  });

  it('surfaces an error when the refund command fails', async () => {
    mockInvokeSuccess('get_transactions', [completedSale]);
    renderWithRouter(<Transactions />);

    await waitFor(() =>
      expect(screen.getAllByText('USD 25.00').length).toBeGreaterThan(0),
    );
    const refundButton = await screen.findByRole('button', { name: /refund/i });
    await userEvent.click(refundButton);

    // Register the error AFTER the open-click so the dialog's confirm step
    // can be reached; failing refund_sale surfaces the error in the toast.
    mockInvokeError('refund_sale', 'sale 1 is already refunded');
    const confirm = await screen.findByRole('button', { name: /confirm refund/i });
    await userEvent.click(confirm);

    await waitFor(() =>
      expect(screen.getByText(/sale 1 is already refunded/i)).toBeTruthy(),
    );
  });
});
