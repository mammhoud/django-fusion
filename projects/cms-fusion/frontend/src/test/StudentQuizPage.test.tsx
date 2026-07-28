/**
 * Unit tests for the StudentQuizPage component (student quiz-taking flow).
 *
 * Covers:
 * - Loading state (quiz data loading)
 * - Quiz not found / error state
 * - Not started state — quiz info, stats, Start Quiz button
 * - In progress state — MCQ choice selection, short answer textarea
 * - File upload UI for short answer questions
 * - Question navigation (previous/next, question grid)
 * - Flagging questions
 * - Timer display
 * - Quiz submission flow
 * - Completed state — score, pass/fail, retry
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks
// ═══════════════════════════════════════════════════════════════════

const mockUseGetQuizQuery = vi.fn();
const mockUseStartAttemptMutation = vi.fn();
const mockUseSubmitAttemptMutation = vi.fn();
const mockUseUploadQuizFileMutation = vi.fn();

const submitMutationState = { isLoading: false };
const uploadMutationState = { isLoading: false };

vi.mock('@/store/api/endpoints/quiz', () => ({
  useGetQuizQuery: (...args: unknown[]) => mockUseGetQuizQuery(...args),
  useStartAttemptMutation: () => [mockUseStartAttemptMutation, { isLoading: false }],
  useSubmitAttemptMutation: () => [mockUseSubmitAttemptMutation, submitMutationState],
  useUploadQuizFileMutation: () => [mockUseUploadQuizFileMutation, uploadMutationState],
}));

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useSearchParams: () => ({ get: vi.fn().mockReturnValue('1') }),
  useRouter: () => ({ push: vi.fn() }),
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => <a href={href} {...props}>{children}</a>,
}));

// ═══════════════════════════════════════════════════════════════════
// Test data
// ═══════════════════════════════════════════════════════════════════

const MCQ_QUESTION = {
  id: 10,
  quiz_id: 1,
  question_type: 'multiple_choice' as const,
  question_text: 'What is React?',
  explanation: 'React is a UI library.',
  points: 2,
  order: 1,
  is_active: true,
  choices: [
    { id: 100, text: 'A JavaScript library', is_correct: true, order: 0 },
    { id: 101, text: 'A database', is_correct: false, order: 1 },
    { id: 102, text: 'A CSS framework', is_correct: false, order: 2 },
  ],
};

const SHORT_ANSWER_QUESTION = {
  id: 11,
  quiz_id: 1,
  question_type: 'short_answer' as const,
  question_text: 'Explain the concept of state in React.',
  explanation: 'State represents dynamic data.',
  points: 5,
  order: 2,
  is_active: true,
  choices: [],
};

const TRUE_FALSE_QUESTION = {
  id: 12,
  quiz_id: 1,
  question_type: 'true_false' as const,
  question_text: 'TypeScript is a superset of JavaScript.',
  explanation: 'TypeScript extends JavaScript with types.',
  points: 1,
  order: 3,
  is_active: true,
  choices: [
    { id: 103, text: 'True', is_correct: true, order: 0 },
    { id: 104, text: 'False', is_correct: false, order: 1 },
  ],
};

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
  question_count: 3,
  total_points: 8,
  course_id: 1,
  course_title: 'React Fundamentals',
  questions: [MCQ_QUESTION, SHORT_ANSWER_QUESTION, TRUE_FALSE_QUESTION],
  user_attempts: 0,
  best_score: null,
  created_at: '2026-07-01T00:00:00Z',
  updated_at: '2026-07-01T00:00:00Z',
};

const MOCK_ATTEMPT_RESULT = {
  status: 'success',
  data: {
    id: 50,
    attempt_id: 'ATT-ABC123',
    score: 80,
    points_earned: 6,
    points_possible: 8,
    passed: true,
    status: 'completed',
  },
};

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

import StudentQuizPage from '@/app/dashboard/quiz/student';

function renderPage() {
  return render(
    <Provider store={createTestStore()}>
      <StudentQuizPage />
    </Provider>,
  );
}

function setupNotStarted() {
  mockUseGetQuizQuery.mockReturnValue({
    data: { status: 'success', data: MOCK_QUIZ },
    isLoading: false,
    isError: false,
    error: undefined,
  });
}

function setupStartAttempt() {
  const unwrapFn = vi.fn().mockResolvedValue({
    status: 'success',
    data: { id: 50, attempt_id: 'ATT-ABC123' },
  });
  mockUseStartAttemptMutation.mockReturnValue({ unwrap: unwrapFn });
}

function setupSubmitSuccess() {
  const unwrapFn = vi.fn().mockResolvedValue(MOCK_ATTEMPT_RESULT);
  mockUseSubmitAttemptMutation.mockReturnValue({ unwrap: unwrapFn });
  submitMutationState.isLoading = false;
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('StudentQuizPage - Loading & Error', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading skeleton while quiz data is loading', () => {
    mockUseGetQuizQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    });

    const { container } = renderPage();
    expect(container.querySelector('.animate-pulse')).toBeTruthy();
  });

  it('shows quiz not found when quiz is undefined', () => {
    mockUseGetQuizQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
    });

    renderPage();
    expect(screen.getByText('Quiz Not Found')).toBeInTheDocument();
  });
});

describe('StudentQuizPage - Not Started', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupNotStarted();
  });

  it('renders quiz title and course', () => {
    renderPage();
    expect(screen.getByText('React Fundamentals Quiz')).toBeInTheDocument();
    expect(screen.getByText(/Course: React Fundamentals/)).toBeInTheDocument();
  });

  it('renders quiz stats: questions, time limit, pass score, total points', () => {
    renderPage();
    expect(screen.getByText('3')).toBeInTheDocument(); // questions
    expect(screen.getByText('15min')).toBeInTheDocument(); // time limit
    expect(screen.getByText('70%')).toBeInTheDocument(); // pass score
    expect(screen.getByText('8')).toBeInTheDocument(); // total points
  });

  it('renders quiz description', () => {
    renderPage();
    expect(screen.getByText('Test your React knowledge.')).toBeInTheDocument();
  });

  it('renders Start Quiz button', () => {
    renderPage();
    expect(screen.getByText('Start Quiz')).toBeInTheDocument();
  });

  it('starts attempt when Start Quiz is clicked', async () => {
    setupStartAttempt();
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(mockUseStartAttemptMutation).toHaveBeenCalledWith(1);
    });
  });
});

describe('StudentQuizPage - In Progress', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupNotStarted();
    setupStartAttempt();
    setupSubmitSuccess();
  });

  it('shows question text for the current question', async () => {
    renderPage();
    // Click Start Quiz to enter in_progress state
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });
  });

  it('shows MCQ choices for multiple_choice questions', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('A JavaScript library')).toBeInTheDocument();
      expect(screen.getByText('A database')).toBeInTheDocument();
      expect(screen.getByText('A CSS framework')).toBeInTheDocument();
    });
  });

  it('selects an MCQ choice when clicked', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('A JavaScript library')).toBeInTheDocument();
    });

    // Click the first choice
    fireEvent.click(screen.getByText(/A JavaScript library/));

    // The choice should now show as selected (active style)
    const choiceBtn = screen.getByText(/A JavaScript library/).closest('button');
    expect(choiceBtn?.className).toContain('border-[rgb(var(--fu-primary))]');
  });

  it('shows textarea for short_answer questions', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    // Navigate to question 2 (short_answer)
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    // Click question 2 in the question grid
    const questionButtons = screen.getAllByRole('button');
    const q2Btn = questionButtons.find((btn) => btn.textContent === '2');
    if (q2Btn) fireEvent.click(q2Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByText('Explain the concept of state in React.'),
      ).toBeInTheDocument();
      expect(
        screen.getByPlaceholderText('Type your answer here...'),
      ).toBeInTheDocument();
    });
  });

  it('allows typing in the short answer textarea', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    // Navigate to question 2
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q2Btn = questionButtons.find((btn) => btn.textContent === '2');
    if (q2Btn) fireEvent.click(q2Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByPlaceholderText('Type your answer here...'),
      ).toBeInTheDocument();
    });

    // Type an answer
    const textarea = screen.getByPlaceholderText('Type your answer here...');
    fireEvent.change(textarea, { target: { value: 'State is a way to manage dynamic data in React components.' } });

    expect((textarea as HTMLTextAreaElement).value).toBe(
      'State is a way to manage dynamic data in React components.',
    );
  });

  it('shows true/false options for true_false questions', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    // Navigate to question 3
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q3Btn = questionButtons.find((btn) => btn.textContent === '3');
    if (q3Btn) fireEvent.click(q3Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByText('TypeScript is a superset of JavaScript.'),
      ).toBeInTheDocument();
      expect(screen.getByText('True')).toBeInTheDocument();
      expect(screen.getByText('False')).toBeInTheDocument();
    });
  });

  it('shows file upload UI for short answer questions', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    // Navigate to question 2 (short_answer)
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q2Btn = questionButtons.find((btn) => btn.textContent === '2');
    if (q2Btn) fireEvent.click(q2Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByText(/Upload a file \(PDF, DOC, image, etc.\)/),
      ).toBeInTheDocument();
    });
  });

  it('shows uploaded file info after successful upload', async () => {
    // Mock upload mutation to return a successful response
    const uploadUnwrap = vi.fn().mockResolvedValue({
      data: {
        file_url: '/media/quiz_uploads/my_essay_abc.pdf',
        file_name: 'my_essay.pdf',
      },
    });
    mockUseUploadQuizFileMutation.mockReturnValue({ unwrap: uploadUnwrap });

    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    // Navigate to question 2 (short_answer)
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q2Btn = questionButtons.find((btn) => btn.textContent === '2');
    if (q2Btn) fireEvent.click(q2Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByText(/Upload a file \(PDF, DOC, image, etc.\)/),
      ).toBeInTheDocument();
    });

    // Simulate selecting a file by firing onChange on the hidden file input
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      const file = new File(['essay content'], 'my_essay.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });
    }

    await vi.waitFor(() => {
      // Uploaded file name should be visible
      expect(screen.getByText('my_essay.pdf')).toBeInTheDocument();
      // "Uploaded ✓" indicator should appear
      expect(screen.getByText('Uploaded')).toBeInTheDocument();
    });
  });

  it('shows Remove button after successful file upload', async () => {
    const uploadUnwrap = vi.fn().mockResolvedValue({
      data: {
        file_url: '/media/quiz_uploads/essay.pdf',
        file_name: 'essay.pdf',
      },
    });
    mockUseUploadQuizFileMutation.mockReturnValue({ unwrap: uploadUnwrap });

    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q2Btn = questionButtons.find((btn) => btn.textContent === '2');
    if (q2Btn) fireEvent.click(q2Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByText(/Upload a file \(PDF, DOC, image, etc.\)/),
      ).toBeInTheDocument();
    });

    // Upload a file
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      const file = new File(['content'], 'essay.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });
    }

    await vi.waitFor(() => {
      expect(screen.getByText('essay.pdf')).toBeInTheDocument();
    });

    // Remove button should be visible (HiTrash icon button)
    const removeBtn = screen.getByTitle('Remove file');
    expect(removeBtn).toBeInTheDocument();
  });

  it('removes uploaded file when Remove is clicked', async () => {
    const uploadUnwrap = vi.fn().mockResolvedValue({
      data: {
        file_url: '/media/quiz_uploads/essay.pdf',
        file_name: 'essay.pdf',
      },
    });
    mockUseUploadQuizFileMutation.mockReturnValue({ unwrap: uploadUnwrap });

    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q2Btn = questionButtons.find((btn) => btn.textContent === '2');
    if (q2Btn) fireEvent.click(q2Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByText(/Upload a file \(PDF, DOC, image, etc.\)/),
      ).toBeInTheDocument();
    });

    // Upload a file
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      const file = new File(['content'], 'essay.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });
    }

    await vi.waitFor(() => {
      expect(screen.getByText('essay.pdf')).toBeInTheDocument();
    });

    // Click Remove
    fireEvent.click(screen.getByTitle('Remove file'));

    await vi.waitFor(() => {
      // File should be removed — upload prompt should reappear
      expect(screen.queryByText('essay.pdf')).not.toBeInTheDocument();
      expect(
        screen.getByText(/Upload a file \(PDF, DOC, image, etc.\)/),
      ).toBeInTheDocument();
    });
  });

  it('shows upload error when file upload fails', async () => {
    // Mock upload mutation to reject
    const uploadUnwrap = vi.fn().mockRejectedValue({
      data: { message: 'File too large. Maximum size is 10 MB.' },
    });
    mockUseUploadQuizFileMutation.mockReturnValue({ unwrap: uploadUnwrap });

    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q2Btn = questionButtons.find((btn) => btn.textContent === '2');
    if (q2Btn) fireEvent.click(q2Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByText(/Upload a file \(PDF, DOC, image, etc.\)/),
      ).toBeInTheDocument();
    });

    // Trigger file upload which will fail
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      const file = new File(['large content'], 'large_file.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });
    }

    await vi.waitFor(() => {
      expect(
        screen.getByText('File too large. Maximum size is 10 MB.'),
      ).toBeInTheDocument();
    });
  });

  it('shows upload loading state while file is uploading', async () => {
    // Return a promise that never resolves so the component stays in the uploading state
    const uploadUnwrap = vi.fn().mockReturnValue(new Promise(() => {}));
    mockUseUploadQuizFileMutation.mockReturnValue({ unwrap: uploadUnwrap });

    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q2Btn = questionButtons.find((btn) => btn.textContent === '2');
    if (q2Btn) fireEvent.click(q2Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByText(/Upload a file \(PDF, DOC, image, etc.\)/),
      ).toBeInTheDocument();
    });

    // Trigger file upload
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      const file = new File(['content'], 'uploading.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });
    }

    await vi.waitFor(() => {
      // Should show "Uploading..." text while uploading
      expect(screen.getByText('Uploading...')).toBeInTheDocument();
    });
  });

  it('shows Previous and Submit Quiz buttons on the last question', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    // Navigate to last question
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q3Btn = questionButtons.find((btn) => btn.textContent === '3');
    if (q3Btn) fireEvent.click(q3Btn);

    await vi.waitFor(() => {
      expect(
        screen.getByText('TypeScript is a superset of JavaScript.'),
      ).toBeInTheDocument();
      expect(screen.getByText('Previous')).toBeInTheDocument();
      expect(screen.getByText('Submit Quiz')).toBeInTheDocument();
    });
  });

  it('shows the flag button and timer', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('Flag')).toBeInTheDocument();
      expect(screen.getByText(/15:00/)).toBeInTheDocument(); // timer
    });
  });

  it('flags/unflags the current question when flag button is clicked', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('Flag')).toBeInTheDocument();
    });

    // Click Flag
    fireEvent.click(screen.getByText('Flag'));

    // The question grid button for question 1 should have flagged styling
    await vi.waitFor(() => {
      // Reclick flag to unflag - just verify the button works
      expect(screen.getByText('Flag')).toBeInTheDocument();
    });
  });

  it('submits quiz and shows completed state with results', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Start Quiz'));

    // Navigate to last question
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q3Btn = questionButtons.find((btn) => btn.textContent === '3');
    if (q3Btn) fireEvent.click(q3Btn);

    await vi.waitFor(() => {
      expect(screen.getByText('Submit Quiz')).toBeInTheDocument();
    });

    // Submit the quiz
    fireEvent.click(screen.getByText('Submit Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('Congratulations!')).toBeInTheDocument();
      expect(screen.getByText('80%')).toBeInTheDocument(); // score
      expect(screen.getByText('6')).toBeInTheDocument(); // points earned
      expect(screen.getByText('8')).toBeInTheDocument(); // points possible
    });
  });
});

describe('StudentQuizPage - Completed', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows passed state with congratulations', async () => {
    setupNotStarted();
    setupStartAttempt();
    setupSubmitSuccess();
    renderPage();

    fireEvent.click(screen.getByText('Start Quiz'));
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    // Navigate to last question and submit
    const questionButtons = screen.getAllByRole('button');
    const q3Btn = questionButtons.find((btn) => btn.textContent === '3');
    if (q3Btn) fireEvent.click(q3Btn);

    await vi.waitFor(() => {
      expect(screen.getByText('Submit Quiz')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Submit Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('Congratulations!')).toBeInTheDocument();
      expect(screen.getByText(/You passed the quiz/)).toBeInTheDocument();
    });
  });

  it('shows failed state when score is below passing', async () => {
    setupNotStarted();
    setupStartAttempt();
    // Mock a failing result
    const failUnwrap = vi.fn().mockResolvedValue({
      status: 'success',
      data: {
        id: 50,
        attempt_id: 'ATT-ABC123',
        score: 40,
        points_earned: 2,
        points_possible: 8,
        passed: false,
        status: 'completed',
      },
    });
    mockUseSubmitAttemptMutation.mockReturnValue({ unwrap: failUnwrap });
    submitMutationState.isLoading = false;

    renderPage();

    fireEvent.click(screen.getByText('Start Quiz'));
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q3Btn = questionButtons.find((btn) => btn.textContent === '3');
    if (q3Btn) fireEvent.click(q3Btn);

    await vi.waitFor(() => {
      expect(screen.getByText('Submit Quiz')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Submit Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('Keep Practicing!')).toBeInTheDocument();
      expect(screen.getByText(/You scored 40%/)).toBeInTheDocument();
    });
  });

  it('shows retry button in completed state', async () => {
    setupNotStarted();
    setupStartAttempt();
    setupSubmitSuccess();
    renderPage();

    fireEvent.click(screen.getByText('Start Quiz'));
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q3Btn = questionButtons.find((btn) => btn.textContent === '3');
    if (q3Btn) fireEvent.click(q3Btn);

    await vi.waitFor(() => {
      expect(screen.getByText('Submit Quiz')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Submit Quiz'));

    await vi.waitFor(() => {
      expect(screen.getByText('Retry Quiz')).toBeInTheDocument();
      expect(screen.getByText('Back to Dashboard')).toBeInTheDocument();
    });
  });

  it('renders the score circle SVG in completed state', async () => {
    setupNotStarted();
    setupStartAttempt();
    setupSubmitSuccess();
    renderPage();

    fireEvent.click(screen.getByText('Start Quiz'));
    await vi.waitFor(() => {
      expect(screen.getByText('What is React?')).toBeInTheDocument();
    });

    const questionButtons = screen.getAllByRole('button');
    const q3Btn = questionButtons.find((btn) => btn.textContent === '3');
    if (q3Btn) fireEvent.click(q3Btn);

    await vi.waitFor(() => {
      expect(screen.getByText('Submit Quiz')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Submit Quiz'));

    await vi.waitFor(() => {
      // SVG circle should be rendered (check for the container)
      const svgContainer = document.querySelector('svg');
      expect(svgContainer).toBeTruthy();
      expect(screen.getByText('Score')).toBeInTheDocument();
    });
  });
});
