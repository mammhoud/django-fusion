/**
 * Unit tests for the InstructorQuizPage (instructor quiz management).
 *
 * Covers:
 * - Loading state
 * - Quiz list rendering with titles, stats, action buttons
 * - Active/Draft status badges
 * - Filter buttons (All, Active, Draft)
 * - Empty state when no quizzes exist
 * - Create quiz inline form
 * - Delete quiz (window.confirm)
 * - Edit/Attempts links
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks
// ═══════════════════════════════════════════════════════════════════

const mockUseGetQuizzesQuery = vi.fn();
const mockUseCreateQuizMutation = vi.fn();
const mockUseDeleteQuizMutation = vi.fn();

const createMutationState = { isLoading: false };

vi.mock('@/store/api/endpoints/quiz', () => ({
  useGetQuizzesQuery: (...args: unknown[]) => mockUseGetQuizzesQuery(...args),
  useCreateQuizMutation: () => [mockUseCreateQuizMutation, createMutationState],
  useDeleteQuizMutation: () => [mockUseDeleteQuizMutation, { isLoading: false }],
}));

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => <a href={href} {...props}>{children}</a>,
}));

// ═══════════════════════════════════════════════════════════════════
// Test data
// ═══════════════════════════════════════════════════════════════════

const MOCK_QUIZZES = [
  {
    id: 1,
    title: 'React Fundamentals Quiz',
    is_active: true,
    course_title: 'React Fundamentals',
    question_count: 5,
    time_limit: 15,
    total_points: 20,
    description: 'Test your React knowledge.',
  },
  {
    id: 2,
    title: 'Python Basics Quiz',
    is_active: false,
    course_title: 'Introduction to Python',
    question_count: 3,
    time_limit: 0,
    total_points: 10,
    description: '',
  },
  {
    id: 3,
    title: 'Machine Learning Quiz',
    is_active: true,
    course_title: 'ML 101',
    question_count: 10,
    time_limit: 30,
    total_points: 50,
    description: 'Advanced ML concepts.',
  },
];

function createQuizResponse(quizzes: typeof MOCK_QUIZZES) {
  return {
    results: quizzes,
    count: quizzes.length,
    next: null,
    previous: null,
  };
}

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

import InstructorQuizPage from '@/app/dashboard/quiz/instructor';

function renderPage() {
  return render(
    <Provider store={createTestStore()}>
      <InstructorQuizPage />
    </Provider>,
  );
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('InstructorQuizPage - Loading State', () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it('shows loading skeleton while quizzes are loading', () => {
    mockUseGetQuizzesQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
    });

    const { container } = renderPage();
    expect(container.querySelector('.animate-pulse')).toBeTruthy();
  });
});

describe('InstructorQuizPage - Quiz List', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetQuizzesQuery.mockReturnValue({
      data: createQuizResponse(MOCK_QUIZZES),
      isLoading: false,
    });
  });

  it('renders the page heading with quiz count', () => {
    renderPage();
    expect(screen.getByText('Quiz Management')).toBeInTheDocument();
    expect(screen.getByText('3 quizzes')).toBeInTheDocument();
  });

  it('renders all quiz titles', () => {
    renderPage();
    expect(screen.getByText('React Fundamentals Quiz')).toBeInTheDocument();
    expect(screen.getByText('Python Basics Quiz')).toBeInTheDocument();
    expect(screen.getByText('Machine Learning Quiz')).toBeInTheDocument();
  });

  it('renders course titles on quiz cards', () => {
    renderPage();
    expect(screen.getByText('React Fundamentals')).toBeInTheDocument();
    expect(screen.getByText('Introduction to Python')).toBeInTheDocument();
    expect(screen.getByText('ML 101')).toBeInTheDocument();
  });

  it('renders status badges (Active/Draft)', () => {
    renderPage();
    // Filter buttons also contain 'Active' and 'Draft', so use a more specific query —
    // only status badges within quiz cards have the bg-green or bg-yellow classes
    const badges = document.querySelectorAll('span.bg-green-100, span.bg-yellow-100');
    expect(badges.length).toBe(3);
    expect(badges[0]).toHaveTextContent('Active');
    expect(badges[1]).toHaveTextContent('Draft');
    expect(badges[2]).toHaveTextContent('Active');
  });

  it('renders question count, time limit, and total points for each quiz', () => {
    renderPage();
    expect(screen.getByText(/5 questions/)).toBeInTheDocument();
    expect(screen.getByText(/15 min/)).toBeInTheDocument();
    expect(screen.getByText(/20 pts/)).toBeInTheDocument();

    expect(screen.getByText(/3 questions/)).toBeInTheDocument();
    expect(screen.getByText(/No min/)).toBeInTheDocument();
    expect(screen.getByText(/10 pts/)).toBeInTheDocument();

    expect(screen.getByText(/10 questions/)).toBeInTheDocument();
    expect(screen.getByText(/30 min/)).toBeInTheDocument();
    expect(screen.getByText(/50 pts/)).toBeInTheDocument();
  });

  it('renders Edit and Delete action buttons for each quiz', () => {
    renderPage();
    // Edit links should exist (check href)
    const editLinks = document.querySelectorAll('a[href*="/edit"]');
    expect(editLinks.length).toBe(3);

    // Delete buttons should exist
    const deleteButtons = screen.getAllByRole('button').filter(
      (btn) => btn.querySelector('svg'), // Has an icon
    );
    expect(deleteButtons.length).toBeGreaterThanOrEqual(3);
  });
});

describe('InstructorQuizPage - Filters', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetQuizzesQuery.mockReturnValue({
      data: createQuizResponse(MOCK_QUIZZES),
      isLoading: false,
    });
  });

  it('shows filter buttons: All, Active, Draft', () => {
    renderPage();
    expect(screen.getByText('All')).toBeInTheDocument();
    // Filter buttons and status badges both contain 'Active'/'Draft' — use getAllByText
    const activeElements = screen.getAllByText('Active');
    expect(activeElements.length).toBeGreaterThanOrEqual(1);
    const draftElements = screen.getAllByText('Draft');
    expect(draftElements.length).toBeGreaterThanOrEqual(1);
  });

  it('defaults to All filter showing all quizzes', () => {
    renderPage();
    expect(screen.getByText('React Fundamentals Quiz')).toBeInTheDocument();
    expect(screen.getByText('Python Basics Quiz')).toBeInTheDocument();
    expect(screen.getByText('Machine Learning Quiz')).toBeInTheDocument();
  });

  it('filters to show only active quizzes when Active filter is clicked', () => {
    renderPage();
    // Use getAllByText to find the Active filter button specifically
    const activeButtons = screen.getAllByText('Active');
    // The Active filter button should come before any badge, click the first one
    fireEvent.click(activeButtons[0]);

    expect(screen.getByText('React Fundamentals Quiz')).toBeInTheDocument();
    expect(screen.getByText('Machine Learning Quiz')).toBeInTheDocument();
    expect(screen.queryByText('Python Basics Quiz')).not.toBeInTheDocument();
  });

  it('filters to show only draft quizzes when Draft filter is clicked', () => {
    renderPage();
    const draftButtons = screen.getAllByText('Draft');
    // The Draft filter button should be before any badge, click the first one
    fireEvent.click(draftButtons[0]);

    expect(screen.queryByText('React Fundamentals Quiz')).not.toBeInTheDocument();
    expect(screen.queryByText('Machine Learning Quiz')).not.toBeInTheDocument();
    expect(screen.getByText('Python Basics Quiz')).toBeInTheDocument();
  });
});

describe('InstructorQuizPage - Empty State', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetQuizzesQuery.mockReturnValue({
      data: createQuizResponse([]),
      isLoading: false,
    });
  });

  it('shows empty state when no quizzes exist', () => {
    renderPage();
    expect(screen.getByText('No quizzes yet')).toBeInTheDocument();
    expect(
      screen.getByText('Create your first quiz to get started.'),
    ).toBeInTheDocument();
  });
});

describe('InstructorQuizPage - Create Quiz', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetQuizzesQuery.mockReturnValue({
      data: createQuizResponse(MOCK_QUIZZES),
      isLoading: false,
    });
  });

  it('shows create quiz inline form when Create Quiz is clicked', () => {
    renderPage();
    fireEvent.click(screen.getByText('Create Quiz'));

    expect(screen.getByPlaceholderText('Enter quiz title...')).toBeInTheDocument();
    expect(screen.getByText('Create')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('calls createQuiz mutation with the title', async () => {
    const unwrapFn = vi.fn().mockResolvedValue({ status: 'success', data: { id: 4 } });
    mockUseCreateQuizMutation.mockReturnValue({ unwrap: unwrapFn });
    createMutationState.isLoading = false;

    renderPage();
    fireEvent.click(screen.getByText('Create Quiz'));

    const input = screen.getByPlaceholderText('Enter quiz title...');
    fireEvent.change(input, { target: { value: 'New Quiz Title' } });

    fireEvent.click(screen.getByText('Create'));

    await vi.waitFor(() => {
      expect(mockUseCreateQuizMutation).toHaveBeenCalledWith({
        title: 'New Quiz Title',
      });
    });
  });

  it('closes the create form when Cancel is clicked', () => {
    renderPage();
    fireEvent.click(screen.getByText('Create Quiz'));
    expect(screen.getByPlaceholderText('Enter quiz title...')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Cancel'));
    expect(
      screen.queryByPlaceholderText('Enter quiz title...'),
    ).not.toBeInTheDocument();
  });

  it('submits on Enter key press', async () => {
    const unwrapFn = vi.fn().mockResolvedValue({ status: 'success', data: { id: 4 } });
    mockUseCreateQuizMutation.mockReturnValue({ unwrap: unwrapFn });
    createMutationState.isLoading = false;

    renderPage();
    fireEvent.click(screen.getByText('Create Quiz'));

    const input = screen.getByPlaceholderText('Enter quiz title...');
    fireEvent.change(input, { target: { value: 'Quick Quiz' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await vi.waitFor(() => {
      expect(mockUseCreateQuizMutation).toHaveBeenCalledWith({
        title: 'Quick Quiz',
      });
    });
  });

  it('does not create quiz with empty title', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Create Quiz'));

    const input = screen.getByPlaceholderText('Enter quiz title...');
    fireEvent.change(input, { target: { value: '   ' } });
    fireEvent.click(screen.getByText('Create'));

    await vi.waitFor(() => {
      expect(mockUseCreateQuizMutation).not.toHaveBeenCalled();
    });
  });
});

describe('InstructorQuizPage - Delete Quiz', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockUseGetQuizzesQuery.mockReturnValue({
      data: createQuizResponse([MOCK_QUIZZES[0]]),
      isLoading: false,
    });
  });

  it('calls deleteQuiz when confirm is accepted', async () => {
    const unwrapFn = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseDeleteQuizMutation.mockReturnValue({ unwrap: unwrapFn });

    // Mock window.confirm to return true
    const originalConfirm = window.confirm;
    window.confirm = vi.fn().mockReturnValue(true);

    renderPage();

    // Find the quiz card's delete button — filter non-link buttons with SVG icons
    const allBtns = screen.getAllByRole('button').filter(
      (btn) => btn.querySelector('svg') && !btn.closest('a'),
    );
    // With only one quiz, the last non-link button with an SVG is the delete button
    const deleteButton = allBtns[allBtns.length - 1];

    fireEvent.click(deleteButton);

    await vi.waitFor(() => {
      expect(window.confirm).toHaveBeenCalled();
    });
    expect(mockUseDeleteQuizMutation).toHaveBeenCalledWith(1);

    window.confirm = originalConfirm;
  });

  it('does not delete quiz when confirm is declined', async () => {
    const unwrapFn = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseDeleteQuizMutation.mockReturnValue({ unwrap: unwrapFn });

    const originalConfirm = window.confirm;
    window.confirm = vi.fn().mockReturnValue(false);

    renderPage();

    // Find delete button the same way
    const allBtns = screen.getAllByRole('button').filter(
      (btn) => btn.querySelector('svg') && !btn.closest('a'),
    );
    const deleteButton = allBtns[allBtns.length - 1];

    fireEvent.click(deleteButton);

    await vi.waitFor(() => {
      expect(window.confirm).toHaveBeenCalled();
    });
    expect(mockUseDeleteQuizMutation).not.toHaveBeenCalled();

    window.confirm = originalConfirm;
  });
});
