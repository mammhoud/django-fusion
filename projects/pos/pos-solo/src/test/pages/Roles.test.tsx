import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import Roles from '../../pages/Roles';

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
});
