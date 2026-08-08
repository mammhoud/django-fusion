import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import Roles from '../../app/pages/admin/Roles';

const mockRoles = [
  { id: 3, name: 'Manager',  permissions: '["read","write","delete"]', is_active: true },
  { id: 1, name: 'Cashier',  permissions: '["read","checkout"]',         is_active: true },
  { id: 2, name: 'Auditor',  permissions: '["read","reports"]',          is_active: true },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_roles', mockRoles);
});

describe('Roles page', () => {
  it('hydrates the role list from the backend', async () => {
    renderWithRouter(<Roles />);

    await waitFor(() => {
      expect(screen.getAllByText('Manager').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText('Cashier').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Auditor').length).toBeGreaterThanOrEqual(1);
  });

  it('renders a debounced search input with result counter', async () => {
    renderWithRouter(<Roles />);

    await waitFor(() => {
      expect(screen.getByLabelText(/roles\.searchPlaceholder|Search roles/)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText('3 / 3')).toBeInTheDocument();
    });
  });

  it('filters roles by name after the idle debounce window', async () => {
    renderWithRouter(<Roles />);

    await waitFor(() => {
      expect(screen.getAllByText('Manager').length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByLabelText(/roles\.searchPlaceholder|Search roles/);
    await userEvent.type(searchInput, 'cash');

    await waitFor(
      () => {
        expect(screen.getAllByText('Cashier').length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText('Manager')).not.toBeInTheDocument();
        expect(screen.queryByText('Auditor')).not.toBeInTheDocument();
        // Result counter reflects the filtered set.
        expect(screen.getByText('1 / 3')).toBeInTheDocument();
      },
      { timeout: 800 },
    );
  });

  it('sort-by-name-asc reorders the rendered list', async () => {
    renderWithRouter(<Roles />);

    await waitFor(() => {
      expect(screen.getAllByText('Cashier').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.selectOptions(screen.getByLabelText(/roles\.sortBy|Sort by/), 'name-asc');

    await waitFor(() => {
      const headings = screen.getAllByRole('heading', { level: 3 });
      expect(headings[0].textContent).toBe('Auditor'); // alphabetical first
      expect(headings[1].textContent).toBe('Cashier');
      expect(headings[2].textContent).toBe('Manager');
    });
  });

  it('shows the no-roles empty state when the list is empty', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_roles', []);
    renderWithRouter(<Roles />);

    await waitFor(() => {
      expect(screen.getByText(/roles\.noRoles|No roles defined/)).toBeInTheDocument();
    });
  });

  it('opens the add form and saves a new role via add_role', async () => {
    mockInvokeSuccess('add_role', { id: 4 });
    renderWithRouter(<Roles />);

    await waitFor(() => {
      expect(screen.getAllByText('Manager').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByRole('button', { name: /Add Role/i }));

    const nameInput = screen.getByPlaceholderText(/e\.g\. Manager, Cashier, Chef/);
    await userEvent.type(nameInput, 'Kitchen Lead');

    await userEvent.click(screen.getByRole('button', { name: /Save/i }));

    // Roles page closes the form and quietly reloads — no toast.
    await waitFor(() => {
      expect(screen.queryByPlaceholderText(/e\.g\. Manager, Cashier, Chef/)).not.toBeInTheDocument();
    });
  });

  it('cancels the add form without saving', async () => {
    renderWithRouter(<Roles />);

    await waitFor(() => {
      expect(screen.getAllByText('Manager').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByRole('button', { name: /Add Role/i }));
    expect(screen.getByPlaceholderText(/e\.g\. Manager, Cashier, Chef/)).toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: /Cancel/i }));

    expect(screen.queryByPlaceholderText(/e\.g\. Manager, Cashier, Chef/)).not.toBeInTheDocument();
  });
});
