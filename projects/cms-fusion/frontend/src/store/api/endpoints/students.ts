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
  course_thumbnail: string | null;
  price: number;
  progress: number;
  status: string;
  payment_status: string;
  payment_transaction_id: number | null;
  enrolled_at: string;
  completed_at: string | null;
  is_completed: boolean;
  instructor_name: string;
  duration: string;
}

export interface ProgressEntry {
  id: number;
  lesson: number;
  lesson_title: string;
  is_completed: boolean;
  completed_at: string | null;
  time_spent: number;
}

export interface DashboardData {
  enrolled_courses: number;
  active_courses: number;
  completed_courses: number;
  total_hours: number;
  recent_activity: any[];
  upcoming_deadlines: any[];
}

export interface PaymentInitRequest {
  provider?: string;
  success_url?: string;
  cancel_url?: string;
}

export interface PaymentInitResponse {
  success: boolean;
  transaction_id: number;
  provider: string;
  amount: number;
  currency: string;
  redirect_url: string | null;
  client_secret: string | null;
  payment_url: string | null;
  metadata: Record<string, any>;
}

export interface PaymentVerifyResponse {
  success: boolean;
  status: string;
  message: string;
  transaction_id: number;
  enrollment_id: number | null;
  course_title: string;
  metadata: Record<string, any>;
}

export const studentsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    // ── Students ──
    getStudents: builder.query<PaginatedResponse<Student>, { page?: number }>({
      query: (params) => ({ url: '/students', params: { page: params.page || 1 } }),
      providesTags: (result) =>
        result ? [...result.results.map(({ id }) => ({ type: 'Student' as const, id })), { type: 'Student', id: 'LIST' }] : [{ type: 'Student', id: 'LIST' }],
    }),
    getStudent: builder.query<Student, number>({
      query: (id) => `/students/${id}`,
      providesTags: (result, error, id) => [{ type: 'Student', id }],
    }),

    // ── Dashboard ──
    getDashboard: builder.query<DashboardData, number>({
      query: (studentId) => `/students/${studentId}/dashboard`,
      providesTags: [{ type: 'Dashboard', id: 'LIST' }],
    }),

    // ── Enrollments ──
    getStudentEnrollments: builder.query<Enrollment[], number>({
      query: (studentId) => `/students/${studentId}/enrollments`,
      providesTags: [{ type: 'Enrollment', id: 'LIST' }],
    }),
    enrollInCourse: builder.mutation<Enrollment, { course_id: number }>({
      query: (body) => ({ url: '/enrollments', method: 'POST', body }),
      invalidatesTags: [{ type: 'Enrollment', id: 'LIST' }, { type: 'Course', id: 'LIST' }],
    }),

    // ── Progress ──
    getEnrollmentProgress: builder.query<ProgressEntry[], number>({
      query: (enrollmentId) => `/enrollments/${enrollmentId}/progress`,
      providesTags: (result, error, id) => [{ type: 'Progress', id }],
    }),
    updateProgress: builder.mutation<{ data: ProgressEntry; created: boolean }, { enrollment_id: number; lesson_id: number; time_spent?: number }>({
      query: ({ enrollment_id, ...body }) => ({
        url: `/enrollments/${enrollment_id}/progress`,
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'Progress', id: 'LIST' }],
    }),

    // ── Payment ──
    initializePayment: builder.mutation<{ data: PaymentInitResponse }, { enrollment_id: number; data: PaymentInitRequest }>({
      query: ({ enrollment_id, data }) => ({
        url: `/enrollments/${enrollment_id}/payment/init`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: [{ type: 'Enrollment', id: 'LIST' }],
    }),
    verifyPayment: builder.mutation<{ data: PaymentVerifyResponse }, { transaction_id: number }>({
      query: ({ transaction_id }) => ({
        url: `/payments/${transaction_id}/verify`,
        method: 'POST',
      }),
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
  useInitializePaymentMutation,
  useVerifyPaymentMutation,
} = studentsApi;
