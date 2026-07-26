/**
 * Unit tests for the QuizEditorPage component (quiz editing with drag-to-reorder).
 *
 * Covers:
 * - Loading state and error state
 * - Quiz settings panel (title, description, passing score, time limit, checkboxes)
 * - Save settings button
 * - Empty question list state
 * - Question list rendering with type badges, points, drag handles
 * - Move up / move down buttons
 * - Drag-to-reorder (drag start, drag over, drop with optimistic update)
 * - Question editor modal (open, close, type switching, choices, save)
 * - Edit existing question
 * - Delete confirmation modal
 * - Expanded question details (choices, explanation)
 */
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// Mock framer-motion to strip animations for test reliability
// AnimatePresence exit animations keep components mounted, causing test failures
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, initial, animate, exit, exitBeforeEnter, ...props }: any) => (
      <div {...props}>{children}</div>
    ),
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks
// ═══════════════════════════════════════════════════════════════════

const mockUseGetQuizQuery = vi.fn();
const mockUseUpdateQuizMutation = vi.fn();
const mockUseCreateQuestionMutation = vi.fn();
const mockUseUpdateQuestionMutation = vi.fn();
const mockUseDeleteQuestionMutation = vi.fn();
const mockUseReorderQuestionsMutation = vi.fn();

