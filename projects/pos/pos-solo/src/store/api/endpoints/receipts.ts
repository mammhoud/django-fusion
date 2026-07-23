/** RTK Query endpoints — Receipt Templates. */
import { api } from '../baseApi';

export interface ReceiptTemplate {
  id: number; name: string; content: string; template_body?: string; is_default: boolean;
  created_at: string; updated_at: string;
}

export const receiptsApi = api.injectEndpoints({
  endpoints: (build) => ({
    getReceiptTemplates: build.query<ReceiptTemplate[], void>({
      query: () => '/receipt-templates',
      providesTags: (result) =>
        result ? [...result.map(({ id }) => ({ type: 'ReceiptTemplate' as const, id })), { type: 'ReceiptTemplate', id: 'LIST' }]
          : [{ type: 'ReceiptTemplate', id: 'LIST' }],
    }),
    addReceiptTemplate: build.mutation<ReceiptTemplate, Partial<ReceiptTemplate>>({
      query: (body) => ({ url: '/receipt-templates', method: 'POST', body }),
      invalidatesTags: [{ type: 'ReceiptTemplate', id: 'LIST' }],
    }),
    updateReceiptTemplate: build.mutation<ReceiptTemplate, { id: number; data: Partial<ReceiptTemplate> }>({
      query: ({ id, data }) => ({ url: `/receipt-templates/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: (result, error, { id }) => [{ type: 'ReceiptTemplate', id }, { type: 'ReceiptTemplate', id: 'LIST' }],
    }),
    deleteReceiptTemplate: build.mutation<void, number>({
      query: (id) => ({ url: `/receipt-templates/${id}`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'ReceiptTemplate', id: 'LIST' }],
    }),
  }),
});

export const { useGetReceiptTemplatesQuery, useAddReceiptTemplateMutation, useUpdateReceiptTemplateMutation, useDeleteReceiptTemplateMutation } = receiptsApi;
