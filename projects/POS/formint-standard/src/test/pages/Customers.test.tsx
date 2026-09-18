import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import Customers from '../../app/pages/customers/Customers';

const mockCustomers = [
  { id: 1, name: 'Alice Smith', phone: '03001111111', email: 'alice@example.com', notes: 'VIP', loyalty_points: 120 },
  { id: 2, name: 'Bob Khan', phone: '03002222222', email: 'bob@example.com', notes: '', loyalty_points: 30 },
  { id: 3, name: 'Carla Singh', phone: '03003333333', email: null, notes: '', loyalty_points: 65 },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_customers', mockCustomers);
});

afterEach(() => {
  vi.useRealTimers();
});

describe('Customers page', () => {
  it('hydrates from the backend and renders customer cards', async () => {
    renderWithRouter(<Customers />);

    await waitFor(() => {
      expect(screen.getAllByText('Alice Smith').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText('Bob Khan').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Carla Singh').length).toBeGreaterThanOrEqual(1);
  });

  it('debounces search input — filter applies only after the idle window', async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    renderWithRouter(<Customers />);

    await waitFor(() => {
      expect(screen.getAllByText('Alice Smith').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('Bob Khan').length).toBeGreaterThanOrEqual(1);
    });

    // i18n mock resolves real en.json → aria-label is 'Search customers...'
    const searchInput = screen.getByLabelText(/Search customers/);
    await userEvent.type(searchInput, 'alice');

    // Right after typing, Bob is still visible (debounce window not elapsed)
    expect(screen.getAllByText('Bob Khan').length).toBeGreaterThanOrEqual(1);

    // After 250ms of idle time only Alice should remain
    await waitFor(
      () => {
        expect(screen.getAllByText('Alice Smith').length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText('Bob Khan')).not.toBeInTheDocument();
        expect(screen.queryByText('Carla Singh')).not.toBeInTheDocument();
      },
      { timeout: 800 },
    );
  });

  it('surfaces load errors via the status toast', async () => {
    resetInvokeMocks();
    mockInvokeError('get_customers', 'Database is offline');
    renderWithRouter(<Customers />);

    await waitFor(() => {
      expect(screen.getByText(/Database is offline/i)).toBeInTheDocument();
    });
  });

  it('shows the empty-state placeholder when no customers exist', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_customers', []);
    renderWithRouter(<Customers />);

    // i18n mock resolves real en.json → empty-state text is 'No customers yet…'
    await waitFor(() => {
      expect(screen.getByText(/No customers yet/)).toBeInTheDocument();
    });
  });

  it('opens the add form and saves a new customer via add_customer', async () => {
    mockInvokeSuccess('add_customer', { id: 4 });
    renderWithRouter(<Customers />);

    await waitFor(() => {
      expect(screen.getAllByText('Alice Smith').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByRole('button', { name: /Add Customer/i }));

    // Form appears with the Name field focused
    const nameInput = screen.getByPlaceholderText('Name');
    await userEvent.type(nameInput, 'Dana White');
    await userEvent.type(screen.getByPlaceholderText('Phone'), '03004444444');

    await userEvent.click(screen.getByRole('button', { name: /Save/i }));

    await waitFor(() => {
      expect(screen.getByText(/Saved/i)).toBeInTheDocument();
    });
  });

  it('closes the add form via Cancel without saving', async () => {
    renderWithRouter(<Customers />);

    await waitFor(() => {
      expect(screen.getAllByText('Alice Smith').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByRole('button', { name: /Add Customer/i }));
    expect(screen.getByPlaceholderText('Name')).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /Cancel/i }));

    await waitFor(() => {
      expect(screen.queryByPlaceholderText('Name')).not.toBeInTheDocument();
    });
  });
});
