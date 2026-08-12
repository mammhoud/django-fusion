import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderWithRouter, screen, waitFor, userEvent } from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import StaffPage from '../../app/pages/admin/StaffPage';

const mockEmployees = [
  { id: 1, name: 'Sarah Johnson', employee_type_id: 1, is_active: true, salary: 0, phone: '03005555555' },
];
const mockEmployeeTypes = [{ id: 1, name: 'Waiter', is_active: true }];
const mockSchedules = [
  { id: 1, employee_id: 1, shift_start: '09:00', shift_end: '17:00', status: 'scheduled', notes: '' },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_employees', mockEmployees);
  mockInvokeSuccess('get_employee_types', mockEmployeeTypes);
  mockInvokeSuccess('get_employee_schedules', mockSchedules);
});

describe('StaffPage (merged Employees / Schedule)', () => {
  it('renders the two staff tabs with Employees active by default', () => {
    renderWithRouter(<StaffPage />);
    const tabs = screen.getAllByRole('tab');
    expect(tabs).toHaveLength(2);
    expect(tabs[0]).toHaveTextContent(/Employees/i);
    expect(tabs[1]).toHaveTextContent(/Schedule/i);
    expect(screen.getByRole('tabpanel')).toHaveAttribute('id', 'staff-panel-employees');
  });

  it('hydrates employees in the default tab', async () => {
    renderWithRouter(<StaffPage />);
    await waitFor(() => expect(screen.getAllByText('Sarah Johnson').length).toBeGreaterThanOrEqual(1));
  });

  it('switches to the Schedule tab', async () => {
    renderWithRouter(<StaffPage />);
    await userEvent.click(screen.getByRole('tab', { name: /Schedule/i }));
    await waitFor(() => expect(screen.getByRole('tabpanel')).toHaveAttribute('id', 'staff-panel-schedule'));
  });

  it('marks the active tab as selected', async () => {
    renderWithRouter(<StaffPage />);
    const scheduleTab = screen.getByRole('tab', { name: /Schedule/i });
    expect(scheduleTab).toHaveAttribute('aria-selected', 'false');
    await userEvent.click(scheduleTab);
    expect(scheduleTab).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tab', { name: /Employees/i })).toHaveAttribute('aria-selected', 'false');
  });
});
