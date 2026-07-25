/**
 * Unit tests for the My Assignments page (student assignment submission workflow).
 *
 * Covers:
 * - Loading state (profile + assignments + submissions)
 * - Error state when assignments fail to load
 * - Empty state when no assignments exist
 * - Assignment list rendering (pending, submitted, graded, past due badges)
 * - Opening the submission modal and typing text
 * - Submitting text assignment
 * - File upload UI states (empty, uploading, uploaded, remove)
 * - Viewing graded feedback (grade, feedback text, submission text, file download link)
 * - Re-submitting ungraded assignments
 * - Authentication check — shows error when not signed in
 */
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

// ═══════════════════════════════════════════════════════════════════
// Mock RTK Query hooks — mutable objects for dynamic test control
// ═══════════════════════════════════════════════════════════════════

const mockUseGetProfileQuery = vi.fn();
const mockUseGetAssignmentsQuery = vi.fn();
const mockUseGetMySubmissionsQuery = vi.fn();
const mockUseSubmitAssignmentMutation = vi.fn();
const mockUseUploadAssignmentFileMutation = vi.fn();

// Shared mutable state for mutation hooks (matches RTK Query tuple pattern)
const submitMutationState = { isLoading: false };
const uploadMutationState = { isLoading: false };

vi.mock('@/store/api/endpoints/auth', () => ({
  useGetProfileQuery: (...args: unknown[]) => mockUseGetProfileQuery(...args),
}));

vi.mock('@/store/api/endpoints/assignments', () => ({
  useGetAssignmentsQuery: (...args: unknown[]) => mockUseGetAssignmentsQuery(...args),
  useGetMySubmissionsQuery: (...args: unknown[]) => mockUseGetMySubmissionsQuery(...args),
  useSubmitAssignmentMutation: () => [mockUseSubmitAssignmentMutation, submitMutationState],
  useUploadAssignmentFileMutation: () => [mockUseUploadAssignmentFileMutation, uploadMutationState],
}));

// ═══════════════════════════════════════════════════════════════════
// Test data
// ═══════════════════════════════════════════════════════════════════

const MOCK_PROFILE = { id: 1, username: 'student1', role: 'student' };

const MOCK_ASSIGNMENTS = [
  {
    id: 1,
    course: 1,
    course_title: 'React Fundamentals',
    title: 'Week 3 Homework',
    description: 'Build a component using hooks.',
    instructions: 'Create a React component that uses useState and useEffect.',
    due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days from now
    max_score: 100,
    is_published: true,
    sort_order: 0,
    created_at: '2026-07-01T00:00:00Z',
    updated_at: '2026-07-01T00:00:00Z',
    submissions_count: 0,
  },
  {
    id: 2,
    course: 2,
    course_title: 'Advanced Python',
    title: 'Final Project',
    description: 'Submit your final project.',
    instructions: 'Submit a link to your GitHub repository.',
    due_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 1 day ago (past due)
    max_score: 200,
    is_published: true,
    sort_order: 1,
    created_at: '2026-07-01T00:00:00Z',
    updated_at: '2026-07-01T00:00:00Z',
    submissions_count: 0,
  },
];

const MOCK_SUBMISSIONS = [
  {
    id: 10,
    assignment: 1,
    assignment_title: 'Week 3 Homework',
    course: 1,
    course_title: 'React Fundamentals',
    student: 1,
    student_name: 'Student One',
    text_submission: 'I built a counter component using useState.',
    file_url: '/media/assignments/myfile_abc123.pdf',
    file_name: 'myfile.pdf',
    status: 'graded' as const,
    score: 85,
    max_score: 100,
    feedback: 'Good work! Try adding useEffect for side effects.',
    graded_by: 2,
    submitted_at: '2026-07-05T00:00:00Z',
    graded_at: '2026-07-06T00:00:00Z',
    is_late: false,
  },
  {
    id: 11,
    assignment: 3,
    assignment_title: 'Quiz 1',
    course: 3,
    course_title: 'Machine Learning',
    student: 1,
    student_name: 'Student One',
    text_submission: 'Submitted answers.',
    file_url: '',
    file_name: '',
    status: 'submitted' as const,
    score: null,
    max_score: 50,
    feedback: '',
    graded_by: null,
    submitted_at: '2026-07-04T00:00:00Z',
    graded_at: null,
    is_late: false,
  },
];

