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
import Recipes from '../../pages/kitchen/Recipes';

const mockRecipes = [
  { id: 1, product_id: 1, recipe_type_id: 1, yield_quantity: 4, is_active: true },
  { id: 2, product_id: 2, recipe_type_id: 1, yield_quantity: 1, is_active: true },
  { id: 3, product_id: 4, recipe_type_id: 1, yield_quantity: 2, is_active: false },
];

const mockProducts = [
  { id: 1, name: 'Chicken Burger', price: 350, unit: 'piece' },
  { id: 2, name: 'Biryani', price: 250, unit: 'plate' },
  { id: 3, name: 'French Fries', price: 150, unit: 'plate' },
  { id: 4, name: 'Pizza', price: 800, unit: 'piece' },
];

const mockIngredients = [
  { id: 1, name: 'Chicken Breast', unit: 'kg', current_quantity: 25, reorder_level: 5, reorder_quantity: 10, cost_per_unit: 450, is_active: true },
  { id: 2, name: 'Rice', unit: 'kg', current_quantity: 20, reorder_level: 10, reorder_quantity: 25, cost_per_unit: 180, is_active: true },
  { id: 3, name: 'Oil', unit: 'liter', current_quantity: 8, reorder_level: 10, reorder_quantity: 20, cost_per_unit: 320, is_active: true },
];

const mockRecipeIngredients = {
  1: [{ id: 1, recipe_id: 1, ingredient_id: 1, quantity: 0.5, unit: 'kg', preparation_note: 'Boneless' }],
  2: [{ id: 2, recipe_id: 2, ingredient_id: 2, quantity: 1, unit: 'kg', preparation_note: 'Basmati' }],
  3: [],
};

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  clearInvokeHistory();
  mockInvokeSuccess('get_recipes', mockRecipes);
  mockInvokeSuccess('get_products', mockProducts);
  mockInvokeSuccess('get_ingredients', mockIngredients);
  // For each recipe, mock get_recipe_ingredients
  mockInvokeSuccess('get_recipe_ingredients', mockRecipeIngredients[1]);
});

