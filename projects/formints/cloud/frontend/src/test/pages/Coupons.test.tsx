import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import Coupons from '../../app/pages/admin/Coupons';

const mockCoupons = [
  { id: 1, code: 'SAVE10', kind: 'percent', value: 10, min_subtotal: 500, is_active: true },
  { id: 2, code: 'WELCOME5', kind: 'fixed', value: 5, min_subtotal: null, is_active: true },
  { id: 3, code: 'OLD20', kind: 'percent', value: 20, min_subtotal: null, is_active: false },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_coupons', mockCoupons);
});

describe('Coupons page', () => {
  it('hydrates the coupon list from the backend', async () => {
    renderWithRouter(<Coupons />);

    await waitFor(() => {
      expect(screen.getByText('SAVE10')).toBeInTheDocument();
    });
    expect(screen.getByText('WELCOME5')).toBeInTheDocument();
    expect(screen.getByText('OLD20')).toBeInTheDocument();
    // Percent renders as "10%" and fixed as a price
    expect(screen.getByText('10%')).toBeInTheDocument();
  });

  it('shows search input + result counter', async () => {
    renderWithRouter(<Coupons />);

    await waitFor(() => {
      expect(screen.getByTestId('coupons-search-input')).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText('3 / 3')).toBeInTheDocument();
    });
  });

  it('search by code filters the list after the idle debounce window', async () => {
    renderWithRouter(<Coupons />);

    await waitFor(() => {
      expect(screen.getByText('3 / 3')).toBeInTheDocument();
    });

    const search = screen.getByTestId('coupons-search-input');
    await userEvent.type(search, 'SAVE');

    await waitFor(() => {
      expect(screen.getByText('1 / 3')).toBeInTheDocument();
    });
    expect(screen.queryByText('WELCOME5')).not.toBeInTheDocument();
  });

  it('toggles a coupon active state via update_coupon', async () => {
    mockInvokeSuccess('update_coupon', { ...mockCoupons[0], is_active: false });
    renderWithRouter(<Coupons />);

    await waitFor(() => {
      expect(screen.getByText('SAVE10')).toBeInTheDocument();
    });

    const toggles = screen.getAllByRole('checkbox', { name: /Toggle active/i });
    await userEvent.click(toggles[0]);

    await waitFor(() => {
      expect(screen.getByText('Coupon saved')).toBeInTheDocument();
    });
  });

  it('deletes a coupon after confirm', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);
    mockInvokeSuccess('delete_coupon', null);
    renderWithRouter(<Coupons />);

    await waitFor(() => {
      expect(screen.getByText('SAVE10')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByTitle(/Delete/i);
    await userEvent.click(deleteButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Coupon deleted')).toBeInTheDocument();
    });
  });
});
