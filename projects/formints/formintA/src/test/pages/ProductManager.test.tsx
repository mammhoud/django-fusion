import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  within,
  userEvent,
  fireEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import { getInvokeHistory, clearInvokeHistory } from '../setup';
import ProductManager from '../../pages/pos/ProductManager';

const mockProducts = [
  { id: 1, name: 'Chicken Burger', price: 350, unit: 'item',  category_id: 1, product_type: 'product' },
  { id: 2, name: 'French Fries',  price: 150, unit: 'plate', category_id: 2, product_type: 'product' },
  { id: 3, name: 'Beef Burger',   price: 450, unit: 'item',  category_id: 1, product_type: 'product' },
];

const mockCategories = [
  { id: 1, name: 'Burgers', color: '#f97316' },
  { id: 2, name: 'Sides', color: '#06b6d4' },
];

// Hydration is async (products + categories + AnimatePresence mode="wait"
// fallback timer). Under combined-run CPU contention the default 1000ms waitFor
// window is occasionally too tight, so give hydration generous headroom.
async function waitForHydration() {
  await waitFor(
    () => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    },
    { timeout: 5000 },
  );
}

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  clearInvokeHistory();
  mockInvokeSuccess('get_products', mockProducts);
  mockInvokeSuccess('get_categories', mockCategories);
});

