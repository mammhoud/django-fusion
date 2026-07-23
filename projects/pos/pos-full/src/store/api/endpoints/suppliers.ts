/** RTK Query endpoints — Suppliers, Purchase Orders. */
import { api, PaginatedResponse } from '../baseApi';

export interface Supplier {
  id: number; name: string; contact_name?: string | null;
  email?: string | null; phone?: string | null; address?: string | null;
  tax_id?: string | null; payment_terms?: string | null;
  is_active: boolean; created_at: string; updated_at: string;
}

export interface PurchaseOrder {
  id: number; supplier_id: number; supplier_name?: string;
  reference_number: string; status: 'draft' | 'ordered' | 'received' | 'cancelled';
  total_amount: number; expected_date: string | null;
  notes: string; created_at: string; updated_at: string;
}

export const suppliersApi = api.injectEndpoints({
  endpoints: (build) => ({
    getSuppliers: build.query<Supplier[], { include_inactive?: boolean }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.include_inactive) p.set('include_inactive', 'true');
        return `/suppliers?${p.toString()}`;
      },
      providesTags: (result) =>
        result ? [...result.map(({ id }) => ({ type: 'Supplier' as const, id })), { type: 'Supplier', id: 'LIST' }]
          : [{ type: 'Supplier', id: 'LIST' }],
    }),

    addSupplier: build.mutation<Supplier, Partial<Supplier>>({
      query: (body) => ({ url: '/suppliers', method: 'POST', body }),
      invalidatesTags: [{ type: 'Supplier', id: 'LIST' }],
    }),

    updateSupplier: build.mutation<Supplier, { id: number; data: Partial<Supplier> }>({
      query: ({ id, data }) => ({ url: `/suppliers/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Supplier', id }, { type: 'Supplier', id: 'LIST' }],
    }),

    deleteSupplier: build.mutation<void, number>({
      query: (id) => ({ url: `/suppliers/${id}`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'Supplier', id: 'LIST' }],
    }),

    getPurchaseOrders: build.query<PaginatedResponse<PurchaseOrder>, { page?: number; per_page?: number }>({
      query: ({ page = 1, per_page = 50 }) => `/purchase-orders?page=${page}&per_page=${per_page}`,
      providesTags: ['PurchaseOrder'],
    }),
  }),
});

export const {
  useGetSuppliersQuery,
  useAddSupplierMutation,
  useUpdateSupplierMutation,
  useDeleteSupplierMutation,
  useGetPurchaseOrdersQuery,
} = suppliersApi;
