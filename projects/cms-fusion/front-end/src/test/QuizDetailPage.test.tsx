/**
 * Unit tests for the QuizDetailPage component.
 *
 * Covers:
 * - Loading state
 * - Quiz not found / error state
 * - Student view: header, stats, Start Quiz, question preview, best score
 * - Instructor view: header, stats, settings summary, Edit Quiz link, View Attempts link
 * - Inactive quiz badge display
 * - Description display
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks
// ═══════════════════════════════════════════════════════════════════

const mockUseGetProfileQuery = vi.fn();
const mockUseGetQuizQuery = vi.fn();

vi.mock('@/store/api/endpoints/auth', () => ({
  useGetProfileQuery: (...args: unknown[]) => mockUseGetProfileQuery(...args),
}));

vi.mock('@/store/api/endpoints/quiz', () => ({
  useGetQuizQuery: (...args: unknown[]) => mockUseGetQuizQuery(...args),
}));

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useParams: () => ({ id: '1' }),
  useRouter: () => ({ push: vi.fn() }),
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => <a href={href} {...props}>{children}</a>,
}));

// ═══════════════════════════════════════════════════════════════════
// Test data
// ═══════════════════════════════════════════════════════════════════

const MOCK_QUESTIONS = [
  {
    id: 10,
    quiz_id: 1,
    question_type: 'multiple_choice',
    question_text: 'What is React?',
    explanation: 'React is a UI library.',
    points: 2,
    order: 1,
    is_active: true,
    choices: [{ id: 100, text: 'A JS library', is_correct: true, order: 0 }],
  },
  {
    id: 11,
    quiz_id: 1,
    question_type: 'short_answer',
    question_text: 'Explain state in React.',
    explanation: 'State is dynamic data.',
    points: 5,
    order: 2,
    is_active: true,
    choices: [],
  },
];

const MOCK_QUIZ = {
  id: 1,
  title: 'React Fundamentals Quiz',
  description: 'Test your React knowledge.',
  passing_score: 70,
  time_limit: 15,
  max_attempts: 3,
  shuffle_questions: false,
  show_correct_answers: true,
  is_active: true,
  question_count: 2,
  total_points: 7,
  course_id: 1,
  course_title: 'React Fundamentals',
  questions: MOCK_QUESTIONS,
  user_attempts: 2,
  best_score: 85,
  created_at: '2026-07-01T00:00:00Z',
  updated_at: '2026-07-01T00:00:00Z',
};

const STUDENT_PROFILE = { id: 1, username: 'student1', role: 'student' };
const INSTRUCTOR_PROFILE = { id: 2, username: 'instructor1', role: 'instructor' };

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

import QuizDetailPage from '@/app/dashboard/quiz/[id]/page';

function renderPage() {
  return render(
    <Provider store={createTestStore()}>
      <QuizDetailPage />
    </Provider>,
  );
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('QuizDetailPage - Loading & Error', () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it('shows loading skeleton while data is loading', () => {
    mockUseGetProfileQuery.mockReturnValue({ data: undefined, isLoading: true });
    mockUseGetQuizQuery.mockReturnValue({ data: undefined, isLoading: false });

    const { container } = renderPage();
    expect(container.querySelector('.animate-pulse')).toBeTruthy();
  });

  it('shows quiz not found when quiz is undefined', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: STUDENT_PROFILE,
      isLoading: false,
    });
    mockUseGetQuizQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
    });

    renderPage();
    expect(screen.getByText('Quiz not found.')).toBeInTheDocument();
  });
});

describe('QuizDetailPage - Student View', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetProfileQuery.mockReturnValue({
      data: STUDENT_PROFILE,
      isLoading: false,
    });
    mockUseGetQuizQuery.mockReturnValue({
      data: { status: 'success', data: MOCK_QUIZ },
      isLoading: false,
      isError: false,
    });
  });

  it('renders quiz title and active badge', () => {
    renderPage();
    expect(screen.getByText('React Fundamentals Quiz')).toBeInTheDocument();
    expect(screen.getByText('Active')).toBeInTheDocument();
  });

  it('renders quiz description', () => {
    renderPage();
    expect(screen.getByText('Test your React knowledge.')).toBeInTheDocument();
  });

  it('renders stats: questions, time, pass score, total points', () => {
    renderPage();
    // Some stat values like '2' appear multiple times (questions count + attempts count)
    // Use getAllByText for values that may appear elsewhere
    const twos = screen.getAllByText('2');
    expect(twos.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('15')).toBeInTheDocument(); // minutes
    expect(screen.getByText('70%')).toBeInTheDocument(); // pass score
    const sevens = screen.getAllByText('7');
    expect(sevens.length).toBeGreaterThanOrEqual(1);
  });

  it('shows Start Quiz button for students', () => {
    renderPage();
    expect(screen.getByText('Start Quiz')).toBeInTheDocument();
  });

  it('shows My Attempts link with count for students with attempts', () => {
    renderPage();
    expect(screen.getByText('My Attempts (2)')).toBeInTheDocument();
  });

  it('shows best score for students with previous attempts', () => {
    renderPage();
    expect(screen.getByText(/Best score:/)).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });

  it('shows question preview for students', () => {
    renderPage();
    expect(screen.getByText('Question Preview')).toBeInTheDocument();
    expect(screen.getByText('What is React?')).toBeInTheDocument();
    expect(screen.getByText('Explain state in React.')).toBeInTheDocument();
  });

  it('shows question type labels in the preview', () => {
    renderPage();
    // Use regex matching since text is inline with other content (e.g. "Multiple Choice · 2 pts")
    expect(screen.getByText(/Multiple Choice/)).toBeInTheDocument();
    expect(screen.getByText(/Short Answer/)).toBeInTheDocument();
  });

  it('shows back to quizzes link', () => {
    renderPage();
    expect(screen.getByText('Back to Quizzes')).toBeInTheDocument();
  });
});

describe('QuizDetailPage - Instructor View', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetProfileQuery.mockReturnValue({
      data: INSTRUCTOR_PROFILE,
      isLoading: false,
    });
    mockUseGetQuizQuery.mockReturnValue({
      data: { status: 'success', data: MOCK_QUIZ },
      isLoading: false,
      isError: false,
    });
  });

  it('renders quiz title', () => {
    renderPage();
    expect(screen.getByText('React Fundamentals Quiz')).toBeInTheDocument();
  });

  it('shows Edit Quiz button for instructors', () => {
    renderPage();
    const editLink = screen.getByText('Edit Quiz');
    expect(editLink).toBeInTheDocument();
    expect(editLink.closest('a')).toHaveAttribute('href', '/dashboard/quiz/1/edit');
  });

  it('shows View Attempts button for instructors', () => {
    renderPage();
    const attemptsLink = screen.getByText('View Attempts');
    expect(attemptsLink).toBeInTheDocument();
  });

  it('shows Quiz Settings panel for instructors', () => {
    renderPage();
    expect(screen.getByText('Quiz Settings')).toBeInTheDocument();
    // max_attempts=3 (truthy), so UI shows '3' not 'Unlimited'
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('No')).toBeInTheDocument(); // shuffle_questions=false
    expect(screen.getByText('Yes')).toBeInTheDocument(); // show_correct_answers=true
  });

  it('shows Quick Actions panel with edit and review links', () => {
    renderPage();
    expect(screen.getByText('Quick Actions')).toBeInTheDocument();
    expect(screen.getByText(/Edit questions & settings/)).toBeInTheDocument();
    expect(screen.getByText(/Review student attempts/)).toBeInTheDocument();
  });

  it('does not show Start Quiz for instructors', () => {
    renderPage();
    expect(screen.queryByText('Start Quiz')).not.toBeInTheDocument();
  });

  it('does not show question preview for instructors', () => {
    renderPage();
    expect(screen.queryByText('Question Preview')).not.toBeInTheDocument();
  });
});

describe('QuizDetailPage - Inactive Quiz', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    const inactiveQuiz = {
      ...MOCK_QUIZ,
      is_active: false,
    };
    mockUseGetProfileQuery.mockReturnValue({
      data: INSTRUCTOR_PROFILE,
      isLoading: false,
    });
    mockUseGetQuizQuery.mockReturnValue({
      data: { status: 'success', data: inactiveQuiz },
      isLoading: false,
      isError: false,
    });
  });

  it('shows Draft badge instead of Active', () => {
    renderPage();
    expect(screen.getByText('Draft')).toBeInTheDocument();
    expect(screen.queryByText('Active')).not.toBeInTheDocument();
  });
});
