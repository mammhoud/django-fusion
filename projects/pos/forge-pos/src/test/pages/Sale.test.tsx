import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import Sale from '../../pages/sales/Sale';

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
    // totalAmount appears in both mobile summary + sidebar — use getAllByText
    const totalAmounts = screen.getAllByText(/sale\.totalAmount|Total Amount/);
    expect(totalAmounts.length).toBeGreaterThanOrEqual(1);
  });

  it('renders order type selector with three options', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const dineIn = screen.getAllByText(/sale\.dineIn|Dine-in/);
      expect(dineIn.length).toBeGreaterThanOrEqual(1);
    });
    // takeaway and delivery appear in both mobile + desktop — use getAllByText
    const takeawayEls = screen.getAllByText(/sale\.takeaway|Takeaway/);
    expect(takeawayEls.length).toBeGreaterThanOrEqual(1);
    const deliveryEls = screen.getAllByText(/sale\.delivery|Delivery/);
    expect(deliveryEls.length).toBeGreaterThanOrEqual(1);
  });

  it('shows table selector when Dine-in is selected by default', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const tables = screen.getAllByText(/tableOption|Table/);
      expect(tables.length).toBeGreaterThanOrEqual(1);
    });
    // tableOption appears in both mobile + desktop selects — use getAllByDisplayValue
    const tableOptions = screen.getAllByDisplayValue(/sale\.tableOption|Table 1/);
    expect(tableOptions.length).toBeGreaterThanOrEqual(1);
  });

  it('switches to delivery and shows delivery fields', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const dineIn = screen.getAllByText(/sale\.dineIn|Dine-in/);
      expect(dineIn.length).toBeGreaterThanOrEqual(1);
    });

    // delivery appears in both mobile + desktop — click the mobile one (first)
    const deliveryEls = screen.getAllByText(/sale\.delivery|Delivery/);
    await userEvent.click(deliveryEls[0]);

    // deliveryType and deliveryAddress only appear when delivery is selected
    await waitFor(() => {
      const deliveryTypes = screen.getAllByText(/sale\.deliveryType|Delivery Type/);
      expect(deliveryTypes.length).toBeGreaterThanOrEqual(1);
    });
    const deliveryAddresses = screen.getAllByPlaceholderText(/sale\.deliveryAddress|Delivery address/);
    expect(deliveryAddresses.length).toBeGreaterThanOrEqual(1);
    // Delivery fee of 50.00 should appear somewhere
    const feeTexts = screen.getAllByText(/50.00/);
    expect(feeTexts.length).toBeGreaterThan(0);
  });

  it('renders employee assignment dropdown', async () => {
    renderWithRouter(<Sale />);

    // assignTo appears in both mobile + desktop — use getAllByText
    await waitFor(() => {
      const assignTos = screen.getAllByText(/sale\.assignTo|Assign to/);
      expect(assignTos.length).toBeGreaterThanOrEqual(1);
    });
    // Ali and Bilal appear in both mobile + desktop selects — use getAllByText
    const aliEls = screen.getAllByText('Ali');
    expect(aliEls.length).toBeGreaterThanOrEqual(1);
    const bilalEls = screen.getAllByText('Bilal');
    expect(bilalEls.length).toBeGreaterThanOrEqual(1);
    const noAssignmentEls = screen.getAllByText(/sale\.noAssignment|— No assignment —/);
    expect(noAssignmentEls.length).toBeGreaterThanOrEqual(1);
  });

  it('adds a product to cart when + button is clicked', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });

    await clickAddToCart('Chicken Burger');

    // cartSummary appears in both main content and sidebar — use getAllByText
    await waitFor(() => {
      const summaries = screen.getAllByText(/sale\.cartSummary|Cart Summary/);
      expect(summaries.length).toBeGreaterThanOrEqual(1);
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

    // cartSummary appears in both main content and sidebar — use getAllByText
    await waitFor(() => {
      const summaries = screen.getAllByText(/sale\.cartSummary|Cart Summary/);
      expect(summaries.length).toBeGreaterThanOrEqual(1);
    });

    // completeSale appears in desktop button + mobile sticky bar — click the first one
    const completeButtons = screen.getAllByText(/sale\.completeSale|Complete Sale/);
    await userEvent.click(completeButtons[0]);

    await waitFor(() => {
      const saleCompletes = screen.getAllByText(/sale\.saleComplete|Sale Complete/);
      expect(saleCompletes.length).toBeGreaterThanOrEqual(1);
    });
    const dineInTexts = screen.getAllByText(/sale\.dineIn|Dine-in/);
    expect(dineInTexts.length).toBeGreaterThanOrEqual(1);
    const startNewSaleBtns = screen.getAllByText(/sale\.startNewSale|Start New Sale/);
    expect(startNewSaleBtns.length).toBeGreaterThanOrEqual(1);
  });

  it('resets form after starting a new sale', async () => {
    mockInvokeSuccess('add_sale', { id: 1, total_amount: 350, currency: 'USD', date: '2026-01-01', time: '12:00', order_type: 'dine-in', status: 'completed' });
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });

    await clickAddToCart('Chicken Burger');

    // cartSummary appears in both main content and sidebar — use getAllByText
    await waitFor(() => {
      const summaries = screen.getAllByText(/sale\.cartSummary|Cart Summary/);
      expect(summaries.length).toBeGreaterThanOrEqual(1);
    });

    // completeSale appears in desktop button + mobile sticky bar — click the first one
    const completeButtons = screen.getAllByText(/sale\.completeSale|Complete Sale/);
    await userEvent.click(completeButtons[0]);

    await waitFor(() => {
      const saleCompletes = screen.getAllByText(/sale\.saleComplete|Sale Complete/);
      expect(saleCompletes.length).toBeGreaterThanOrEqual(1);
    });

    // startNewSale appears only in the success dialog — single element
    const startNewSaleBtns = screen.getAllByText(/sale\.startNewSale|Start New Sale/);
    await userEvent.click(startNewSaleBtns[0]);

    await waitFor(() => {
      expect(screen.queryByText(/sale\.saleComplete|Sale Complete/)).not.toBeInTheDocument();
      const summaries = screen.queryAllByText(/sale\.cartSummary|Cart Summary/);
      expect(summaries.length).toBe(0);
    });
  });

  it('disables Complete Sale button when cart is empty', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      const burgers = screen.getAllByText('Chicken Burger');
      expect(burgers.length).toBeGreaterThanOrEqual(1);
    });

    // completeSale appears in desktop button + mobile sticky bar — pick the first one
    const completeButtons = screen.getAllByText(/sale\.completeSale|Complete Sale/);
    const completeBtn = completeButtons[0].closest('button');
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

    const categorySelect = screen.getByLabelText(/sale\.categoryFilter|Filter by category/);
    await userEvent.selectOptions(categorySelect, '2');

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

    const categorySelect = screen.getByLabelText(/sale\.categoryFilter|Filter by category/);
    await userEvent.selectOptions(categorySelect, '2');

    await waitFor(() => {
      expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
    });

    await userEvent.selectOptions(categorySelect, 'all');

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
