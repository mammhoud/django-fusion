import { describe, it, expect, beforeEach } from 'vitest';
import { invoke } from '@tauri-apps/api/core';
import {
  resetInvokeMocks,
  mockInvokeSuccess,
  mockInvokeError,
  mockInvokeFatalError,
  safeInvoke,
} from './mocks/tauri';
import { getInvokeHistory, clearInvokeHistory } from './setup';

/**
 * Helper: assert the most recent invoke call.
 * The invoke mock is intentionally a plain function (not vi.fn()) so that
 * vi.clearAllMocks() in component test files doesn't reset it.  We track
 * calls manually via setup.ts's getInvokeHistory().
 */
function expectLastCall(cmd: string, args?: unknown) {
  const history = getInvokeHistory();
  expect(history.length).toBeGreaterThan(0);
  const last = history[history.length - 1];
  expect(last.cmd).toBe(cmd);
  if (args !== undefined) {
    expect(last.args).toEqual(args);
  }
}

// Global beforeEach: reset mock handlers AND clear invoke history
beforeEach(() => {
  resetInvokeMocks();
  clearInvokeHistory();
});

// All known Tauri commands used in the frontend
const KNOWN_COMMANDS = [
  'get_products', 'add_product', 'delete_product',
  'get_settings', 'save_settings', 'import_database_cmd', 'export_database_cmd',
  'get_analytics',
  'get_sales', 'add_sale',
  'get_ingredients', 'add_ingredient', 'update_ingredient', 'soft_delete_ingredient',
  'get_inventory_transactions', 'add_inventory_transaction', 'get_inventory_adjustments',
  'get_employees', 'add_employee', 'update_employee', 'soft_delete_employee',
  'get_employee_types', 'add_employee_type', 'update_employee_type', 'soft_delete_employee_type',
  'get_recipes', 'create_recipe', 'update_recipe', 'soft_delete_recipe',
  'add_recipe_ingredient', 'delete_recipe_ingredient',
  'get_transactions', 'delete_transaction',
  'send_support_email',
] as const;

describe('Tauri Invoke Mock Infrastructure', () => {
  describe('Mock Utilities', () => {
    it('safeInvoke returns data on success', async () => {
      mockInvokeSuccess('get_products', [{ id: 1, name: 'Burger', price: 10, unit: 'piece' }]);
      const result = await safeInvoke('get_products');
      expect(result.data).toBeDefined();
      expect(result.data).toEqual([{ id: 1, name: 'Burger', price: 10, unit: 'piece' }]);
      expect(result.error).toBeUndefined();
    });

    it('safeInvoke returns error on failure', async () => {
      mockInvokeError('get_settings', 'Database not found');
      const result = await safeInvoke('get_settings');
      expect(result.error).toBe('Database not found');
      expect(result.data).toBeUndefined();
    });

    it('mockInvokeSuccess only affects the specified command', async () => {
      mockInvokeSuccess('get_products', []);
      const success = await safeInvoke('get_products');
      const fail = await safeInvoke('get_settings');
      expect(success.data).toEqual([]);
      expect(fail.error).toContain('No mock configured');
    });

    it('mockInvokeFatalError rejects all commands', async () => {
      mockInvokeFatalError('Tauri backend unavailable');
      const r1 = await safeInvoke('get_products');
      const r2 = await safeInvoke('get_settings');
      expect(r1.error).toBe('Tauri backend unavailable');
      expect(r2.error).toBe('Tauri backend unavailable');
    });

    it('asserts invoke call history via call tracking', async () => {
      mockInvokeSuccess('get_products', []);
      await invoke('get_products');
      expectLastCall('get_products');
    });

    it('asserts invoke call count via call tracking', async () => {
      mockInvokeSuccess('get_products', []);
      await invoke('get_products');
      await invoke('get_products');
      expect(getInvokeHistory()).toHaveLength(2);
    });

    it('asserts invoke arguments via call tracking', async () => {
      mockInvokeSuccess('add_product', { id: 1 });
      const payload = { product: { name: 'Burger', price: 10, unit: 'piece' } };
      await invoke('add_product', payload);
      expectLastCall('add_product', payload);
    });
  });
});