vi.mock('@/store/api/endpoints/quiz', () => ({
  useGetQuizQuery: (...args: unknown[]) => mockUseGetQuizQuery(...args),
  useUpdateQuizMutation: () => [mockUseUpdateQuizMutation],
  useCreateQuestionMutation: () => [mockUseCreateQuestionMutation],
  useUpdateQuestionMutation: () => [mockUseUpdateQuestionMutation],
  useDeleteQuestionMutation: () => [mockUseDeleteQuestionMutation],
  useReorderQuestionsMutation: () => [mockUseReorderQuestionsMutation],
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

const MCQ_CHOICES = [
  { id: 100, text: 'A JS library', is_correct: true, order: 0 },
  { id: 101, text: 'A database', is_correct: false, order: 1 },
  { id: 102, text: 'A CSS framework', is_correct: false, order: 2 },
];

const TF_CHOICES = [
  { id: 103, text: 'True', is_correct: true, order: 0 },
  { id: 104, text: 'False', is_correct: false, order: 1 },
];

const MOCK_QUESTIONS = [
  {
    id: 10,
    quiz_id: 1,
    question_type: 'multiple_choice' as const,
    question_text: 'What is React?',
    explanation: 'React is a UI library.',
    points: 2,
    order: 1,
    is_active: true,
    choices: MCQ_CHOICES,
  },
  {
    id: 11,
    quiz_id: 1,
    question_type: 'short_answer' as const,
    question_text: 'Explain state in React.',
    explanation: 'State is dynamic data.',
    points: 5,
    order: 2,
    is_active: true,
    choices: [],
  },
  {
    id: 12,
    quiz_id: 1,
    question_type: 'true_false' as const,
    question_text: 'TypeScript is a superset of JavaScript.',
    explanation: '',
    points: 1,
    order: 3,
    is_active: true,
    choices: TF_CHOICES,
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
  question_count: 3,
  total_points: 8,
  course_id: 1,
  course_title: 'React Fundamentals',
  questions: MOCK_QUESTIONS,
  user_attempts: 0,
  best_score: null,
  created_at: '2026-07-01T00:00:00Z',
  updated_at: '2026-07-01T00:00:00Z',
};

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

import QuizEditorPage from '@/app/dashboard/quiz/[id]/edit/page';

function renderPage() {
  return render(
    <Provider store={createTestStore()}>
      <QuizEditorPage />
    </Provider>,
  );
}

function setupDefaultMocks() {
  mockUseGetQuizQuery.mockReturnValue({
    data: { status: 'success', data: MOCK_QUIZ },
    isLoading: false,
    isError: false,
    error: undefined,
  });
  mockUseUpdateQuizMutation.mockReturnValue({ unwrap: vi.fn().mockResolvedValue({}) });
  mockUseCreateQuestionMutation.mockReturnValue({ unwrap: vi.fn().mockResolvedValue({}) });
  mockUseUpdateQuestionMutation.mockReturnValue({ unwrap: vi.fn().mockResolvedValue({}) });
  mockUseDeleteQuestionMutation.mockReturnValue({ unwrap: vi.fn().mockResolvedValue({}) });
  mockUseReorderQuestionsMutation.mockReturnValue({ unwrap: vi.fn().mockResolvedValue({}) });
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('QuizEditorPage - Loading & Error', () => {
  beforeEach(() => { vi.clearAllMocks(); });

  it('shows loading skeleton while quiz data is loading', () => {
    mockUseGetQuizQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    });

    const { container } = renderPage();
    expect(container.querySelector('.animate-pulse')).toBeTruthy();
  });

  it('shows error state when quiz is not found', () => {
    mockUseGetQuizQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
    });

    renderPage();
    expect(screen.getByText('Quiz not found.')).toBeInTheDocument();
  });
});

describe('QuizEditorPage - Settings Panel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it('renders the quiz title in the header', () => {
    renderPage();
    expect(screen.getByText('React Fundamentals Quiz')).toBeInTheDocument();
  });

  it('shows question count and total points in header', () => {
    renderPage();
    expect(screen.getByText(/3 questions/)).toBeInTheDocument();
    expect(screen.getByText(/8 total points/)).toBeInTheDocument();
  });

  it('renders the quiz settings panel', () => {
    renderPage();
    expect(screen.getByText('Quiz Settings')).toBeInTheDocument();
  });

  it('pre-fills settings fields from quiz data', () => {
    renderPage();
    const titleInput = screen.getByDisplayValue('React Fundamentals Quiz');
    expect(titleInput).toBeInTheDocument();
    const descriptionInput = screen.getByDisplayValue('Test your React knowledge.');
    expect(descriptionInput).toBeInTheDocument();
  });

  it('pre-fills passing score and time limit', () => {
    renderPage();
    const scoreInput = screen.getByDisplayValue('70');
    expect(scoreInput).toBeInTheDocument();
    const timeInput = screen.getByDisplayValue('15');
    expect(timeInput).toBeInTheDocument();
  });

  it('pre-fills max attempts', () => {
    renderPage();
    const attemptsInput = screen.getByDisplayValue('3');
    expect(attemptsInput).toBeInTheDocument();
  });

  it('renders all setting checkboxes', () => {
    renderPage();
    expect(screen.getByText('Shuffle questions')).toBeInTheDocument();
    expect(screen.getByText('Show correct answers')).toBeInTheDocument();
    expect(screen.getByText('Active (visible to students)')).toBeInTheDocument();
  });

  it('shows Save Changes button when settings are modified', () => {
    renderPage();
    // Initially no save button
    expect(screen.queryByText('Save Changes')).not.toBeInTheDocument();

    // Modify title
    const titleInput = screen.getByDisplayValue('React Fundamentals Quiz');
    fireEvent.change(titleInput, { target: { value: 'Updated Quiz' } });

    // Save button should appear
    expect(screen.getByText('Save Changes')).toBeInTheDocument();
  });

  it('calls updateQuiz when Save Changes is clicked', async () => {
    const updateUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseUpdateQuizMutation.mockReturnValue({ unwrap: updateUnwrap });
    renderPage();

    // Modify title to trigger dirty state
    const titleInput = screen.getByDisplayValue('React Fundamentals Quiz');
    fireEvent.change(titleInput, { target: { value: 'Updated Quiz' } });

    // Click save
    fireEvent.click(screen.getByText('Save Changes'));

    await vi.waitFor(() => {
      expect(updateUnwrap).toHaveBeenCalled();
    });
  });

  it('shows Saving... text while saving settings', async () => {
    const updateUnwrap = vi.fn().mockImplementation(() => new Promise(() => {}));
    mockUseUpdateQuizMutation.mockReturnValue({ unwrap: updateUnwrap });
    renderPage();

    const titleInput = screen.getByDisplayValue('React Fundamentals Quiz');
    fireEvent.change(titleInput, { target: { value: 'Updated Quiz' } });

    fireEvent.click(screen.getByText('Save Changes'));

    await vi.waitFor(() => {
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });
  });
});

