import { api, PaginatedResponse } from '../baseApi';

export interface Course {
  id: number;
  title: string;
  slug: string;
  description: string;
  short_description: string;
  price: number;
  discounted_price: number | null;
  thumbnail: string;
  category: number;
  category_name: string;
  instructor: number;
  instructor_name: string;
  duration: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  language: string;
  curriculum: Lesson[];
  students_count: number;
  rating: number;
  reviews_count: number;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

export interface Lesson {
  id: number;
  title: string;
  description: string;
  video_url: string;
  duration: string;
  order: number;
  is_free: boolean;
}

export const coursesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getCourses: builder.query<PaginatedResponse<Course>, { page?: number; search?: string; category?: string; level?: string }>({
      query: (params) => ({
        url: '/apis/courses/',
        params: { page: params.page || 1, search: params.search, category: params.category, level: params.level },
      }),
      providesTags: (result) =>
        result
          ? [...result.results.map(({ id }) => ({ type: 'Course' as const, id })), { type: 'Course', id: 'LIST' }]
          : [{ type: 'Course', id: 'LIST' }],
    }),
    getCourse: builder.query<Course, number>({
      query: (id) => `/apis/courses/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Course', id }],
    }),
    createCourse: builder.mutation<Course, Partial<Course>>({
      query: (body) => ({ url: '/apis/courses/', method: 'POST', body }),
      invalidatesTags: [{ type: 'Course', id: 'LIST' }],
    }),
    updateCourse: builder.mutation<Course, { id: number; data: Partial<Course> }>({
      query: ({ id, data }) => ({ url: `/apis/courses/${id}/`, method: 'PATCH', body: data }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Course', id }, { type: 'Course', id: 'LIST' }],
    }),
    deleteCourse: builder.mutation<void, number>({
      query: (id) => ({ url: `/apis/courses/${id}/`, method: 'DELETE' }),
      invalidatesTags: [{ type: 'Course', id: 'LIST' }],
    }),
    getCategories: builder.query<{ id: number; name: string; slug: string }[], void>({
      query: () => '/apis/categories/',
      providesTags: [{ type: 'Category', id: 'LIST' }],
    }),
    getFeaturedCourses: builder.query<Course[], void>({
      query: () => '/apis/courses/featured/',
      providesTags: [{ type: 'Course', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetCoursesQuery,
  useGetCourseQuery,
  useCreateCourseMutation,
  useUpdateCourseMutation,
  useDeleteCourseMutation,
  useGetCategoriesQuery,
  useGetFeaturedCoursesQuery,
} = coursesApi;