const MOCK_ASSIGNMENTS_EXTRA = [
  ...MOCK_ASSIGNMENTS,
  {
    id: 3,
    course: 3,
    course_title: 'Machine Learning',
    title: 'Quiz 1',
    description: 'Weekly quiz.',
    instructions: 'Answer all questions.',
    due_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
    max_score: 50,
    is_published: true,
    sort_order: 2,
    created_at: '2026-07-01T00:00:00Z',
    updated_at: '2026-07-01T00:00:00Z',
    submissions_count: 1,
  },
];

function createAssignmentResponse(assignments: typeof MOCK_ASSIGNMENTS) {
  return { results: assignments, count: assignments.length, next: null, previous: null };
}

function createSubmissionResponse(submissions: typeof MOCK_SUBMISSIONS) {
  return { results: submissions, count: submissions.length, next: null, previous: null };
}

// ═══════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════

function createTestStore() {
  return configureStore({ reducer: {} });
}

import MyAssignmentsPage from '@/app/dashboard/my-assignments/page';

function renderPage() {
  return render(
    <Provider store={createTestStore()}>
      <MyAssignmentsPage />
    </Provider>,
  );
}

function setupDefaultMocks() {
  mockUseGetProfileQuery.mockReturnValue({
    data: MOCK_PROFILE,
    isLoading: false,
    error: undefined,
  });
  mockUseGetAssignmentsQuery.mockReturnValue({
    data: createAssignmentResponse(MOCK_ASSIGNMENTS_EXTRA),
    isLoading: false,
    error: undefined,
  });
  mockUseGetMySubmissionsQuery.mockReturnValue({
    data: createSubmissionResponse(MOCK_SUBMISSIONS),
    isLoading: false,
    error: undefined,
    refetch: vi.fn(),
  });
  const unwrapFn = vi.fn().mockResolvedValue({ status: 'success', data: { id: 99 } });
  mockUseSubmitAssignmentMutation.mockReturnValue({ unwrap: unwrapFn });
}

// ═══════════════════════════════════════════════════════════════════
// Tests
// ═══════════════════════════════════════════════════════════════════

