/** RTK Query endpoints — Reports, Analytics, Cashback. */
import { api } from '../baseApi';

export interface SalesReport {
  report_type: string; date_from: string; date_to: string;
  summary: { total_orders: number; total_revenue: number; total_cashback: number; average_order: number; };
}

export interface InventoryCountReport {
  report_type: string; inventory_id: string;
  total_products: number; low_stock_count: number;
  data: { product_id: number; name: string; current_stock: number; is_low_stock: boolean; }[];
}

export interface CashbackReport {
  report_type: string; date_from: string; date_to: string;
  summary: { total_cashback: number; cashback_transactions: number; average_cashback: number; };
  top_cashback_sales: { sale_id: number; total: number; cashback: number; }[];
}

export const analyticsApi = api.injectEndpoints({
  endpoints: (build) => ({
    getSalesReport: build.query<SalesReport, { date_from?: string; date_to?: string }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.date_from) p.set('date_from', params.date_from);
        if (params.date_to) p.set('date_to', params.date_to);
        return `/reports/sales?${p.toString()}`;
      },
      providesTags: ['Report'],
    }),

    getInventoryCount: build.query<InventoryCountReport, { inventory_id?: string; low_stock?: boolean }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.inventory_id) p.set('inventory_id', params.inventory_id);
        if (params.low_stock) p.set('low_stock', 'true');
        return `/reports/inventory/count?${p.toString()}`;
      },
      providesTags: ['Report'],
    }),

    getCashbackReport: build.query<CashbackReport, { date_from?: string; date_to?: string }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.date_from) p.set('date_from', params.date_from);
        if (params.date_to) p.set('date_to', params.date_to);
        return `/reports/sales/cashback?${p.toString()}`;
      },
      providesTags: ['Report'],
    }),
  }),
});

export const {
  useGetSalesReportQuery,
  useGetInventoryCountQuery,
  useGetCashbackReportQuery,
} = analyticsApi;
