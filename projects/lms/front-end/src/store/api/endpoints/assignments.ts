import { api, PaginatedResponse } from '../baseApi';

export interface Assignment {
  id: number;
  course: number;
  course_title: string;
  title: string;
  description: string;
  instructions: string;
  due_date: string | null;
  max_score: number;
  is_published: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
  submissions_count: number;
}

export interface AssignmentSubmission {
  id: number;
  assignment: number;
  assignment_title: string;
  course: number;
  course_title: string;
  student: number;
  student_name: string;
  text_submission: string;
  file_url: string;
  file_name: string;
  status: 'submitted' | 'graded' | 'returned';
  score: number | null;
  max_score: number;
  feedback: string;
  graded_by: number | null;
  submitted_at: string;
  graded_at: string | null;
  is_late: boolean;
}

export interface AssignmentCreatePayload {
  title: string;
  course_id: number;
  description?: string;
  instructions?: string;
  due_date?: string;
  max_score?: number;
  is_published?: boolean;
}

export interface AssignmentSubmitPayload {
  text_submission?: string;
  file_url?: string;
  file_name?: string;
}

export interface GradePayload {
  score: number;
  feedback?: string;
}

export const assignmentsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getAssignments: builder.query<
      PaginatedResponse<Assignment>,
      { course?: number } | void
    >({
      query: (params) => ({
        url: '/apis/assignments/',
        params: params || undefined,
      }),
      providesTags: [{ type: 'Assignment', id: 'LIST' }],
    }),

    getAssignment: builder.query<Assignment, number>({
      query: (id) => `/apis/assignments/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Assignment', id }],
    }),

    createAssignment: builder.mutation<
      Assignment,
      AssignmentCreatePayload
    >({
      query: (body) => ({
        url: '/apis/assignments/create/',
        method: 'POST',
        body,
      }),
      invalidatesTags: [{ type: 'Assignment', id: 'LIST' }],
    }),

    updateAssignment: builder.mutation<
      Assignment,
      { id: number; data: Partial<AssignmentCreatePayload> }
    >({
      query: ({ id, data }) => ({
        url: `/apis/assignments/${id}/update/`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { id }) => [
        { type: 'Assignment', id },
        { type: 'Assignment', id: 'LIST' },
      ],
    }),

    deleteAssignment: builder.mutation<void, number>({
      query: (id) => ({
        url: `/apis/assignments/${id}/delete/`,
        method: 'DELETE',
      }),
      invalidatesTags: [{ type: 'Assignment', id: 'LIST' }],
    }),

    // ── Submissions ──
    submitAssignment: builder.mutation<
      AssignmentSubmission,
      { assignmentId: number; data: AssignmentSubmitPayload }
    >({
      query: ({ assignmentId, data }) => ({
        url: `/apis/assignments/${assignmentId}/submit/`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { assignmentId }) => [
        { type: 'Submission', id: 'LIST' },
        { type: 'Assignment', id: assignmentId },
      ],
    }),

    getAssignmentSubmissions: builder.query<
      PaginatedResponse<AssignmentSubmission>,
      number
    >({
      query: (assignmentId) =>
        `/apis/assignments/${assignmentId}/submissions/`,
      providesTags: (result, error, id) => [
        { type: 'Submission', id: `assignment-${id}` },
      ],
    }),

    getMySubmissions: builder.query<
      PaginatedResponse<AssignmentSubmission>,
      void
    >({
      query: () => '/apis/submissions/',
      providesTags: [{ type: 'Submission', id: 'MY' }],
    }),

    gradeSubmission: builder.mutation<
      AssignmentSubmission,
      { submissionId: number; data: GradePayload }
    >({
      query: ({ submissionId, data }) => ({
        url: `/apis/submissions/${submissionId}/grade/`,
        method: 'PATCH',
        body: data,
      }),
      invalidatesTags: (result, error, { submissionId }) => [
        { type: 'Submission', id: submissionId },
        { type: 'Submission', id: 'LIST' },
        { type: 'Assignment', id: 'LIST' },
      ],
    }),
  }),
});

export const {
  useGetAssignmentsQuery,
  useGetAssignmentQuery,
  useCreateAssignmentMutation,
  useUpdateAssignmentMutation,
  useDeleteAssignmentMutation,
  useSubmitAssignmentMutation,
  useGetAssignmentSubmissionsQuery,
  useGetMySubmissionsQuery,
  useGradeSubmissionMutation,
} = assignmentsApi;