describe('My Assignments Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ── Loading States ──

  it('shows profile loading skeleton while profile is loading', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: undefined,
    });
    // These hooks are called before the profileLoading early return, so they must be mocked
    mockUseGetAssignmentsQuery.mockReturnValue({ data: undefined, isLoading: false, error: undefined });
    mockUseGetMySubmissionsQuery.mockReturnValue({ data: undefined, isLoading: false, error: undefined, refetch: vi.fn() });

    const { container } = renderPage();

    // Should NOT show the page heading
    expect(screen.queryByText('My Assignments')).not.toBeInTheDocument();
    // LoadingSkeleton should be rendered
    expect(container.querySelector('.animate-pulse')).toBeTruthy();
  });

  it('shows card loading skeleton while assignments/submissions are loading', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: undefined,
    });

    const { container } = renderPage();

    // Page heading should be visible
    expect(screen.getByText('My Assignments')).toBeInTheDocument();
    // LoadingSkeleton should be rendered
    expect(container.querySelector('.animate-pulse')).toBeTruthy();
  });

  // ── Auth Check ──

  it('shows error state when user is not signed in', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Not authenticated'),
    });

    renderPage();

    expect(screen.getByText(/Please sign in to view your assignments/i)).toBeInTheDocument();
  });

  // ── Error State ──

  it('shows error state when assignments fail to load', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Failed to load'),
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: undefined,
    });

    renderPage();

    expect(screen.getByText('Failed to load assignments.')).toBeInTheDocument();
  });

  // ── Empty State ──

  it('shows empty state when no assignments exist', () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();

    expect(screen.getByText('No assignments yet')).toBeInTheDocument();
    expect(
      screen.getByText(/Your instructors haven't posted any assignments yet/i),
    ).toBeInTheDocument();
  });

  // ── Assignment List Rendering ──

  it('renders the page heading and description', () => {
    setupDefaultMocks();
    renderPage();

    expect(screen.getByText('My Assignments')).toBeInTheDocument();
    expect(screen.getByText('View and submit your course assignments')).toBeInTheDocument();
  });

  it('renders all assignment cards with titles', () => {
    setupDefaultMocks();
    renderPage();

    expect(screen.getByText('Week 3 Homework')).toBeInTheDocument();
    expect(screen.getByText('Final Project')).toBeInTheDocument();
    expect(screen.getByText('Quiz 1')).toBeInTheDocument();
  });

  it('renders course titles on assignment cards', () => {
    setupDefaultMocks();
    renderPage();

    expect(screen.getByText('React Fundamentals')).toBeInTheDocument();
    expect(screen.getByText('Advanced Python')).toBeInTheDocument();
    expect(screen.getByText('Machine Learning')).toBeInTheDocument();
  });

  // ── Status Badges ──

  it('shows graded badge with score for graded submissions', () => {
    setupDefaultMocks();
    renderPage();

    // Assignment 1 (Week 3 Homework) has a graded submission
    expect(screen.getByText('85/100')).toBeInTheDocument();
  });

  it('shows submitted badge for ungraded submissions', () => {
    setupDefaultMocks();
    renderPage();

    // Assignment 3 (Quiz 1) has a submitted (not graded) submission
    expect(screen.getByText('Submitted')).toBeInTheDocument();
  });

  it('shows past due badge for overdue assignments without submissions', () => {
    setupDefaultMocks();
    renderPage();

    // Assignment 2 (Final Project) is past due with no submission
    expect(screen.getByText('Past Due')).toBeInTheDocument();
  });

  it('shows pending badge for future assignments without submissions', () => {
    // Override: remove the submission for assignment 1 so it shows as pending
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse(MOCK_ASSIGNMENTS),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();

    // Assignment 1 (Week 3 Homework) has future due date and no submission
    expect(screen.getByText('Pending')).toBeInTheDocument();
  });

  // ── Action Buttons ──

  it('shows View Feedback button for graded submissions', () => {
    setupDefaultMocks();
    renderPage();

    // Assignment 1 is graded
    const viewFeedbackButtons = screen.getAllByText('View Feedback');
    expect(viewFeedbackButtons.length).toBeGreaterThanOrEqual(1);
  });

  it('shows Submit button for pending assignments', () => {
    // Use assignments where only pending ones exist
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse(MOCK_ASSIGNMENTS),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();

    // Assignment 1 has future date and no submission → "Submit" button
    const submitButtons = screen.getAllByText('Submit');
    expect(submitButtons.length).toBeGreaterThanOrEqual(1);
  });

  it('shows Re-submit button for submitted but ungraded assignments', () => {
    setupDefaultMocks();
    renderPage();

    // Assignment 3 (Quiz 1) has submitted status (not graded)
    const resubmitButtons = screen.getAllByText('Re-submit');
    expect(resubmitButtons.length).toBeGreaterThanOrEqual(1);
  });

  // ── Submission Modal ──

  it('opens submission modal when Submit is clicked', async () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();

    // Click Submit on the first assignment
    fireEvent.click(screen.getByText('Submit'));

    // Modal should open with assignment details
    await vi.waitFor(() => {
      // The assignment title appears twice (card + modal header), use getAllByText for multiple matches
      const titles = screen.getAllByText('Week 3 Homework');
      expect(titles.length).toBeGreaterThanOrEqual(2);
      expect(
        screen.getByText(/Create a React component that uses useState and useEffect/),
      ).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/Write or paste your assignment submission/i)).toBeInTheDocument();
    });
  });

  it('shows the Submit Assignment button in the modal', async () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByText('Submit Assignment')).toBeInTheDocument();
    });
  });

  it('shows instructions in the submission modal', async () => {
    setupDefaultMocks();
    renderPage();

    // Click View Feedback on graded assignment (opens modal)
    fireEvent.click(screen.getAllByText('View Feedback')[0]);

    await vi.waitFor(() => {
      expect(screen.getByText('Instructions')).toBeInTheDocument();
      expect(
        screen.getByText(/Create a React component that uses useState and useEffect/),
      ).toBeInTheDocument();
    });
  });

  it('shows due date in the submission modal', async () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByText(/Due:/)).toBeInTheDocument();
      expect(screen.getByText(/Max Score:/)).toBeInTheDocument();
    });
  });

  // ── Text Submission ──

  it('calls submitAssignment with text when submitting', async () => {
    const unwrapFn = vi.fn().mockResolvedValue({ status: 'success', data: { id: 99 } });
    mockUseSubmitAssignmentMutation.mockReturnValue({ unwrap: unwrapFn });
    submitMutationState.isLoading = false;

    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
      refetch: vi.fn(),
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByPlaceholderText(/Write or paste your assignment submission/i)).toBeInTheDocument();
    });

    // Type text in the submission textarea
    const textarea = screen.getByPlaceholderText(/Write or paste your assignment submission/i);
    fireEvent.change(textarea, { target: { value: 'My homework submission text.' } });

    // Click Submit Assignment
    fireEvent.click(screen.getByText('Submit Assignment'));

    await vi.waitFor(() => {
      expect(mockUseSubmitAssignmentMutation).toHaveBeenCalledWith({
        assignmentId: 1,
        data: {
          text_submission: 'My homework submission text.',
          file_url: '',
          file_name: '',
        },
      });
    });
  });

  // ── File Upload UI ──

  it('shows file upload area with click to upload text', async () => {
    // Use a pending assignment (no submissions, future due date) so Submit button exists
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByText(/Click to upload a file/i)).toBeInTheDocument();
    });
  });

  it('shows upload error when file upload fails', async () => {
    // Mock upload mutation to reject
    const uploadUnwrap = vi.fn().mockRejectedValue({
      data: { message: 'File too large. Maximum size is 50 MB.' },
    });
    mockUseUploadAssignmentFileMutation.mockReturnValue({ unwrap: uploadUnwrap });
    uploadMutationState.isLoading = false;

    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByText(/Click to upload a file/i)).toBeInTheDocument();
    });

    // Trigger file upload which will fail
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      const file = new File(['test'], 'large_file.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });
    }

    await vi.waitFor(() => {
      expect(screen.getByText(/File too large/i)).toBeInTheDocument();
    });
  });

  it('disables submit button when both text and file are empty', async () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByPlaceholderText(/Write or paste your assignment submission/i)).toBeInTheDocument();
    });

    // Submit Assignment button should be disabled when both text and file are empty
    const submitBtn = screen.getByText('Submit Assignment') as HTMLButtonElement;
    expect(submitBtn.disabled).toBe(true);
  });

  it('enables submit button when text is typed', async () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByPlaceholderText(/Write or paste your assignment submission/i)).toBeInTheDocument();
    });

    // Submit button should be disabled initially
    const submitBtn = screen.getByText('Submit Assignment') as HTMLButtonElement;
    expect(submitBtn.disabled).toBe(true);

    // Type text — button should become enabled
    const textarea = screen.getByPlaceholderText(/Write or paste your assignment submission/i);
    fireEvent.change(textarea, { target: { value: 'My submission' } });

    expect(submitBtn.disabled).toBe(false);
  });

  it('shows uploaded file info after file upload', async () => {
    // Mock the upload mutation to return a successful response
    const uploadUnwrap = vi.fn().mockResolvedValue({
      file_url: '/media/assignments/myfile_abc.pdf',
      file_name: 'myfile.pdf',
    });
    mockUseUploadAssignmentFileMutation.mockReturnValue({ unwrap: uploadUnwrap });
    uploadMutationState.isLoading = false;

    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByText(/Click to upload a file/i)).toBeInTheDocument();
    });

    // Simulate selecting a file by firing the onChange on the hidden input
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      const file = new File(['test'], 'myfile.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });
    }

    await vi.waitFor(() => {
      expect(screen.getByText('myfile.pdf')).toBeInTheDocument();
      expect(screen.getByText(/Uploaded ✓/)).toBeInTheDocument();
    });
  });

  it('shows Remove button after file upload', async () => {
    const uploadUnwrap = vi.fn().mockResolvedValue({
      file_url: '/media/assignments/myfile_abc.pdf',
      file_name: 'myfile.pdf',
    });
    mockUseUploadAssignmentFileMutation.mockReturnValue({ unwrap: uploadUnwrap });
    uploadMutationState.isLoading = false;

    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByText(/Click to upload a file/i)).toBeInTheDocument();
    });

    // Upload a file
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    if (fileInput) {
      const file = new File(['test'], 'myfile.pdf', { type: 'application/pdf' });
      fireEvent.change(fileInput, { target: { files: [file] } });
    }

    await vi.waitFor(() => {
      expect(screen.getByText('myfile.pdf')).toBeInTheDocument();
    });

    // Remove button should be visible
    expect(screen.getByText('Remove')).toBeInTheDocument();

    // Click Remove
    fireEvent.click(screen.getByText('Remove'));

    await vi.waitFor(() => {
      expect(screen.queryByText('myfile.pdf')).not.toBeInTheDocument();
      expect(screen.getByText(/Click to upload a file/i)).toBeInTheDocument();
    });
  });

  // ── Graded Feedback Display ──

  it('shows grade, feedback, and submission text when viewing graded feedback', async () => {
    setupDefaultMocks();
    renderPage();

    // Click View Feedback on the graded assignment (Assignment 1)
    fireEvent.click(screen.getAllByText('View Feedback')[0]);

    await vi.waitFor(() => {
      // Grade
      expect(screen.getByText(/Grade:/)).toBeInTheDocument();
      expect(screen.getByText('85/100')).toBeInTheDocument();

      // Feedback
      expect(screen.getByText('Feedback:')).toBeInTheDocument();
      expect(
        screen.getByText(/Good work! Try adding useEffect for side effects/),
      ).toBeInTheDocument();

      // Submission text
      expect(screen.getByText('Your submission:')).toBeInTheDocument();
      expect(
        screen.getByText('I built a counter component using useState.'),
      ).toBeInTheDocument();
    });
  });

  it('shows file download link in graded feedback', async () => {
    setupDefaultMocks();
    renderPage();

    fireEvent.click(screen.getAllByText('View Feedback')[0]);

    await vi.waitFor(() => {
      // File download link
      const fileLink = screen.getByText('📎 myfile.pdf');
      expect(fileLink).toBeInTheDocument();
      expect(fileLink.closest('a')).toHaveAttribute('href', '/media/assignments/myfile_abc123.pdf');
    });
  });

  // ── Re-submit ──

  it('pre-fills text when clicking Re-submit on ungraded submission', async () => {
    setupDefaultMocks();
    renderPage();

    // Click Re-submit on Assignment 3 (submitted but not graded)
    fireEvent.click(screen.getAllByText('Re-submit')[0]);

    await vi.waitFor(() => {
      const textarea = screen.getByPlaceholderText(/Write or paste your assignment submission/i) as HTMLTextAreaElement;
      expect(textarea.value).toBe('Submitted answers.');
    });
  });

  // ── Cancel ──

  it('closes modal when clicking the backdrop overlay', async () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByPlaceholderText(/Write or paste your assignment submission/i)).toBeInTheDocument();
    });

    // Click the modal backdrop (the fixed overlay behind the modal card)
    const backdrop = document.querySelector('.fixed.inset-0');
    if (backdrop) fireEvent.click(backdrop);

    await vi.waitFor(() => {
      expect(screen.queryByPlaceholderText(/Write or paste your assignment submission/i)).not.toBeInTheDocument();
    });
  });

  it('closes modal when the close button is clicked', async () => {
    mockUseGetProfileQuery.mockReturnValue({
      data: MOCK_PROFILE,
      isLoading: false,
      error: undefined,
    });
    mockUseGetAssignmentsQuery.mockReturnValue({
      data: createAssignmentResponse([MOCK_ASSIGNMENTS[0]]),
      isLoading: false,
      error: undefined,
    });
    mockUseGetMySubmissionsQuery.mockReturnValue({
      data: createSubmissionResponse([]),
      isLoading: false,
      error: undefined,
    });

    renderPage();
    fireEvent.click(screen.getByText('Submit'));

    await vi.waitFor(() => {
      expect(screen.getByPlaceholderText(/Write or paste your assignment submission/i)).toBeInTheDocument();
    });

    // Click Cancel button in modal footer
    fireEvent.click(screen.getByText('Cancel'));

    await vi.waitFor(() => {
      expect(screen.queryByPlaceholderText(/Write or paste your assignment submission/i)).not.toBeInTheDocument();
    });
  });
});
