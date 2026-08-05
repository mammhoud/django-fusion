import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import Sale from '../../pages/Sale';

const mockProducts = [
  { id: 1, name: 'Chicken Burger', price: 350, unit: 'piece', category_id: 1 },
  { id: 2, name: 'French Fries', price: 150, unit: 'plate', category_id: 2 },
  { id: 3, name: 'Beef Burger', price: 450, unit: 'piece', category_id: 1 },
];

const mockCategories = [
  { id: 1, name: 'Burgers' },
  { id: 2, name: 'Sides' },
];

const mockSettings = {
  restaurant_name: 'Test Restaurant',
  address: '123 Main St',
  phone: '03001234567',
  currency: 'USD',
  receipt_footer: 'Thank you!',
  dine_in_tables: 10,
  delivery_fee: 50,
  delivery_fee_per_km: 10,
};

const mockDeliveryTypes = [
  { id: 1, name: 'Standard', description: 'Normal delivery', fee_multiplier: 1.0, is_active: true },
  { id: 2, name: 'Express', description: 'Fast delivery', fee_multiplier: 1.5, is_active: true },
];

const mockEmployees = [
  { id: 1, name: 'Ali', phone: '03001111111', email: null, employee_type_id: 1, salary: 30000, is_active: true, joined_at: '2026-01-01' },
  { id: 2, name: 'Bilal', phone: '03002222222', email: null, employee_type_id: 2, salary: 25000, is_active: true, joined_at: '2026-01-15' },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_products', mockProducts);
  mockInvokeSuccess('get_settings', mockSettings);
  mockInvokeSuccess('get_delivery_types', mockDeliveryTypes);
  mockInvokeSuccess('get_employees', mockEmployees);
  mockInvokeSuccess('get_categories', mockCategories);
  mockInvokeSuccess('check_auth_required', false);
});

/** Helper: find the add-to-cart button inside a product card by product name */
async function clickAddToCart(productName: string) {
  const productEls = screen.getAllByText(productName);
  expect(productEls.length).toBeGreaterThanOrEqual(1);
  const card = productEls[0].closest('[class*="rounded-xl"]') || productEls[0];
  const addButton = card.querySelector('button');
  expect(addButton).toBeDefined();
  await userEvent.click(addButton!);
}

