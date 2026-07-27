import { api } from '../baseApi';

export interface DashboardContent {
  slug: string;
  title: string;
  encoded: string;
  language: string;
}

export const dashboardApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getDashboardContent: builder.query<DashboardContent, void>({
      query: () => '/apis/dashboard/content/',
      providesTags: [{ type: 'Dashboard' as const, id: 'CMS' }],
    }),
  }),
});

export const { useGetDashboardContentQuery } = dashboardApi;