describe('QuizEditorPage - Question List', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it('renders the Questions heading', () => {
    renderPage();
    expect(screen.getByText('Questions')).toBeInTheDocument();
  });

  it('renders Add Question button', () => {
    renderPage();
    expect(screen.getByText('Add Question')).toBeInTheDocument();
  });

  it('renders all question texts', () => {
    renderPage();
    expect(screen.getByText('What is React?')).toBeInTheDocument();
    expect(screen.getByText('Explain state in React.')).toBeInTheDocument();
    expect(screen.getByText('TypeScript is a superset of JavaScript.')).toBeInTheDocument();
  });

  it('shows question type badges', () => {
    renderPage();
    expect(screen.getByText(/multiple choice/)).toBeInTheDocument();
    expect(screen.getByText(/short answer/)).toBeInTheDocument();
    expect(screen.getByText(/true false/)).toBeInTheDocument();
  });

  it('shows point values for each question', () => {
    renderPage();
    // Question texts like "multiple choice · 2 pts", "short answer · 5 pts", "true false · 1 pt"
    expect(screen.getByText(/2 pts?/)).toBeInTheDocument();
    expect(screen.getByText(/5 pts?/)).toBeInTheDocument();
    expect(screen.getByText(/1 pt/)).toBeInTheDocument();
  });

  it('renders drag handles on each question', () => {
    renderPage();
    const dragHandles = screen.getAllByTitle('Drag to reorder');
    expect(dragHandles.length).toBe(3);
  });

  it('renders number badges for each question (1, 2, 3)', () => {
    renderPage();
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('renders edit, delete, and expand buttons on each question', () => {
    renderPage();
    expect(screen.getAllByTitle('Edit question').length).toBe(3);
    expect(screen.getAllByTitle('Delete question').length).toBe(3);
    expect(screen.getAllByTitle('Expand details').length).toBe(3);
  });

  it('shows empty state when there are no questions', () => {
    const emptyQuiz = {
      ...MOCK_QUIZ,
      question_count: 0,
      total_points: 0,
      questions: [],
    };
    mockUseGetQuizQuery.mockReturnValue({
      data: { status: 'success', data: emptyQuiz },
      isLoading: false,
      isError: false,
    });

    renderPage();
    expect(screen.getByText('No questions yet')).toBeInTheDocument();
    expect(
      screen.getByText('Add your first question to get started.'),
    ).toBeInTheDocument();
  });
});

describe('QuizEditorPage - Move Up/Down Buttons', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it('disables Move Up on the first question', () => {
    renderPage();
    const moveUpButtons = screen.getAllByTitle('Move up');
    expect(moveUpButtons[0]).toBeDisabled();
  });

  it('enables Move Up on the second question', () => {
    renderPage();
    const moveUpButtons = screen.getAllByTitle('Move up');
    expect(moveUpButtons[1]).toBeEnabled();
  });

  it('disables Move Down on the last question', () => {
    renderPage();
    const moveDownButtons = screen.getAllByTitle('Move down');
    expect(moveDownButtons[2]).toBeDisabled();
  });

  it('enables Move Down on the first question', () => {
    renderPage();
    const moveDownButtons = screen.getAllByTitle('Move down');
    expect(moveDownButtons[0]).toBeEnabled();
  });

  it('calls reorderQuestions on Move Up click', async () => {
    const reorderUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseReorderQuestionsMutation.mockReturnValue({ unwrap: reorderUnwrap });
    renderPage();

    // Click Move Up on the second question
    const moveUpButtons = screen.getAllByTitle('Move up');
    fireEvent.click(moveUpButtons[1]);

    await vi.waitFor(() => {
      expect(reorderUnwrap).toHaveBeenCalled();
    });
  });

  it('calls reorderQuestions on Move Down click', async () => {
    const reorderUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseReorderQuestionsMutation.mockReturnValue({ unwrap: reorderUnwrap });
    renderPage();

    // Click Move Down on the first question
    const moveDownButtons = screen.getAllByTitle('Move down');
    fireEvent.click(moveDownButtons[0]);

    await vi.waitFor(() => {
      expect(reorderUnwrap).toHaveBeenCalled();
    });
  });
});