describe('Sale Page', () => {
  it('renders the page and loads products', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });
    const fries = screen.getAllByText('French Fries');
    expect(fries.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/sale\.totalAmount|Total Amount/)).toBeInTheDocument();
  });

  it('renders order type selector with three options', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const dineIn = screen.getAllByText(/sale\.dineIn|Dine-in/);
      expect(dineIn.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByText(/sale\.takeaway|Takeaway/)).toBeInTheDocument();
    expect(screen.getByText(/sale\.delivery|Delivery/)).toBeInTheDocument();
  });

  it('shows table selector when Dine-in is selected by default', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const tables = screen.getAllByText(/tableOption|Table/);
      expect(tables.length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getByDisplayValue(/sale\.tableOption|Table 1/)).toBeInTheDocument();
  });

  it('switches to delivery and shows delivery fields', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const dineIn = screen.getAllByText(/sale\.dineIn|Dine-in/);
      expect(dineIn.length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByText(/sale\.delivery|Delivery/));

    await waitFor(() => {
      expect(screen.getByText(/sale\.deliveryType|Delivery Type/)).toBeInTheDocument();
    });
    expect(screen.getByPlaceholderText(/sale\.deliveryAddress|Delivery address/)).toBeInTheDocument();
    // Delivery fee of 50.00 should appear somewhere
    const feeTexts = screen.getAllByText(/50.00/);
    expect(feeTexts.length).toBeGreaterThan(0);
  });

  it('renders employee assignment dropdown', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getByText(/sale\.assignTo|Assign to/)).toBeInTheDocument();
    });
    expect(screen.getByText('Ali')).toBeInTheDocument();
    expect(screen.getByText('Bilal')).toBeInTheDocument();
    expect(screen.getByText(/sale\.noAssignment|— No assignment —/)).toBeInTheDocument();
  });

  it('adds a product to cart when + button is clicked', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });

    await clickAddToCart('Chicken Burger');

    await waitFor(() => {
      expect(screen.getByText(/sale\.cartSummary|Cart Summary/)).toBeInTheDocument();
    });
  });

  it('completes a sale and shows success dialog', async () => {
    mockInvokeSuccess('add_sale', { id: 1, total_amount: 350, currency: 'USD', date: '2026-01-01', time: '12:00', order_type: 'dine-in', status: 'completed' });
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });

    await clickAddToCart('Chicken Burger');

    await waitFor(() => {
      expect(screen.getByText(/sale\.cartSummary|Cart Summary/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/sale\.completeSale|Complete Sale/));

    await waitFor(() => {
      expect(screen.getByText(/sale\.saleComplete|Sale Complete/)).toBeInTheDocument();
    });
    const dineInTexts = screen.getAllByText(/sale\.dineIn|Dine-in/);
    expect(dineInTexts.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/sale\.startNewSale|Start New Sale/)).toBeInTheDocument();
  });

  it('resets form after starting a new sale', async () => {
    mockInvokeSuccess('add_sale', { id: 1, total_amount: 350, currency: 'USD', date: '2026-01-01', time: '12:00', order_type: 'dine-in', status: 'completed' });
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });

    await clickAddToCart('Chicken Burger');

    await waitFor(() => {
      expect(screen.getByText(/sale\.cartSummary|Cart Summary/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/sale\.completeSale|Complete Sale/));

    await waitFor(() => {
      expect(screen.getByText(/sale\.saleComplete|Sale Complete/)).toBeInTheDocument();
    });

    await userEvent.click(screen.getByText(/sale\.startNewSale|Start New Sale/));

    await waitFor(() => {
      expect(screen.queryByText(/sale\.saleComplete|Sale Complete/)).not.toBeInTheDocument();
      expect(screen.queryByText(/sale\.cartSummary|Cart Summary/)).not.toBeInTheDocument();
    });
  });

  it('disables Complete Sale button when cart is empty', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });

    const completeBtn = screen.getByText(/sale\.completeSale|Complete Sale/).closest('button');
    expect(completeBtn).toBeDisabled();
  });

  it('filters products by search query', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText(/sale\.searchProducts|Search products/);
    await userEvent.type(searchInput, 'fries');

    await waitFor(() => {
      expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
      expect(screen.queryByText('Beef Burger')).not.toBeInTheDocument();
      expect(screen.getByText('French Fries')).toBeInTheDocument();
    });
  });

  it('filters products by category', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
    });

    // Click the "Sides" category tag pill
    const sidesTag = screen.getByRole('button', { name: 'Sides' });
    await userEvent.click(sidesTag);

    await waitFor(() => {
      expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
      expect(screen.queryByText('Beef Burger')).not.toBeInTheDocument();
      expect(screen.getByText('French Fries')).toBeInTheDocument();
    });
  });

  it('resets category filter to show all products', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
    });

    // Click "Sides" tag to filter
    const sidesTag = screen.getByRole('button', { name: 'Sides' });
    await userEvent.click(sidesTag);

    await waitFor(() => {
      expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
    });

    // Click "All" tag to reset
    const allTag = screen.getByRole('button', { name: /sale\.allCategories|All categories/ });
    await userEvent.click(allTag);

    await waitFor(() => {
      expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
      expect(screen.getByText('Beef Burger')).toBeInTheDocument();
      expect(screen.getByText('French Fries')).toBeInTheDocument();
    });
  });

  it('surfaces load errors via the status toast (one of the Promise.all invokes throws)', async () => {
    resetInvokeMocks();
    mockInvokeError('get_products', 'Backend timed out');
    mockInvokeSuccess('get_settings', mockSettings);
    mockInvokeSuccess('get_delivery_types', mockDeliveryTypes);
    mockInvokeSuccess('get_employees', mockEmployees);
    mockInvokeSuccess('get_categories', mockCategories);
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getByText(/Backend timed out/i)).toBeInTheDocument();
    });
  });
});
