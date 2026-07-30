import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import ProductManager from '../../pages/inventory/ProductManager';

const mockProducts = [
  { id: 1, name: 'Chicken Burger', price: 350, unit: 'item',  category_id: 1, product_type: 'product' },
  { id: 2, name: 'French Fries',  price: 150, unit: 'plate', category_id: 2, product_type: 'product' },
  { id: 3, name: 'Beef Burger',   price: 450, unit: 'item',  category_id: 1, product_type: 'product' },
];

const mockCategories = [
  { id: 1, name: 'Burgers' },
  { id: 2, name: 'Sides' },
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

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_products', mockProducts);
  mockInvokeSuccess('get_categories', mockCategories);
  mockInvokeSuccess('get_settings', mockSettings);
});

describe('ProductManager page', () => {
  it('hydrates product grid from the backend', async () => {
    renderWithRouter(<ProductManager />);

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText('French Fries').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Beef Burger').length).toBeGreaterThanOrEqual(1);
  });

  it('debounces the search input — filter applies only after the idle window', async () => {
    renderWithRouter(<ProductManager />);

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

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

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

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

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

    const categorySelect = screen.getByTestId('pm-category-filter');
    await userEvent.selectOptions(categorySelect, '2');

    await waitFor(() => {
      expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
      expect(screen.getAllByText('French Fries').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('opens the add-product modal when the Add button is clicked', async () => {
    renderWithRouter(<ProductManager />);

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByTestId('pm-add-button'));

    await waitFor(() => {
      expect(screen.getByTestId('pm-modal')).toBeInTheDocument();
    });
  });
});
