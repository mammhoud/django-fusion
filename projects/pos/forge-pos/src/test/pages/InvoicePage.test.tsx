import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks, mockInvokeError } from '../mocks/tauri';
import InvoicePage from '../../pages/InvoicePage';

const mockSettings = {
  restaurant_name: 'Test Restaurant',
  address: '123 Main St',
  phone: '+1234567890',
  email: 'test@restaurant.com',
  tax_rate: '10',
  currency: 'USD',
  opening_time: '09:00',
  closing_time: '22:00',
  receipt_footer: 'Thank you!',
  dine_in_tables: 10,
  delivery_fee: 5,
  delivery_fee_per_km: 2,
};

const mockCustomers = [
  { id: 1, name: 'John Doe', phone: '1234567890', email: 'john@example.com', loyalty_points: 100, notes: '', created_at: '2026-01-01T10:00:00Z', updated_at: '2026-01-01T10:00:00Z' },
  { id: 2, name: 'Jane Smith', phone: '0987654321', email: 'jane@example.com', loyalty_points: 50, notes: 'Regular customer', created_at: '2026-01-01T10:00:00Z', updated_at: '2026-01-01T10:00:00Z' },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_settings', mockSettings);
  mockInvokeSuccess('get_customers', mockCustomers);
});

describe('InvoicePage', () => {
  it('renders the invoice builder title', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getByText(/Invoice Builder/)).toBeInTheDocument();
    });
  });

  it('renders action buttons (Print, PDF, Preview)', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getByText('Print')).toBeInTheDocument();
      expect(screen.getByText(/PDF/)).toBeInTheDocument();
      expect(screen.getByText('Preview')).toBeInTheDocument();
    });
  });

  it('renders sidebar tabs', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      const invoiceTab = screen.getAllByText('invoice');
      expect(invoiceTab.length).toBeGreaterThanOrEqual(1);
      const itemsTab = screen.getAllByText('items');
      expect(itemsTab.length).toBeGreaterThanOrEqual(1);
      const customerTab = screen.getAllByText('customer');
      expect(customerTab.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows invoice type label', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getByText(/Invoice Type/)).toBeInTheDocument();
    });
  });

  it('shows page design options', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getAllByText(/Page Design/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText('Modern')).toBeInTheDocument();
      expect(screen.getByText('Classic')).toBeInTheDocument();
      expect(screen.getByText('Minimal')).toBeInTheDocument();
    });
  });

  it('shows invoice number field', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      const numberLabels = screen.getAllByText(/Invoice #/);
      expect(numberLabels.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows date field', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getAllByText('Date').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows due date field', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getByText(/Due Date/)).toBeInTheDocument();
    });
  });

  it('shows currency selector', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getByText(/Currency/)).toBeInTheDocument();
    });
  });

  it('shows tax rate field', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      const taxLabels = screen.getAllByText(/Tax Rate/);
      expect(taxLabels.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows notes field', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getAllByText('Notes').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows footer message field', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getByText(/Footer Message/)).toBeInTheDocument();
    });
  });

  it('switches to items tab', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      const itemsTabs = screen.getAllByText('items');
      expect(itemsTabs.length).toBeGreaterThanOrEqual(1);
    });

    const itemsTabs = screen.getAllByText('items');
    await userEvent.click(itemsTabs[0]);

    await waitFor(() => {
      const lineItems = screen.getAllByText(/Line Items/);
      expect(lineItems.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('switches to customer tab', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      const customerTabs = screen.getAllByText('customer');
      expect(customerTabs.length).toBeGreaterThanOrEqual(1);
    });

    const customerTabs = screen.getAllByText('customer');
    await userEvent.click(customerTabs[0]);

    await waitFor(() => {
      expect(screen.getByText(/Select Customer/)).toBeInTheDocument();
    });
  });

  it('shows customer dropdown in customer tab', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      const customerTabs = screen.getAllByText('customer');
      expect(customerTabs.length).toBeGreaterThanOrEqual(1);
    });

    const customerTabs = screen.getAllByText('customer');
    await userEvent.click(customerTabs[0]);

    await waitFor(() => {
      expect(screen.getByText(/manual entry/)).toBeInTheDocument();
    });
  });

  it('handles settings load failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeError('get_settings', 'Failed to load');
    mockInvokeSuccess('get_customers', mockCustomers);

    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getByText(/Invoice Builder/)).toBeInTheDocument();
    });
  });

  it('handles customers load failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_settings', mockSettings);
    mockInvokeError('get_customers', 'Failed to load');

    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getByText(/Invoice Builder/)).toBeInTheDocument();
    });
  });

  it('shows sidecar status badge', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      expect(screen.getByText(/sanic sidecar/i)).toBeInTheDocument();
    });
  });

  it('shows category section in invoice tab', async () => {
    renderWithRouter(<InvoicePage />);

    await waitFor(() => {
      const categoryLabels = screen.getAllByText(/Category/);
      expect(categoryLabels.length).toBeGreaterThanOrEqual(1);
    });
  });
});
