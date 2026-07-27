import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks, mockInvokeError } from '../mocks/tauri';
import Analytics from '../../pages/Analytics';

const mockAnalyticsData = {
  daily_revenue: [
    { date: '2026-01-01', revenue: 1500, orders: 12 },
    { date: '2026-01-02', revenue: 1800, orders: 15 },
    { date: '2026-01-03', revenue: 1200, orders: 10 },
  ],
  top_products: [
    { name: 'Chicken Burger', sales: 45, revenue: 15750 },
    { name: 'Biryani', sales: 30, revenue: 7500 },
  ],
  product_distribution: [
    { name: 'Burgers', value: 40 },
    { name: 'Biryani', value: 30 },
    { name: 'Drinks', value: 20 },
    { name: 'Sides', value: 10 },
  ],
  summary: {
    total_orders: 37,
    total_revenue: 4500,
    average_order_value: 121.62,
  },
};

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

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_analytics', mockAnalyticsData);
  mockInvokeSuccess('get_settings', mockSettings);
});

describe('Analytics Page', () => {
  it('renders the analytics title', async () => {
    renderWithRouter(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/analytics\.title|Analytics Dashboard/)).toBeInTheDocument();
    });
  });

  it('renders summary cards with data', async () => {
    renderWithRouter(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/analytics\.totalRevenue|Total Revenue/)).toBeInTheDocument();
      expect(screen.getByText(/analytics\.growthRate|Growth Rate/)).toBeInTheDocument();
      expect(screen.getByText(/analytics\.totalOrders|Total Orders/)).toBeInTheDocument();
      expect(screen.getByText(/analytics\.avgOrderValue|Avg\. Order Value/)).toBeInTheDocument();
    });
  });

  it('displays revenue amount from summary data', async () => {
    renderWithRouter(<Analytics />);

    await waitFor(() => {
      // Check that the revenue is displayed (4500)
      const revenueElements = screen.getAllByText(/4500\.00/);
      expect(revenueElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('displays total orders count', async () => {
    renderWithRouter(<Analytics />);

    await waitFor(() => {
      const orderElements = screen.getAllByText('37');
      expect(orderElements.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders revenue trend chart section', async () => {
    renderWithRouter(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/analytics\.revenueTrend|Revenue Trend/)).toBeInTheDocument();
    });
  });

  it('renders top products chart section', async () => {
    renderWithRouter(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/analytics\.topProducts|Top Products/)).toBeInTheDocument();
    });
  });

  it('renders product distribution chart section', async () => {
    renderWithRouter(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/analytics\.productDistribution|Product Distribution/)).toBeInTheDocument();
    });
  });

  it('renders daily orders chart section', async () => {
    renderWithRouter(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/analytics\.dailyOrders|Daily Orders Trend/)).toBeInTheDocument();
    });
  });

  it('shows empty state when no data exists', async () => {
    const emptyData = {
      daily_revenue: [],
      top_products: [],
      product_distribution: [],
      summary: { total_orders: 0, total_revenue: 0, average_order_value: 0 },
    };
    resetInvokeMocks();
    mockInvokeSuccess('get_analytics', emptyData);
    mockInvokeSuccess('get_settings', mockSettings);

    renderWithRouter(<Analytics />);

    await waitFor(() => {
      const emptyTexts = screen.getAllByText(/analytics\.noData|No data available yet/);
      expect(emptyTexts.length).toBeGreaterThanOrEqual(1);
    });
  });

  it('handles API failure gracefully', async () => {
    resetInvokeMocks();
    mockInvokeError('get_analytics', 'Network error');
    mockInvokeSuccess('get_settings', mockSettings);

    renderWithRouter(<Analytics />);

    await waitFor(() => {
      // Should still render the page title
      expect(screen.getByText(/analytics\.title|Analytics Dashboard/)).toBeInTheDocument();
    });
  });

  it('shows no-data hints when chart data is empty', async () => {
    const partialData = {
      daily_revenue: [],
      top_products: [],
      product_distribution: [],
      summary: { total_orders: 5, total_revenue: 1000, average_order_value: 200 },
    };
    resetInvokeMocks();
    mockInvokeSuccess('get_analytics', partialData);
    mockInvokeSuccess('get_settings', mockSettings);

    renderWithRouter(<Analytics />);

    await waitFor(() => {
      expect(screen.getByText(/analytics\.noRevenueData|No revenue data available/)).toBeInTheDocument();
      expect(screen.getByText(/analytics\.noProductData|No product sales data available/)).toBeInTheDocument();
    });
  });
});
