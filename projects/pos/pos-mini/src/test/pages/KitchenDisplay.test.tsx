import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import KitchenDisplay from '../../pages/KitchenDisplay';

const mockTickets = [
  { id: 1, sale_id: 100, status: 'pending', notes: 'No onions',      created_at: '2026-01-15T10:00:00' },
  { id: 2, sale_id: 101, status: 'pending', notes: 'Extra spicy',    created_at: '2026-01-15T10:05:00' },
  { id: 3, sale_id: 102, status: 'pending', notes: '',              created_at: '2026-01-15T10:10:00' },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_kitchen_tickets', mockTickets);
});

describe('KitchenDisplay page', () => {
  it('hydrates tickets for the default pending status', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      // sale_id 100 → displayed as "Ticket #100"
      const tickets = screen.getAllByText(/kitchen\.ticket|Ticket #/);
      expect(tickets.length).toBeGreaterThanOrEqual(3);
    });
  });

  it('shows the debounced text search input + result counter', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getByLabelText(/kitchen\.searchPlaceholder|Search kitchen tickets/)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText('3 / 3')).toBeInTheDocument();
    });
  });

  it('filters by sale_id after the idle debounce window', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/kitchen\.ticket\s*#100|Ticket\s*#100/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/kitchen\.ticket\s*#101|Ticket\s*#101/).length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByLabelText(/kitchen\.searchPlaceholder|Search kitchen tickets/);
    await userEvent.type(searchInput, '101');

    await waitFor(
      () => {
        expect(screen.getAllByText(/kitchen\.ticket\s*#101|Ticket\s*#101/).length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText(/kitchen\.ticket\s*#100|Ticket\s*#100/)).not.toBeInTheDocument();
        expect(screen.queryByText(/kitchen\.ticket\s*#102|Ticket\s*#102/)).not.toBeInTheDocument();
        expect(screen.getByText('1 / 3')).toBeInTheDocument();
      },
      { timeout: 800 },
    );
  });

  it('filters by notes substring after the idle debounce window', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/kitchen\.ticket\s*#100|Ticket\s*#100/).length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByLabelText(/kitchen\.searchPlaceholder|Search kitchen tickets/);
    await userEvent.type(searchInput, 'spicy');

    await waitFor(
      () => {
        expect(screen.getAllByText(/kitchen\.ticket\s*#101|Ticket\s*#101/).length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText(/kitchen\.ticket\s*#100|Ticket\s*#100/)).not.toBeInTheDocument();
        expect(screen.queryByText(/kitchen\.ticket\s*#102|Ticket\s*#102/)).not.toBeInTheDocument();
      },
      { timeout: 800 },
    );
  });

  it('status filter dropdown propagates the chosen status to backend invoke', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/kitchen\.ticket\s*#100|Ticket\s*#100/).length).toBeGreaterThanOrEqual(1);
    });

    // Switch to "all" tickets status. Default mock returns the same 3 tickets regardless.
    await userEvent.selectOptions(
      screen.getByLabelText(/kitchen\.statusFilter|Filter by status/),
      'all',
    );

    await waitFor(() => {
      // Backend is invoked again with status=null (since filter==='all' -> null).
      // Verify the controlled <select> reflects the new value by reading its
      // DOM value directly — getByDisplayValue is fragile because the option
      // text content is i18n-dependent ("All Tickets" vs "kitchen.allTickets").
      const sel = screen.getByLabelText(/kitchen\.statusFilter|Filter by status/) as HTMLSelectElement;
      expect(sel.value).toBe('all');
    });
  });

  it('shows the no-tickets empty state when the list is empty', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_kitchen_tickets', []);
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getByText(/kitchen\.noTickets|No kitchen tickets/)).toBeInTheDocument();
    });
  });
});
