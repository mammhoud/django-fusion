/** RTK Query endpoints — Inventory Transactions & Inventory Count. */
import { api, PaginatedResponse } from '../baseApi';

export interface InventoryTransaction {
  id: number; ingredient_id: number;
  transaction_type: 'in' | 'out' | 'adjustment' | 'return' | 'transfer_out' | 'transfer_in' | 'waste' | 'restock';
  quantity_change: number; reference_id?: number | null;
  note?: string | null; created_at: string;
}

export interface InventoryCountItem {
  product_id: number; name: string; sku: string;
  category: string; current_stock: number;
  low_stock_threshold: number; is_low_stock: boolean;
  inventory_ids: string[]; price: number;
}

export const inventoryApi = api.injectEndpoints({
  endpoints: (build) => ({
    getInventoryTransactions: build.query<PaginatedResponse<InventoryTransaction>, {
      page?: number; per_page?: number;
      inventory_id?: string; transaction_type?: string;
    }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.page) p.set('page', String(params.page));
        if (params.per_page) p.set('per_page', String(params.per_page));
        if (params.inventory_id) p.set('inventory_id', params.inventory_id);
        if (params.transaction_type) p.set('transaction_type', params.transaction_type);
        return `/inventory?${p.toString()}`;
      },
      providesTags: ['Inventory'],
    }),

    addInventoryTransaction: build.mutation<InventoryTransaction, Partial<InventoryTransaction>>({
      query: (body) => ({ url: '/inventory', method: 'POST', body }),
      invalidatesTags: ['Inventory'],
    }),

    getInventoryCount: build.query<{ report_type: string; inventory_id: string; total_products: number; low_stock_count: number; data: InventoryCountItem[] }, {
      inventory_id?: string; low_stock?: boolean; category_id?: number;
    }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.inventory_id) p.set('inventory_id', params.inventory_id);
        if (params.low_stock) p.set('low_stock', 'true');
        if (params.category_id) p.set('category_id', String(params.category_id));
        return `/reports/inventory/count?${p.toString()}`;
      },
      providesTags: ['Inventory'],
    }),

    transferInventory: build.mutation<any, {
      source_inventory: string; target_inventory: string;
      items: { product_id: number; quantity: number; notes?: string }[];
    }>({
      query: (body) => ({ url: '/reports/inventory/transfer', method: 'POST', body }),
      invalidatesTags: ['Inventory'],
    }),
  }),
});

export const {
  useGetInventoryTransactionsQuery,
  useAddInventoryTransactionMutation,
  useGetInventoryCountQuery,
  useTransferInventoryMutation,
} = inventoryApi;
