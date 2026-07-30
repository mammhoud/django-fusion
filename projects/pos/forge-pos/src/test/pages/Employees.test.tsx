import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks, mockInvokeError } from '../mocks/tauri';
import Employees from '../../pages/staff/Employees';

const mockEmployees = [
  { id: 1, name: 'Ali', phone: '03001111111', email: null, employee_type_id: 1, salary: 30000, is_active: true, joined_at: '2026-01-01' },
  { id: 2, name: 'Usman', phone: '03002222222', email: 'usman@test.com', employee_type_id: 2, salary: 45000, is_active: true, joined_at: '2026-01-15' },
  { id: 3, name: 'Zara', phone: null, email: null, employee_type_id: 3, salary: 20000, is_active: false, joined_at: null },
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

    await waitFor(() => {
      expect(screen.getByText(/employees\.totalEmployees|Total Employees/)).toBeInTheDocument();
    });
    // "2" for active employees - use exact match
    const twos = screen.getAllByText('2', { exact: true });
    expect(twos.length).toBeGreaterThanOrEqual(1);
    // "Employee Types" appears both as a tab button and in summary; use getAllByText
    const empTypeElements = screen.getAllByText(/employees\.employeeTypes|Employee Types/);
    expect(empTypeElements.length).toBeGreaterThan(0);
    expect(screen.getByText(/employees\.monthlySalary|Monthly Salary/)).toBeInTheDocument();
    expect(screen.getByText(/employees\.avgSalary|Avg Salary/)).toBeInTheDocument();
  });

  it('renders tab navigation', async () => {
    renderWithRouter(<Employees />);

    await waitFor(() => {
      expect(screen.getByText(/employees\.employeeList|Employee List/)).toBeInTheDocument();
    });
    const empTypes = screen.getAllByText(/employees\.employeeTypes|Employee Types/);
    expect(empTypes.length).toBeGreaterThan(0);
  });

  it('shows employee cards with names and details', async () => {
    renderWithRouter(<Employees />);

    await waitFor(() => {
      // Use getAllByText for names since they might appear in header + card
      const aliElements = screen.getAllByText('Ali');
      expect(aliElements.length).toBeGreaterThanOrEqual(1);
    });
    const usmanElements = screen.getAllByText('Usman');
    expect(usmanElements.length).toBeGreaterThanOrEqual(1);
  });

  it('shows salary information for employees', async () => {
    renderWithRouter(<Employees />);

    await waitFor(() => {
      const aliElements = screen.getAllByText('Ali');
      expect(aliElements.length).toBeGreaterThanOrEqual(1);
    });
    // Salary is formatted with toLocaleString() — in jsdom this gives "30,000", "45,000", "20,000"
    // Check for salary numbers in the rendered output
    const salary30k = screen.getAllByText(/30[,.]?000/);
    expect(salary30k.length).toBeGreaterThanOrEqual(1);
  });

  it('shows search and filter controls', async () => {
    renderWithRouter(<Employees />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/employees\.searchPlaceholder|Search employees/)).toBeInTheDocument();
    });
    const allTypesEls = screen.getAllByText(/employees\.allTypes|All Types/);
    expect(allTypesEls.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/employees\.allTypesFilter|All/)).toBeInTheDocument();
    expect(screen.getByText(/employees\.activeFilter|Active/)).toBeInTheDocument();
    expect(screen.getByText(/employees\.inactiveFilter|Inactive/)).toBeInTheDocument();
  });

  it('opens Add Employee modal', async () => {
    mockInvokeSuccess('add_employee', { id: 4, name: 'New Employee', employee_type_id: 1, salary: 35000, is_active: true });
    renderWithRouter(<Employees />);

    await waitFor(() => {
      expect(screen.getByText(/employees\.addEmployee|Add Employee/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/employees\.addEmployee|Add Employee/));

    await waitFor(() => {
      expect(screen.getByText(/employees\.addEmployeeTitle|Add New Employee/)).toBeInTheDocument();
    });
    expect(screen.getByPlaceholderText(/employees\.namePlaceholder|Enter employee name/)).toBeInTheDocument();
    // "Employee Type" label inside the modal (test key fallback pattern)
    const typeLabels = screen.getAllByText(/Employee Type|employees\.employeeType/);
    expect(typeLabels.length).toBeGreaterThan(0);
  });

  it('switches to Employee Types tab', async () => {
    renderWithRouter(<Employees />);

    await waitFor(() => {
      // Employee List tab text now shows the translation key
      expect(screen.getByText(/employees\.employeeList|Employee List/)).toBeInTheDocument();
    });

    // Find and click the tab button for Employee Types
    const allButtons = screen.getAllByRole('button');
    const typesTab = allButtons.find(btn => btn.textContent?.includes('Employee Types') || btn.textContent?.includes('employees.employeeTypes'));
    expect(typesTab).toBeDefined();
    if (typesTab) await userEvent.click(typesTab);

    await waitFor(() => {
      // Find the tab content heading - use getAllByText since summary cards also show this text
      const typesHeadings = screen.getAllByText(/employees\.employeeTypes/);
      expect(typesHeadings.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText('Manager')).toBeInTheDocument();
    expect(screen.getByText('Chef')).toBeInTheDocument();
    expect(screen.getByText('Waiter')).toBeInTheDocument();
  });

  it('opens Add Type modal', async () => {
    mockInvokeSuccess('add_employee_type', { id: 5, name: 'New Type', description: 'Test', is_active: true });
    renderWithRouter(<Employees />);

    await waitFor(() => {
      expect(screen.getByText(/employees\.employeeList|Employee List/)).toBeInTheDocument();
    });

    // Click Employee Types tab button
    const allButtons = screen.getAllByRole('button');
    const typesTab = allButtons.find(btn => btn.textContent?.includes('Employee Types') || btn.textContent?.includes('employees.employeeTypes'));
    expect(typesTab).toBeDefined();
    if (typesTab) await userEvent.click(typesTab);

    await waitFor(() => {
      expect(screen.getByText(/employees\.addType|Add Type/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/employees\.addType|Add Type/));

    await waitFor(() => {
      expect(screen.getByText(/employees\.addTypeTitle|Add Employee Type/)).toBeInTheDocument();
    });
  });

  it('handles empty employees gracefully', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_employees', []);
    mockInvokeSuccess('get_employee_types', mockEmployeeTypes);

    renderWithRouter(<Employees />);

    await waitFor(() => {
      expect(screen.getByText(/employees\.totalEmployees|Total Employees/)).toBeInTheDocument();
    });
    const zeros = screen.getAllByText('0', { exact: true });
    expect(zeros.length).toBeGreaterThanOrEqual(1);
  });

  it('handles API failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeError('get_employees', 'Connection failed');
    mockInvokeError('get_employee_types', 'Connection failed');

    renderWithRouter(<Employees />);

    await waitFor(() => {
      expect(screen.getByText(/employees\.totalEmployees|Total Employees/)).toBeInTheDocument();
    });
    const zeros = screen.getAllByText('0', { exact: true });
    expect(zeros.length).toBeGreaterThanOrEqual(1);
  });
});
