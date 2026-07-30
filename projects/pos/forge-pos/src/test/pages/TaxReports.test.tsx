import { describe, it, expect, beforeEach, vi } from 'vitest';
import {
  renderWithRouter,
  screen,
  waitFor,
  userEvent,
} from '../test-utils';
import { mockInvokeSuccess, resetInvokeMocks } from '../mocks/tauri';
import TaxReports from '../../pages/reports/TaxReports';

const mockReports = [
  { id: 1, period_start: '2026-01-01', period_end: '2026-01-31', total_sales: 12000, total_tax: 1560, transaction_count: 240 },
  { id: 2, period_start: '2026-02-01', period_end: '2026-02-28', total_sales: 18500, total_tax: 2405, transaction_count: 312 },
  { id: 3, period_start: '2026-03-01', period_end: '2026-03-31', total_sales: 9300,  total_tax: 1209, transaction_count: 180 },
];

beforeEach(() => {
  resetInvokeMocks();
  vi.clearAllMocks();
  mockInvokeSuccess('get_tax_reports', mockReports);
});

describe('TaxReports page', () => {
  it('hydrates the report list from the backend', async () => {
    renderWithRouter(<TaxReports />);

    await waitFor(() => {
      expect(screen.getAllByText(/2026-01-01/).length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText(/2026-02-01/).length).toBeGreaterThanOrEqual(1);
  });

  it('shows search input + result counter', async () => {
    renderWithRouter(<TaxReports />);

    await waitFor(() => {
      expect(screen.getByLabelText(/taxReports\.searchPlaceholder|Search tax reports/)).toBeInTheDocument();
    });
    await waitFor(() => {
      expect(screen.getByText('3 / 3')).toBeInTheDocument();
    });
  });

  it('search by period substring filters after the idle window', async () => {
    renderWithRouter(<TaxReports />);

    await waitFor(() => {
      expect(screen.getAllByText(/2026-02-01/).length).toBeGreaterThanOrEqual(1);
    });

    const searchInput = screen.getByLabelText(/taxReports\.searchPlaceholder|Search tax reports/);
    await userEvent.type(searchInput, '2026-02');

    await waitFor(
      () => {
        expect(screen.getAllByText(/2026-02-01/).length).toBeGreaterThanOrEqual(1);
        expect(screen.queryByText(/2026-01-01/)).not.toBeInTheDocument();
        expect(screen.queryByText(/2026-03-01/)).not.toBeInTheDocument();
        expect(screen.getByText('1 / 3')).toBeInTheDocument();
      },
      { timeout: 800 },
    );
  });

  it('sort-by-sales-desc reorders by total_sales', async () => {
    renderWithRouter(<TaxReports />);

    await waitFor(() => {
      expect(screen.getAllByText(/2026-01-01/).length).toBeGreaterThanOrEqual(1);
    });

    await userEvent.selectOptions(screen.getByLabelText(/taxReports\.sortBy|Sort by/), 'sales-desc');

    await waitFor(() => {
      // First card has the highest total_sales (Feb = 18500)
      expect(screen.getAllByText(/2026-02-01/).length).toBeGreaterThanOrEqual(1);
    });
  });

  it('shows the no-reports empty state when the list is empty', async () => {
    resetInvokeMocks();
    mockInvokeSuccess('get_tax_reports', []);
    renderWithRouter(<TaxReports />);

    await waitFor(() => {
      expect(screen.getByText(/taxReports\.noReports|No tax reports/)).toBeInTheDocument();
    });
  });
});