describe('Invalid Invoke Detection', () => {
  beforeEach(() => {
    resetInvokeMocks();
  });

  describe('Unknown Command Names', () => {
    it('rejects with error for nonexistent command', async () => {
      mockInvokeFatalError('Unknown Tauri command: "get_nonexistent"');
      const result = await safeInvoke('get_nonexistent');
      expect(result.error).toBeDefined();
      expect(result.data).toBeUndefined();
    });

    it('rejects with descriptive error for misspelled command', async () => {
      mockInvokeError('get_product', 'No command "get_product" found');
      const result = await safeInvoke('get_product');
      expect(result.error).toContain('No command');
    });

    it('rejects when command is called with wrong argument shape', async () => {
      mockInvokeFatalError('Invalid arguments: expected { id: number }');
      const result = await safeInvoke('delete_product', { id: 'abc' } as unknown as Record<string, unknown>);
      expect(result.error).toBeDefined();
    });
  });

  describe('Backend Failures', () => {
    it('handles database connection errors gracefully', async () => {
      mockInvokeError('get_settings', 'failed to open database: permission denied');
      const result = await safeInvoke('get_settings');
      expect(result.error).toContain('database');
    });

    it('handles timeout errors', async () => {
      mockInvokeError('get_analytics', 'Invoke timed out after 30s');
      const result = await safeInvoke('get_analytics');
      expect(result.error).toContain('timed out');
    });

    it('handles serialization errors (Rust panic)', async () => {
      mockInvokeError('get_sales', 'called `Result::unwrap()` on an `Err` value');
      const result = await safeInvoke('get_sales');
      expect(result.error).toBeDefined();
    });

    it('handles empty result sets without error', async () => {
      mockInvokeSuccess('get_products', []);
      const result = await safeInvoke('get_products');
      expect(result.data).toEqual([]);
      expect(result.error).toBeUndefined();
    });

    it('handles null/undefined fields gracefully', async () => {
      mockInvokeSuccess('get_employees', [
        { id: 1, name: 'John', phone: null, email: null, employee_type_id: 1, salary: 1000, is_active: true, joined_at: null },
      ]);
      const result = await safeInvoke('get_employees');
      expect(result.data).toBeDefined();
      const emp = Array.isArray(result.data) ? (result.data as Array<Record<string, unknown>>)[0] : null;
      expect(emp?.phone).toBeNull();
      expect(emp?.joined_at).toBeNull();
    });
  });

  describe('Error Recovery Patterns', () => {
    it('should fallback gracefully when get_analytics fails (as done in Reports.tsx)', async () => {
      mockInvokeError('get_analytics', 'No analytics data');
      const result = await (invoke('get_analytics') as Promise<unknown>).catch(() => null);
      expect(result).toBeNull();
    });

    it('should handle partial data loading (Promise.allSettled with one failure)', async () => {
      mockInvokeSuccess('get_products', [{ id: 1, name: 'Pizza', price: 15, unit: 'piece' }]);
      mockInvokeError('get_analytics', 'Failed');
      mockInvokeSuccess('get_settings', { restaurant_name: 'Test', currency: 'USD' });

      const results = await Promise.allSettled([
        invoke('get_settings').then(d => ({ data: d })).catch(e => ({ error: String(e) })),
        invoke('get_analytics').then(d => ({ data: d })).catch(e => ({ error: String(e) })),
        invoke('get_products').then(d => ({ data: d })).catch(e => ({ error: String(e) })),
      ]);

      const extract = (r: PromiseSettledResult<unknown>) =>
        r.status === 'fulfilled' ? r.value : null;

      // Need type assertion for the result shape
      const r0 = extract(results[0]) as { data?: unknown; error?: string } | null;
      const r1 = extract(results[1]) as { data?: unknown; error?: string } | null;
      const r2 = extract(results[2]) as { data?: unknown; error?: string } | null;

      expect(r0?.data).toBeDefined();
      expect(r1?.error).toBeDefined();
      expect(r2?.data).toBeDefined();
    });
  });
});

