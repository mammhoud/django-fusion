import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import { getInvokeHistory, clearInvokeHistory } from '../setup';
import KitchenDisplay from '../../pages/kitchen/KitchenDisplay';

// priority: 1=dine-in, 2=takeaway, 3=delivery — required so the KDS
// preferred-priorities filter (default [1,2,3]) keeps these tickets visible.
const mockTickets = [
  { id: 1, sale_id: 100, priority: 1, status: 'pending', notes: 'No onions',      created_at: '2026-01-15T10:00:00' },
  { id: 2, sale_id: 101, priority: 1, status: 'pending', notes: 'Extra spicy',    created_at: '2026-01-15T10:05:00' },
  { id: 3, sale_id: 102, priority: 1, status: 'pending', notes: '',              created_at: '2026-01-15T10:10:00' },
];

// Product-category rows returned by get_kitchen_ticket_categories.
// ticket 1 → Burgers (id 1), ticket 2 → Sides (id 2), ticket 3 → Burgers.
const mockCategoryRows = [
  { ticket_id: 1, category_id: 1, name: 'Burgers', color: '#ff9900' },
  { ticket_id: 3, category_id: 1, name: 'Burgers', color: '#ff9900' },
  { ticket_id: 2, category_id: 2, name: 'Sides', color: '#22c55e' },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  clearInvokeHistory();
  // The priority-preferences test writes kds-preferred-priorities — reset so
  // later tests in this file always start from the default [1,2,3].
  localStorage.removeItem('kds-preferred-priorities');
  mockInvokeSuccess('get_kitchen_tickets', mockTickets);
  mockInvokeSuccess('get_kitchen_ticket_categories', mockCategoryRows);
});

