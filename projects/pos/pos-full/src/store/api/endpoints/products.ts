/**
 * RTK Query endpoints — Products CRUD with pagination.
 * Replaces: useProductStore (Zustand)
 */

import { api, PaginatedResponse } from '../baseApi';

export interface Product {
  id: number; name: string; price: number; unit: string;
  category_id: number | null; image: string | null;
  created_at: string; updated_at: string; uploaded: boolean;
}

interface ProductListParams {
  page?: number;
  per_page?: number;
}

export const productsApi = api.injectEndpoints({
  endpoints: (build) => ({
    getProducts: build.query<PaginatedResponse<Product>, ProductListParams>({
      query: ({ page = 1, per_page = 50 }) =>
        `/products?page=${page}&per_page=${per_page}`,
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'Product' as const, id })),
              { type: 'Product', id: 'LIST' },
            ]
          : [{ type: 'Product', id: 'LIST' }],
    }),

    getProduct: build.query<Product, number>({
      query: (id) => `/products/${id}`,
      providesTags: (result, error, id) => [{ type: 'Product', id }],
    }),

    addProduct: build.mutation<Product, Partial<Product>>({
      query: (body) => ({ url: '/products', method: 'POST', body }),
      invalidatesTags: [{ type: 'Product', id: 'LIST' }],
    }),

    updateProduct: build.mutation<Product, { id: number; data: Partial<Product> }>({
      query: ({ id, data }) => ({ url: `/products/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Product', id },
        { type: 'Product', id: 'LIST' },
      ],
    }),

    deleteProduct: build.mutation<void, number>({
      query: (id) => ({ url: `/products/${id}`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'Product', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetProductsQuery,
  useGetProductQuery,
  useAddProductMutation,
  useUpdateProductMutation,
  useDeleteProductMutation,
} = productsApi;
