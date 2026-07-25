import { api, PaginatedResponse } from '../baseApi';

// ─── Types ──────────────────────────────────────────────────────────

export interface QuizChoice {
  id: number;
  text: string;
  is_correct: boolean | null;
  order: number;
}

export interface QuizQuestion {
  id: number;
  quiz_id: number;
  question_type: 'multiple_choice' | 'true_false' | 'short_answer' | 'multiple_select';
  question_text: string;
  explanation: string;
  points: number;
  order: number;
  is_active: boolean;
  choices: QuizChoice[];
}

export interface Quiz {
  id: number;
  title: string;
  description: string;
  passing_score: number;
  time_limit: number;
  max_attempts: number;
  shuffle_questions: boolean;
  show_correct_answers: boolean;
  is_active: boolean;
  question_count: number;
  total_points: number;
  course_id?: number;
  course_title?: string;
  module_title?: string;
  lesson_title?: string;
  questions?: QuizQuestion[];
  user_attempts: number;
  best_score: number | null;
  created_at: string;
  updated_at: string;
}

export interface QuizAttemptAnswer {
  id: number;
  question_id: number;
  question_text: string;
  question_type: string;
  selected_choice_ids: number[];
  text_answer: string;
  is_correct: boolean | null;
  points_awarded: number;
  points_possible: number;
}

export interface QuizAttempt {
  id: number;
  attempt_id: string;
  user_id: number;
  username: string;
  quiz_id: number;
  quiz_title: string;
  status: 'in_progress' | 'completed' | 'timed_out';
  score: number | null;
  points_earned: number;
  points_possible: number;
  passed: boolean | null;
  started_at: string;
  completed_at: string | null;
  time_spent: number;
  questions?: QuizQuestion[];
  answers?: QuizAttemptAnswer[];
}

// ─── Endpoints ──────────────────────────────────────────────────────

export const quizApi = api.injectEndpoints({
  endpoints: (builder) => ({
    // ── Quiz CRUD ──
    getQuizzes: builder.query<PaginatedResponse<Quiz>, { search?: string; course_id?: number }>({
      query: (params) => ({
        url: '/apis/quizzes/',
        params: { search: params.search, course_id: params.course_id },
      }),
      providesTags: ['Quiz'],
    }),
    getQuiz: builder.query<{ status: string; data: Quiz }, number>({
      query: (id) => `/apis/quizzes/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Quiz', id }],
    }),
    createQuiz: builder.mutation<{ status: string; data: Quiz }, Partial<Quiz>>({
      query: (body) => ({ url: '/apis/quizzes/create/', method: 'POST', body }),
      invalidatesTags: ['Quiz'],
    }),
    updateQuiz: builder.mutation<{ status: string; data: Quiz }, { id: number; data: Partial<Quiz> }>({
      query: ({ id, data }) => ({ url: `/apis/quizzes/${id}/update/`, method: 'PATCH', body: data }),
      invalidatesTags: (result, error, { id }) => [{ type: 'Quiz', id }, 'Quiz'],
    }),
    deleteQuiz: builder.mutation<void, number>({
      query: (id) => ({ url: `/apis/quizzes/${id}/delete/`, method: 'DELETE' }),
      invalidatesTags: ['Quiz'],
    }),

    // ── Questions ──
    createQuestion: builder.mutation<
      { status: string; data: QuizQuestion },
      { quiz_id: number; data: Partial<QuizQuestion> & { choices?: { text: string; is_correct: boolean }[] } }
    >({
      query: ({ quiz_id, data }) => ({
        url: `/apis/quizzes/${quiz_id}/questions/`,
        method: 'POST',
        body: data,
      }),
      invalidatesTags: (result, error, { quiz_id }) => [{ type: 'Quiz', id: quiz_id }, 'Quiz'],
    }),
    updateQuestion: builder.mutation<{ status: string; data: QuizQuestion }, { id: number; data: Partial<QuizQuestion> }>({
      query: ({ id, data }) => ({ url: `/apis/quizzes/questions/${id}/update/`, method: 'PATCH', body: data }),
      invalidatesTags: ['Quiz'],
    }),
    deleteQuestion: builder.mutation<void, number>({
      query: (id) => ({ url: `/apis/quizzes/questions/${id}/delete/`, method: 'DELETE' }),
      invalidatesTags: ['Quiz'],
    }),

    // ── Attempts ──
    startAttempt: builder.mutation<{ status: string; data: QuizAttempt }, number>({
      query: (quizId) => ({
        url: `/apis/quizzes/${quizId}/attempts/start/`,
        method: 'POST',
      }),
      invalidatesTags: ['Attempt'],
    }),
    submitAttempt: builder.mutation<
      { status: string; data: QuizAttempt },
      { attempt_id: number; answers: { question_id: number; selected_choice_id?: number; selected_choice_ids?: number[]; text_answer?: string }[] }
    >({
      query: ({ attempt_id, answers }) => ({
        url: `/apis/attempts/${attempt_id}/submit/`,
        method: 'POST',
        body: { answers },
      }),
      invalidatesTags: ['Attempt', 'Quiz'],
    }),
    getAttempts: builder.query<PaginatedResponse<QuizAttempt>, void>({
      query: () => '/apis/attempts/',
      providesTags: ['Attempt'],
    }),
    getAttempt: builder.query<{ status: string; data: QuizAttempt }, number>({
      query: (id) => `/apis/attempts/${id}/`,
      providesTags: (result, error, id) => [{ type: 'Attempt', id }],
    }),
    getQuizAttempts: builder.query<PaginatedResponse<QuizAttempt>, number>({
      query: (quizId) => `/apis/quizzes/${quizId}/attempts/`,
      providesTags: ['Attempt'],
    }),
    gradeAttempt: builder.mutation<
      { status: string; data: QuizAttempt },
      { attempt_id: number; graded_answers: { answer_id: number; is_correct: boolean; points_awarded: number }[] }
    >({
      query: ({ attempt_id, graded_answers }) => ({
        url: `/apis/attempts/${attempt_id}/grade/`,
        method: 'PATCH',
        body: { graded_answers },
      }),
      invalidatesTags: (result, error, { attempt_id }) => [{ type: 'Attempt', id: attempt_id }, 'Attempt'],
    }),
  }),
});

export const {
  useGetQuizzesQuery,
  useGetQuizQuery,
  useCreateQuizMutation,
  useUpdateQuizMutation,
  useDeleteQuizMutation,
  useCreateQuestionMutation,
  useUpdateQuestionMutation,
  useDeleteQuestionMutation,
  useStartAttemptMutation,
  useSubmitAttemptMutation,
  useGetAttemptsQuery,
  useGetAttemptQuery,
  useGetQuizAttemptsQuery,
  useGradeAttemptMutation,
} = quizApi;
