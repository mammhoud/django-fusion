/**
 * RTK Query endpoints — Loyalty & Client Settings.
 *
 * - ClientCategories   : tier CRUD (people as client categories, points thresholds)
 * - LoyaltyTransactions: points ledger (earn / redeem / adjust)
 * - UserSettings       : per-user POS settings (same data as the front Settings page)
 *
 * Consumed by the Settings page Loyalty tab.
 */

import { api, PaginatedResponse } from '../baseApi';
import type { ClientCategory, LoyaltyTransaction, UserSettings } from '../../../types';

export const loyaltyApi = api.injectEndpoints({
  endpoints: (build) => ({
    // ── Client Categories ──
    getClientCategories: build.query<PaginatedResponse<ClientCategory>, { page?: number; per_page?: number }>({
      query: ({ page = 1, per_page = 50 } = {}) =>
        `/client-categories?page=${page}&per_page=${per_page}`,
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'ClientCategory' as const, id })),
              { type: 'ClientCategory', id: 'LIST' },
            ]
          : [{ type: 'ClientCategory', id: 'LIST' }],
    }),

    addClientCategory: build.mutation<ClientCategory, Partial<ClientCategory>>({
      query: (body) => ({ url: '/client-categories', method: 'POST', body }),
      invalidatesTags: [{ type: 'ClientCategory', id: 'LIST' }],
    }),

    updateClientCategory: build.mutation<ClientCategory, { id: number; data: Partial<ClientCategory> }>({
      query: ({ id, data }) => ({ url: `/client-categories/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: (_result, _error, { id }) => [
        { type: 'ClientCategory', id },
        { type: 'ClientCategory', id: 'LIST' },
      ],
    }),

    deleteClientCategory: build.mutation<void, number>({
      query: (id) => ({ url: `/client-categories/${id}`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'ClientCategory', id: 'LIST' }],
    }),

    // ── Loyalty Transactions (points ledger) ──
    getLoyaltyTransactions: build.query<PaginatedResponse<LoyaltyTransaction>, { page?: number; per_page?: number }>({
      query: ({ page = 1, per_page = 50 } = {}) =>
        `/loyalty-transactions?page=${page}&per_page=${per_page}`,
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'LoyaltyTransaction' as const, id })),
              { type: 'LoyaltyTransaction', id: 'LIST' },
            ]
          : [{ type: 'LoyaltyTransaction', id: 'LIST' }],
    }),

    addLoyaltyTransaction: build.mutation<LoyaltyTransaction, Partial<LoyaltyTransaction>>({
      query: (body) => ({ url: '/loyalty-transactions', method: 'POST', body }),
      invalidatesTags: [
        { type: 'LoyaltyTransaction', id: 'LIST' },
        { type: 'Customer', id: 'LIST' },
      ],
    }),

    // ── User Settings ──
    getUserSettings: build.query<PaginatedResponse<UserSettings>, { page?: number; per_page?: number }>({
      query: ({ page = 1, per_page = 50 } = {}) =>
        `/user-settings?page=${page}&per_page=${per_page}`,
      providesTags: (result) =>
        result
          ? [
              ...result.data.map(({ id }) => ({ type: 'UserSettings' as const, id })),
              { type: 'UserSettings', id: 'LIST' },
            ]
          : [{ type: 'UserSettings', id: 'LIST' }],
    }),

    updateUserSettings: build.mutation<UserSettings, { id: number; data: Partial<UserSettings> }>({
      query: ({ id, data }) => ({ url: `/user-settings/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: (_result, _error, { id }) => [
        { type: 'UserSettings', id },
        { type: 'UserSettings', id: 'LIST' },
      ],
    }),

    createUserSettings: build.mutation<UserSettings, Partial<UserSettings>>({
      query: (body) => ({ url: '/user-settings', method: 'POST', body }),
      invalidatesTags: [{ type: 'UserSettings', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetClientCategoriesQuery,
  useAddClientCategoryMutation,
  useUpdateClientCategoryMutation,
  useDeleteClientCategoryMutation,
  useGetLoyaltyTransactionsQuery,
  useAddLoyaltyTransactionMutation,
  useGetUserSettingsQuery,
  useUpdateUserSettingsMutation,
  useCreateUserSettingsMutation,
} = loyaltyApi;