describe('KitchenDisplay page', () => {
  it('hydrates tickets for the default pending status', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      // sale_id 100/101/102 → displayed as "#100" / "#101" / "#102"
      expect(screen.getAllByText(/#100|#101|#102/).length).toBeGreaterThanOrEqual(3);
    });
  });

  it('shows the debounced text search input + result counter', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getByLabelText(/kitchen\.searchPlaceholder|Search by ticket/)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText('3 / 3')).toBeInTheDocument();
    });
  });

  it('filters by sale_id after the idle debounce window', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/#101/).length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByLabelText(/kitchen\.searchPlaceholder|Search by ticket/);
    await userEvent.type(searchInput, '101');

    await waitFor(
      () => {
        expect(screen.getAllByText(/#101/).length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText(/#100/)).not.toBeInTheDocument();
        expect(screen.queryByText(/#102/)).not.toBeInTheDocument();
        expect(screen.getByText('1 / 3')).toBeInTheDocument();
      },
      { timeout: 800 },
    );
  });

  it('filters by notes substring after the idle debounce window', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByLabelText(/kitchen\.searchPlaceholder|Search by ticket/);
    await userEvent.type(searchInput, 'spicy');

    await waitFor(
      () => {
        expect(screen.getAllByText(/#101/).length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText(/#100/)).not.toBeInTheDocument();
        expect(screen.queryByText(/#102/)).not.toBeInTheDocument();
      },
      { timeout: 800 },
    );
  });

  it('renders product-category pills and filters tickets by category', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getByTestId('kds-category-filter-all')).toBeInTheDocument();
      expect(screen.getByTestId('kds-category-filter-1')).toHaveTextContent('Burgers');
      expect(screen.getByTestId('kds-category-filter-2')).toHaveTextContent('Sides');
    });

    // Burgers appears on tickets 1 and 3 → clicking it hides ticket 2
    await userEvent.click(screen.getByTestId('kds-category-filter-1'));

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/#102/).length).toBeGreaterThanOrEqual(1);
      expect(screen.queryByText(/#101/)).not.toBeInTheDocument();
      expect(screen.getByTestId('kds-category-filter-1')).toHaveAttribute('aria-pressed', 'true');
    });

    // Toggle-to-reset: clicking the active pill again restores all tickets
    await userEvent.click(screen.getByTestId('kds-category-filter-1'));
    await waitFor(() => {
      expect(screen.getAllByText(/#101/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByTestId('kds-category-filter-all')).toHaveAttribute('aria-pressed', 'true');
    });
  });

  it('status filter pills propagate the chosen status to backend invoke', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
    });

    // Switch to "all" tickets status. Default mock returns the same 3 tickets regardless.
    await userEvent.click(screen.getByTestId('kds-status-filter-all'));

    await waitFor(() => {
      // Backend is invoked again with status=null (since filter==='all' -> null).
      const allCall = getInvokeHistory().find(h => h.cmd === 'get_kitchen_tickets' && h.args?.status === null);
      expect(allCall).toBeDefined();
      // And the pill reflects the active selection via aria-pressed.
      const allPill = screen.getByTestId('kds-status-filter-all');
      expect(allPill).toHaveAttribute('aria-pressed', 'true');
    });
  });

  it('shows the no-tickets empty state when the list is empty', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_kitchen_tickets', []);
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getByText(/kitchen\.noTickets|No kitchen tickets/)).toBeInTheDocument();
    });
  });

  // ── Order-type priority preference filters ──
  it('filters tickets by order-type priority when a preference is unchecked', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
    });

    // Open the preferences panel
    await userEvent.click(screen.getByTitle('Display preferences'));

    // All 3 mock tickets are priority 1 (Dine-in). Uncheck Dine-in → all hidden.
    const dineInCheckbox = screen.getByRole('checkbox', { name: /Dine-in \/ Extra/ });
    expect(dineInCheckbox).toBeChecked();
    await userEvent.click(dineInCheckbox);

    await waitFor(() => {
      expect(screen.queryByText(/#100/)).not.toBeInTheDocument();
      expect(screen.queryByText(/#101/)).not.toBeInTheDocument();
      expect(screen.queryByText(/#102/)).not.toBeInTheDocument();
      // With zero filtered tickets the counter is hidden and the empty state shows
      expect(screen.getByText(/kitchen\.noTickets|No kitchen tickets/)).toBeInTheDocument();
    });

    // Re-check Dine-in → tickets come back
    await userEvent.click(screen.getByRole('checkbox', { name: /Dine-in \/ Extra/ }));
    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
    });
  });

  // ── Status filter propagates a specific status to the backend ──
  it('propagates a specific status (preparing) to get_kitchen_tickets', async () => {
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getByTestId('kds-status-filter-preparing'));

    await waitFor(() => {
      const call = getInvokeHistory().find(
        h => h.cmd === 'get_kitchen_tickets' && h.args?.status === 'preparing',
      );
      expect(call).toBeDefined();
      const pill = screen.getByTestId('kds-status-filter-preparing');
      expect(pill).toHaveAttribute('aria-pressed', 'true');
    });
  });

  // ── Per-product accent colors on sale-item rows in the detail modal ──
  it('renders sale items with a unique per-product accent color', async () => {
    const saleItems = [
      { id: 1, sale_id: 100, product_name: 'Chicken Burger', price: 350, quantity: 2, unit: 'piece', subtotal: 700, created_at: '2026-01-15T10:00:00' },
      { id: 2, sale_id: 100, product_name: 'French Fries', price: 150, quantity: 1, unit: 'plate', subtotal: 150, created_at: '2026-01-15T10:00:00' },
    ];
    mockInvokeSuccess('get_sale_items_by_sale_id', saleItems);
    mockInvokeSuccess('get_sale_by_id', { order_type: 'dine-in', total_amount: 25 });
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getAllByText(/#100/)[0]);

    await waitFor(() => {
      expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
      expect(screen.getByText('French Fries')).toBeInTheDocument();
    });

    // Each item row carries a left accent border derived from its product name.
    // The styled row is the outer div (with inline style) wrapping the item.
    const burgerRow = screen.getByText('Chicken Burger').closest('div[style]') as HTMLElement | null;
    const friesRow = screen.getByText('French Fries').closest('div[style]') as HTMLElement | null;
    expect(burgerRow).not.toBeNull();
    expect(friesRow).not.toBeNull();
    expect(burgerRow!.style.borderLeft).toContain('solid');
    expect(friesRow!.style.borderLeft).toContain('solid');
    // Distinct products get distinct accent colors.
    expect(burgerRow!.style.borderLeft).not.toBe(friesRow!.style.borderLeft);
  });

  it('renders sale-item rows without accent rails when unique card colors are disabled', async () => {
    const saleItems = [
      { id: 1, sale_id: 100, product_name: 'Chicken Burger', price: 350, quantity: 2, unit: 'piece', subtotal: 700, created_at: '2026-01-15T10:00:00' },
    ];
    mockInvokeSuccess('get_settings', { unique_card_colors: false });
    mockInvokeSuccess('get_sale_items_by_sale_id', saleItems);
    mockInvokeSuccess('get_sale_by_id', { order_type: 'dine-in', total_amount: 25 });
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getAllByText(/#100/)[0]);

    await waitFor(() => {
      expect(screen.getByText('Chicken Burger')).toBeInTheDocument();
    });

    // Accent styling disabled → the item row has no inline accent style.
    const burgerRow = screen.getByText('Chicken Burger').closest('div') as HTMLElement | null;
    expect(burgerRow).not.toBeNull();
    expect(burgerRow!.style.borderLeft).toBe('');
    expect(burgerRow!.style.backgroundColor).toBe('');
  });

  // ── Prep-steps checklist from selectable preparation notes ──
  it('renders prep steps from a selectable preparation note in the detail modal', async () => {
    const selectableNotes = [
      {
        id: 10,
        name: 'Burger Prep',
        template_body: '',
        category: 'preparation',
        is_default: false,
        use_as_template: false,
        selectable: true,
        steps: JSON.stringify([
          { title: 'Toast the bun', details: '2 min, golden brown' },
          { title: 'Grill the patty', details: 'Medium, 6 min' },
        ]),
      },
    ];
    mockInvokeSuccess('get_selectable_notes', selectableNotes);
    mockInvokeSuccess('get_sale_items_by_sale_id', []);
    mockInvokeSuccess('get_sale_by_id', { order_type: 'dine-in', total_amount: 25 });
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
    });

    // Open the ticket detail modal
    await userEvent.click(screen.getAllByText(/#100/)[0]);

    await waitFor(() => {
      expect(screen.getByText(/kitchen\.prepSteps|Prep Steps/)).toBeInTheDocument();
      expect(screen.getByText(/Toast the bun/)).toBeInTheDocument();
      expect(screen.getByText(/Grill the patty/)).toBeInTheDocument();
    });

    // Check off the first step — progress counter updates
    expect(screen.getByText('0/2 done')).toBeInTheDocument();
    await userEvent.click(screen.getByText(/Toast the bun/));
    await waitFor(() => {
      expect(screen.getByText('1/2 done')).toBeInTheDocument();
    });
  });

  // This test opens the detail modal, mounts the add-note form, types and saves
  // — under full-suite CPU contention it can exceed vitest's default 5000ms
  // per-test timeout (fails at ~5.2s under parallel-file load, ~1.4s alone).
  it('quick-adds a new selectable note and attaches it to the ticket', { timeout: 15000 }, async () => {
    mockInvokeSuccess('get_selectable_notes', []);
    mockInvokeSuccess('get_sale_items_by_sale_id', []);
    mockInvokeSuccess('get_sale_by_id', { order_type: 'dine-in', total_amount: 25 });
    mockInvokeSuccess('add_note', {
      id: 42,
      name: 'Grill Tips',
      template_body: 'Preheat grill to high',
      category: 'preparation',
      is_default: false,
      use_as_template: false,
      selectable: true,
      steps: null,
    });
    renderWithRouter(<KitchenDisplay />);

    await waitFor(() => {
      expect(screen.getAllByText(/#100/).length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.click(screen.getAllByText(/#100/)[0]);

    await waitFor(
      () => {
        expect(screen.getByText(/kitchen\.quickNotes|Quick Notes/)).toBeInTheDocument();
      },
      { timeout: 3000 },
    );    // Open the add-note form and create a note. The form mounts behind the
    // AnimatePresence exit window, so wait for its fields before typing
    // (full-suite CPU contention otherwise races the placeholder query).
    await userEvent.click(screen.getByRole('button', { name: /kitchen\.addNote|Add note/ }));
    await waitFor(
      () => {
        expect(screen.getAllByPlaceholderText(/notes\.name|Template Name/).length).toBeGreaterThanOrEqual(1);
      },
      { timeout: 3000 },
    );
    await userEvent.type(screen.getAllByPlaceholderText(/notes\.name|Template Name/)[0], 'Grill Tips');
    await userEvent.type(screen.getAllByPlaceholderText(/orderNotesPlaceholder|Special instructions/)[0], 'Preheat grill to high');
    await userEvent.click(screen.getByRole('button', { name: /common\.save|Save/ }));

    await waitFor(() => {
      const addCall = getInvokeHistory().find(h => h.cmd === 'add_note');
      expect(addCall).toBeDefined();
      const tpl = addCall!.args!.template as Record<string, unknown>;
      expect(tpl.selectable).toBe(true);
      expect(tpl.category).toBe('preparation');
      // The new note is attached to the ticket via update_kitchen_ticket
      const attachCall = getInvokeHistory().find(h => h.cmd === 'update_kitchen_ticket');
      expect(attachCall).toBeDefined();
      const update = attachCall!.args!.update as Record<string, unknown>;
      expect(String(update.notes)).toContain('Grill Tips');
    });
  });
});
