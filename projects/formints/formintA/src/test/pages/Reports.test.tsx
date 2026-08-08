import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import Reports from '../../app/pages/analytics/Reports';

const mockSettings = {
  restaurant_name: 'Test Restaurant',
  address: '123 Street',
  phone: '03001234567',
  currency: 'USD',
  receipt_footer: 'Thank you!',
  dine_in_tables: 10,
  delivery_fee: 50,
  delivery_fee_per_km: 10,
};

const mockAnalytics = {
  summary: { total_orders: 12, total_revenue: 15000, average_order_value: 1250 },
  daily_revenue: [
    { date: '2026-01-10', revenue: 5000, orders: 4 },
    { date: '2026-01-11', revenue: 6000, orders: 5 },
    { date: '2026-01-12', revenue: 4000, orders: 3 },
  ],
  top_products: [
    { name: 'Chicken Burger', sales: 20, revenue: 7000 },
    { name: 'Biryani', sales: 15, revenue: 3750 },
  ],
  product_distribution: [
    { name: 'Burgers', value: 40 },
    { name: 'BBQ', value: 30 },
  ],
};

const mockSales = [
  { id: 1, total_amount: 5000, currency: 'USD', date: '2026-01-10', time: '12:00', order_type: 'dine-in', status: 'completed', table_number: 5, delivery_type_id: null, delivery_address: null, employee_id: 1 },
  { id: 2, total_amount: 3500, currency: 'USD', date: '2026-01-11', time: '13:00', order_type: 'delivery', status: 'completed', table_number: null, delivery_type_id: 1, delivery_address: 'House 12, Street 5', employee_id: 2 },
  { id: 3, total_amount: 2500, currency: 'USD', date: '2026-01-12', time: '14:00', order_type: 'takeaway', status: 'completed', table_number: null, delivery_type_id: null, delivery_address: null, employee_id: null },
];

const mockIngredients = [
  { id: 1, name: 'Chicken Breast', unit: 'kg', current_quantity: 25, reorder_level: 5, reorder_quantity: 10, cost_per_unit: 450, is_active: true },
  { id: 2, name: 'Cooking Oil', unit: 'liter', current_quantity: 3, reorder_level: 10, reorder_quantity: 20, cost_per_unit: 320, is_active: true },
  { id: 3, name: 'Salt', unit: 'kg', current_quantity: 2, reorder_level: 2, reorder_quantity: 5, cost_per_unit: 50, is_active: false },
];

const mockInventoryTxns = [
  { id: 1, ingredient_id: 1, transaction_type: 'purchase', quantity_change: 10, reference_id: null, note: 'Weekly stock', created_at: '2026-01-15T10:00:00' },
];

const mockRecipes = [
  { id: 1, product_id: 1, recipe_type_id: 1, yield_quantity: 4, is_active: true },
  { id: 2, product_id: 2, recipe_type_id: 1, yield_quantity: 1, is_active: false },
];

const mockProducts = [
  { id: 1, name: 'Chicken Burger', price: 350, unit: 'piece' },
  { id: 2, name: 'Biryani', price: 250, unit: 'plate' },
];

const mockEmployees = [
  { id: 1, name: 'Ali', phone: '03001111111', employee_type_id: 1, salary: 30000, is_active: true, joined_at: '2026-01-01' },
  { id: 2, name: 'Bilal', phone: '03002222222', employee_type_id: 2, salary: 25000, is_active: true, joined_at: '2026-01-15' },
];

const mockTaxReports = [
  { id: 1, period_start: '2026-01-01', period_end: '2026-01-31', total_sales: 12000, total_tax: 1560, transaction_count: 240 },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_settings', mockSettings);
  mockInvokeSuccess('get_analytics', mockAnalytics);
  mockInvokeSuccess('get_sales', mockSales);
  mockInvokeSuccess('get_ingredients', mockIngredients);
  mockInvokeSuccess('get_inventory_transactions', mockInventoryTxns);
  mockInvokeSuccess('get_recipes', mockRecipes);
  mockInvokeSuccess('get_products', mockProducts);
  mockInvokeSuccess('get_employees', mockEmployees);
  mockInvokeSuccess('get_transactions', []);
  mockInvokeSuccess('get_delivery_types', []);
  mockInvokeSuccess('get_tax_reports', mockTaxReports);
});