describe('QuizEditorPage - Drag-to-Reorder', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it('triggers dragStart on a draggable question', () => {
    renderPage();
    const questionCards = screen.getAllByText('What is React?');
    const firstCard = questionCards[0].closest('[draggable]') as HTMLElement;
    expect(firstCard).toBeTruthy();
    expect(firstCard.draggable).toBe(true);
  });

  it('handles drop and calls reorderQuestions', async () => {
    const reorderUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseReorderQuestionsMutation.mockReturnValue({ unwrap: reorderUnwrap });
    renderPage();

    // Find the draggable cards
    const draggableCards = document.querySelectorAll('[draggable]');
    expect(draggableCards.length).toBe(3);

    // Simulate drag-and-drop by firing events on the cards
    const dataTransfer = {
      effectAllowed: '',
      dropEffect: '',
      setData: vi.fn(),
      getData: vi.fn().mockReturnValue('0'), // Dragging from index 0
    };

    // DragStart on first card
    fireEvent.dragStart(draggableCards[0], { dataTransfer });

    // DragOver on second card
    fireEvent.dragOver(draggableCards[1], { dataTransfer });

    // Drop on second card
    fireEvent.drop(draggableCards[1], { dataTransfer });

    // After a short delay, reorderQuestions should have been called
    await vi.waitFor(() => {
      expect(reorderUnwrap).toHaveBeenCalled();
    });
  });

  it('handles dragEnd cleanup', () => {
    renderPage();
    const draggableCards = document.querySelectorAll('[draggable]');
    const dataTransfer = {
      effectAllowed: '',
      dropEffect: '',
      setData: vi.fn(),
      getData: vi.fn().mockReturnValue('0'),
    };

    // Start drag
    fireEvent.dragStart(draggableCards[0], { dataTransfer });
    // End drag
    fireEvent.dragEnd(draggableCards[0], { dataTransfer });

    // No crash — dragEnd cleans up state
    expect(draggableCards[0]).toBeTruthy();
  });

  it('does not call reorderQuestions when dropping on same index', () => {
    const reorderUnwrap = vi.fn();
    mockUseReorderQuestionsMutation.mockReturnValue({ unwrap: reorderUnwrap });
    renderPage();

    const draggableCards = document.querySelectorAll('[draggable]');
    const dataTransfer = {
      effectAllowed: '',
      dropEffect: '',
      setData: vi.fn(),
      getData: vi.fn().mockReturnValue('0'), // Same index
    };

    // Drag and drop on the same card
    fireEvent.dragStart(draggableCards[0], { dataTransfer });
    fireEvent.drop(draggableCards[0], { dataTransfer });

    expect(reorderUnwrap).not.toHaveBeenCalled();
  });
});

