import { api, PaginatedResponse } from '../baseApi';
import type { Course } from './courses';

export interface Instructor {
  id: number;
  user: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  avatar: string;
  title: string;
  bio: string;
  expertise: string[];
  courses_count: number;
  students_count: number;
  total_reviews: number;
  average_rating: number;
  joined_at: string;
}

export interface InstructorDashboard {
  total_courses: number;
  total_students: number;
  total_revenue: number;
  average_rating: number;
  recent_enrollments: number;
  pending_reviews: number;
  monthly_earnings: { month: string; amount: number }[];
  enrollment_trends: { month: string; count: number }[];
  total_enrollments: number;
  completed_enrollments: number;
  active_enrollments: number;
  completion_rate: number;
  popular_courses: { id: number; title: string; student_count: number; course_revenue: number; course_completed: number }[];
}

export const instructorsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getInstructors: builder.query<PaginatedResponse<Instructor>, { page?: number }>({
      query: (params) => ({ url: '/apis/instructors/', params: { page: params.page || 1 } }),
      providesTags: (result) =>
        result ? [...result.results.map(({ id }) => ({ type: 'Instructor' as const, id })), { type: 'Instructor', id: 'LIST' }] : [{ type: 'Instructor', id: 'LIST' }],
    }),
    getInstructor: builder.query<Instructor, number>({
      query: (id) => `/apis/instructors/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Instructor', id }],
    }),
    getInstructorDashboard: builder.query<InstructorDashboard, number>({
      query: (id) => `/apis/instructors/${id}/dashboard/`,
      providesTags: [{ type: 'Dashboard', id: 'LIST' }],
    }),
    getInstructorCourses: builder.query<Course[], number>({
      query: (id) => `/apis/instructors/${id}/courses/`,
      providesTags: [{ type: 'Course', id: 'LIST' }],
    }),
    getInstructorReviews: builder.query<any[], number>({
      query: (id) => `/apis/instructors/${id}/reviews/`,
      providesTags: [{ type: 'Review', id: 'LIST' }],
    }),
    deleteCourse: builder.mutation<void, number>({
      query: (id) => ({ url: `/apis/instructors/courses/${id}/`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'Course', id: 'LIST' }],
    }),
    updateInstructorProfile: builder.mutation<Instructor, { id: number; data: Partial<Instructor> }>({
      query: ({ id, data }) => ({ url: `/apis/instructors/${id}/`, method: 'PATCH', body: data }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Instructor', id }, { type: 'Instructor', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetInstructorsQuery,
  useGetInstructorQuery,
  useGetInstructorDashboardQuery,
  useGetInstructorCoursesQuery,
  useGetInstructorReviewsQuery,
  useDeleteCourseMutation as useDeleteInstructorCourseMutation,
  useUpdateInstructorProfileMutation,
} = instructorsApi;
