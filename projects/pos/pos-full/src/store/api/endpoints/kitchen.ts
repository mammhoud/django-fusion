/** RTK Query endpoints — Kitchen Tickets, Recipes, Supplier Transactions. */
import { api } from '../baseApi';

export interface KitchenTicket { id: number; order_id: number; table_number: number | null; items: any[]; status: 'pending' | 'preparing' | 'ready' | 'served'; notes: string; created_at: string; updated_at: string; }
export interface Recipe { id: number; name: string; product_id: number; ingredients: { ingredient_id: number; quantity: number; unit: string; }[]; instructions: string; yield_quantity: number; created_at: string; updated_at: string; }
export interface Transaction { id: number; supplier_id: number; type: 'payment' | 'purchase'; amount: number; reference: string; notes: string; created_at: string; }

export const kitchenApi = api.injectEndpoints({
  endpoints: (build) => ({
    getKitchenTickets: build.query<KitchenTicket[], { status?: string }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.status) p.set('status', params.status);
        return `/kitchen-tickets?${p.toString()}`;
      },
      providesTags: ['KitchenTicket'],
    }),
    updateKitchenTicket: build.mutation<KitchenTicket, { id: number; data: Partial<KitchenTicket> }>({
      query: ({ id, data }) => ({ url: `/kitchen-tickets/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: ['KitchenTicket'],
    }),
    getRecipes: build.query<Recipe[], void>({
      query: () => '/recipes',
      providesTags: ['Recipe'],
    }),
    addRecipe: build.mutation<Recipe, Partial<Recipe>>({
      query: (body) => ({ url: '/recipes', method: 'POST', body }),
      invalidatesTags: ['Recipe'],
    }),
    updateRecipe: build.mutation<Recipe, { id: number; data: Partial<Recipe> }>({
      query: ({ id, data }) => ({ url: `/recipes/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: ['Recipe'],
    }),
    deleteRecipe: build.mutation<void, number>({
      query: (id) => ({ url: `/recipes/${id}`, method: 'DELETE' }),
      invalidatesTags: ['Recipe'],
    }),
    getTransactions: build.query<Transaction[], void>({
      query: () => '/transactions',
      providesTags: ['Transaction'],
    }),
    deleteTransaction: build.mutation<void, number>({
      query: (id) => ({ url: `/transactions/${id}`, method: 'DELETE' }),
      invalidatesTags: ['Transaction'],
    }),
  }),
});

export const { useGetKitchenTicketsQuery, useUpdateKitchenTicketMutation, useGetRecipesQuery, useAddRecipeMutation, useUpdateRecipeMutation, useDeleteRecipeMutation, useGetTransactionsQuery, useDeleteTransactionMutation } = kitchenApi;
