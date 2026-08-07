import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderWithRouter, screen, waitFor, userEvent } from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import ProductsPage from '../../pages/pos/ProductsPage';

const mockSettings = {
  restaurant_name: 'Test',
  address: '',
  phone: '',
  currency: 'USD',
  receipt_footer: '',
};

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_products', []);
  mockInvokeSuccess('get_categories', []);
  mockInvokeSuccess('get_settings', mockSettings);
  mockInvokeSuccess('get_ingredients', []);
  mockInvokeSuccess('get_inventory_transactions', []);
  mockInvokeSuccess('get_inventory_adjustments', []);
  mockInvokeSuccess('get_recipes', []);
  mockInvokeSuccess('get_recipe_ingredients', []);
  mockInvokeSuccess('check_auth_required', false);
});

describe('ProductsPage', () => {
  it('renders the three product tabs', () => {
    renderWithRouter(<ProductsPage />);
    // Tab labels resolve through real en.json: nav.productManager='Product Manager', etc.
    expect(screen.getByRole('tab', { name: /Product Manager/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Inventory/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /Recipes/i })).toBeInTheDocument();
  });

  it('renders ProductManager by default', async () => {
    renderWithRouter(<ProductsPage />);
    await waitFor(() => {
      expect(screen.getByTestId('pm-search-input')).toBeInTheDocument();
    });
  });

  it('switches to the Inventory tab', async () => {
    renderWithRouter(<ProductsPage />);
    await userEvent.click(screen.getByRole('tab', { name: /Inventory/i }));
    await waitFor(() => {
      expect(screen.getByText(/inventory\.totalIngredients|Total Ingredients/)).toBeInTheDocument();
    });
  });

  it('switches to the Recipes tab', async () => {
    renderWithRouter(<ProductsPage />);
    await userEvent.click(screen.getByRole('tab', { name: /Recipes/i }));
    // The panel id is deterministic; 'Recipes' text appears both in the tab
    // and inside the page, so scope to the tabpanel element.
    await waitFor(() => {
      expect(screen.getByRole('tabpanel')).toHaveAttribute('id', 'products-panel-recipes');
    });
  });

  it('marks the active tab with aria-selected', async () => {
    renderWithRouter(<ProductsPage />);
    const managerTab = screen.getByRole('tab', { name: /Product Manager/i });
    expect(managerTab).toHaveAttribute('aria-selected', 'true');
    await userEvent.click(screen.getByRole('tab', { name: /Inventory/i }));
    expect(screen.getByRole('tab', { name: /Inventory/i })).toHaveAttribute('aria-selected', 'true');
    expect(managerTab).toHaveAttribute('aria-selected', 'false');
  });
});
