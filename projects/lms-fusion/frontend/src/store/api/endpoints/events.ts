import { api, PaginatedResponse } from '../baseApi';

export interface Event {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  featured_image: string;
  start_date: string;
  end_date: string;
  location: string;
  is_online: boolean;
  meeting_url: string;
  capacity: number;
  registered_count: number;
  price: number;
  is_free: boolean;
  organizer: string;
  status: 'upcoming' | 'ongoing' | 'completed' | 'cancelled';
  created_at: string;
}

export interface EventRegistration {
  id: number;
  event: number;
  event_title: string;
  full_name: string;
  email: string;
  phone: string;
  registered_at: string;
  is_attended: boolean;
}

export const eventsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getEvents: builder.query<PaginatedResponse<Event>, { page?: number; status?: string }>({
      query: (params) => ({
        url: '/events/',
        params: { page: params.page || 1, status: params.status },
      }),
      providesTags: (result) =>
        result ? [...result.results.map(({ id }) => ({ type: 'Event' as const, id })), { type: 'Event', id: 'LIST' }] : [{ type: 'Event', id: 'LIST' }],
    }),
    getEvent: builder.query<Event, number>({
      query: (id) => `/events/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Event', id }],
    }),
    registerForEvent: builder.mutation<EventRegistration, { event_id: number; full_name: string; email: string; phone?: string }>({
      query: (body) => ({ url: '/events/register/', method: 'POST', body }),
      invalidatesTags: [{ type: 'EventRegistration', id: 'LIST' }],
    }),
    getUpcomingEvents: builder.query<Event[], void>({
      query: () => '/events/upcoming/',
      providesTags: [{ type: 'Event', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetEventsQuery,
  useGetEventQuery,
  useRegisterForEventMutation,
  useGetUpcomingEventsQuery,
} = eventsApi;
