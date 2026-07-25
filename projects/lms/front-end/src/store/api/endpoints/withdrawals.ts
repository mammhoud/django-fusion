import { api, PaginatedResponse } from '../baseApi';

export interface Withdrawal {
  id: number;
  instructor: number;
  instructor_name: string;
  amount: number;
  current_balance: number;
  status: 'pending' | 'approved' | 'processing' | 'completed' | 'rejected' | 'cancelled';
  status_display: string;
  payment_method: 'paypal' | 'bank_transfer' | 'stripe';
  payment_method_display: string;
  payment_details: Record<string, unknown>;
  notes: string;
  reference: string;
  processed_by: number | null;
  created_at: string | null;
  updated_at: string | null;
  processed_at: string | null;
  can_cancel: boolean;
  is_completed: boolean;
  is_pending: boolean;
}

export interface WithdrawalSummary {
  current_balance: number;
  pending_amount: number;
  total_withdrawn: number;
  total_earned: number;
  pending_count: number;
  recent_withdrawals: Withdrawal[];
}

export const withdrawalsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getWithdrawals: builder.query<PaginatedResponse<Withdrawal>, { page?: number; status?: string }>({
      query: (params) => ({ url: '/apis/withdrawals/', params }),
      providesTags: (result) =>
        result
          ? [
              ...result.results.map(({ id }) => ({ type: 'Withdrawal' as const, id })),
              { type: 'Withdrawal', id: 'LIST' },
            ]
          : [{ type: 'Withdrawal', id: 'LIST' }],
    }),
    getWithdrawal: builder.query<Withdrawal, number>({
      query: (id) => `/apis/withdrawals/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Withdrawal', id }],
    }),
    createWithdrawal: builder.mutation<Withdrawal, { amount: number; payment_method: string; payment_details?: Record<string, unknown> }>({
      query: (body) => ({ url: '/apis/withdrawals/create/', method: 'POST', body }),
      invalidatesTags: [{ type: 'Withdrawal', id: 'LIST' }],
    }),
    cancelWithdrawal: builder.mutation<Withdrawal, number>({
      query: (id) => ({ url: `/apis/withdrawals/${id}/cancel/`, method: 'PATCH' }),
      invalidatesTags: (result, error, id) => [{ type: 'Withdrawal', id }, { type: 'Withdrawal', id: 'LIST' }],
    }),
    getWithdrawalSummary: builder.query<WithdrawalSummary, void>({
    query: () => '/apis/withdrawals/summary/',
    providesTags: [{ type: 'Withdrawal', id: 'SUMMARY' }],
  }),
  approveWithdrawal: builder.mutation<Withdrawal, number>({
      query: (id) => ({ url: `/apis/withdrawals/${id}/approve/`, method: 'PATCH' }),
      invalidatesTags: (result, error, id) => [{ type: 'Withdrawal', id }, { type: 'Withdrawal', id: 'LIST' }],
    }),
    rejectWithdrawal: builder.mutation<Withdrawal, { id: number; reason?: string }>({
      query: ({ id, reason }) => ({ url: `/apis/withdrawals/${id}/reject/`, method: 'PATCH', body: { reason } }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Withdrawal', id }, { type: 'Withdrawal', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetWithdrawalsQuery,
  useGetWithdrawalQuery,
  useGetWithdrawalSummaryQuery,
  useCreateWithdrawalMutation,
  useCancelWithdrawalMutation,
  useApproveWithdrawalMutation,
  useRejectWithdrawalMutation,
} = withdrawalsApi;
