/**
 * RTK Query endpoints — Customers CRUD with pagination.
 * Replaces: useCustomerStore (Zustand)
 */

import { api, PaginatedResponse } from '../baseApi';

export interface Customer {
  id: number; name: string; phone: string | null; email: string | null;
  loyalty_points: number; notes: string | null;
  created_at: string; updated_at: string;
}

interface CustomerListParams {
  page?: number;
  per_page?: number;
}

export const customersApi = api.injectEndpoints({
  endpoints: (build) => ({
    getCustomers: build.query<PaginatedResponse<Customer>, CustomerListParams>({
      query: ({ page = 1, per_page = 50 }) =>
        `/customers?page=${page}&per_page=${per_page}`,
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Customer' as const, id })),
              { type: 'Customer', id: 'LIST' },
            ]
          : [{ type: 'Customer', id: 'LIST' }],
    }),

    addCustomer: build.mutation<Customer, Partial<Customer>>({
      query: (body) => ({ url: '/customers', method: 'POST', body }),
      invalidatesTags: [{ type: 'Customer', id: 'LIST' }],
    }),

    updateCustomer: build.mutation<Customer, { id: number; data: Partial<Customer> }>({
      query: ({ id, data }) => ({ url: `/customers/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Customer', id },
        { type: 'Customer', id: 'LIST' },
      ],
    }),

    deleteCustomer: build.mutation<void, number>({
      query: (id) => ({ url: `/customers/${id}`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'Customer', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetCustomersQuery,
  useAddCustomerMutation,
  useUpdateCustomerMutation,
  useDeleteCustomerMutation,
} = customersApi;
