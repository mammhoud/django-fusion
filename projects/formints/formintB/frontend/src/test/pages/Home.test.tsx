import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import Home from '../../app/pages/dashboard/Home';

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
  logo: 'data:image/png;base64,test',
  dine_in_tables: 10,
  delivery_fee: 5,
  delivery_fee_per_km: 2,
};

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_settings', mockSettings);
});

describe('Home Page', () => {
  it('renders the restaurant name from settings', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      const names = screen.getAllByText('Test Restaurant');
      expect(names.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders the dashboard subtitle', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      const subs = screen.getAllByText(/home\.dashboard|Dashboard/);
      expect(subs.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders the logo image', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      const images = screen.getAllByRole('img');
      expect(images.length).toBeGreaterThanOrEqual(1);
    });
  });
  // (logo test already uses getAllByRole, no change needed)

  it('renders all menu categories with headers', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      expect(screen.getAllByText(/nav\.categorySales|Sales & Operations/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/nav\.categoryProducts|Inventory & Products/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/nav\.categoryStaff|Staff & Customers/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/nav\.categoryReports|Reports & Analytics/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/nav\.categorySystem|Settings & System/).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders sale menu items', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      expect(screen.getAllByText(/nav\.newSale|New Sale/).length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText(/nav\.transactions|Transaction History/).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders product manager menu item', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      const items = screen.getAllByText(/nav\.productManager|Product Manager/);
      expect(items.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders settings menu item', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      const items = screen.getAllByText(/nav\.settings|Settings/);
      expect(items.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders navigation buttons that can be clicked', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      const items = screen.getAllByText(/nav\.newSale|New Sale/);
      expect(items.length).toBeGreaterThanOrEqual(1);
    });

    const saleButton = (await screen.findAllByText(/nav\.newSale|New Sale/))[0].closest('button');
    expect(saleButton).not.toBeNull();
  });

  it('renders menu descriptions', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      const descs = screen.getAllByText(/Employees, Schedule|Manager, Inventory|Orders, Transactions|Analytics & Tax/);
      expect(descs.length).toBeGreaterThan(0);
    });
  });
  // (description test already uses getAllByText, no change needed)

  it('shows loading spinner when navigating', async () => {
    renderWithRouter(<Home />);

    await waitFor(() => {
      const items = screen.getAllByText(/nav\.newSale|New Sale/);
      // Persistent sidebar renders the same text — the LAST match is the Home page button
      expect(items.length).toBeGreaterThanOrEqual(1);
    });

    const saleButtons = screen.getAllByText(/nav\.newSale|New Sale/);
    // Use the LAST element (skip persistent sidebar nav item)
    const saleButton = saleButtons[saleButtons.length - 1].closest('button');
    if (saleButton) {
      await userEvent.click(saleButton);
      // After click, loadingRoute state disables the button
      await waitFor(() => {
        const updatedButton = screen.getAllByText(/nav\.newSale|New Sale/).slice(-1)[0].closest('button');
        expect(updatedButton).toHaveAttribute('disabled');
      });
    }
  });

  it('renders without crashing when settings load fails', async () => {
    resetInvokeMocks();

    renderWithRouter(<Home />);

    await waitFor(() => {
      const cats = screen.getAllByText(/nav\.categorySales|Sales & Operations/);
      expect(cats.length).toBeGreaterThanOrEqual(1);
    });
  });
});