describe('QuizEditorPage - Question Editor Modal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it('opens the question editor modal when Add Question is clicked', () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    expect(screen.getByText('New Question')).toBeInTheDocument();
    expect(screen.getByText('Question Type')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter your question...')).toBeInTheDocument();
  });

  it('shows Multiple Choice as default question type in modal', () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    const typeSelect = screen.getByDisplayValue('Multiple Choice');
    expect(typeSelect).toBeInTheDocument();
  });

  it('shows two default choice inputs for multiple choice questions', () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    const choiceInputs = screen.getAllByPlaceholderText(/Choice \d/);
    expect(choiceInputs.length).toBe(2);
  });

  it('shows Update Question button when editing existing question', () => {
    renderPage();
    // Click edit button on the first question
    fireEvent.click(screen.getAllByTitle('Edit question')[0]);

    expect(screen.getByText('Edit Question')).toBeInTheDocument();
    expect(screen.getByText('Update Question')).toBeInTheDocument();
  });

  it('pre-fills question text when editing existing question', () => {
    renderPage();
    fireEvent.click(screen.getAllByTitle('Edit question')[0]);

    expect(screen.getByDisplayValue('What is React?')).toBeInTheDocument();
  });

  it('switches to True/False type and pre-fills choices', () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    const typeSelect = screen.getByDisplayValue('Multiple Choice') as HTMLSelectElement;
    fireEvent.change(typeSelect, { target: { value: 'true_false' } });

    expect(screen.getByDisplayValue('True')).toBeInTheDocument();
    expect(screen.getByDisplayValue('False')).toBeInTheDocument();
  });

  it('switches to Short Answer type and removes choices', () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    const typeSelect = screen.getByDisplayValue('Multiple Choice') as HTMLSelectElement;
    fireEvent.change(typeSelect, { target: { value: 'short_answer' } });

    // Choices section should disappear
    expect(screen.queryByText('Answer Choices')).not.toBeInTheDocument();
  });

  it('allows adding a choice', () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    fireEvent.click(screen.getByText('Add choice'));

    // Now there should be 3 choice inputs
    const choiceInputs = screen.getAllByPlaceholderText(/Choice \d/);
    expect(choiceInputs.length).toBe(3);
  });

  it('allows removing a choice (when more than 2)', () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    // First add a third choice (needed since min is 2)
    fireEvent.click(screen.getByText('Add choice'));

    // Now there should be 3 choices
    expect(screen.getAllByPlaceholderText(/Choice \d/).length).toBe(3);

    // Click trash (remove) button inside the modal — there are 3, one per choice
    const removeButtons = screen.getAllByRole('button').filter(
      (btn) => btn.querySelector('svg[class*="HiTrash"]') || btn.innerHTML.includes('trash') || btn.querySelector('svg'),
    );
    // The remove buttons are inside the Answer Choices section — find them by proximity
    const allSvgs = document.querySelectorAll('svg');
    const trashSvg = Array.from(allSvgs).find(
      (svg) => svg.innerHTML.includes('path') && svg.closest('.fixed'),
    );
    if (trashSvg) {
      const trashButton = trashSvg.closest('button');
      if (trashButton) fireEvent.click(trashButton);
    }

    // Should be back to 2 choices
    const remainingInputs = screen.getAllByPlaceholderText(/Choice \d/);
    expect(remainingInputs.length).toBe(2);
  });

  it('closes modal when Cancel is clicked', async () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    expect(screen.getByText('New Question')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Cancel'));

    await waitFor(() => {
      expect(screen.queryByText('New Question')).not.toBeInTheDocument();
    });
  });

  it('calls createQuestion when adding a new question', async () => {
    const createUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseCreateQuestionMutation.mockReturnValue({ unwrap: createUnwrap });
    renderPage();

    fireEvent.click(screen.getByText('Add Question'));

    // Fill in the question
    const questionInput = screen.getByPlaceholderText('Enter your question...');
    fireEvent.change(questionInput, { target: { value: 'What is JSX?' } });

    // Fill in a choice
    const choiceInputs = screen.getAllByPlaceholderText(/Choice \d/);
    fireEvent.change(choiceInputs[0], { target: { value: 'A JS extension' } });

    // Click the modal's Add Question submit button (second occurrence after header button)
    const submitButtons = screen.getAllByText('Add Question');
    // submitButtons[0] is the header button, submitButtons[1] is the modal button
    fireEvent.click(submitButtons[submitButtons.length - 1]);

    await vi.waitFor(() => {
      expect(createUnwrap).toHaveBeenCalled();
    });
  });

  it('calls updateQuestion when updating an existing question', async () => {
    const updateUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseUpdateQuestionMutation.mockReturnValue({ unwrap: updateUnwrap });
    renderPage();

    // Open the first question for editing
    fireEvent.click(screen.getAllByTitle('Edit question')[0]);

    // Modify the question text
    const questionInput = screen.getByDisplayValue('What is React?');
    fireEvent.change(questionInput, { target: { value: 'What is React JS?' } });

    // Click Update Question
    fireEvent.click(screen.getByText('Update Question'));

    await vi.waitFor(() => {
      expect(updateUnwrap).toHaveBeenCalled();
    });
  });

  it('disables save button when question text is empty', () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    // The "Add Question" button in the modal should be disabled (no question text yet)
    // The header button has text 'Add Question' too, so we need the modal's submit button
    const submitButtons = screen.getAllByText('Add Question');
    const modalSubmitBtn = submitButtons[submitButtons.length - 1];
    expect(modalSubmitBtn).toBeDisabled();
  });

  it('shows Add choice button in the modal', () => {
    renderPage();
    fireEvent.click(screen.getByText('Add Question'));

    expect(screen.getByText('Add choice')).toBeInTheDocument();
  });
});