describe('Reports Page', () => {
  it('renders and loads all data', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const titleElements = screen.getAllByText(/reports\.title|Reports/);
      expect(titleElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows tab navigation with all tabs', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /Overview/ })).toBeInTheDocument();
    });
    expect(screen.getByRole('tab', { name: /Inventory/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Recipes/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Employees/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Transaction History/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Products Sales/ })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Invoices/ })).toBeInTheDocument();
    // 'Sales' matches both the 'Sales' tab and the 'Products Sales' tab
    const salesMatches = screen.getAllByRole('tab', { name: /Sales/ });
    expect(salesMatches.length).toBe(2); // Both 'Sales' tab and 'Products Sales' tab
  });

  it('shows Sales tab content with summary cards by default', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByText(/reports\.totalRevenue|Total Revenue/)).toBeInTheDocument();
    });

    // Sales tab is active by default - should show summary cards
    expect(screen.getByText(/reports\.totalOrders|Total Orders/)).toBeInTheDocument();
    expect(screen.getByText(/reports\.avgOrderValue|Avg\. Order Value/)).toBeInTheDocument();
    expect(screen.getByText(/reports\.orderTypes|Order Types/)).toBeInTheDocument();
  });

  it('opens Tax Reports as an inline tab (no full-page navigation)', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /Tax Reports/ })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole('tab', { name: /Tax Reports/ }));

    // The panel renders inline within the Reports page (not a separate route)
    await waitFor(() => {
      expect(screen.getAllByText(/2026-01-01/).length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText(/taxReports\.periods|Periods/)).toBeInTheDocument();
  });

  it('shows order types breakdown in sales tab', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByText(/reports\.ordersByType|Orders by Type/)).toBeInTheDocument();
    });
    // Labels now appear in both the filter pills and the breakdown rows
    expect(screen.getAllByText('Dine-in').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Delivery').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Takeaway').length).toBeGreaterThanOrEqual(1);
  });

  it('shows Top Products in sales tab', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByText(/reports\.topProducts|Top Products/)).toBeInTheDocument();
    });
    expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
    expect(screen.getByText('Biryani')).toBeInTheDocument();
  });

  it('switches to Overview tab and shows KPI cards', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByText(/reports\.overview|Overview/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/reports\.overview|Overview/));

    await waitFor(() => {
      expect(screen.getByText(/reports\.totalOrders|Total Orders/)).toBeInTheDocument();
    });
    expect(screen.getByText(/reports\.stockValueLabel|Stock Value/)).toBeInTheDocument();
    expect(screen.getByText(/reports\.activeRecipes|Active Recipes/)).toBeInTheDocument();
    const activeEmpElements = screen.getAllByText(/reports\.activeEmployees|Active Employees/);
    expect(activeEmpElements.length).toBeGreaterThanOrEqual(1);
  });

  it('switches to Inventory tab and shows inventory data', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /Inventory/ })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole('tab', { name: /Inventory/ }));

    await waitFor(() => {
      expect(screen.getByText(/reports\.stockValueLabel|Stock Value/)).toBeInTheDocument();
    });
    expect(screen.getByText(/reports\.lowStockAlerts|Low Stock Alerts/)).toBeInTheDocument();
    expect(screen.getByText(/reports\.ingredientStockLevels|Ingredient Stock Levels/)).toBeInTheDocument();
  });

  it('switches to Recipes tab and shows recipe data', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /Recipes/ })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole('tab', { name: /Recipes/ }));

    await waitFor(() => {
      expect(screen.getByText(/reports\.totalRecipes|Total Recipes/)).toBeInTheDocument();
    });
    expect(screen.getByText(/reports\.productCatalog|Product Catalog/)).toBeInTheDocument();
  });

  it('switches to Employees tab and shows employee data', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByRole('tab', { name: /Employees/ })).toBeInTheDocument();
    });

    await userEvent.click(screen.getByRole('tab', { name: /Employees/ }));

    await waitFor(() => {
      const activeEmpElements = screen.getAllByText(/reports\.activeEmployees|Active Employees/);
    expect(activeEmpElements.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText(/reports\.employeeDirectory|Employee Directory/)).toBeInTheDocument();
    // Employee names may appear in multiple sections (performance chart + directory)
    const aliElements = screen.getAllByText('Ali');
    expect(aliElements.length).toBeGreaterThanOrEqual(1);
    const bilalElements = screen.getAllByText('Bilal');
    expect(bilalElements.length).toBeGreaterThanOrEqual(1);
  });

  it('shows Export PDF button', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByText(/reports\.exportPDF|Export PDF/)).toBeInTheDocument();
    });
  });

  it('shows and uses date range filter', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getAllByText(/common\.period|Period/).length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText(/reports\.dateToday|Today/)).toBeInTheDocument();
    expect(screen.getByText(/reports\.date7Days|7 Days/)).toBeInTheDocument();
    expect(screen.getByText(/reports\.date30Days|30 Days/)).toBeInTheDocument();
    expect(screen.getByText(/reports\.dateThisMonth|This Month/)).toBeInTheDocument();
  });

  it('hides date range when period filter is applied', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByText(/reports\.dateToday|Today/)).toBeInTheDocument();
    });

    // Click "Today" button to apply date filter
    await userEvent.click(screen.getByText(/reports\.dateToday|Today/));

    await waitFor(() => {
      // The date indicator should now show
      expect(screen.getByText(/showingDataFrom|Showing data from/)).toBeInTheDocument();
    });
    expect(screen.getByText(/reports\.dateClear|Clear/)).toBeInTheDocument();
  });

  it('shows CSV export buttons on relevant tabs', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByText(/reports\.totalRevenue|Total Revenue/)).toBeInTheDocument();
    });

    // Sales tab has CSV export
    const csvButtons = screen.getAllByText(/reports\.exportCSV|Export CSV/);
    expect(csvButtons.length).toBeGreaterThan(0);
  });

  it('handles empty data gracefully', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_settings', mockSettings);
    mockInvokeSuccess('get_analytics', null);
    mockInvokeSuccess('get_sales', []);
    mockInvokeSuccess('get_ingredients', []);
    mockInvokeSuccess('get_inventory_transactions', []);
    mockInvokeSuccess('get_recipes', []);
    mockInvokeSuccess('get_products', []);
    mockInvokeSuccess('get_employees', []);
    mockInvokeSuccess('get_transactions', []);
    mockInvokeSuccess('get_delivery_types', []);

    renderWithRouter(<Reports />);

    await waitFor(() => {
      expect(screen.getByText(/reports\.totalRevenue|Total Revenue/)).toBeInTheDocument();
    });
    // Should not crash with empty data
    expect(screen.getByText(/reports\.totalOrders|Total Orders/)).toBeInTheDocument();
  });
});