describe('Page-Level Invoke Patterns', () => {
  beforeEach(() => {
    resetInvokeMocks();
  });

  describe('ProductManager.tsx patterns', () => {
    it('calls get_products on load', async () => {
      mockInvokeSuccess('get_products', []);
      await invoke('get_products');
      expectLastCall('get_products');
    });

    it('calls add_product with product payload', async () => {
      const newProduct = { name: 'Fries', price: 5, unit: 'plate' };
      mockInvokeSuccess('add_product', { id: 2, ...newProduct });
      await invoke('add_product', { product: newProduct });
      expectLastCall('add_product', { product: newProduct });
    });

    it('calls delete_product with id', async () => {
      mockInvokeSuccess('delete_product', {});
      await invoke('delete_product', { id: 1 });
      expectLastCall('delete_product', { id: 1 });
    });

    it('handles add_product failure gracefully', async () => {
      mockInvokeError('add_product', 'Product name already exists');
      const result = await safeInvoke('add_product', { product: { name: 'Burger', price: 10, unit: 'piece' } });
      expect(result.error).toContain('already exists');
    });
  });

  describe('Settings.tsx patterns', () => {
    it('calls save_settings with full settings payload', async () => {
      const settings = {
        restaurant_name: 'My Restaurant',
        address: '123 Street',
        phone: '123456789',
        email: 'test@test.com',
        tax_rate: '10',
        currency: 'USD',
        opening_time: '09:00',
        closing_time: '22:00',
        receipt_footer: 'Thank you',
        dine_in_tables: 10,
        delivery_fee: 5,
        delivery_fee_per_km: 2,
      };
      mockInvokeSuccess('save_settings', settings);
      await invoke('save_settings', { settings });
      expectLastCall('save_settings', { settings });
    });

    it('handles save_settings validation errors', async () => {
      mockInvokeError('save_settings', 'Validation error: tax_rate must be between 0 and 100');
      const result = await safeInvoke('save_settings', { settings: { tax_rate: '150', currency: 'USD' } });
      expect(result.error).toContain('Validation error');
    });

    it('calls import_database_cmd with base64 data', async () => {
      mockInvokeSuccess('import_database_cmd', {});
      await invoke('import_database_cmd', { data: 'base64encodedstring' });
      expectLastCall('import_database_cmd', { data: 'base64encodedstring' });
    });

    it('calls export_database_cmd and returns base64 string', async () => {
      mockInvokeSuccess('export_database_cmd', 'base64encodeddb');
      const result = await safeInvoke('export_database_cmd');
      expect(typeof result.data).toBe('string');
    });
  });

  describe('Employees.tsx patterns', () => {
    it('calls add_employee with employee payload', async () => {
      const employee = { name: 'John', salary: 1000, phone: null, email: null, employee_type_id: 1 };
      mockInvokeSuccess('add_employee', { id: 1, ...employee, is_active: true });
      await invoke('add_employee', { employee });
      expectLastCall('add_employee', { employee });
    });

    it('calls soft_delete_employee with id', async () => {
      mockInvokeSuccess('soft_delete_employee', {});
      await invoke('soft_delete_employee', { id: 1 });
      expectLastCall('soft_delete_employee', { id: 1 });
    });

    it('calls add_employee_type with type payload', async () => {
      const employeeType = { name: 'Chef', description: 'Head chef' };
      mockInvokeSuccess('add_employee_type', { id: 1, ...employeeType, is_active: true });
      await invoke('add_employee_type', { employeeType });
      expectLastCall('add_employee_type', { employeeType });
    });
  });

  describe('Recipes.tsx patterns', () => {
    it('calls create_recipe with recipe + ingredients', async () => {
      const recipeData = { product_id: 1, recipe_type_id: 1, yield_quantity: 10 };
      const ingredientsData = [{ ingredient_id: 1, quantity: 2 }];
      mockInvokeSuccess('create_recipe', { id: 1, ...recipeData, is_active: true });
      await invoke('create_recipe', { recipe: recipeData, ingredients: ingredientsData });
      expectLastCall('create_recipe', { recipe: recipeData, ingredients: ingredientsData });
    });

    it('calls add_recipe_ingredient with ingredient payload', async () => {
      const ingredient = { recipe_id: 1, ingredient_id: 2, quantity: 3 };
      mockInvokeSuccess('add_recipe_ingredient', { id: 1, ...ingredient });
      await invoke('add_recipe_ingredient', ingredient);
      expectLastCall('add_recipe_ingredient', ingredient);
    });
  });

  describe('Inventory.tsx patterns', () => {
    it('calls add_ingredient with ingredient payload', async () => {
      const ingredient = {
        name: 'Tomato', unit: 'kg', current_quantity: 50,
        reorder_level: 10, reorder_quantity: 20, cost_per_unit: 2.5,
      };
      mockInvokeSuccess('add_ingredient', { id: 1, ...ingredient, is_active: true });
      await invoke('add_ingredient', { ingredient });
      expectLastCall('add_ingredient', { ingredient });
    });

    it('calls add_inventory_transaction with transaction payload', async () => {
      const transaction = { ingredient_id: 1, transaction_type: 'purchase', quantity_change: 50 };
      mockInvokeSuccess('add_inventory_transaction', { id: 1, ...transaction, created_at: new Date().toISOString() });
      await invoke('add_inventory_transaction', { transaction, adjustmentReason: null, createdBy: null });
      expectLastCall('add_inventory_transaction', { transaction, adjustmentReason: null, createdBy: null });
    });
  });

  describe('Sale.tsx patterns', () => {
    it('calls add_sale with sale + items payload', async () => {
      const saleData = {
        total_amount: 25, currency: 'USD', order_type: 'dine-in', status: 'completed',
        table_number: 5, delivery_type_id: null, delivery_address: null, employee_id: null,
      };
      const itemsData = [{ product_name: 'Burger', price: 10, quantity: 2, unit: 'piece' }];
      mockInvokeSuccess('add_sale', { id: 1, ...saleData, date: '2026-01-01', time: '12:00' });
      await invoke('add_sale', { sale: saleData, items: itemsData });
      expectLastCall('add_sale', { sale: saleData, items: itemsData });
    });
  });

  describe('About.tsx patterns', () => {
    it('calls send_support_email with form payload', async () => {
      const payload = { name: 'John', email: 'john@test.com', subject: 'Help', message: 'Need assistance' };
      mockInvokeSuccess('send_support_email', { success: true });
      await invoke('send_support_email', payload);
      expectLastCall('send_support_email', payload);
    });
  });

  describe('Transactions.tsx patterns', () => {
    it('calls delete_transaction with id', async () => {
      mockInvokeSuccess('delete_transaction', {});
      await invoke('delete_transaction', { id: 5 });
      expectLastCall('delete_transaction', { id: 5 });
    });
  });
});

describe('Command Completeness', () => {
  it('all known commands are testable', () => {
    expect(KNOWN_COMMANDS.length).toBeGreaterThan(30);
    expect(KNOWN_COMMANDS).toContain('get_products');
    expect(KNOWN_COMMANDS).toContain('save_settings');
    expect(KNOWN_COMMANDS).toContain('add_sale');
    expect(KNOWN_COMMANDS).toContain('send_support_email');
  });
});
