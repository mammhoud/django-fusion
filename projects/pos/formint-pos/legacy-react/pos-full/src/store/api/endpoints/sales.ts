/**
 * RTK Query endpoints — Sales CRUD with pagination.
 * Replaces: useSaleStore (Zustand)
 */

import { api, PaginatedResponse } from '../baseApi';

export interface Sale {
  id: number; total_amount: number; currency: string; date: string; time: string;
  order_type: string; status: string; table_number: number | null;
  delivery_type_id: number | null; delivery_address: string | null;
  employee_id: number | null; customer_id: number | null;
  created_at: string; updated_at: string; uploaded: boolean;
}

interface SaleListParams {
  page?: number;
  per_page?: number;
}

export const salesApi = api.injectEndpoints({
  endpoints: (build) => ({
    getSales: build.query<PaginatedResponse<Sale>, SaleListParams>({
      query: ({ page = 1, per_page = 50 }) =>
        `/sales?page=${page}&per_page=${per_page}`,
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Sale' as const, id })),
              { type: 'Sale', id: 'LIST' },
            ]
          : [{ type: 'Sale', id: 'LIST' }],
    }),

    addSale: build.mutation<Sale, { sale: Partial<Sale>; items: any[] }>({
      query: ({ sale, items }) => ({
        url: '/sales',
        method: 'POST',
        body: { ...sale, items },
      }),
      invalidatesTags: [{ type: 'Sale', id: 'LIST' }],
    }),

    updateSale: build.mutation<Sale, { id: number; data: Partial<Sale> }>({
      query: ({ id, data }) => ({ url: `/sales/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Sale', id },
        { type: 'Sale', id: 'LIST' },
      ],
    }),

    deleteSale: build.mutation<void, number>({
      query: (id) => ({ url: `/sales/${id}`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'Sale', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetSalesQuery,
  useAddSaleMutation,
  useUpdateSaleMutation,
  useDeleteSaleMutation,
} = salesApi;
