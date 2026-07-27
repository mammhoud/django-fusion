import { api, PaginatedResponse } from '../baseApi';

// ─── Types ──────────────────────────────────────────────────────────

export interface Notification {
  id: number;
  type: string;
  type_label: string;
  title: string;
  message: string;
  link: string;
  is_read: boolean;
  created_at: string;
  time_ago: string;
}

export interface NotificationPreference {
  in_app_notifications: boolean;
  email_notifications: boolean;
  enrollment_notifications: boolean;
  course_update_notifications: boolean;
  assignment_notifications: boolean;
  grading_notifications: boolean;
  quiz_notifications: boolean;
  review_notifications: boolean;
  announcement_notifications: boolean;
  system_notifications: boolean;
  digest_frequency: 'immediate' | 'daily' | 'weekly' | 'never';
}

interface UnreadCountResponse {
  unread_count: number;
}

// ─── Endpoints ──────────────────────────────────────────────────────

export const notificationsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    // ── List notifications ──
    getNotifications: builder.query<
      PaginatedResponse<Notification>,
      { unread_only?: boolean; limit?: number; offset?: number }
    >({
      query: (params) => ({
        url: '/apis/notifications/',
        params: {
          unread_only: params.unread_only ? 'true' : undefined,
          limit: params.limit || 20,
          offset: params.offset || 0,
        },
      }),
      providesTags: ['Notification'],
    }),

    // ── Unread count ──
    getUnreadCount: builder.query<UnreadCountResponse, void>({
      query: () => '/apis/notifications/unread-count/',
      providesTags: ['Notification'],
    }),

    // ── Mark single as read ──
    markNotificationRead: builder.mutation<Notification, number>({
      query: (id) => ({
        url: `/apis/notifications/${id}/read/`,
        method: 'PATCH',
      }),
      invalidatesTags: ['Notification'],
    }),

    // ── Mark all as read ──
    markAllNotificationsRead: builder.mutation<{ marked_read: number }, void>({
      query: () => ({
        url: '/apis/notifications/mark-all-read/',
        method: 'POST',
      }),
      invalidatesTags: ['Notification'],
    }),

    // ── Dismiss notification ──
    dismissNotification: builder.mutation<void, number>({
      query: (id) => ({
        url: `/apis/notifications/${id}/`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Notification'],
    }),

    // ── Get preferences ──
    getNotificationPreferences: builder.query<
      { status: string; data: NotificationPreference },
      void
    >({
      query: () => '/apis/notifications/preferences/',
      providesTags: ['NotificationPrefs'],
    }),

    // ── Update preferences ──
    updateNotificationPreferences: builder.mutation<
      { status: string; data: NotificationPreference },
      Partial<NotificationPreference>
    >({
      query: (data) => ({
        url: '/apis/notifications/preferences/update/',
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: ['NotificationPrefs', 'Notification'],
    }),
  }),
});

export const {
  useGetNotificationsQuery,
  useGetUnreadCountQuery,
  useMarkNotificationReadMutation,
  useMarkAllNotificationsReadMutation,
  useDismissNotificationMutation,
  useGetNotificationPreferencesQuery,
  useUpdateNotificationPreferencesMutation,
} = notificationsApi;
