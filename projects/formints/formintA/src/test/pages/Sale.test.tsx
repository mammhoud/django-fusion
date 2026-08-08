import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, mockInvokeError, resetInvokeMocks } from '../mocks/tauri';
import Sale from '../../app/pages/pos/Sale';

const mockProducts = [
  { id: 1, name: 'Chicken Burger', price: 350, unit: 'piece', category_id: 1 },
  { id: 2, name: 'French Fries', price: 150, unit: 'plate', category_id: 2 },
  { id: 3, name: 'Beef Burger', price: 450, unit: 'piece', category_id: 1 },
];

const mockCategories = [
  { id: 1, name: 'Burgers', color: '#f97316' },
  { id: 2, name: 'Sides', color: '#10b981' },
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
  mockInvokeSuccess('get_delivery_zones', []);
  mockInvokeSuccess('get_employees', mockEmployees);
  mockInvokeSuccess('get_categories', mockCategories);
  mockInvokeSuccess('get_notes', []);
  mockInvokeSuccess('get_customers', [
    { id: 7, name: 'Sara Khalil', phone: '01001234567', email: 'sara@example.com', loyalty_points: 120, notes: null, created_at: '2026-01-01', updated_at: '2026-01-01' },
    { id: 8, name: 'Omar Haddad', phone: '01009876543', email: null, loyalty_points: 45, notes: null, created_at: '2026-01-01', updated_at: '2026-01-01' },
  ]);
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


  it('uses one uniform primary color for all product cards', async () => {
    resetInvokeMocks();
    // Every card (incl. category-less ones) shares the single theme-primary
    // color — no per-product accent colors.
    mockInvokeSuccess('get_products', [...mockProducts, { id: 9, name: 'Lemonade', price: 50, unit: 'glass' }]);
    mockInvokeSuccess('get_settings', mockSettings);
    mockInvokeSuccess('get_delivery_types', mockDeliveryTypes);
    mockInvokeSuccess('get_delivery_zones', []);
    mockInvokeSuccess('get_employees', mockEmployees);
    mockInvokeSuccess('get_categories', mockCategories);
    mockInvokeSuccess('get_notes', []);
    mockInvokeSuccess('check_auth_required', false);

    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getByText('Lemonade')).toBeInTheDocument();
    });

    const lemonadeCard = screen.getByText('Lemonade').closest('[class*="rounded-xl"]') as HTMLElement | null;
    const addBtn = lemonadeCard!.querySelector('button') as HTMLButtonElement | null;
    expect(addBtn).not.toBeNull();
    // Uniform mode → no per-product inline accent; the card uses the shared
    // theme-primary classes instead.
    expect(addBtn!.style.backgroundColor).toBe('');
    expect(addBtn!.className).toContain('bg-primary');
  });

  it('filters products by category via colored tag pills', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
    });

    // Category filter is now a row of colored tag pills — click the 'Sides' pill (id 2)
    const sidesPill = screen.getByTestId('sale-category-filter-2');
    expect(sidesPill).toHaveClass('tag');
    // Category color dot is rendered inside the pill
    // jsdom normalizes hex → rgb(), so assert the computed background color
    const colorDot = sidesPill.querySelector('span[style]');
    expect(colorDot).not.toBeNull();
    expect(colorDot).toHaveStyle({ backgroundColor: 'rgb(16, 185, 129)' }); // #10b981
    // Product-count badge renders inside the pill (1 product → category 2)
    const badge = sidesPill.querySelector('.badge');
    expect(badge).not.toBeNull();
    expect(badge!.textContent).toBe('1');
    await userEvent.click(sidesPill);

    await waitFor(() => {
      expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
      expect(screen.queryByText('Beef Burger')).not.toBeInTheDocument();
      expect(screen.getByText('French Fries')).toBeInTheDocument();
    });
  });

  it('shows the category color legend with per-category product counts', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
    });

    // The legend panel starts collapsed
    expect(screen.queryByTestId('sale-category-filter-legend')).not.toBeInTheDocument();

    // Pills carry a native tooltip with the product count
    const burgersPill = screen.getByTestId('sale-category-filter-1');
    expect(burgersPill).toHaveAttribute('title', expect.stringContaining('Burgers'));
    const sidesPill = screen.getByTestId('sale-category-filter-2');
    expect(sidesPill).toHaveAttribute('title', expect.stringContaining('Sides'));

    // Open the legend via the palette toggle
    await userEvent.click(screen.getByTestId('sale-category-filter-legend-toggle'));

    const legend = screen.getByTestId('sale-category-filter-legend');
    expect(legend).toBeInTheDocument();

    // Legend rows list each category with its color swatch, name, and count
    const rows = legend.querySelectorAll('li');
    expect(rows.length).toBe(2);
    // Burgers (id 1) → Chicken Burger + Beef Burger = 2 ; Sides (id 2) → French Fries = 1
    expect(rows[0].textContent).toContain('Burgers');
    expect(rows[0].textContent).toContain('2');
    expect(rows[1].textContent).toContain('Sides');
    expect(rows[1].textContent).toContain('1');
  });

  it('resets category filter to show all products', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
    });

    // Click the 'Sides' pill (id 2), then the 'All categories' pill to reset
    await userEvent.click(screen.getByTestId('sale-category-filter-2'));

    await waitFor(() => {
      expect(screen.queryByText('Chicken Burger')).not.toBeInTheDocument();
    });

    await userEvent.click(screen.getByTestId('sale-category-filter-all'));

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

    // The toast is surfaced via the shared status-toast hook; this environment
    // is slow (imports take 30s+), so give it a generous timeout to avoid
    // intermittent failures.
    await waitFor(
      () => {
        expect(screen.getByText(/Backend timed out/i)).toBeInTheDocument();
      },
      { timeout: 8000 },
    );
  });

  // ── Cart operations ──
  it('increments and decrements cart quantity with the +/- controls', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

    await clickAddToCart('Chicken Burger');

    // Cart line shows quantity 1 (appears in sidebar + mobile bar)
    await waitFor(() => {
      expect(screen.getAllByText(/Chicken Burger\s*×\s*1/).length).toBeGreaterThanOrEqual(1);
    });

    // Chicken Burger unit is 'piece' → +/- steps by 0.5 (only 'item' steps by 1)
    const increaseBtns = screen.getAllByLabelText(/sale\.increaseQuantity|Increase/);
    await userEvent.click(increaseBtns[0]);
    await waitFor(() => {
      expect(screen.getAllByText(/Chicken Burger\s*×\s*1\.5/).length).toBeGreaterThanOrEqual(1);
      // 1.5 × 350 = 525
      expect(screen.getAllByText(/525\.00/).length).toBeGreaterThanOrEqual(1);
    });

    // Decrease → back to 1
    await userEvent.click(screen.getAllByLabelText(/sale\.decreaseQuantity|Decrease/)[0]);
    await waitFor(() => {
      expect(screen.getAllByText(/Chicken Burger\s*×\s*1/).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('removes an item from the cart when quantity drops below the minimum', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

    await clickAddToCart('Chicken Burger');

    await waitFor(() => {
      expect(screen.getAllByText(/Chicken Burger\s*×\s*1/).length).toBeGreaterThanOrEqual(1);
    });

    // 'piece' steps by 0.5: 1 → 0.5 → 0 (below min 0.5) → item removed
    const decreaseBtns = screen.getAllByLabelText(/sale\.decreaseQuantity|Decrease/);
    await userEvent.click(decreaseBtns[0]);
    await waitFor(() => {
      expect(screen.getAllByText(/Chicken Burger\s*×\s*0\.5/).length).toBeGreaterThanOrEqual(1);
    });
    await userEvent.click(screen.getAllByLabelText(/sale\.decreaseQuantity|Decrease/)[0]);

    await waitFor(() => {
      // Cart line gone + +/- controls gone (add button is back)
      expect(screen.queryAllByText(/Chicken Burger\s*×/).length).toBe(0);
      expect(screen.queryAllByLabelText(/sale\.increaseQuantity/).length).toBe(0);
    });
  });

  // ── Checkout wizard ──
  async function openCheckoutWizard() {
    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });
    await clickAddToCart('Chicken Burger');
    await waitFor(() => {
      expect(screen.getAllByText(/sale\.cartSummary|Cart Summary/).length).toBeGreaterThanOrEqual(1);
    });
    // The Preview button opens the checkout wizard
    const previewButtons = screen.getAllByText(/sale\.previewOrder|Preview/);
    await userEvent.click(previewButtons[0]);
    await waitFor(() => {
      expect(screen.getAllByPlaceholderText(/sale\.wizardSearchCustomer|Search customers/).length).toBeGreaterThanOrEqual(1);
    });
  }

  it('wizard: navigates through the 3 steps and shows offers + review sections', async () => {
    renderWithRouter(<Sale />);
    await openCheckoutWizard();

    // Step 2 — Offers & Payment
    const continueButtons = screen.getAllByText(/sale\.wizardOffers|Offers & Payment/);
    expect(continueButtons.length).toBeGreaterThanOrEqual(1);
    await userEvent.click(screen.getAllByText(/common\.continue|Continue/)[0]);
    await waitFor(() => {
      expect(screen.getAllByText(/sale\.specialOffer|Special offer/).length).toBeGreaterThanOrEqual(1);
    });

    // Step 3 — Review
    await userEvent.click(screen.getAllByText(/common\.continue|Continue/)[0]);
    await waitFor(() => {
      expect(screen.getAllByText(/sale\.wizardReview|Review/).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('wizard: selects an existing customer from the searchable list', async () => {
    renderWithRouter(<Sale />);
    await openCheckoutWizard();

    const search = screen.getByPlaceholderText(/sale\.wizardSearchCustomer|Search customers/);
    await userEvent.type(search, 'Sara');
    await waitFor(() => {
      expect(screen.getAllByText('Sara Khalil').length).toBeGreaterThanOrEqual(1);
    });
    await userEvent.click(screen.getAllByText('Sara Khalil')[0]);
    await waitFor(() => {
      expect(screen.getAllByText(/120/).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('wizard: quick-adds a new customer and keeps the sale flow intact', async () => {
    const created = { id: 99, name: 'Nadia Fawzy', phone: '01005556677', email: null, loyalty_points: 0, notes: null, created_at: '2026-01-01', updated_at: '2026-01-01' };
    mockInvokeSuccess('add_customer', created);
    renderWithRouter(<Sale />);
    await openCheckoutWizard();

    const nameInput = screen.getByPlaceholderText(/sale\.wizardCustomerName|Full name/);
    await userEvent.type(nameInput, 'Nadia Fawzy');
    await userEvent.click(screen.getAllByText(/sale\.wizardAddCustomer|Add customer/)[0]);

    await waitFor(() => {
      expect(screen.getAllByText('Nadia Fawzy').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('wizard: applying a special offer reduces the grand total (clamped)', async () => {
    renderWithRouter(<Sale />);
    await openCheckoutWizard();

    // Advance to step 2
    await userEvent.click(screen.getAllByText(/common\.continue|Continue/)[0]);
    await waitFor(() => {
      expect(screen.getAllByText(/sale\.specialOffer|Special offer/).length).toBeGreaterThanOrEqual(1);
    });

    // Chicken Burger = 350.00; apply a special offer of 100 → total 250.00
    const offerInputs = screen.getAllByPlaceholderText(/0\.00 USD|0.00 USD/);
    await userEvent.type(offerInputs[0], '100');
    await waitFor(() => {
      expect(screen.getAllByText(/250\.00/).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('tracks the cart total as items are added and quantity changes', async () => {
    renderWithRouter(<Sale />);

    await waitFor(() => {
      expect(screen.getAllByText('Chicken Burger').length).toBeGreaterThanOrEqual(1);
    });

    // Add two different products: 350 + 150 = 500
    await clickAddToCart('Chicken Burger');
    await clickAddToCart('French Fries');

    await waitFor(() => {
      expect(screen.getAllByText(/500\.00/).length).toBeGreaterThanOrEqual(1);
    });

    // Remove the fries (decrease twice for 'plate' unit) → back to 350
    const decreaseBtns = screen.getAllByLabelText(/sale\.decreaseQuantity|Decrease/);
    // Fries card control — second occurrence (fries render after the burger)
    await userEvent.click(decreaseBtns[decreaseBtns.length - 1]);
    await userEvent.click(screen.getAllByLabelText(/sale\.decreaseQuantity|Decrease/)[decreaseBtns.length - 1]);
    await waitFor(() => {
      expect(screen.getAllByText(/350\.00/).length).toBeGreaterThanOrEqual(1);
    });
  });
});
