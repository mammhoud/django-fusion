import { api, PaginatedResponse } from '../baseApi';

export interface Inquiry {
  id: number;
  name: string;
  email: string;
  subject: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface ContactRequest {
  name: string;
  email: string;
  subject: string;
  message: string;
}

export const contactApi = api.injectEndpoints({
  endpoints: (builder) => ({
    submitContact: builder.mutation<Inquiry, ContactRequest>({
      query: (body) => ({ url: '/contact/', method: 'POST', body }),
      invalidatesTags: [{ type: 'Contact', id: 'LIST' }],
    }),
    getInquiries: builder.query<PaginatedResponse<Inquiry>, { page?: number }>({
      query: (params) => ({ url: '/contact/inquiries/', params: { page: params.page || 1 } }),
      providesTags: (result) =>
        result ? [...result.results.map(({ id }) => ({ type: 'Contact' as const, id })), { type: 'Contact', id: 'LIST' }] : [{ type: 'Contact', id: 'LIST' }],
    }),
    markInquiryRead: builder.mutation<void, number>({
      query: (id) => ({ url: `/contact/${id}/mark-read/`, method: 'POST' }),
      invalidatesTags: (result, error, id) => [{ type: 'Contact', id }],
    }),
  }),
});

export const {
  useSubmitContactMutation,
  useGetInquiriesQuery,
  useMarkInquiryReadMutation,
} = contactApi;
