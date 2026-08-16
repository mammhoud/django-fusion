import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderWithRouter, screen, waitFor, userEvent, within } from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks, mockInvokeError } from '../mocks/tauri';
import { getInvokeHistory } from '../setup';
import Employees from '../../app/pages/admin/Employees';

const mockEmployees = [
  {
    id: 1, name: 'Ali', phone: '03001111111', email: null, employee_type_id: 1, is_active: true,
    joined_at: '2026-01-01', address: 'Lahore', date_of_birth: '1990-05-10', national_id: '35202-1234567-1',
    emergency_contact: 'Bilal · 03001234567', notes: 'Works weekends',
  },
  { id: 2, name: 'Usman', phone: '03002222222', email: 'usman@test.com', employee_type_id: 2, is_active: true, joined_at: '2026-01-15' },
  { id: 3, name: 'Zara', phone: null, email: null, employee_type_id: 3, is_active: false, joined_at: null },
];

const mockEmployeeTypes = [
  { id: 1, name: 'Manager', description: 'Restaurant manager', is_active: true },
  { id: 2, name: 'Chef', description: 'Head chef', is_active: true },
  { id: 3, name: 'Waiter', description: 'Server', is_active: true },
  { id: 4, name: 'Cashier', description: 'Cashier', is_active: false },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_employees', mockEmployees);
  mockInvokeSuccess('get_employee_types', mockEmployeeTypes);
});

describe('Employees Page', () => {
  it('renders summary cards with correct counts', async () => {
    renderWithRouter(<Employees />);
    await waitFor(() => expect(screen.getByText(/employees\.totalEmployees|Total Employees/)).toBeInTheDocument());
    expect(screen.getAllByText('2', { exact: true }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/employees\.employeeTypes|Employee Types/).length).toBeGreaterThan(0);
  });

  it('renders employee tabs and cards', async () => {
    renderWithRouter(<Employees />);
    await waitFor(() => expect(screen.getByText(/employees\.employeeList|Employee List/)).toBeInTheDocument());
    expect(screen.getAllByText('Ali').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Usman').length).toBeGreaterThanOrEqual(1);
  });

  it('shows search and filter controls', async () => {
    renderWithRouter(<Employees />);
    await waitFor(() => expect(screen.getByPlaceholderText(/employees\.searchPlaceholder|Search employees/)).toBeInTheDocument());
    expect(screen.getByRole('button', { name: 'All' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Active' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Inactive' })).toBeInTheDocument();
  });

  it('walks through the 3-step Add Employee wizard', async () => {
    mockInvokeSuccess('add_employee', { id: 4, name: 'New Employee', employee_type_id: 1, is_active: true });
    renderWithRouter(<Employees />);
    await waitFor(() => expect(screen.getByText(/employees\.addEmployee|Add Employee/)).toBeInTheDocument());
    await userEvent.click(screen.getByText(/employees\.addEmployee|Add Employee/));

    await waitFor(() => expect(screen.getByText(/employees\.addEmployeeTitle|Add New Employee/)).toBeInTheDocument());
    const nameInput = screen.getByPlaceholderText(/employees\.namePlaceholder|Enter employee name/);
    const nextBtn = screen.getByRole('button', { name: /Next/ });
    expect(nextBtn).toBeDisabled();
    await userEvent.type(nameInput, 'New Employee');
    await userEvent.click(nextBtn);
    await userEvent.click(screen.getByRole('button', { name: /Next/ }));

    const roleStep = screen.getByTestId('employee-form-modal-step-role');
    await userEvent.selectOptions(within(roleStep).getByRole('combobox'), '1');
    await userEvent.click(screen.getByTestId('employee-form-modal-submit'));

    await waitFor(() => expect(getInvokeHistory().find(h => h.cmd === 'add_employee')?.args).toEqual({
      employee: {
        name: 'New Employee', phone: null, email: null, employee_type_id: 1,
        joined_at: null, address: null, date_of_birth: null, national_id: null,
        emergency_contact: null, notes: null,
      },
    }));
  });

  it('opens the employee detail view with profile and audit trail only', async () => {
    mockInvokeSuccess('get_user_actions_for_entity', [
      { id: 5, action: 'add_employee', entity_type: 'employee', entity_id: 1, details: '{}', user_id: null, created_at: '2026-01-01T09:00:00' },
    ]);
    renderWithRouter(<Employees />);
    await waitFor(() => expect(screen.getByText(/employees\.addEmployee|Add Employee/)).toBeInTheDocument());
    await userEvent.click(screen.getAllByTitle('View details')[0]);
    await waitFor(() => expect(screen.getByTestId('employee-detail-modal')).toBeInTheDocument());
    expect(screen.getByText('35202-1234567-1')).toBeInTheDocument();
    expect(screen.getByText(/Audit trail/)).toBeInTheDocument();
    expect(screen.queryByText(/Salary|Payroll/)).toBeNull();
  });

  it('reactivates an inactive employee', async () => {
    mockInvokeSuccess('update_employee', { id: 3, name: 'Zara', is_active: true });
    renderWithRouter(<Employees />);
    await waitFor(() => expect(screen.getByText(/employees\.addEmployee|Add Employee/)).toBeInTheDocument());
    await userEvent.click(screen.getByRole('button', { name: 'Inactive' }));
    await waitFor(() => expect(screen.getAllByTitle('Activate').length).toBeGreaterThanOrEqual(1));
    await userEvent.click(screen.getAllByTitle('Activate')[0]);
    await waitFor(() => expect(getInvokeHistory().find(h => h.cmd === 'update_employee')?.args).toEqual({ id: 3, update: { is_active: true } }));
  });

  it('switches to Employee Types tab', async () => {
    renderWithRouter(<Employees />);
    await waitFor(() => expect(screen.getByText(/employees\.employeeList|Employee List/)).toBeInTheDocument());
    const typesTab = screen.getAllByRole('button').find(btn => btn.textContent?.includes('Employee Types') || btn.textContent?.includes('employees.employeeTypes'));
    expect(typesTab).toBeDefined();
    if (typesTab) await userEvent.click(typesTab);
    await waitFor(() => expect(screen.getAllByText(/Employee Types/).length).toBeGreaterThanOrEqual(1));
    expect(screen.getByText('Manager')).toBeInTheDocument();
  });

  it('handles empty employees gracefully', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_employees', []);
    mockInvokeSuccess('get_employee_types', mockEmployeeTypes);
    renderWithRouter(<Employees />);
    await waitFor(() => expect(screen.getByText(/employees\.totalEmployees|Total Employees/)).toBeInTheDocument());
    expect(screen.getAllByText('0', { exact: true }).length).toBeGreaterThanOrEqual(1);
  });

  it('handles API failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeError('get_employees', 'Connection failed');
    mockInvokeError('get_employee_types', 'Connection failed');
    renderWithRouter(<Employees />);
    await waitFor(() => expect(screen.getByText(/employees\.totalEmployees|Total Employees/)).toBeInTheDocument());
    expect(screen.getAllByText('0', { exact: true }).length).toBeGreaterThanOrEqual(1);
  });
});
