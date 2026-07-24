import { api, PaginatedResponse } from '../baseApi';

export interface Student {
  id: number;
  user: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  avatar: string;
  bio: string;
  enrolled_courses_count: number;
  completed_courses_count: number;
  total_learning_hours: number;
  date_joined: string;
}

export interface Enrollment {
  id: number;
  student: number;
  course: number;
  course_title: string;
  course_thumbnail: string;
  progress: number;
  enrolled_at: string;
  completed_at: string | null;
  is_completed: boolean;
}

export interface Progress {
  id: number;
  enrollment: number;
  lesson: number;
  lesson_title: string;
  is_completed: boolean;
  completed_at: string | null;
  time_spent: number;
}

export const studentsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getStudents: builder.query<PaginatedResponse<Student>, { page?: number }>({
      query: (params) => ({ url: '/apis/students/', params: { page: params.page || 1 } }),
      providesTags: (result) =>
        result ? [...result.results.map(({ id }) => ({ type: 'Student' as const, id })), { type: 'Student', id: 'LIST' }] : [{ type: 'Student', id: 'LIST' }],
    }),
    getStudent: builder.query<Student, number>({
      query: (id) => `/apis/students/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Student', id }],
    }),
    getStudentEnrollments: builder.query<Enrollment[], number>({
      query: (studentId) => `/apis/students/${studentId}/enrollments/`,
      providesTags: [{ type: 'Enrollment', id: 'LIST' }],
    }),
    getEnrollmentProgress: builder.query<Progress[], number>({
      query: (enrollmentId) => `/apis/enrollments/${enrollmentId}/progress/`,
      providesTags: (result, error, id) => [{ type: 'Progress', id }],
    }),
    enrollInCourse: builder.mutation<Enrollment, { student_id: number; course_id: number }>({
      query: (body) => ({ url: '/apis/enrollments/', method: 'POST', body }),
      invalidatesTags: [{ type: 'Enrollment', id: 'LIST' }, { type: 'Course', id: 'LIST' }],
    }),
    updateProgress: builder.mutation<void, { enrollment_id: number; lesson_id: number; time_spent: number }>({
      query: ({ enrollment_id, ...body }) => ({
        url: `/apis/enrollments/${enrollment_id}/progress/`,
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'Progress', id: 'LIST' }],
    }),
    getDashboard: builder.query<{
      enrolled_courses: number;
      completed_courses: number;
      total_hours: number;
      recent_activity: any[];
      upcoming_deadlines: any[];
    }, number>({
      query: (studentId) => `/apis/students/${studentId}/dashboard/`,
      providesTags: [{ type: 'Dashboard', id: 'LIST' }],
    }),
  }),
});

export const {
  useGetStudentsQuery,
  useGetStudentQuery,
  useGetStudentEnrollmentsQuery,
  useGetEnrollmentProgressQuery,
  useEnrollInCourseMutation,
  useUpdateProgressMutation,
  useGetDashboardQuery,
} = studentsApi;
