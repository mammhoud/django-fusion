import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import Reports from '../../pages/Reports';

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
});

describe('Reports Page', () => {
  it('renders and loads all data', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const titleEls = screen.getAllByText(/reports\.title|Reports/);
      expect(titleEls.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows tab navigation with all tabs', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const overviewEls = screen.getAllByText(/reports\.overview|Overview/);
      expect(overviewEls.length).toBeGreaterThanOrEqual(1);
    });
    const inventoryEls = screen.getAllByText(/reports\.inventory|Inventory/);
    expect(inventoryEls.length).toBeGreaterThanOrEqual(1);
    const recipesEls = screen.getAllByText(/reports\.recipes|Recipes/);
    expect(recipesEls.length).toBeGreaterThanOrEqual(1);
    const employeesEls = screen.getAllByText(/reports\.employees|Employees/);
    expect(employeesEls.length).toBeGreaterThanOrEqual(1);
    const transactionsEls = screen.getAllByText(/reports\.transactions|Transaction History/);
    expect(transactionsEls.length).toBeGreaterThanOrEqual(1);
    const productsSalesEls = screen.getAllByText(/reports\.productsSales|Products Sales/);
    expect(productsSalesEls.length).toBeGreaterThanOrEqual(1);
    const invoicesEls = screen.getAllByText(/reports\.invoices|Invoices/);
    expect(invoicesEls.length).toBeGreaterThanOrEqual(1);
    // 'Sales' appears in both 'Sales' tab and 'Products Sales' tab
    const salesMatches = screen.getAllByText(/reports\.sales|Sales/);
    expect(salesMatches.length).toBeGreaterThanOrEqual(2);
  });

  it('shows Sales tab content with summary cards by default', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const totalRevenueEls = screen.getAllByText(/reports\.totalRevenue|Total Revenue/);
      expect(totalRevenueEls.length).toBeGreaterThanOrEqual(1);
    });

    // Sales tab is active by default - should show summary cards
    const totalOrdersEls = screen.getAllByText(/reports\.totalOrders|Total Orders/);
    expect(totalOrdersEls.length).toBeGreaterThanOrEqual(1);
    const avgOrderValueEls = screen.getAllByText(/reports\.avgOrderValue|Avg\. Order Value/);
    expect(avgOrderValueEls.length).toBeGreaterThanOrEqual(1);
    const orderTypesEls = screen.getAllByText(/reports\.orderTypes|Order Types/);
    expect(orderTypesEls.length).toBeGreaterThanOrEqual(1);
  });

  it('shows order types breakdown in sales tab', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const ordersByTypeEls = screen.getAllByText(/reports\.ordersByType|Orders by Type/);
      expect(ordersByTypeEls.length).toBeGreaterThanOrEqual(1);
    });
    // Dine-in/Delivery/Takeaway may appear in charts + tables
    const dineInEls = screen.getAllByText('Dine-in');
    expect(dineInEls.length).toBeGreaterThanOrEqual(1);
    const deliveryEls = screen.getAllByText('Delivery');
    expect(deliveryEls.length).toBeGreaterThanOrEqual(1);
    const takeawayEls = screen.getAllByText('Takeaway');
    expect(takeawayEls.length).toBeGreaterThanOrEqual(1);
  });

  it('shows Top Products in sales tab', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const topProductsEls = screen.getAllByText(/reports\.topProducts|Top Products/);
      expect(topProductsEls.length).toBeGreaterThanOrEqual(1);
    });
    const chickenEls = screen.getAllByText('Chicken Burger');
    expect(chickenEls.length).toBeGreaterThanOrEqual(1);
    const biryaniEls = screen.getAllByText('Biryani');
    expect(biryaniEls.length).toBeGreaterThanOrEqual(1);
  });

  it('switches to Overview tab and shows KPI cards', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const overviewEls = screen.getAllByText(/reports\.overview|Overview/);
      expect(overviewEls.length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getAllByText(/reports\.overview|Overview/)[0]);

    await waitFor(() => {
      const totalOrdersEls = screen.getAllByText(/reports\.totalOrders|Total Orders/);
      expect(totalOrdersEls.length).toBeGreaterThanOrEqual(1);
    });
    const stockValueEls = screen.getAllByText(/reports\.stockValueLabel|Stock Value/);
    expect(stockValueEls.length).toBeGreaterThanOrEqual(1);
    const activeRecipesEls = screen.getAllByText(/reports\.activeRecipes|Active Recipes/);
    expect(activeRecipesEls.length).toBeGreaterThanOrEqual(1);
    const activeEmpElements = screen.getAllByText(/reports\.activeEmployees|Active Employees/);
    expect(activeEmpElements.length).toBeGreaterThanOrEqual(1);
  });

  it('switches to Inventory tab and shows inventory data', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const inventoryEls = screen.getAllByText(/reports\.inventory|Inventory/);
      expect(inventoryEls.length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getAllByText(/reports\.inventory|Inventory/)[0]);

    await waitFor(() => {
      const stockValueEls = screen.getAllByText(/reports\.stockValueLabel|Stock Value/);
      expect(stockValueEls.length).toBeGreaterThanOrEqual(1);
    });
    const lowStockEls = screen.getAllByText(/reports\.lowStockAlerts|Low Stock Alerts/);
    expect(lowStockEls.length).toBeGreaterThanOrEqual(1);
    const ingredientStockEls = screen.getAllByText(/reports\.ingredientStockLevels|Ingredient Stock Levels/);
    expect(ingredientStockEls.length).toBeGreaterThanOrEqual(1);
  });

  it('switches to Recipes tab and shows recipe data', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const recipesEls = screen.getAllByText(/reports\.recipes|Recipes/);
      expect(recipesEls.length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getAllByText(/reports\.recipes|Recipes/)[0]);

    await waitFor(() => {
      const totalRecipesEls = screen.getAllByText(/reports\.totalRecipes|Total Recipes/);
      expect(totalRecipesEls.length).toBeGreaterThanOrEqual(1);
    });
    const productCatalogEls = screen.getAllByText(/reports\.productCatalog|Product Catalog/);
    expect(productCatalogEls.length).toBeGreaterThanOrEqual(1);
  });

  it('switches to Employees tab and shows employee data', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const employeesEls = screen.getAllByText(/reports\.employees|Employees/);
      expect(employeesEls.length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getAllByText(/reports\.employees|Employees/)[0]);

    await waitFor(() => {
      const activeEmpElements = screen.getAllByText(/reports\.activeEmployees|Active Employees/);
      expect(activeEmpElements.length).toBeGreaterThanOrEqual(1);
    });
    const employeeDirectoryEls = screen.getAllByText(/reports\.employeeDirectory|Employee Directory/);
    expect(employeeDirectoryEls.length).toBeGreaterThanOrEqual(1);
    // Employee names may appear in multiple sections (performance chart + directory)
    const aliElements = screen.getAllByText('Ali');
    expect(aliElements.length).toBeGreaterThanOrEqual(1);
    const bilalElements = screen.getAllByText('Bilal');
    expect(bilalElements.length).toBeGreaterThanOrEqual(1);
  });

  it('shows Export PDF button', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const exportPDFEls = screen.getAllByText(/reports\.exportPDF|Export PDF/);
      expect(exportPDFEls.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows and uses date range filter', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const periodEls = screen.getAllByText(/common\.period|Period/);
      expect(periodEls.length).toBeGreaterThanOrEqual(1);
    });
    const todayEls = screen.getAllByText(/reports\.dateToday|Today/);
    expect(todayEls.length).toBeGreaterThanOrEqual(1);
    const days7Els = screen.getAllByText(/reports\.date7Days|7 Days/);
    expect(days7Els.length).toBeGreaterThanOrEqual(1);
    const days30Els = screen.getAllByText(/reports\.date30Days|30 Days/);
    expect(days30Els.length).toBeGreaterThanOrEqual(1);
    const thisMonthEls = screen.getAllByText(/reports\.dateThisMonth|This Month/);
    expect(thisMonthEls.length).toBeGreaterThanOrEqual(1);
  });

  it('hides date range when period filter is applied', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const todayEls = screen.getAllByText(/reports\.dateToday|Today/);
      expect(todayEls.length).toBeGreaterThanOrEqual(1);
    });

    // Click "Today" button to apply date filter
    await userEvent.click(screen.getAllByText(/reports\.dateToday|Today/)[0]);

    await waitFor(() => {
      // The date indicator should now show
      const showingDataEls = screen.getAllByText(/showingDataFrom|Showing data from/);
      expect(showingDataEls.length).toBeGreaterThanOrEqual(1);
    });
    const clearEls = screen.getAllByText(/reports\.dateClear|Clear/);
    expect(clearEls.length).toBeGreaterThanOrEqual(1);
  });

  it('shows CSV export buttons on relevant tabs', async () => {
    renderWithRouter(<Reports />);

    await waitFor(() => {
      const totalRevenueEls = screen.getAllByText(/reports\.totalRevenue|Total Revenue/);
      expect(totalRevenueEls.length).toBeGreaterThanOrEqual(1);
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
      const totalRevenueEls = screen.getAllByText(/reports\.totalRevenue|Total Revenue/);
      expect(totalRevenueEls.length).toBeGreaterThanOrEqual(1);
    });
    // Should not crash with empty data
    const totalOrdersEls = screen.getAllByText(/reports\.totalOrders|Total Orders/);
    expect(totalOrdersEls.length).toBeGreaterThanOrEqual(1);
  });
});