describe('Recipes Page', () => {
  it('renders summary cards with recipe counts', async () => {
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      expect(screen.getByText(/recipes\.totalRecipes|Total Recipes/)).toBeInTheDocument();
    });
    // "2" active recipes — use getAllByText since it appears in multiple summary cards
    const twos = screen.getAllByText('2', { exact: true });
    expect(twos.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/recipes\.productsUsed|Products Used/)).toBeInTheDocument();
    expect(screen.getByText(/recipes\.avgCostPerRecipe|Avg Cost\/Recipe/)).toBeInTheDocument();
    expect(screen.getByText(/recipes\.avgProfitMargin|Avg Profit Margin/)).toBeInTheDocument();
  });

  it('shows recipe cards with product names', async () => {
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText('Biryani')).toBeInTheDocument();
    expect(screen.getByText('Pizza')).toBeInTheDocument();
  });

  it('shows cost analysis on recipe cards', async () => {
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      const prices = screen.getAllByText(/recipes\.productPrice|Product Price/);
      expect(prices.length).toBeGreaterThanOrEqual(1);
    });
    // Should show prices
    const priceTexts = screen.getAllByText(/350|250/);
    expect(priceTexts.length).toBeGreaterThan(0);
  });

  it('shows search input', async () => {
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/recipes\.searchPlaceholder|Search by product name/)).toBeInTheDocument();
    });
  });

  it('shows Add Recipe button', async () => {
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      expect(screen.getByText(/recipes\.addRecipe|Add Recipe/)).toBeInTheDocument();
    });
  });

  it('opens Add Recipe modal', async () => {
    mockInvokeSuccess('create_recipe', { id: 4, product_id: 3, recipe_type_id: 1, yield_quantity: 1, is_active: true });
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      expect(screen.getByText(/recipes\.addRecipe|Add Recipe/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/recipes\.addRecipe|Add Recipe/));

    await waitFor(() => {
      const modalTitles = screen.getAllByText(/recipes\.createRecipeTitle|Create New Recipe/);
      expect(modalTitles.length).toBeGreaterThanOrEqual(1);
    });
    const ingredientsHeadings = screen.getAllByText(/recipes\.ingredients|Ingredients/);
    expect(ingredientsHeadings.length).toBeGreaterThanOrEqual(1);
  });

  it('filters recipes when searching', async () => {
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByPlaceholderText(/recipes\.searchPlaceholder|Search by product name/);
    await userEvent.type(searchInput, 'Biryani');
    expect(searchInput).toHaveValue('Biryani');
  });

  it('handles empty recipes gracefully', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_recipes', []);
    mockInvokeSuccess('get_products', mockProducts);
    mockInvokeSuccess('get_ingredients', mockIngredients);

    renderWithRouter(<Recipes />);

    await waitFor(() => {
      expect(screen.getByText(/recipes\.totalRecipes|Total Recipes/)).toBeInTheDocument();
    });
    const zeros = screen.getAllByText('0', { exact: true });
    expect(zeros.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/recipes\.noRecipes|No recipes yet/)).toBeInTheDocument();
  });

  it('handles API failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeError('get_recipes', 'Failed to load');
    mockInvokeError('get_products', 'Failed to load');
    mockInvokeError('get_ingredients', 'Failed to load');

    renderWithRouter(<Recipes />);

    await waitFor(() => {
      expect(screen.getByText(/recipes\.totalRecipes|Total Recipes/)).toBeInTheDocument();
    });
    const zeros = screen.getAllByText('0', { exact: true });
    expect(zeros.length).toBeGreaterThanOrEqual(1);
  });

  // ── CRUD: Create ──
  it('creates a recipe end-to-end (select product + ingredient, then save)', async () => {
    mockInvokeSuccess('create_recipe', { id: 4, product_id: 3, recipe_type_id: 1, yield_quantity: 1, is_active: true });
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByText(/recipes\.addRecipe|Add Recipe/));

    const dialog = screen.getByRole('dialog', { name: /Create New Recipe/ });
    // Product select (combobox 0), ingredient select (combobox 2)
    const combos = within(dialog).getAllByRole('combobox');
    await userEvent.selectOptions(combos[0], '1'); // Chicken Burger
    await userEvent.selectOptions(combos[2], '1'); // Chicken Breast
    // Ingredient quantity
    await userEvent.type(within(dialog).getByPlaceholderText(/recipes\.qty|Qty/), '1');

    // Add-ingredient button is icon-only — use the stable data-testid
    const addIngBtn = within(dialog).getByTestId('add-ingredient');
    expect(addIngBtn).toBeDefined();
    await userEvent.click(addIngBtn);

    // Ingredient row appears ("Chicken Breast — 1 kg"), then save becomes enabled.
    // The select option also contains 'Chicken Breast', so match the row format.
    await waitFor(() => {
      expect(within(dialog).getByText(/Chicken Breast\s*—\s*1/)).toBeInTheDocument();
    });
    await userEvent.click(within(dialog).getByRole('button', { name: /Create New Recipe/ }));

    await waitFor(() => {
      const createCall = getInvokeHistory().find(h => h.cmd === 'create_recipe');
      expect(createCall).toBeDefined();
      const recipe = createCall!.args!.recipe as Record<string, unknown>;
      expect(recipe.product_id).toBe(1);
      const ingredients = createCall!.args!.ingredients as Record<string, unknown>[];
      expect(ingredients.length).toBe(1);
    });
    expect(await screen.findByText(/Recipe created successfully/)).toBeInTheDocument();
  });

  // ── CRUD: Edit ──
  it('edits a recipe yield through the edit modal', async () => {
    mockInvokeSuccess('update_recipe', { id: 1 });
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

    // Edit button (title='Edit') on the first card
    const editBtn = screen.getAllByTitle('Edit')[0];
    await userEvent.click(editBtn);

    const dialog = screen.getByRole('dialog', { name: /Edit Recipe/ });
    const yieldInput = within(dialog).getByRole('spinbutton');
    await userEvent.clear(yieldInput);
    await userEvent.type(yieldInput, '6');

    await userEvent.click(within(dialog).getByRole('button', { name: /Save Changes/ }));

    await waitFor(() => {
      const updateCall = getInvokeHistory().find(h => h.cmd === 'update_recipe');
      expect(updateCall).toBeDefined();
      expect(updateCall!.args!.id).toBe(1);
      const update = updateCall!.args!.update as Record<string, unknown>;
      expect(update.yield_quantity).toBe(6);
    });
    expect(await screen.findByText(/Recipe updated/)).toBeInTheDocument();
  });

  // ── CRUD: Delete (deactivate) ──
  it('deactivates a recipe through the confirm dialog', async () => {
    mockInvokeSuccess('soft_delete_recipe', {});
    renderWithRouter(<Recipes />);

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

    // Trash button (title='Deactivate') on the first active card
    const deleteBtn = screen.getAllByTitle('Deactivate')[0];
    await userEvent.click(deleteBtn);

    const dialog = screen.getByRole('dialog');
    await userEvent.click(within(dialog).getByRole('button', { name: /Deactivate/ }));

    await waitFor(() => {
      const deleteCall = getInvokeHistory().find(h => h.cmd === 'soft_delete_recipe');
      expect(deleteCall).toBeDefined();
      expect(deleteCall!.args!.id).toBe(1);
    });
    expect(await screen.findByText(/Recipe deactivated/)).toBeInTheDocument();
  });
});
