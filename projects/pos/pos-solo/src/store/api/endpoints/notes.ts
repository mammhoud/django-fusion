/** RTK Query endpoints — Notes CRUD with draft / restore. */
import { api } from '../baseApi';

export interface Note {
  id: number;
  title: string;
  content: string;
  status: 'draft' | 'saved' | 'archived';
  reference_type: '' | 'cart' | 'inventory' | 'count' | 'order' | 'customer';
  reference_id: number | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export const notesApi = api.injectEndpoints({
  endpoints: (build) => ({
    getNotes: build.query<Note[], { status?: string; reference_type?: string }>({
      query: (params) => {
        const p = new URLSearchParams();
        if (params.status) p.set('status', params.status);
        if (params.reference_type) p.set('reference_type', params.reference_type);
        return `/notes?${p.toString()}`;
      },
      providesTags: (result) =>
        result
          ? [...result.map(({ id }) => ({ type: 'Note' as const, id })), { type: 'Note', id: 'LIST' }]
          : [{ type: 'Note', id: 'LIST' }],
    }),

    getNote: build.query<Note, number>({
      query: (id) => `/notes/${id}`,
      providesTags: (result, error, id) => [{ type: 'Note', id }],
    }),

    addNote: build.mutation<Note, Partial<Note>>({
      query: (body) => ({ url: '/notes', method: 'POST', body }),
      invalidatesTags: [{ type: 'Note', id: 'LIST' }],
    }),

    updateNote: build.mutation<Note, { id: number; data: Partial<Note> }>({
      query: ({ id, data }) => ({ url: `/notes/${id}`, method: 'PATCH', body: data }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Note', id },
        { type: 'Note', id: 'LIST' },
      ],
    }),

    deleteNote: build.mutation<void, number>({
      query: (id) => ({ url: `/notes/${id}`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'Note', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetNotesQuery,
  useGetNoteQuery,
  useAddNoteMutation,
  useUpdateNoteMutation,
  useDeleteNoteMutation,
} = notesApi;
