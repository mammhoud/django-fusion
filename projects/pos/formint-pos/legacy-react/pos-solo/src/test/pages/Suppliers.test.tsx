import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import Suppliers from '../../pages/Suppliers';

const mockSuppliers = [
  { id: 3, name: 'Zebra Foods',  contact_name: 'Zane',  email: 'z@z.com', phone: '1', address: 'a', tax_id: '', payment_terms: '', is_active: true },
  { id: 1, name: 'Alpha Meats',  contact_name: 'Avi',   email: 'a@a.com', phone: '2', address: 'b', tax_id: '', payment_terms: '', is_active: true },
  { id: 2, name: 'Mango Drinks', contact_name: 'Mira',  email: 'm@m.com', phone: '3', address: 'c', tax_id: '', payment_terms: '', is_active: true },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_suppliers', mockSuppliers);
});

describe('Suppliers page', () => {
  it('hydrates supplier list from the backend', async () => {
    renderWithRouter(<Suppliers />);

    await waitFor(() => {
      expect(screen.getAllByText('Alpha Meats').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText('Zebra Foods').length).toBeGreaterThanOrEqual(1);
  });

  it('debounces search input — query lands only after idle window', async () => {
    renderWithRouter(<Suppliers />);

    await waitFor(() => {
      expect(screen.getAllByText('Alpha Meats').length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByLabelText(/suppliers\.searchPlaceholder/);
    await userEvent.type(searchInput, 'mango');

    await waitFor(
      () => {
        expect(screen.queryByText('Alpha Meats')).not.toBeInTheDocument();
        expect(screen.queryByText('Zebra Foods')).not.toBeInTheDocument();
        expect(screen.getAllByText('Mango Drinks').length).toBeGreaterThanOrEqual(1);
      },
      { timeout: 800 },
    );
  });

  it('sort-by-name-asc reorders the list', async () => {
    renderWithRouter(<Suppliers />);

    await waitFor(() => {
      expect(screen.getAllByText('Alpha Meats').length).toBeGreaterThanOrEqual(1);
    });

    // Newest (default) order → Zebra, Alpha, Mango (by id desc)
    const sortSelect = screen.getByLabelText(/suppliers\.sortBy/);
    await userEvent.selectOptions(sortSelect, 'name-asc');

    await waitFor(() => {
      // First visible card title should now be Alpha (sorted name ascending)
      const headings = screen.getAllByRole('heading', { level: 3 });
      expect(headings[0].textContent).toBe('Alpha Meats');
    });
  });

  it('surfaces load errors via the status toast', async () => {
    resetInvokeMocks();
    mockInvokeError('get_suppliers', 'Network unreachable');
    renderWithRouter(<Suppliers />);

    await waitFor(() => {
      expect(screen.getByText(/Network unreachable/i)).toBeInTheDocument();
    });
  });
});
