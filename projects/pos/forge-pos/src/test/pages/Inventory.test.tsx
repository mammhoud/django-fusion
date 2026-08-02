import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
  within,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks, mockInvokeError } from '../mocks/tauri';
import { getInvokeHistory, clearInvokeHistory } from '../setup';
import Inventory from '../../pages/kitchen/Inventory';

const mockIngredients = [
  { id: 1, name: 'Chicken Breast', unit: 'kg', current_quantity: 25, reorder_level: 5, reorder_quantity: 10, cost_per_unit: 450, is_active: true },
  { id: 2, name: 'Cooking Oil', unit: 'liter', current_quantity: 3, reorder_level: 10, reorder_quantity: 20, cost_per_unit: 320, is_active: true },
  { id: 3, name: 'Salt', unit: 'kg', current_quantity: 0, reorder_level: 2, reorder_quantity: 5, cost_per_unit: 50, is_active: false },
];

const mockTransactions = [
  { id: 1, ingredient_id: 1, transaction_type: 'purchase', quantity_change: 10, reference_id: null, note: 'Weekly stock', created_at: '2026-01-15T10:00:00' },
  { id: 2, ingredient_id: 2, transaction_type: 'usage', quantity_change: -2, reference_id: null, note: 'Used for frying', created_at: '2026-01-15T12:00:00' },
];

const mockAdjustments = [
  { id: 1, ingredient_id: 1, previous_quantity: 23, new_quantity: 25, reason: 'Inventory count correction', created_by: 'Manager', created_at: '2026-01-14T09:00:00' },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  clearInvokeHistory();
  mockInvokeSuccess('get_ingredients', mockIngredients);
  mockInvokeSuccess('get_inventory_transactions', mockTransactions);
  mockInvokeSuccess('get_inventory_adjustments', mockAdjustments);
});