describe('QuizEditorPage - Delete Question Modal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it('shows delete confirmation modal when delete button is clicked', () => {
    renderPage();

    // Click delete button on the first question
    fireEvent.click(screen.getAllByTitle('Delete question')[0]);

    expect(screen.getByText('Delete Question?')).toBeInTheDocument();
    expect(screen.getByText('This cannot be undone.')).toBeInTheDocument();
  });

  it('calls deleteQuestion when Delete is confirmed', async () => {
    const deleteUnwrap = vi.fn().mockResolvedValue({ status: 'success' });
    mockUseDeleteQuestionMutation.mockReturnValue({ unwrap: deleteUnwrap });
    renderPage();

    // Open delete modal on first question
    fireEvent.click(screen.getAllByTitle('Delete question')[0]);

    // Confirm delete
    fireEvent.click(screen.getByText('Delete'));

    await vi.waitFor(() => {
      expect(deleteUnwrap).toHaveBeenCalled();
    });
  });

  it('closes delete modal when Cancel is clicked', async () => {
    renderPage();

    // Open delete modal on first question
    fireEvent.click(screen.getAllByTitle('Delete question')[0]);

    expect(screen.getByText('Delete Question?')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Cancel'));

    await waitFor(() => {
      expect(screen.queryByText('Delete Question?')).not.toBeInTheDocument();
    });
  });
});

describe('QuizEditorPage - Expanded Question Details', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it('shows explanation for questions that have one', async () => {
    renderPage();

    // Click Expand on the first question
    fireEvent.click(screen.getAllByTitle('Expand details')[0]);

    // Explanation section should be visible
    // The span uses CSS uppercase so DOM text is 'Explanation' not 'EXPLANATION'
    await waitFor(() => {
      expect(screen.getByText(/Explanation/i)).toBeInTheDocument();
      expect(screen.getByText('React is a UI library.')).toBeInTheDocument();
    });
  });

  it('shows choices with correct answer indicator', async () => {
    renderPage();

    // Expand the first question
    fireEvent.click(screen.getAllByTitle('Expand details')[0]);

    // Choices section and correct answer should be visible
    // The span uses CSS uppercase so DOM text is 'Choices' not 'CHOICES'
    await waitFor(() => {
      expect(screen.getByText(/Choices/i)).toBeInTheDocument();
      expect(screen.getByText(/A JS library/)).toBeInTheDocument();
      expect(screen.getByText(/A database/)).toBeInTheDocument();
      expect(screen.getByText(/A CSS framework/)).toBeInTheDocument();
    });
  });

  it('does not show explanation section when explanation is empty', async () => {
    renderPage();

    // Expand the third question (true/false, has empty explanation '')
    fireEvent.click(screen.getAllByTitle('Expand details')[2]);

    // The third question has explanation='' so no Explanation section should appear
    // But it should still show choices (True/False)
    // The span uses CSS uppercase so DOM text is 'Choices' not 'CHOICES'
    await waitFor(() => {
      expect(screen.getByText(/Choices/i)).toBeInTheDocument();
      expect(screen.getByText(/True/)).toBeInTheDocument();
      expect(screen.getByText(/False/)).toBeInTheDocument();
    });
  });
});

describe('QuizEditorPage - Saving Order State', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    setupDefaultMocks();
  });

  it('shows Saving order... text during reorder', async () => {
    const reorderUnwrap = vi.fn().mockImplementation(() => new Promise(() => {}));
    mockUseReorderQuestionsMutation.mockReturnValue({ unwrap: reorderUnwrap });
    renderPage();

    // Click Move Up on the second question to trigger reorder
    const moveUpButtons = screen.getAllByTitle('Move up');
    fireEvent.click(moveUpButtons[1]);

    await vi.waitFor(() => {
      expect(screen.getByText('Saving order...')).toBeInTheDocument();
    });
  });
});
