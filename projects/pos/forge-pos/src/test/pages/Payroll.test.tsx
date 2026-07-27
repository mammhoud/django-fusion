import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks, mockInvokeError } from '../mocks/tauri';
import Payroll from '../../pages/Payroll';

const mockEmployees = [
  { id: 1, name: 'John Doe', phone: '1234567890', email: 'john@example.com', employee_type_id: 1, salary: 3000, is_active: true, joined_at: '2024-01-15' },
  { id: 2, name: 'Jane Smith', phone: '0987654321', email: 'jane@example.com', employee_type_id: 2, salary: 3500, is_active: true, joined_at: '2024-03-01' },
];

const mockPayrolls = [
  { id: 1, employee_id: 1, period_start: '2026-01-01', period_end: '2026-01-31', regular_hours: 160, overtime_hours: 10, total_pay: 3200.00, status: 'paid', created_at: '2026-01-31T10:00:00Z', updated_at: '2026-01-31T10:00:00Z' },
  { id: 2, employee_id: 2, period_start: '2026-01-01', period_end: '2026-01-31', regular_hours: 160, overtime_hours: 5, total_pay: 3800.00, status: 'pending', created_at: '2026-01-31T10:00:00Z', updated_at: '2026-01-31T10:00:00Z' },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_payrolls', mockPayrolls);
  mockInvokeSuccess('get_employees', mockEmployees);
});

describe('Payroll Page', () => {
  it('renders the payroll title', async () => {
    renderWithRouter(<Payroll />);

    await waitFor(() => {
      const titles = screen.getAllByText(/payroll\.title|Payroll/);
      expect(titles.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders add payroll button', async () => {
    renderWithRouter(<Payroll />);

    await waitFor(() => {
      expect(screen.getByText(/payroll\.addPayroll|Add Payroll/)).toBeInTheDocument();
    });
  });

  it('displays payroll cards with employee names', async () => {
    renderWithRouter(<Payroll />);

    await waitFor(() => {
      const johns = screen.getAllByText('John Doe');
      expect(johns.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('shows payroll status badges', async () => {
    renderWithRouter(<Payroll />);

    await waitFor(() => {
      const statuses = screen.getAllByText(/paid|pending/);
      expect(statuses.length).toBeGreaterThanOrEqual(2);
    });
  });

  it('shows total pay amounts on payroll cards', async () => {
    renderWithRouter(<Payroll />);

    await waitFor(() => {
      const payLabels = screen.getAllByText(/payroll\.totalPay|Total Pay/);
      expect(payLabels.length).toBeGreaterThanOrEqual(2);
    });
  });

  it('opens add payroll form when clicking add button', async () => {
    renderWithRouter(<Payroll />);

    await waitFor(() => {
      const addButtons = screen.getAllByText(/payroll\.addPayroll|Add Payroll/);
      expect(addButtons.length).toBeGreaterThanOrEqual(1);
    });

    const addButtons = screen.getAllByText(/payroll\.addPayroll|Add Payroll/);
    await userEvent.click(addButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/payroll\.selectEmployee|Select employee/)).toBeInTheDocument();
    });
  });

  it('shows regular and overtime hour labels', async () => {
    renderWithRouter(<Payroll />);

    await waitFor(() => {
      const regularLabels = screen.getAllByText(/payroll\.regularHours|Regular Hours/);
      expect(regularLabels.length).toBeGreaterThanOrEqual(1);
    });
    const overtimeLabels = screen.getAllByText(/payroll\.overtimeHours|Overtime Hours/);
    expect(overtimeLabels.length).toBeGreaterThanOrEqual(1);
  });

  it('handles empty payrolls gracefully', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_payrolls', []);
    mockInvokeSuccess('get_employees', mockEmployees);

    renderWithRouter(<Payroll />);

    await waitFor(() => {
      expect(screen.getByText(/payroll\.noPayrolls|No payroll records/)).toBeInTheDocument();
    });
  });

  it('handles API failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeError('get_payrolls', 'Failed to load');
    mockInvokeError('get_employees', 'Failed to load');

    renderWithRouter(<Payroll />);

    await waitFor(() => {
      const titles = screen.getAllByText(/payroll\.title|Payroll/);
      expect(titles.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows loading state initially', () => {
    // Delay the response with never-resolving promises
    const delayPromise = new Promise<never>(() => {});
    mockInvokeSuccess('get_payrolls', delayPromise);
    mockInvokeSuccess('get_employees', delayPromise);

    renderWithRouter(<Payroll />);

    // Check loading text is visible immediately (no async needed since promise never resolves)
    expect(screen.getByText(/common\.loading|Loading\.\.\./)).toBeInTheDocument();
  });
});