describe('Inventory Page', () => {
  it('renders summary cards with ingredient counts', async () => {
    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.totalIngredients|Total Ingredients/)).toBeInTheDocument();
    });
    // "3" total ingredients — use getAllByText since "3" might appear elsewhere
    const threes = screen.getAllByText('3', { exact: true });
    expect(threes.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/inventory\.lowStockItems|Low Stock Items/)).toBeInTheDocument();
    // "Out of Stock" appears as summary card heading AND status labels — use getAllByText
    const outOfStock = screen.getAllByText(/inventory\.outOfStock|Out of Stock/);
    expect(outOfStock.length).toBeGreaterThanOrEqual(1);
  });

  it('renders tab navigation and switches between tabs', async () => {
    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.stockLevels|Stock Levels/)).toBeInTheDocument();
    });
    expect(screen.getByText(/inventory\.transactions|Transactions/)).toBeInTheDocument();
    expect(screen.getByText(/inventory\.adjustments|Adjustments/)).toBeInTheDocument();

    // Click Transactions tab
    await userEvent.click(screen.getByText(/inventory\.transactions|Transactions/));
    await waitFor(() => {
      expect(screen.getByText(/inventory\.transactionLog|Transaction Log/)).toBeInTheDocument();
    });

    // Click Adjustments tab
    await userEvent.click(screen.getByText(/inventory\.adjustments|Adjustments/));
    await waitFor(() => {
      expect(screen.getByText(/inventory\.manualAdjustments|Manual Adjustments/)).toBeInTheDocument();
    });
  });

  it('shows stock levels tab content with ingredient list', async () => {
    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.allIngredients|All Ingredients/)).toBeInTheDocument();
    });
    const chickenElements = screen.getAllByText('Chicken Breast');
    expect(chickenElements.length).toBeGreaterThanOrEqual(1);
    const oilElements = screen.getAllByText('Cooking Oil');
    expect(oilElements.length).toBeGreaterThanOrEqual(1);
  });

  it('shows low stock indicator for items below reorder level', async () => {
    renderWithRouter(<Inventory />);

    await waitFor(() => {
      const oilElements = screen.getAllByText('Cooking Oil');
      expect(oilElements.length).toBeGreaterThanOrEqual(1);
    });
    // getStockStatus still returns hardcoded 'Low Stock' — no key change needed
    const lowStockElements = screen.getAllByText(/inventory\.lowStock|Low Stock/);
    expect(lowStockElements.length).toBeGreaterThan(0);
  });

  it('shows Add Ingredient button and opens modal', async () => {
    mockInvokeSuccess('add_ingredient', { id: 4, name: 'New Ingredient', unit: 'kg', current_quantity: 10, reorder_level: 2, reorder_quantity: 5, cost_per_unit: 100, is_active: true });
    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.addIngredient|Add Ingredient/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/inventory\.addIngredient|Add Ingredient/));

    await waitFor(() => {
      expect(screen.getByText(/inventory\.addIngredientTitle|Add New Ingredient/)).toBeInTheDocument();
    });
  });

  it('shows ingredient filter in transactions tab', async () => {
    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.transactions|Transactions/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/inventory\.transactions|Transactions/));

    await waitFor(() => {
      expect(screen.getByText(/inventory\.transactionLog|Transaction Log/)).toBeInTheDocument();
    });
    expect(screen.getByText(/inventory\.allIngredientsFilter|All Ingredients/)).toBeInTheDocument();
  });

  it('shows adjustments list', async () => {
    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.adjustments|Adjustments/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/inventory\.adjustments|Adjustments/));

    await waitFor(() => {
      expect(screen.getByText(/inventory\.manualAdjustments|Manual Adjustments/)).toBeInTheDocument();
    });
    expect(screen.getByText(/Inventory count correction/)).toBeInTheDocument();
  });

  it('handles empty inventory gracefully', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_ingredients', []);
    mockInvokeSuccess('get_inventory_transactions', []);
    mockInvokeSuccess('get_inventory_adjustments', []);

    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.totalIngredients|Total Ingredients/)).toBeInTheDocument();
    });
    const zeros = screen.getAllByText('0', { exact: true });
    expect(zeros.length).toBeGreaterThanOrEqual(1);
  });

  it('handles API failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeError('get_ingredients', 'Network error');
    mockInvokeError('get_inventory_transactions', 'Network error');
    mockInvokeError('get_inventory_adjustments', 'Network error');

    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.totalIngredients|Total Ingredients/)).toBeInTheDocument();
    });
    const zeros = screen.getAllByText('0', { exact: true });
    expect(zeros.length).toBeGreaterThanOrEqual(1);
  });

  // ── Adjustments: POST a manual adjustment ──
  it('posts a manual adjustment with reason via the transaction modal', async () => {
    mockInvokeSuccess('add_inventory_transaction', { id: 3 });
    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.adjustments|Adjustments/)).toBeInTheDocument();
    });
    await userEvent.click(screen.getByText(/inventory\.adjustments|Adjustments/));
    await waitFor(() => {
      expect(screen.getByText(/inventory\.manualAdjustments|Manual Adjustments/)).toBeInTheDocument();
    });

    // Add Adjustment button opens the transaction modal pre-set to 'adjustment'
    await userEvent.click(screen.getByText(/inventory\.addAdjustment|Add Adjustment/));

    const dialog = screen.getByRole('dialog', { name: /Record Transaction/ });
    const combos = within(dialog).getAllByRole('combobox');
    await userEvent.selectOptions(combos[0], '1'); // Chicken Breast
    await userEvent.selectOptions(combos[1], 'adjustment');

    // Quantity change input (placeholder from inventory.quantityPlaceholder)
    await userEvent.type(within(dialog).getByPlaceholderText(/Positive = add/), '5');

    // Text inputs appear in DOM order: note, then (adjustment-only) reason + createdBy
    const textboxes = within(dialog).getAllByRole('textbox');
    await userEvent.type(textboxes[1], 'Stock count correction'); // reason
    await userEvent.type(textboxes[2], 'Manager'); // created by

    await userEvent.click(within(dialog).getByRole('button', { name: /Record Transaction/ }));

    await waitFor(() => {
      const call = getInvokeHistory().find(h => h.cmd === 'add_inventory_transaction');
      expect(call).toBeDefined();
      const tx = call!.args!.transaction as Record<string, unknown>;
      expect(tx.transaction_type).toBe('adjustment');
      expect(tx.ingredient_id).toBe(1);
      expect(tx.quantity_change).toBe(5);
      expect(call!.args!.adjustmentReason).toBe('Stock count correction');
      expect(call!.args!.createdBy).toBe('Manager');
    });
    expect(await screen.findByText(/Transaction recorded/)).toBeInTheDocument();
  });

  // ── Adjustments: DELETE reverses the stock delta ──
  it('deletes a manual adjustment through the confirm dialog', async () => {
    mockInvokeSuccess('delete_inventory_adjustment', {});
    renderWithRouter(<Inventory />);

    await waitFor(() => {
      expect(screen.getByText(/inventory\.adjustments|Adjustments/)).toBeInTheDocument();
    });
    await userEvent.click(screen.getByText(/inventory\.adjustments|Adjustments/));
    await waitFor(() => {
      expect(screen.getByText(/Inventory count correction/)).toBeInTheDocument();
    });

    // Trash button on the adjustment card (title='Delete')
    const deleteBtn = screen.getAllByTitle('Delete')[0];
    await userEvent.click(deleteBtn);

    const dialog = screen.getByRole('dialog');
    await userEvent.click(within(dialog).getByRole('button', { name: /Delete|Deactivate/ }));

    await waitFor(() => {
      const deleteCall = getInvokeHistory().find(h => h.cmd === 'delete_inventory_adjustment');
      expect(deleteCall).toBeDefined();
      expect(deleteCall!.args!.id).toBe(1);
    });
    expect(await screen.findByText(/Adjustment deleted/)).toBeInTheDocument();
  });
});
