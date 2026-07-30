import { api, PaginatedResponse } from '../baseApi';

export interface Announcement {
  id: number;
  title: string;
  content: string;
  audience: 'all' | 'instructor' | 'student';
  link: string;
  link_label: string;
  is_published: boolean;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnnouncementCreatePayload {
  title: string;
  content: string;
  audience?: 'all' | 'instructor' | 'student';
  link?: string;
  link_label?: string;
  publish_now?: boolean;
}

export interface AnnouncementUpdatePayload {
  title?: string;
  content?: string;
  audience?: 'all' | 'instructor' | 'student';
  link?: string;
  link_label?: string;
  is_published?: boolean;
}

export const announcementsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getAnnouncements: builder.query<
      PaginatedResponse<Announcement>,
      { audience?: string; page?: number } | void
    >({
      query: (params) => ({
        url: '/announcements/',
        params: params || undefined,
      }),
      providesTags: [{ type: 'Announcement', id: 'LIST' }],
    }),

    getAnnouncement: builder.query<Announcement, number>({
      query: (id) => `/announcements/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Announcement', id }],
    }),

    createAnnouncement: builder.mutation<
      Announcement,
      AnnouncementCreatePayload
    >({
      query: (body) => ({
        url: '/announcements/create/',
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'Announcement', id: 'LIST' }],
    }),

    updateAnnouncement: builder.mutation<
      Announcement,
      { id: number; data: AnnouncementUpdatePayload }
    >({
      query: ({ id, data }) => ({
        url: `/announcements/${id}/update/`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Announcement', id },
        { type: 'Announcement', id: 'LIST' },
      ],
    }),

    deleteAnnouncement: builder.mutation<void, number>({
      query: (id) => ({
        url: `/announcements/${id}/delete/`,
        method: 'DELETE',
      }),
      invalidatesTags: [{ type: 'Announcement', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetAnnouncementsQuery,
  useGetAnnouncementQuery,
  useCreateAnnouncementMutation,
  useUpdateAnnouncementMutation,
  useDeleteAnnouncementMutation,
} = announcementsApi;
