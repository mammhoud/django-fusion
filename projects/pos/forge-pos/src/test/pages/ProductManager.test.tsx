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

const mockSettings = {
  restaurant_name: 'Test',
  address: '',
  phone: '',
  currency: 'USD',
  receipt_footer: '',
  dine_in_tables: 10,
  delivery_fee: 0,
  delivery_fee_per_km: 0,
};

// Hydration is async (products + categories + settings + AnimatePresence mode="wait"
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
  mockInvokeSuccess('get_settings', mockSettings);
});

describe('ProductManager page', () => {
  it('falls back to palette colors when unique card colors are disabled', async () => {
    mockInvokeSuccess('get_products', [...mockProducts, { id: 9, name: 'Lemonade', price: 50, unit: 'glass' }]);
    mockInvokeSuccess('get_settings', { ...mockSettings, unique_card_colors: false });
    renderWithRouter(<ProductManager />);

    await waitForHydration();

    // Lemonade has no category → with unique colors off it must NOT get an
    // inline accent color on its initial-letter span (rotating palette only).
    const lemonadeCard = screen.getByText('Lemonade').closest('[role="button"]') as HTMLElement | null;
    const initial = lemonadeCard?.querySelector('[data-testid="product-initial"]') as HTMLElement | null;
    expect(initial).not.toBeNull();
    expect(initial!.style.color).toBe('');
  });

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
