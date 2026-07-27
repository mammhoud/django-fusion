import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks, mockInvokeError } from '../mocks/tauri';
import EmployeeSchedule from '../../pages/EmployeeSchedule';

const mockEmployees = [
  { id: 1, name: 'John Doe', phone: '1234567890', email: 'john@example.com', employee_type_id: 1, salary: 3000, is_active: true, joined_at: '2024-01-15' },
  { id: 2, name: 'Jane Smith', phone: '0987654321', email: 'jane@example.com', employee_type_id: 2, salary: 3500, is_active: true, joined_at: '2024-03-01' },
];

const mockSchedules = [
  { id: 1, employee_id: 1, shift_start: '2026-01-15T09:00:00Z', shift_end: '2026-01-15T17:00:00Z', status: 'scheduled', notes: 'Morning shift', created_at: '2026-01-10T10:00:00Z', updated_at: '2026-01-10T10:00:00Z' },
  { id: 2, employee_id: 2, shift_start: '2026-01-15T14:00:00Z', shift_end: '2026-01-15T22:00:00Z', status: 'scheduled', notes: 'Evening shift', created_at: '2026-01-10T10:00:00Z', updated_at: '2026-01-10T10:00:00Z' },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_employee_schedules', mockSchedules);
  mockInvokeSuccess('get_employees', mockEmployees);
});

describe('EmployeeSchedule Page', () => {
  it('renders the schedule title', async () => {
    renderWithRouter(<EmployeeSchedule />);

    await waitFor(() => {
      const titles = screen.getAllByText(/schedule\.title|Employee Schedule/);
      expect(titles.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders add shift button', async () => {
    renderWithRouter(<EmployeeSchedule />);

    await waitFor(() => {
      const shiftButtons = screen.getAllByText(/schedule\.addShift|Add Shift/);
      expect(shiftButtons.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('displays schedule cards with employee names', async () => {
    renderWithRouter(<EmployeeSchedule />);

    await waitFor(() => {
      const johns = screen.getAllByText('John Doe');
      expect(johns.length).toBeGreaterThanOrEqual(1);
    });
    const janes = screen.getAllByText('Jane Smith');
    expect(janes.length).toBeGreaterThanOrEqual(1);
  });

  it('shows schedule status badges', async () => {
    renderWithRouter(<EmployeeSchedule />);

    await waitFor(() => {
      const statuses = screen.getAllByText('scheduled');
      expect(statuses.length).toBeGreaterThanOrEqual(2);
    });
  });

  it('shows schedule notes on cards', async () => {
    renderWithRouter(<EmployeeSchedule />);

    await waitFor(() => {
      expect(screen.getByText('Morning shift')).toBeInTheDocument();
      expect(screen.getByText('Evening shift')).toBeInTheDocument();
    });
  });

  it('opens add shift form when clicking add button', async () => {
    renderWithRouter(<EmployeeSchedule />);

    await waitFor(() => {
      expect(screen.getByText(/schedule\.addShift|Add Shift/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/schedule\.addShift|Add Shift/));

    await waitFor(() => {
      expect(screen.getByText(/schedule\.selectEmployee|Select employee/)).toBeInTheDocument();
    });
  });

  it('handles empty schedules gracefully', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_employee_schedules', []);
    mockInvokeSuccess('get_employees', mockEmployees);

    renderWithRouter(<EmployeeSchedule />);

    await waitFor(() => {
      expect(screen.getByText(/schedule\.noShifts|No shifts scheduled/)).toBeInTheDocument();
    });
  });

  it('handles API failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeError('get_employee_schedules', 'Failed to load');
    mockInvokeError('get_employees', 'Failed to load');

    renderWithRouter(<EmployeeSchedule />);

    await waitFor(() => {
      const titles = screen.getAllByText(/schedule\.title|Employee Schedule/);
      expect(titles.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows delete button on schedule cards', async () => {
    renderWithRouter(<EmployeeSchedule />);

    await waitFor(() => {
      const deleteButtons = screen.getAllByRole('button');
      const deleteIcons = deleteButtons.filter(b =>
        b.innerHTML.includes('MdDelete') || b.querySelector('svg')
      );
      expect(deleteIcons.length).toBeGreaterThanOrEqual(2);
    });
  });
});
