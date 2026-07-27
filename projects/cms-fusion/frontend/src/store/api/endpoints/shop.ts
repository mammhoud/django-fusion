import { api, PaginatedResponse } from '../baseApi';

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  price: number;
  discounted_price: number | null;
  images: string[];
  category: number;
  category_name: string;
  stock: number;
  is_available: boolean;
  created_at: string;
}

export interface CartItem {
  id: number;
  product: number;
  product_name: string;
  product_image: string;
  product_price: number;
  quantity: number;
  subtotal: number;
}

export interface Order {
  id: number;
  items: CartItem[];
  total: number;
  status: 'pending' | 'processing' | 'completed' | 'cancelled';
  payment_method: string;
  shipping_address: string;
  created_at: string;
}

export const shopApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getProducts: builder.query<PaginatedResponse<Product>, { page?: number; category?: string; search?: string }>({
      query: (params) => ({
        url: '/apis/shop/products/',
        params: { page: params.page || 1, category: params.category, search: params.search },
      }),
      providesTags: (result) =>
        result ? [...result.results.map(({ id }) => ({ type: 'Product' as const, id })), { type: 'Product', id: 'LIST' }] : [{ type: 'Product', id: 'LIST' }],
    }),
    getProduct: builder.query<Product, number>({
      query: (id) => `/apis/shop/products/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Product', id }],
    }),
    getCart: builder.query<CartItem[], void>({
      query: () => '/apis/shop/cart/',
      providesTags: [{ type: 'Cart', id: 'LIST' }],
    }),
    addToCart: builder.mutation<CartItem, { product_id: number; quantity: number }>({
      query: (body) => ({ url: '/apis/shop/cart/add/', method: 'POST', body }),
      invalidatesTags: [{ type: 'Cart', id: 'LIST' }],
    }),
    updateCartItem: builder.mutation<CartItem, { item_id: number; quantity: number }>({
      query: ({ item_id, ...body }) => ({ url: `/apis/shop/cart/${item_id}/`, method: 'PATCH', body }),
      invalidatesTags: [{ type: 'Cart', id: 'LIST' }],
    }),
    removeFromCart: builder.mutation<void, number>({
      query: (itemId) => ({ url: `/apis/shop/cart/${itemId}/`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'Cart', id: 'LIST' }],
    }),
    createOrder: builder.mutation<Order, { shipping_address: string; payment_method: string }>({
      query: (body) => ({ url: '/apis/shop/orders/', method: 'POST', body }),
      invalidatesTags: [{ type: 'Order', id: 'LIST' }, { type: 'Cart', id: 'LIST' }],
    }),
    getOrders: builder.query<PaginatedResponse<Order>, { page?: number }>({
      query: (params) => ({ url: '/apis/shop/orders/', params: { page: params.page || 1 } }),
      providesTags: (result) =>
        result ? [...result.results.map(({ id }) => ({ type: 'Order' as const, id })), { type: 'Order', id: 'LIST' }] : [{ type: 'Order', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetProductsQuery,
  useGetProductQuery,
  useGetCartQuery,
  useAddToCartMutation,
  useUpdateCartItemMutation,
  useRemoveFromCartMutation,
  useCreateOrderMutation,
  useGetOrdersQuery,
} = shopApi;