describe('ProductManager page', () => {

  it('hydrates product grid from the backend', async () => {
    renderWithRouter(<ProductManager />);

    await waitForHydration();
    expect(screen.getAllByText('French Fries').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Beef Burger').length).toBeGreaterThanOrEqual(1);
  });

  it('debounces the search input — filter applies only after the idle window', async () => {
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    const searchInput = screen.getByTestId('pm-search-input');
    await userEvent.type(searchInput, 'fries');

    await waitFor(
      () => {
        expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
        expect(screen.queryByText('Beef Burger')).not.toBeInTheDocument();
        expect(screen.getAllByText('French Fries').length).toBeGreaterThanOrEqual(1);
      },
      { timeout: 1000 },
    );
  });

  it('shows the debounce spinner while the user is typing', async () => {
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    const searchInput = screen.getByTestId('pm-search-input');
    await userEvent.type(searchInput, 'beef');

    // Right after typing, the filtering spinner should be present
    expect(screen.getByLabelText('filtering')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
      expect(screen.queryByText('French Fries')).not.toBeInTheDocument();
      expect(screen.getAllByText('Beef Burger').length).toBeGreaterThanOrEqual(1);
    }, { timeout: 1000 });

    // After debounce flushes (250ms), the spinner should be removed
    await waitFor(() => {
      expect(screen.queryByLabelText('filtering')).not.toBeInTheDocument();
    }, { timeout: 1000 });
  });

  it('category filter narrows the list', async () => {
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    const sidesTag = screen.getByText('Sides');
    await userEvent.click(sidesTag);

    await waitFor(() => {
      expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
      expect(screen.getAllByText('French Fries').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('opens the add-product modal when the Add button is clicked', async () => {
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    await userEvent.click(screen.getByTestId('pm-add-button'));

    await waitFor(() => {
      expect(screen.getByTestId('pm-modal')).toBeInTheDocument();
    });
  });

  it('walks the add wizard — Basics → Recipe & Options → Review with recipe creation on save', async () => {
    mockInvokeSuccess('get_ingredients', [
      { id: 1, name: 'Chicken Breast', unit: 'kg', current_quantity: 25, reorder_level: 5, reorder_quantity: 10, cost_per_unit: 450, is_active: true },
      { id: 2, name: 'Cooking Oil', unit: 'liter', current_quantity: 3, reorder_level: 10, reorder_quantity: 20, cost_per_unit: 320, is_active: true },
    ]);
    mockInvokeSuccess('add_product', { id: 99, name: 'Wizard Burger', price: 550, unit: 'item', product_type: 'product' });
    mockInvokeSuccess('create_recipe', { id: 7, product_id: 99, recipe_type_id: 1, yield_quantity: 2 });
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    await userEvent.click(screen.getByTestId('pm-add-button'));
    await waitFor(() => expect(screen.getByTestId('pm-modal')).toBeInTheDocument());

    // Step 1 — Basics: fill name + price, then Next
    await userEvent.type(screen.getByTestId('pm-name-input'), 'Wizard Burger');
    await userEvent.type(screen.getByTestId('pm-price-input'), '550');
    await userEvent.click(screen.getByTestId('pm-next'));

    // Step 2 — Recipe & Options: add an ingredient row + yield, then Next
    const modal = within(screen.getByTestId('pm-modal'));
    expect(modal.getByText(/Recipe Ingredients/i)).toBeInTheDocument();
    await userEvent.click(modal.getByRole('button', { name: /Add ingredient/i }));
    const ingredientSelect = modal.getAllByRole('combobox')[0];
    await userEvent.selectOptions(ingredientSelect, '1');
    const qtyInput = screen.getByPlaceholderText('Qty');
    await userEvent.type(qtyInput, '2');
    await userEvent.click(screen.getByTestId('pm-next'));

    // Step 3 — Review: summary visible, Save submits product + recipe
    expect(screen.getByText(/Wizard Burger/i)).toBeInTheDocument();
    await userEvent.click(screen.getByTestId('pm-submit'));

    await waitFor(() => {
      const history = getInvokeHistory();
      const saved = history.find(h => h.cmd === 'add_product');
      expect(saved).toBeTruthy();
      const recipe = history.find(h => h.cmd === 'create_recipe');
      expect(recipe).toBeTruthy();
      const recipeArgs = recipe!.args as {
        recipe: { product_id: number };
        ingredients: { ingredient_id: number }[];
      };
      expect(recipeArgs.recipe.product_id).toBe(99);
      expect(recipeArgs.ingredients).toHaveLength(1);
      expect(recipeArgs.ingredients[0].ingredient_id).toBe(1);
    });
  });
});

describe('Category CRUD — color round-trip through the modal', () => {
  it('adds a category with a selected color', async () => {
    mockInvokeSuccess('add_category', { id: 3, name: 'Drinks', color: '#06b6d4' });
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    // Open the category CRUD modal
    await userEvent.click(screen.getByTestId('pm-manage-categories'));
    await waitFor(
      () => {
        expect(screen.getByTestId('pm-category-name-input')).toBeInTheDocument();
      },
      { timeout: 3000 },
    );

    // Fill name + pick a palette color
    await userEvent.type(screen.getByTestId('pm-category-name-input'), 'Drinks');
    await userEvent.click(screen.getByRole('button', { name: 'Color #06b6d4' }));

    // Submit
    await userEvent.click(screen.getByTestId('pm-category-submit'));

    await waitFor(() => {
      const history = getInvokeHistory();
      const addCall = history.find(h => h.cmd === 'add_category');
      expect(addCall).toBeDefined();
      expect(addCall!.args).toEqual({ data: { name: 'Drinks', color: '#06b6d4' } });
    });
  });

  it('adds a category with a custom color from the color input', async () => {
    mockInvokeSuccess('add_category', { id: 4, name: 'Snacks', color: '#ff00aa' });
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    await userEvent.click(screen.getByTestId('pm-manage-categories'));
    await waitFor(() => {
      expect(screen.getByTestId('pm-category-name-input')).toBeInTheDocument();
    });

    await userEvent.type(screen.getByTestId('pm-category-name-input'), 'Snacks');

    // Use the native color input for a custom hex
    // (aria-label is the i18n key under the mocked t() → accept either)
    // type=color inputs aren't editable via userEvent.clear/type — use fireEvent.change
    const customColor = screen.getByLabelText(/productManager\.categoryCustomColor|Custom color/);
    fireEvent.change(customColor, { target: { value: '#ff00aa' } });

    await userEvent.click(screen.getByTestId('pm-category-submit'));

    await waitFor(() => {
      const history = getInvokeHistory();
      const addCall = history.find(h => h.cmd === 'add_category');
      expect(addCall).toBeDefined();
      expect(addCall!.args).toEqual({ data: { name: 'Snacks', color: '#ff00aa' } });
    });
  });

  it('validates an empty category name and does not invoke add_category', async () => {
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    await userEvent.click(screen.getByTestId('pm-manage-categories'));
    await waitFor(() => {
      expect(screen.getByTestId('pm-category-name-input')).toBeInTheDocument();
    });

    // Submit without a name
    await userEvent.click(screen.getByTestId('pm-category-submit'));

    await waitFor(() => {
      expect(screen.getByText(/productManager\.categoryValidationName|Please enter a category name/)).toBeInTheDocument();
    });
    const history = getInvokeHistory();
    expect(history.some(h => h.cmd === 'add_category')).toBe(false);
  });

  it('edits an existing category name and color', async () => {
    mockInvokeSuccess('update_category', { id: 1, name: 'Gourmet', color: '#8b5cf6' });
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    await userEvent.click(screen.getByTestId('pm-manage-categories'));
    await waitFor(
      () => {
        expect(screen.getByTestId('pm-category-name-input')).toBeInTheDocument();
      },
      { timeout: 3000 },
    );

    // The existing-categories list shows an edit (pencil) button per row.
    // Scope to the category dialog — the product grid's edit buttons share
    // the same 'Edit' accessible name, so an unscoped query hits the grid
    // first (opens the product modal instead of the category edit).
    const categoryDialog = screen.getByRole('dialog', { name: /Add Category|Edit Category/ });
    const editButtons = within(categoryDialog).getAllByRole('button', { name: /common\.edit|Edit/ });
    await userEvent.click(editButtons[0]);

    // Modal should now be prefilled with the category being edited
    await waitFor(() => {
      expect(screen.getByTestId('pm-category-name-input')).toHaveValue('Burgers');
    });

    await userEvent.clear(screen.getByTestId('pm-category-name-input'));
    await userEvent.type(screen.getByTestId('pm-category-name-input'), 'Gourmet');
    await userEvent.click(screen.getByRole('button', { name: 'Color #8b5cf6' }));
    await userEvent.click(screen.getByTestId('pm-category-submit'));

    await waitFor(() => {
      const history = getInvokeHistory();
      const updateCall = history.find(h => h.cmd === 'update_category');
      expect(updateCall).toBeDefined();
      expect(updateCall!.args).toEqual({ id: 1, update: { name: 'Gourmet', color: '#8b5cf6' } });
    });
  });

  it('deletes a category through the confirmation modal', async () => {
    mockInvokeSuccess('delete_category', null);
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    await userEvent.click(screen.getByTestId('pm-manage-categories'));
    await waitFor(() => {
      expect(screen.getByTestId('pm-category-name-input')).toBeInTheDocument();
    });

    // Delete the second category (Sides) from the existing-categories list
    const deleteButtons = screen.getAllByRole('button', { name: /productManager\.deleteCategory|Delete Category/ });
    await userEvent.click(deleteButtons[1]);

    // Confirmation modal appears — confirm the delete
    await waitFor(() => {
      expect(screen.getByText(/productManager\.deleteCategoryConfirm|Delete this category/)).toBeInTheDocument();
    });
    const confirmButtons = screen.getAllByRole('button', { name: /productManager\.confirmDelete|Yes, Delete/ });
    await userEvent.click(confirmButtons[confirmButtons.length - 1]);

    await waitFor(() => {
      const history = getInvokeHistory();
      const deleteCall = history.find(h => h.cmd === 'delete_category');
      expect(deleteCall).toBeDefined();
      expect(deleteCall!.args).toEqual({ id: 2 });
    });
  });
});

describe('ProductManager bulk actions (table view)', () => {
  async function openTableView() {
    renderWithRouter(<ProductManager />);
    await waitForHydration();
    await userEvent.click(screen.getByRole('button', { name: /Switch to table view/ }));
    await waitFor(() => {
      expect(screen.getAllByRole('checkbox').length).toBeGreaterThanOrEqual(4);
    });
  }

  // Helper: select the first N product rows. Each row renders TWO checkboxes
  // (desktop + mobile), so desktop rows sit at odd indices (1, 3, 5, …) —
  // index 0 is the header select-all checkbox.
  async function selectRows(count: number) {
    const checkboxes = screen.getAllByRole('checkbox');
    for (let i = 0; i < count; i++) {
      await userEvent.click(checkboxes[1 + i * 2]);
    }
  }

  it('shows bulk action buttons only after selecting rows', async () => {
    await openTableView();

    expect(screen.queryByTestId('pm-bulk-delete')).not.toBeInTheDocument();
    expect(screen.queryByTestId('pm-bulk-category')).not.toBeInTheDocument();
    expect(screen.queryByTestId('pm-bulk-type')).not.toBeInTheDocument();

    await selectRows(2);

    expect(screen.getByTestId('pm-bulk-delete')).toBeInTheDocument();
    expect(screen.getByTestId('pm-bulk-category')).toBeInTheDocument();
    expect(screen.getByTestId('pm-bulk-type')).toBeInTheDocument();
  });

  it('bulk deletes selected products after confirmation', async () => {
    mockInvokeSuccess('delete_product', null);
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true);
    await openTableView();

    await selectRows(2); // table sorts by newest (id desc) → rows 3 + 2

    await userEvent.click(screen.getByTestId('pm-bulk-delete'));

    await waitFor(() => {
      const history = getInvokeHistory();
      const deleteCalls = history.filter(h => h.cmd === 'delete_product');
      expect(deleteCalls.length).toBe(2);
      expect(deleteCalls.map(c => c.args)).toEqual([{ id: 3 }, { id: 2 }]);
    });
    confirmSpy.mockRestore();
  });

  it('bulk delete asks for confirmation first and skips when cancelled', async () => {
    mockInvokeSuccess('delete_product', null);
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false);
    await openTableView();

    await selectRows(1);
    await userEvent.click(screen.getByTestId('pm-bulk-delete'));

    expect(confirmSpy).toHaveBeenCalled();
    const history = getInvokeHistory();
    expect(history.some(h => h.cmd === 'delete_product')).toBe(false);
    confirmSpy.mockRestore();
  });

  it('bulk change category updates all selected products', async () => {
    mockInvokeSuccess('update_product', { id: 1, name: 'X', price: 0, unit: 'item' });
    await openTableView();

    await selectRows(2); // rows 3 + 2 (newest-first order)

    await userEvent.click(screen.getByTestId('pm-bulk-category'));
    await waitFor(() => {
      expect(screen.getByTestId('pm-bulk-category-select')).toBeInTheDocument();
    });
    await userEvent.selectOptions(screen.getByTestId('pm-bulk-category-select'), '2');
    await userEvent.click(screen.getByTestId('pm-bulk-category-apply'));

    await waitFor(() => {
      const history = getInvokeHistory();
      const updateCalls = history.filter(h => h.cmd === 'update_product');
      expect(updateCalls.length).toBe(2);
      expect(updateCalls.map(c => c.args)).toEqual([
        { id: 3, update: { category_id: 2 } },
        { id: 2, update: { category_id: 2 } },
      ]);
    });
  });

  it('bulk change type updates all selected products', async () => {
    mockInvokeSuccess('update_product', { id: 1, name: 'X', price: 0, unit: 'item' });
    await openTableView();

    await selectRows(2); // rows 3 + 2 (newest-first order)

    await userEvent.click(screen.getByTestId('pm-bulk-type'));
    await waitFor(() => {
      expect(screen.getByTestId('pm-bulk-type-select')).toBeInTheDocument();
    });
    await userEvent.selectOptions(screen.getByTestId('pm-bulk-type-select'), 'combo');
    await userEvent.click(screen.getByTestId('pm-bulk-type-apply'));

    await waitFor(() => {
      const history = getInvokeHistory();
      const updateCalls = history.filter(h => h.cmd === 'update_product');
      expect(updateCalls.length).toBe(2);
      expect(updateCalls.map(c => c.args)).toEqual([
        { id: 3, update: { product_type: 'combo' } },
        { id: 2, update: { product_type: 'combo' } },
      ]);
    });
  });

  it('bulk category modal can set products to no category (0 → null)', async () => {
    mockInvokeSuccess('update_product', { id: 1, name: 'X', price: 0, unit: 'item' });
    await openTableView();

    await selectRows(1); // row 3 (newest-first)

    await userEvent.click(screen.getByTestId('pm-bulk-category'));
    await waitFor(() => {
      expect(screen.getByTestId('pm-bulk-category-select')).toBeInTheDocument();
    });
    // Leave default (empty = no category) and apply
    await userEvent.click(screen.getByTestId('pm-bulk-category-apply'));

    await waitFor(() => {
      const history = getInvokeHistory();
      const updateCalls = history.filter(h => h.cmd === 'update_product');
      expect(updateCalls.length).toBe(1);
      expect(updateCalls[0].args).toEqual({ id: 3, update: { category_id: null } });
    });
  });

  it('clears selection after a successful bulk action', async () => {
    mockInvokeSuccess('update_product', { id: 1, name: 'X', price: 0, unit: 'item' });
    await openTableView();

    await selectRows(1);
    expect(screen.getByTestId('pm-bulk-type')).toBeInTheDocument();

    await userEvent.click(screen.getByTestId('pm-bulk-type'));
    await waitFor(() => {
      expect(screen.getByTestId('pm-bulk-type-select')).toBeInTheDocument();
    });
    await userEvent.selectOptions(screen.getByTestId('pm-bulk-type-select'), 'service');
    await userEvent.click(screen.getByTestId('pm-bulk-type-apply'));

    await waitFor(() => {
      expect(screen.queryByTestId('pm-bulk-type')).not.toBeInTheDocument();
    });
  });
});
